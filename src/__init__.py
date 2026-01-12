"""DEPRECATED: Legacy source directory.

This module is deprecated. Please use the cardforge package instead.

Migration Guide:
    # Old imports (DEPRECATED)
    from src.database import ...
    from src.services import ...
    
    # New imports (USE THESE)
    from cardforge.data import ...          # Database/repositories
    from cardforge.core import ...          # Models/types/exceptions
    from cardforge.services import ...      # Business logic
    from cardforge.integrations import ...  # External APIs

See docs/architecture/ARCHITECTURE.md for the new structure.
"""

import warnings

warnings.warn(
    "The 'src' package is deprecated. Use 'cardforge' package instead. "
    "See docs/architecture/ARCHITECTURE.md for migration guide.",
    DeprecationWarning,
    stacklevel=2
)

__version__ = "0.1.0"
__author__ = "Hunter"
