import js  # noqa

from .callbacks import check_registering_cell, add_to_callback_registry
from .comlink import ComlinkProxy
from .utils import run_async


class Grist:
    def __init__(self):
        self.raw = ComlinkProxy(js.Comlink.wrap(js).grist)

    def on_records(self, callback):
        check_registering_cell()

        @run_async
        async def run():
            wrapper = await add_to_callback_registry(self, "onRecords", callback)
            await wrapper(None)

    def on_record(self, callback):
        check_registering_cell()

        @run_async
        async def run():
            wrapper = await add_to_callback_registry(self, "onRecord", callback)
            await wrapper(await self.raw.getCurrentRecord())


grist = Grist()
