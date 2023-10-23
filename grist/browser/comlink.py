import js  # noqa
import pyodide_js  # noqa
from pyodide.ffi import to_js, create_proxy  # noqa

from .utils import maybe_await

js.importScripts("https://unpkg.com/comlink@4.4.1/dist/umd/comlink.js")
pyodide_js.registerComlink(js.Comlink)


class ComlinkProxy:
    def __init__(self, proxy, name=None):
        self._proxy = proxy
        self._name = name

    def __getattr__(self, name):
        return ComlinkProxy(getattr(self._proxy, name), name)

    async def __call__(self, *args, **kwargs):
        if any(callable(arg) for arg in args):
            assert (
                len(args) == 1 and not kwargs
            ), "Only one argument is supported for callbacks"
            [callback] = args

            async def wrapper(*callback_args):
                callback_args = [
                    a.to_py() if hasattr(a, "to_py") else a for a in callback_args
                ]
                await maybe_await(callback(*callback_args))

            js._grist_tmp1 = self._proxy
            js._grist_tmp2 = js.Comlink.proxy(create_proxy(wrapper))
            result = await js.eval("_grist_tmp1(_grist_tmp2)")
        else:
            args = [to_js(arg, dict_converter=js.Object.fromEntries) for arg in args]
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
