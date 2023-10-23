import asyncio
import builtins
import inspect
import sys
import traceback
import warnings

import IPython.core.display_functions
import IPython.display
from IPython import get_ipython
import js  # noqa
import pyodide_js  # noqa
from pyodide.ffi import to_js, create_proxy  # noqa

original_print = print
original_display = IPython.display.display


async def maybe_await(value):
    while inspect.isawaitable(value):
        value = await value
    return value


def run_async(coro):
    if inspect.iscoroutinefunction(coro):
        coro = coro()
    asyncio.get_running_loop().run_until_complete(coro)


class ComlinkProxy:
    def __init__(self, proxy, name=None):
        self._proxy = proxy
        self._name = name

    def __getattr__(self, name):
        return ComlinkProxy(getattr(self._proxy, name), name)

    async def __call__(self, *args, **kwargs):
        if any(callable(arg) for arg in args):
            assert len(args) == 1 and not kwargs, "Only one argument is supported for callbacks"
            [callback] = args

            async def wrapper(*callback_args):
                callback_args = [
                    a.to_py() if hasattr(a, "to_py") else a
                    for a in callback_args
                ]
                await maybe_await(callback(*callback_args))

            js._grist_tmp1 = self._proxy
            js._grist_tmp2 = js.Comlink.proxy(create_proxy(wrapper))
            result = await js.eval("_grist_tmp1(_grist_tmp2)")
        else:
            args = [
                to_js(arg, dict_converter=js.Object.fromEntries)
                for arg in args
            ]
            kwargs = {
                key: to_js(value, dict_converter=js.Object.fromEntries)
                for key, value in kwargs.items()
            }
            result = await self._proxy(*args, **kwargs)

        if self._name == "getTable":
            result = ComlinkProxy(result)
        elif hasattr(result, "to_py"):
            result = result.to_py()
        return result


js.importScripts("https://unpkg.com/comlink@4.4.1/dist/umd/comlink.js")
pyodide_js.registerComlink(js.Comlink)

get_ipython().display_formatter.formatters['text/plain'].for_type(
    str, lambda string, pp, cycle: pp.text(string)
)

lock = asyncio.Lock()


def wrap_with_display(func):
    handles = [original_display(display_id=True) for _ in range(45)]

    def in_wrapper_frame():
        frame = inspect.currentframe().f_back
        while frame:
            if frame.f_code == inner_wrapper.__code__:
                return True
            frame = frame.f_back

    async def inner_wrapper(*args):
        for handle in handles:
            handle.update({}, raw=True)

        i = 0

        def displayer(*objs, **kwargs):
            nonlocal i
            if not in_wrapper_frame():
                return original_display(*objs, **kwargs)

            for obj in objs:
                if i == len(handles) - 1:
                    handles[i].update("Too many display calls!")
                else:
                    handles[i].update(obj, **kwargs)
                    i += 1

        def new_print(*print_args, sep=' ', end='\n', **kwargs):
            if not in_wrapper_frame():
                return original_print(*print_args, sep=sep, end=end, **kwargs)

            if len(print_args) == 1 and end == '\n':
                displayer(print_args[0])
            else:
                displayer(sep.join(map(str, print_args)) + end)

        async with lock:
            builtins.print = new_print
            patched_modules = []
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                for module in list(sys.modules.values()):
                    try:
                        if module != IPython.core.display_functions and getattr(module, "display",
                                                                                "") == original_display:
                            module.display = displayer
                            patched_modules.append(module)
                    except:
                        pass

            try:
                await maybe_await(func(*args))
            except Exception as e:
                displayer("".join(traceback.format_exception(
                    e.__class__, e, skip_traceback_internals(e.__traceback__)
                )))
            finally:
                builtins.print = original_print
                for module in patched_modules:
                    module.display = original_display

    return inner_wrapper


callback_registry = dict(
    onRecords={},
    onRecord={},
)


async def on_records_dispatch(*_):
    records = await grist.raw.fetchSelectedTable(keepEncoded=True)
    for callback in callback_registry['onRecords'].values():
        await callback(records)


async def on_record_dispatch(record, *_rest):
    if not record:
        return

    record = await grist.raw.fetchSelectedRecord(record['id'], keepEncoded=True)
    for callback in callback_registry['onRecord'].values():
        await callback(record)


last_registering_cell_filename = None


def check_registering_cell():
    global last_registering_cell_filename
    frame = inspect.currentframe().f_back
    while True:
        code = frame.f_code
        if code.co_filename == last_registering_cell_filename:
            raise Exception("Only one callback can be registered per cell.")
        if code.co_name == "<module>" and code.co_filename.startswith("<ipython-input-"):
            last_registering_cell_filename = code.co_filename
            break
        frame = frame.f_back


async def add_to_callback_registry(name, callback):
    registry = callback_registry[name]
    if callback.__name__ in registry:
        print(f"A callback named {callback.__name__} has already been registered, so I'm assuming "
              "you want to replace it. If not, please rename the function.\n")
    wrapped = wrap_with_display(callback)
    if not registry:
        dispatch = dict(
            onRecords=on_records_dispatch,
            onRecord=on_record_dispatch,
        )[name]
        method = getattr(grist.raw, name)
        await method(dispatch)
    registry[callback.__name__] = wrapped
    return wrapped


def skip_traceback_internals(tb):
    filename = (lambda: 0).__code__.co_filename
    original = tb
    while tb and tb.tb_frame.f_code.co_filename == filename:
        tb = tb.tb_next
    if tb:
        return tb
    else:
        return original


class Grist:
    def __init__(self):
        self.raw = ComlinkProxy(js.Comlink.wrap(js).grist)

    def on_records(self, callback):
        check_registering_cell()

        @run_async
        async def run():
            wrapper = await add_to_callback_registry('onRecords', callback)
            await wrapper(None)

    def on_record(self, callback):
        check_registering_cell()

        @run_async
        async def run():
            wrapper = await add_to_callback_registry('onRecord', callback)
            await wrapper(await self.raw.getCurrentRecord())


grist = Grist()
