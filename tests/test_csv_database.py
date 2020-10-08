import os

import pytest
from _pytest import tmpdir

# NOTE: if would be nice to write just import ormy.column
from ormy.column import *
from ormy.csv_database import CsvDatabase
from ormy.datatabase_exception import DatabaseException
from ormy.model import Model

FORMAT_STR = "%Y-%m-%d %H:%M:%S.%f"

class F1Model(Model):
    __csv_file__ = "f1.csv"
    __table_name__ = "f1"

    columns = [
        Column('intcol', IntegerColumnType()),
        Column('floatcol', FloatColumnType()),
        Column('stringcol', StringColumnType()),
        Column('datecol', DateColumnType(FORMAT_STR))
    ]


class TestCsvDatabase:
    def test_validate_path_path_dne(self):
        # create a temp directory, validate it, and then delete it.
        path_to_database = "c:/bad"
        with pytest.raises(DatabaseException) as db_err:
            db = CsvDatabase(path_to_database)
        err_str = "root directory '%s' does not exist" % path_to_database
        assert err_str == str(db_err.value)

    def test_validate_path_path_dne(self, tmpdir):
        good_dir = tmpdir.mkdir("good")
        db = CsvDatabase(good_dir)
        # no exception is raised therefore the database initializes the directory correctly
        # however, loading the CSV files is a separate step.
        assert True

    # def test_convert_row_to_class_instance(self):
    #     assert False
    #
    # def test_convert_columns_to_fields(self):
    #     assert False
    #
    # def test_process_csv_file(self):
    #     assert False

    def test_load_model(self, tmpdir):
        f1 = tmpdir.join("f1.csv")
        # f2 = tmpdir.join("f2.csv")
        f1.write("""intcol,floatcol,stringcol,datecol
100,1.00234,foobar,2020-08-19 17:44:49.732176
""")
        db = CsvDatabase(str(tmpdir))
        data = db.load_model(F1Model)
        m1 = data[0]
        assert isinstance(m1.intcol, int) and m1.intcol == 100
        assert isinstance(m1.floatcol, float) and m1.floatcol == 1.00234
        assert isinstance(m1.stringcol, str) and m1.stringcol == 'foobar'
        d = datetime.strptime('2020-08-19 17:44:49.732176', FORMAT_STR)
        assert isinstance(m1.datecol, datetime) and m1.datecol == d