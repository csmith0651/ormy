from abc import abstractmethod, ABC
from datetime import datetime

from ormy.model import Model


class PrimaryKey(object):
    def __str__(self):
        return "PK()"


class ForeignKey(object):
    # TODO: move field to the end of the param list and default to None. If not specified uses the same field name
    #   in the parent table.
    def __init__(self, field: str, model: Model):
        # TODO: lookup foreign_key_name in model and confirm exists
        #    Also validate, somewhere else probably, that type of FK and key in FK model match.
        # NOTE: the FK doesn't have to reference the PK of the other table!
        self.field = field
        self.model = model
        # TODO: support nullable FKs? Interesting different constraints on nullable key:
        #   https://stackoverflow.com/questions/7573590/can-a-foreign-key-be-null-and-or-duplicate
        # I particularly like the reference to the oracle documentation

    def __str__(self):
        return "FK('%s', %s)" % (self.field, self.model.__name__)


class ColumnException(Exception):
    def __init__(self, message):
        self.message = message


class ColumnType(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def compatible_type(self, value):
        pass

    @abstractmethod
    def cast(self, value):
        pass

    @abstractmethod
    def __str__(self):
        pass


# todo: could save memory by creating singletons for each of the column types.
class IntegerColumnType(ColumnType):
    def __init__(self):
        super().__init__()

    def compatible_type(self, value):
        return isinstance(value, int)

    def cast(self, value):
        return int(value)

    def __str__(self):
        return "IntegerColumnType()"


class FloatColumnType(ColumnType):
    def __init__(self):
        super().__init__()

    def compatible_type(self, value):
        return isinstance(value, float)

    def cast(self, value):
        return float(value)

    def __str__(self):
        return "FloatColumnType()"


class DateColumnType(ColumnType):
    def __init__(self, date_format):
        super().__init__()
        self.format = date_format

    def compatible_type(self, value):
        return isinstance(value, datetime)

    def cast(self, value):
        return datetime.strptime(value, self.format)

    def __str__(self):
        return "DateColumnType(format=%s)" % self.format


class StringColumnType(ColumnType):
    def __init__(self):
        super().__init__()

    def compatible_type(self, value):
        return isinstance(value, str)

    def cast(self, value):
        return str(value)

    def __str__(self):
        return "StringColumnType()"


# TODO: remove references to columns and instead they are fields that may or may not *come* from columns in a
#  table/csv file.
class Column(object):
    def __init__(self, field: str, column_type: ColumnType, **kwargs):
        self.field = field
        self.column_type = column_type

        self.file_column_name = kwargs.get('file_column_name', field)
        self.key = kwargs.get('key')
        self.tags = kwargs.get('tags', [])
        # TODO: check that value of object_field does not intersect with existing field
        self.object_field = kwargs.get('object_field', None)
        if self.has_fk() and 'object_field' not in kwargs:
            raise ColumnException('for field "%s" with foreign field, must define an "object_field" parameter'
                                  % self.field)

    def compatible_type(self, value):
        return self.column_type.compatible_type(value)

    def has_fk(self):
        return isinstance(self.key, ForeignKey)

    def set_field(self, entity, value):
        if not self.compatible_type(value):
            raise ColumnException('Cannot cast value of "%s" to type "%s"' % (value, self.column_type))
        setattr(entity, self.field, value)

    def get_field(self, entity, strict=True):
        if strict:
            return getattr(entity, self.field)
        return getattr(entity, self.field, None)

    def has_field(self, entity):
        return hasattr(entity, self.field)

    def __str__(self):
        optional_str = ""
        if self.key is not None:
            optional_str += "," + str(self.key)
            if isinstance(self.key, ForeignKey):
                optional_str += ",object_field=%s" % self.object_field
        return "column(field='%s',type=%s%s" % (self.field, self.column_type, optional_str)
