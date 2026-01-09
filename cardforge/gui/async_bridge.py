"""
Async Bridge for Tkinter GUI
Bridges async CardForge services with synchronous Tkinter
"""

import asyncio
import threading
from typing import Callable, Any, Optional, TypeVar, Coroutine
from functools import wraps

T = TypeVar('T')


class AsyncBridge:
    """
    Bridge between async services and synchronous Tkinter GUI.

    Runs an asyncio event loop in a background thread and provides
    utilities to call async functions from the GUI thread.
    """

    def __init__(self):
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.thread: Optional[threading.Thread] = None
        self._started = False

    def start(self):
        """Start the async event loop in a background thread."""
        if self._started:
            return

        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        self._started = True

    def _run_loop(self):
        """Run the asyncio event loop."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def run_async(
        self,
        coro: Coroutine[Any, Any, T],
        callback: Optional[Callable[[T], None]] = None,
        error_callback: Optional[Callable[[Exception], None]] = None
    ):
        """
        Run an async coroutine and optionally call callback with result.

        Args:
            coro: The coroutine to run
            callback: Called with the result when complete
            error_callback: Called with exception if error occurs
        """
        if not self.loop:
            raise RuntimeError("AsyncBridge not started")

        def _done_callback(future: asyncio.Future):
            try:
                result = future.result()
                if callback:
                    callback(result)
            except Exception as e:
                if error_callback:
                    error_callback(e)
                else:
                    print(f"Async error: {e}")

        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        future.add_done_callback(_done_callback)

    def run_async_blocking(self, coro: Coroutine[Any, Any, T], timeout: float = 30.0) -> T:
        """
        Run an async coroutine and block until complete.

        Args:
            coro: The coroutine to run
            timeout: Maximum time to wait

        Returns:
            The result of the coroutine

        Raises:
            TimeoutError: If the operation times out
            Exception: Any exception from the coroutine
        """
        if not self.loop:
            raise RuntimeError("AsyncBridge not started")

        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result(timeout=timeout)

    def stop(self):
        """Stop the async event loop."""
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)
        self._started = False


def async_task(bridge_attr: str = 'async_bridge'):
    """
    Decorator to make calling async methods easier from GUI.

    Usage:
        class MyWidget:
            def __init__(self, async_bridge):
                self.async_bridge = async_bridge

            @async_task()
            async def load_data(self):
                return await some_async_function()
    """
    def decorator(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            bridge: AsyncBridge = getattr(self, bridge_attr)
            coro = func(self, *args, **kwargs)
            return bridge.run_async_blocking(coro)
        return wrapper
    return decorator
