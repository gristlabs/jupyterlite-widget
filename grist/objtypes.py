# This file is essentially copied from the main grist repo.

from . import moment


def decode_object(value):
    """
    Given a Grist-encoded value, returns an object represented by it.
    """
    if not isinstance(value, (list, tuple)):
        return value
    code = value[0]
    args = value[1:]
    if code == "R":
        return RecordStub(args[0], args[1])
    elif code == "r":
        return RecordSetStub(args[0], args[1])
    elif code == "D":
        return moment.ts_to_dt(args[0], moment.Zone(args[1]))
    elif code == "d":
        return moment.ts_to_date(args[0])
    elif code == "E":
        return RaisedException(*args)
    elif code == "L":
        return [decode_object(item) for item in args]
    elif code == "O":
        return {decode_object(key): decode_object(val) for key, val in args[0].items()}
    elif code == "P":
        return _pending_sentinel
    elif code == "C":
        return _censored_sentinel
    elif code == "U":
        return UnmarshallableValue(args[0])
    else:
        return UnknownType(args)


class UnknownType(object):
    def __init__(self, raw):
        self.raw = raw


class UnmarshallableValue(object):
    """
    Represents an UnmarshallableValue. There is nothing we can do with it except encode it back.
    """

    def __init__(self, value_repr):
        self.value_repr = value_repr


# Unique sentinel value representing a pending value. It's encoded as ['P'], and shown to the user
# as "Loading..." text. With the switch to stored formulas, it's currently only used when a
# document was just migrated.
_pending_sentinel = object()


# A placeholder for a value hidden by access control rules.
# Depending on the types of the columns involved, copying
# a censored value and pasting elsewhere will either use
# CensoredValue.__repr__ (python) or CensoredValue.toString (typescript)
# so they should match
class CensoredValue(object):
    def __repr__(self):
        return "CENSORED"


_censored_sentinel = CensoredValue()


class RecordStub(object):
    def __init__(self, table_id, row_id):
        self.table_id = table_id
        self.row_id = row_id


class RecordSetStub(object):
    def __init__(self, table_id, row_ids):
        self.table_id = table_id
        self.row_ids = row_ids


class RaisedException(object):
    """
    RaisedException is a special type of object which indicates that a value in a cell isn't a plain
    value but an exception to be raised. All caught exceptions are wrapped in RaisedException. The
    original exception is saved in the .error attribute. The traceback is saved in .details
    attribute only when needed (flag include_details is set).

    RaisedException is registered under a special short name ("E") to save bytes since it's such a
    widely-used wrapper. To encode_args, it simply returns the entire encoded stored error, e.g.
    RaisedException(ValueError("foo")) is encoded as ["E", "ValueError", "foo"].

    When user_input is passed, RaisedException(ValueError("foo"), user_input=2) is encoded as:
    ["E", "ValueError", "foo", {u: 2}].
    """

    # Marker object that indicates that there was no user input.
    NO_INPUT = object()

    def __init__(self, *args):
        args = list(args)
        self._name = safe_shift(args)
        self._message = safe_shift(args)
        self.details = safe_shift(args)
        self.user_input = safe_shift(args, {})
        self.user_input = decode_object(
            self.user_input.get("u", RaisedException.NO_INPUT)
        )


def safe_shift(arg, default=None):
    value = arg.pop(0) if arg else None
    return default if value is None else value


def decode_bulk_values(bulk_values):
    """
    Decode objects in values of the form {col_id: array_of_values}, as present in bulk DocActions
    and UserActions.
    """
    return {
        k: [decode_object(value) for value in values]
        for k, values in bulk_values.items()
    }


def decode_record(rec):
    return {k: decode_object(value) for k, value in rec.items()}
