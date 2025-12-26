"""
CardForge Base Model
Common functionality for all models
"""

from typing import TypeVar, Type, Optional, Any, Dict
from datetime import datetime
from decimal import Decimal
import json
from pydantic import BaseModel as PydanticBaseModel, ConfigDict


T = TypeVar('T', bound='BaseModel')


class BaseModel(PydanticBaseModel):
    """
    Base model class with common functionality.
    
    Features:
    - JSON serialization with datetime/Decimal handling
    - Database row conversion
    - Dictionary conversion
    """
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
        validate_assignment=True,
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary with JSON-safe values."""
        return json.loads(self.model_dump_json())
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create model from dictionary."""
        return cls.model_validate(data)
    
    @classmethod
    def from_row(cls: Type[T], row: Any) -> Optional[T]:
        """
        Create model from database row (aiosqlite.Row or dict-like).
        
        Args:
            row: Database row with column access by name
        
        Returns:
            Model instance or None if row is None
        """
        if row is None:
            return None
        
        # Convert row to dict, handling sqlite Row objects
        if hasattr(row, 'keys'):
            data = dict(row)
        else:
            data = dict(row._asdict()) if hasattr(row, '_asdict') else dict(row)
        
        # Parse JSON fields
        for key, value in data.items():
            if isinstance(value, str) and value.startswith(('[', '{')):
                try:
                    data[key] = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    pass
        
        return cls.model_validate(data)
    
    # Fields that map to separate tables (not columns)
    _relationship_fields: set[str] = set()
    
    def to_db_dict(self) -> Dict[str, Any]:
        """
        Convert model to dictionary suitable for database insertion.
        
        Serializes nested objects to JSON strings.
        Excludes computed fields and relationship fields.
        """
        # Exclude computed fields and relationship fields
        exclude_fields = set(getattr(self, '_relationship_fields', set()))
        
        for field_name, field_info in self.model_fields.items():
            if hasattr(field_info, 'computed') and field_info.computed:
                exclude_fields.add(field_name)
        
        # Also exclude any property fields not in model_fields
        data = self.model_dump(
            exclude_none=False, 
            exclude=exclude_fields,
            exclude_unset=False
        )
        
        # Filter out computed_field decorated properties
        field_names = set(self.model_fields.keys()) - exclude_fields
        data = {k: v for k, v in data.items() if k in field_names}
        
        for key, value in list(data.items()):
            # Skip nested model objects (relationships stored in separate tables)
            if isinstance(value, list) and value and isinstance(value[0], BaseModel):
                del data[key]
            elif isinstance(value, BaseModel):
                del data[key]
            elif isinstance(value, (list, dict)):
                data[key] = json.dumps(value)
            elif isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, Decimal):
                data[key] = float(value)
        
        return data


class TimestampMixin(PydanticBaseModel):
    """Mixin for models with timestamps."""
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


def json_serial(obj: Any) -> Any:
    """JSON serializer for objects not serializable by default."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    if hasattr(obj, 'value'):  # Enum
        return obj.value
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    raise TypeError(f"Type {type(obj)} not serializable")
