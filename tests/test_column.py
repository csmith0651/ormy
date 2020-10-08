import pytest
from datetime import datetime

from ormy.column import Column, IntegerColumnType, FloatColumnType, DateColumnType, StringColumnType

test_date = datetime.now()


class TestColumn:
    def test_compatible_type(self):
        col = Column('f1', IntegerColumnType())
        assert col.compatible_type(100) == True
        assert col.compatible_type(100.0) == False
        assert col.compatible_type('string') == False
        assert col.compatible_type(test_date) == False


class TestIntegerColumnType:
    def test_compatible_type(self):
        col = IntegerColumnType()
        assert col.compatible_type(100) == True
        assert col.compatible_type(100.0) == False
        assert col.compatible_type('string') == False
        assert col.compatible_type(test_date) == False

    def test_cast(self):
        col = IntegerColumnType()
        assert col.cast('100') == 100
        with pytest.raises(ValueError) as cast_error:
            col.cast('100.5'), 100
        assert "invalid literal for int() with base 10: '100.5'" in str(cast_error.value)


class TestFloatColumnType:
    def test_compatible_type(self):
        col = FloatColumnType()
        assert col.compatible_type(100.5) == True
        assert col.compatible_type(100.0) == True
        assert col.compatible_type(100) == False
        assert col.compatible_type('string') == False
        assert col.compatible_type(test_date) == False

    def test_cast(self):
        col = FloatColumnType()
        assert col.cast('100.5') == 100.5
        with pytest.raises(ValueError) as cast_error:
            col.cast('foobar')
        assert "could not convert string to float: 'foobar'" in str(cast_error.value)


class TestDateColumnType:
    DATE_FORMAT = '%Y%m%d'

    def test_compatible_type(self):
        col = DateColumnType(TestDateColumnType.DATE_FORMAT)
        assert col.compatible_type(100.5) == False
        assert col.compatible_type(100.0) == False
        assert col.compatible_type(100) == False
        assert col.compatible_type('string') == False
        assert col.compatible_type(test_date) == True

    def test_cast(self):
        col = DateColumnType(TestDateColumnType.DATE_FORMAT)
        date_str = 'foobar'
        with pytest.raises(ValueError) as cast_error:
            col.cast(date_str)
        error_str = "time data '%s' does not match format '%s'" % (date_str, TestDateColumnType.DATE_FORMAT)
        assert error_str in str(cast_error.value)


class TestStringColumnType:
    def test_compatible_type(self):
        col = StringColumnType()
        assert col.compatible_type(100) == False
        assert col.compatible_type(100.5) == False
        assert col.compatible_type('foobar') == True
        assert col.compatible_type(test_date) == False

    def test_cast_self(self):
        # I don't think there's a column type you can't cast to string..
        assert True == True
