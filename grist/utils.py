import asyncio
import inspect


async def maybe_await(value):
    while inspect.isawaitable(value):
        value = await value
    return value


def run_async(coro):
    if inspect.iscoroutinefunction(coro):
        coro = coro()
    asyncio.get_running_loop().run_until_complete(coro)


def skip_traceback_internals(tb):
    filename = (lambda: 0).__code__.co_filename
    original = tb
    while tb and tb.tb_frame.f_code.co_filename == filename:
        tb = tb.tb_next
    if tb:
        return tb
    else:
        return original
