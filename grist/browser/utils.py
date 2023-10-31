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
