"""
Async Bridge for PyQt6
Integrates async CardForge services with PyQt6's event loop
"""

import asyncio
from typing import Callable, Any, TypeVar, Coroutine, Optional
from functools import wraps
import sys

from PyQt6.QtCore import QObject, pyqtSignal, QThread, pyqtSlot

T = TypeVar('T')


class AsyncWorker(QThread):
    """
    Worker thread that runs async coroutines.

    Signals:
        finished: Emitted when coroutine completes successfully (result)
        error: Emitted when coroutine raises an exception (exception)
    """

    finished = pyqtSignal(object)  # result
    error = pyqtSignal(Exception)  # exception

    def __init__(self, coro: Coroutine):
        super().__init__()
        self.coro = coro
        self.loop: Optional[asyncio.AbstractEventLoop] = None

    def run(self):
        """Run the coroutine in this thread's event loop."""
        try:
            # Create new event loop for this thread
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

            # Run the coroutine
            result = self.loop.run_until_complete(self.coro)

            # Emit success signal
            self.finished.emit(result)

        except Exception as e:
            # Emit error signal
            self.error.emit(e)

        finally:
            # Clean up
            if self.loop:
                self.loop.close()


class AsyncBridge(QObject):
    """
    Bridge between async CardForge services and PyQt6.

    This provides a clean interface for running async operations
    without blocking the Qt event loop.

    Example:
        bridge = AsyncBridge()
        bridge.run_async(
            collection_service.get_stats(collection_id),
            on_success=self.handle_stats,
            on_error=self.handle_error
        )
    """

    def __init__(self):
        super().__init__()
        self.workers: list[AsyncWorker] = []

    def run_async(
        self,
        coro: Coroutine[Any, Any, T],
        on_success: Optional[Callable[[T], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None
    ) -> AsyncWorker:
        """
        Run an async coroutine in a background thread.

        Args:
            coro: The coroutine to run
            on_success: Callback when coroutine completes successfully
            on_error: Callback when coroutine raises an exception

        Returns:
            AsyncWorker instance (can be used to stop/track the operation)
        """
        worker = AsyncWorker(coro)

        # Connect signals
        if on_success:
            worker.finished.connect(on_success)

        if on_error:
            worker.error.connect(on_error)

        # Clean up when done
        worker.finished.connect(lambda: self._cleanup_worker(worker))
        worker.error.connect(lambda: self._cleanup_worker(worker))

        # Track and start
        self.workers.append(worker)
        worker.start()

        return worker

    def _cleanup_worker(self, worker: AsyncWorker):
        """Remove completed worker from tracking list."""
        if worker in self.workers:
            self.workers.remove(worker)

    def cancel_all(self):
        """Cancel all running workers."""
        for worker in self.workers[:]:  # Copy list to avoid modification during iteration
            if worker.isRunning():
                worker.quit()
                worker.wait()
        self.workers.clear()


# Decorator for async methods in Qt widgets
def async_slot(*args):
    """
    Decorator to make async methods work as Qt slots.

    Usage:
        class MyWidget(QWidget):
            def __init__(self):
                self.async_bridge = AsyncBridge()

            @async_slot()
            async def load_data(self):
                data = await some_async_function()
                return data

            def on_button_clicked(self):
                self.async_bridge.run_async(
                    self.load_data(),
                    on_success=self.handle_data
                )
    """
    def decorator(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable:
        @wraps(func)
        def wrapper(self, *method_args, **method_kwargs):
            # This returns a coroutine that can be passed to AsyncBridge
            return func(self, *method_args, **method_kwargs)
        return wrapper

    # Handle both @async_slot and @async_slot()
    if len(args) == 1 and callable(args[0]):
        return decorator(args[0])
    return decorator
