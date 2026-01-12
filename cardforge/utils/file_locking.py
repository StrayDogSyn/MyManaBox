"""
File locking utility for safe concurrent file access.
Implements a PID-based lock file mechanism with timeouts and stale lock detection.
"""

import os
import time
import logging
import contextlib
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class FileLockError(Exception):
    """Raised when a file lock cannot be acquired."""
    pass

class FileLock:
    """
    A file-based lock for ensuring exclusive access to a resource.
    
    Attributes:
        lock_file (Path): Path to the lock file.
        timeout (float): Maximum time to wait for lock in seconds.
        retry_interval (float): Time to sleep between retries.
    """
    
    def __init__(self, target_file: Path, timeout: float = 10.0, retry_interval: float = 0.1):
        """
        Initialize the lock.
        
        Args:
            target_file: The file to lock access to.
            timeout: Max wait time in seconds.
            retry_interval: Poll interval in seconds.
        """
        self.target_file = Path(target_file)
        self.lock_file = self.target_file.with_suffix(self.target_file.suffix + '.lock')
        self.timeout = timeout
        self.retry_interval = retry_interval
        self._is_locked = False
        
    def acquire(self) -> None:
        """
        Acquire the lock.
        
        Raises:
            FileLockError: If lock cannot be acquired within timeout.
        """
        start_time = time.time()
        
        while True:
            try:
                # Exclusive creation - fails if file exists
                # This is atomic on most OSes
                with open(self.lock_file, 'x') as f:
                    f.write(f"{os.getpid()},{time.time()}")
                    f.flush()
                    os.fsync(f.fileno())
                
                self._is_locked = True
                logger.debug(f"Lock acquired for {self.target_file}")
                return
                
            except FileExistsError:
                # Check for stale lock
                if self._is_stale():
                    logger.warning(f"Removing stale lock file: {self.lock_file}")
                    self._force_release()
                    continue
                
                # Check timeout
                if time.time() - start_time > self.timeout:
                    raise FileLockError(f"Timeout waiting for lock: {self.lock_file}")
                
                time.sleep(self.retry_interval)
                
            except OSError as e:
                raise FileLockError(f"Error acquiring lock: {e}")

    def release(self) -> None:
        """Release the lock."""
        if not self._is_locked:
            return
            
        try:
            if self.lock_file.exists():
                os.remove(self.lock_file)
                self._is_locked = False
                logger.debug(f"Lock released for {self.target_file}")
        except OSError as e:
            logger.error(f"Error releasing lock: {e}")

    def _is_stale(self) -> bool:
        """Check if the current lock is stale (process died or timeout exceeded)."""
        try:
            if not self.lock_file.exists():
                return False
                
            content = self.lock_file.read_text().strip()
            if not content:
                return True # Empty lock file is invalid
                
            parts = content.split(',')
            if len(parts) != 2:
                return True # Invalid format
                
            pid, timestamp = int(parts[0]), float(parts[1])
            
            # Check if process exists (local only)
            # This is tricky cross-platform, so we mainly rely on timestamp
            # If lock is older than timeout + buffer, consider it stale
            if time.time() - timestamp > (self.timeout * 2):
                return True
                
            return False
            
        except (ValueError, OSError):
            return True # Error reading means probably broken/stale

    def _force_release(self) -> None:
        """Force remove the lock file."""
        try:
            if self.lock_file.exists():
                os.remove(self.lock_file)
        except OSError:
            pass

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
