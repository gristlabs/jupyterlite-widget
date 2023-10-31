import js  # noqa

from .callbacks import check_registering_cell, add_to_callback_registry
from .comlink import ComlinkProxy
from .utils import run_async
from ..objtypes import decode_bulk_values, decode_record, decode_object


class Grist:
    def __init__(self):
        self.raw = ComlinkProxy(js.Comlink.wrap(js).grist)

    def on_records(self, callback):
        check_registering_cell()

        @run_async
        async def run():
            wrapper = await add_to_callback_registry(self, "onRecords", callback)
            await wrapper(await grist.fetch_selected_table())

    def on_record(self, callback):
        check_registering_cell()

        @run_async
        async def run():
            wrapper = await add_to_callback_registry(self, "onRecord", callback)
            await wrapper(await self.fetch_selected_record())

    async def fetch_selected_table(self):
        return decode_bulk_values(await self.raw.fetchSelectedTable(keepEncoded=True))

    async def fetch_table(self, table_id):
        return decode_bulk_values(await self.raw.docApi.fetchTable(table_id))

    async def fetch_selected_record(self, row_id=None):
        if row_id is None:
            row_id = (await self.raw.getCurrentRecord())["id"]
        return decode_record(
            await self.raw.fetchSelectedRecord(row_id, keepEncoded=True)
        )

    def get_table(self, table_id):
        return TableOperations(self, table_id)

    def decode_cell_value(self, value):
        return decode_object(value)


class TableOperations:
    def __init__(self, grist_obj, table_id):
        self.grist = grist_obj
        self.table_id = table_id
        self._operations = None

    async def _ops(self):
        if self._operations is None:
            self._operations = await self.grist.raw.getTable(self.table_id)
        return self._operations

    async def create(self, records, parse_strings=True):
        ops = await self._ops()
        return await ops.create(records, parseStrings=parse_strings)

    async def update(self, records, parse_strings=True):
        ops = await self._ops()
        return await ops.update(records, parseStrings=parse_strings)

    async def upsert(
        self,
        records,
        parse_strings=True,
        add=True,
        update=True,
        on_many="first",
        allow_empty_require=False,
    ):
        ops = await self._ops()
        return await ops.upsert(
            records,
            parseStrings=parse_strings,
            add=add,
            update=update,
            onMany=on_many,
            allowEmptyRequire=allow_empty_require,
        )

    async def destroy(self, row_ids):
        ops = await self._ops()
        return await ops.destroy(row_ids)


grist = Grist()
