import asyncio
import threading
import time


def _start_async():
    loop = asyncio.new_event_loop()
    threading.Thread(target=loop.run_forever).start()
    return loop


_loop = _start_async()


# Submits awaitable to the event loop, but *doesn't* wait for it to
# complete. Returns a concurrent.futures.Future which *may* be used to
# wait for and retrieve the result (or exception, if one was raised)
def submit_async(awaitable):
    time.sleep(3)
    return asyncio.run_coroutine_threadsafe(awaitable, _loop)


def stop_async():
    _loop.call_soon_threadsafe(_loop.stop)
