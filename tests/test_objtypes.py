import datetime

from grist import objtypes, moment


def test_decode_bulk_values():
    result = objtypes.decode_bulk_values(
        dict(
            A=[1, 2, "3", True, False, None],
            B=[
                ["R", "Table1", 123],
                ["r", "Table1", [1, 2, 3]],
                ["d", 1000000],
                ["D", 100000, "America/Los_Angeles"],
                ["L", 1, 2, ["O", {"a": 1, "b": 2}]],
                ["P"],
                ["C"],
                ["U", "some value"],
                ["X", 1, 2],
            ],
        )
    )
    assert result.keys() == {"A", "B"}
    assert result["A"] == [1, 2, "3", True, False, None]

    rec = result["B"][0]
    assert isinstance(rec, objtypes.RecordStub)
    assert rec.table_id == "Table1"
    assert rec.row_id == 123

    recset = result["B"][1]
    assert isinstance(recset, objtypes.RecordSetStub)
    assert recset.table_id == "Table1"
    assert recset.row_ids == [1, 2, 3]

    assert result["B"][2] == datetime.date(1970, 1, 12)

    assert result["B"][3] == datetime.datetime(
        1970, 1, 1, 19, 46, 40, tzinfo=moment.tzinfo("America/Los_Angeles")
    )

    assert result["B"][4] == [1, 2, {"a": 1, "b": 2}]

    assert result["B"][5] is objtypes._pending_sentinel

    assert result["B"][6] is objtypes._censored_sentinel

    unmars = result["B"][7]
    assert isinstance(unmars, objtypes.UnmarshallableValue)
    assert unmars.value_repr == "some value"

    unknown = result["B"][8]
    assert isinstance(unknown, objtypes.UnknownType)
    assert unknown.raw == [1, 2]
