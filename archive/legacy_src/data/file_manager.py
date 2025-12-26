"""File management utilities."""

from pathlib import Path
from typing import List, Optional
import shutil
from datetime import datetime


class FileManager:
    """Handles file operations for MyManaBox."""
    
    @staticmethod
    def ensure_directory(directory: str) -> Path:
        """Ensure directory exists, create if it doesn't."""
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def create_backup(file_path: str, backup_dir: str = "backups") -> Optional[str]:
        """Create a backup of a file."""
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                return None
            
            # Create backup directory
            backup_path = FileManager.ensure_directory(backup_dir)
            
            # Generate backup filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"{source_path.stem}_{timestamp}{source_path.suffix}"
            backup_file = backup_path / backup_filename
            
            # Copy file
            shutil.copy2(source_path, backup_file)
            return str(backup_file)
            
        except Exception:
            return None
    
    @staticmethod
    def list_backups(file_path: str, backup_dir: str = "backups") -> List[str]:
        """List available backups for a file."""
        try:
            source_path = Path(file_path)
            backup_path = Path(backup_dir)
            
            if not backup_path.exists():
                return []
            
            # Find backup files matching the pattern
            pattern = f"{source_path.stem}_*{source_path.suffix}"
            backups = list(backup_path.glob(pattern))
            
            return [str(backup) for backup in sorted(backups)]
            
        except Exception:
            return []
    
    @staticmethod
    def restore_backup(backup_file: str, target_file: str) -> bool:
        """Restore a backup file."""
        try:
            backup_path = Path(backup_file)
            target_path = Path(target_file)
            
            if not backup_path.exists():
                return False
            
            # Create target directory if needed
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy backup to target
            shutil.copy2(backup_path, target_path)
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def cleanup_old_backups(backup_dir: str = "backups", keep_count: int = 10) -> int:
        """Clean up old backup files, keeping only the most recent ones."""
        try:
            backup_path = Path(backup_dir)
            if not backup_path.exists():
                return 0
            
            # Group backups by base filename
            backup_groups = {}
            for backup_file in backup_path.glob("*_*.*"):
                # Extract base name (everything before the timestamp)
                parts = backup_file.stem.split('_')
                if len(parts) >= 2:
                    base_name = '_'.join(parts[:-1])  # Everything except the timestamp
                    if base_name not in backup_groups:
                        backup_groups[base_name] = []
                    backup_groups[base_name].append(backup_file)
            
            cleaned_count = 0
            for base_name, backups in backup_groups.items():
                # Sort by modification time (newest first)
                backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                
                # Remove old backups
                for old_backup in backups[keep_count:]:
                    try:
                        old_backup.unlink()
                        cleaned_count += 1
                    except:
                        pass
            
            return cleaned_count
            
        except Exception:
            return 0
