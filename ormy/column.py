from abc import abstractmethod, ABC
from datetime import datetime


class Column(object):
    def __init__(self, field, column_type, file_column_name='', primary_key=False, tags=None):
        file_column_name = field if file_column_name == '' else file_column_name
        self.field = field
        self.column_type = column_type
        self.file_column_name = file_column_name  # the name of the column in the data source
        self.tags = [] if tags is None else tags
        self.primary_key = primary_key

    def compatible_type(self, value):
        return self.column_type.compatible_type(value)


class ColumnType(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def compatible_type(self, value):
        pass

    @abstractmethod
    def cast(self, value):
        pass


# todo: could save memory by creating singletons for each of the column types.
class IntegerColumnType(ColumnType):
    def __init__(self):
        super().__init__()

    def compatible_type(self, value):
        return isinstance(value, int)

    def cast(self, value):
        return int(value)


class FloatColumnType(ColumnType):
    def __init__(self):
        super().__init__()

    def compatible_type(self, value):
        return isinstance(value, float)

    def cast(self, value):
        return float(value)


class DateColumnType(ColumnType):
    def __init__(self, date_format):
        super().__init__()
        self.format = date_format

    def compatible_type(self, value):
        return isinstance(value, datetime)

    def cast(self, value):
        return datetime.strptime(value, self.format)


class StringColumnType(ColumnType):
    def __init__(self):
        super().__init__()

    def compatible_type(self, value):
        return isinstance(value, str)

    def cast(self, value):
        return str(value)
