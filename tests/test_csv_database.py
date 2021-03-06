import pytest

from ormy.column import *
from ormy.csv_database import CsvDatabase
from ormy.datatabase_exception import DatabaseException
from ormy.model import Model
from tests.models_for_testing import Person, AllValueTypes, \
    ModelLevel2, ModelLevel3, ModelLevel1


class TestCsvDatabase:
    def test_validate_path_path_dne(self):
        path_to_database = "c:/bad"
        with pytest.raises(DatabaseException) as db_err:
            CsvDatabase(path_to_database)
        err_str = "root directory '%s' does not exist" % path_to_database
        assert err_str == str(db_err.value)

    def test_validate_path(self, tmpdir):
        good_dir = tmpdir.mkdir("good")
        CsvDatabase(good_dir)
        # no exception is raised therefore the database initializes the directory correctly
        # however, loading the CSV files is a separate step.
        assert True

    def test_query_no_filter(self, tmpdir):
        f1 = tmpdir.join(AllValueTypes.__csv_file__)
        f1.write("""int_col,float_col,string_col,date_col
100,1.00234,foobar,2020-08-19 17:44:49.732176
""")
        db = CsvDatabase(str(tmpdir))
        data = db.query(AllValueTypes).exec()
        m1 = data[0]
        assert isinstance(m1.int_col, int) and m1.int_col == 100
        assert isinstance(m1.float_col, float) and m1.float_col == 1.00234
        assert isinstance(m1.string_col, str) and m1.string_col == 'foobar'
        d = datetime.strptime('2020-08-19 17:44:49.732176', AllValueTypes.ALL_VALUE_TYPES_FORMAT_STR)
        assert isinstance(m1.date_col, datetime) and m1.date_col == d

    def test_query_simple_filter(self, tmpdir):
        f1 = tmpdir.join(AllValueTypes.__csv_file__)
        f1.write("""int_col,float_col,string_col,date_col
100,1.00234,foobar,2020-08-19 17:44:49.732176
111,1.00234,foobar,2020-08-19 17:44:49.732176
""")
        db = CsvDatabase(str(tmpdir))
        data = db.query(AllValueTypes).field('int_col').eq().value(100).exec()
        m1 = data[0]
        assert len(data) == 1
        assert isinstance(m1.int_col, int) and m1.int_col == 100
        assert isinstance(m1.float_col, float) and m1.float_col == 1.00234
        assert isinstance(m1.string_col, str) and m1.string_col == 'foobar'
        d = datetime.strptime('2020-08-19 17:44:49.732176', AllValueTypes.ALL_VALUE_TYPES_FORMAT_STR)
        assert isinstance(m1.date_col, datetime) and m1.date_col == d

    def test_query_simple_filter_multiple_data(self, tmpdir):
        f1 = tmpdir.join(AllValueTypes.__csv_file__)
        f1.write("""int_col,float_col,string_col,date_col
100,1.00234,foobar,2020-08-19 17:44:49.732176
111,1.00234,foobar,2020-08-19 17:44:49.732176
""")
        db = CsvDatabase(str(tmpdir))
        data = db.query(AllValueTypes).field('string_col').eq().value('foobar').exec()
        assert len(data) == 2
        m1 = data[0]
        m2 = data[1]
        assert isinstance(m1.int_col, int) and m1.int_col == 100
        assert isinstance(m1.float_col, float) and m1.float_col == 1.00234
        assert isinstance(m1.string_col, str) and m1.string_col == 'foobar'
        d = datetime.strptime('2020-08-19 17:44:49.732176', AllValueTypes.ALL_VALUE_TYPES_FORMAT_STR)
        assert isinstance(m1.date_col, datetime) and m1.date_col == d

        assert isinstance(m2.int_col, int) and m2.int_col == 111
        assert isinstance(m2.float_col, float) and m2.float_col == 1.00234
        assert isinstance(m2.string_col, str) and m2.string_col == 'foobar'
        d = datetime.strptime('2020-08-19 17:44:49.732176', AllValueTypes.ALL_VALUE_TYPES_FORMAT_STR)
        assert isinstance(m2.date_col, datetime) and m2.date_col == d

    def test_query_and(self, tmpdir):
        f1 = tmpdir.join(AllValueTypes.__csv_file__)
        f1.write("""int_col,float_col,string_col,date_col
100,1.00234,foobar1,2020-08-19 17:44:49.732176
101,1.00234,foobar2,2020-08-19 17:44:49.732176
102,1.00234,foobar3,2020-08-19 17:44:49.732176
100,1.00234,foobar4,2020-08-19 17:44:49.732176
""")
        db = CsvDatabase(str(tmpdir))
        data = db.query(AllValueTypes).field('int_col').eq().value(100).AND().field('string_col').eq().value(
            'foobar4').exec()
        assert len(data) == 1
        m = data[0]
        assert m.int_col == 100 and m.string_col == 'foobar4'

    def test_query_or(self, tmpdir):
        f1 = tmpdir.join(AllValueTypes.__csv_file__)
        f1.write("""int_col,float_col,string_col,date_col
100,1.00234,foobar1,2020-08-19 17:44:49.732176
101,1.00234,foobar2,2020-08-19 17:44:49.732176
102,1.00234,foobar3,2020-08-19 17:44:49.732176
100,1.00234,foobar4,2020-08-19 17:44:49.732176
""")
        db = CsvDatabase(str(tmpdir))
        data = db.query(AllValueTypes).field('int_col').eq().value(102).OR().field('string_col').eq().value(
            'foobar2').exec()
        assert len(data) == 2
        m1 = data[0]
        m2 = data[1]
        assert m1.int_col == 101 and m1.string_col == 'foobar2'
        assert m2.int_col == 102 and m2.string_col == 'foobar3'

    def test_query_two_ands(self, tmpdir):
        f1 = tmpdir.join(AllValueTypes.__csv_file__)
        f1.write("""int_col,float_col,string_col,date_col
100,1.00234,foobar1,2020-08-19 17:44:49.732176
101,1.00234,foobar2,2020-08-19 17:44:49.732176
102,1.00234,foobar3,2020-08-19 17:44:49.732176
100,1.00234,foobar4,2020-08-19 17:44:49.732176
""")
        db = CsvDatabase(str(tmpdir))
        data = db.query(AllValueTypes).field('int_col').flambda(lambda x: x == 100) \
            .AND().rlambda(lambda rec: rec.string_col == 'foobar4') \
            .AND().value(True).exec()
        assert len(data) == 1
        m = data[0]
        assert m.int_col == 100 and m.string_col == 'foobar4'

    def test_multiple_fk_one_deep(self, tmpdir):
        db = CsvDatabase(str(tmpdir))
        f1 = tmpdir.join(ModelLevel2.__csv_file__)
        f1.write("""id,value,level3_id
1,200,3
22,200,3
""")
        f2 = tmpdir.join(ModelLevel3.__csv_file__)
        f2.write("""id,value
3,300
""")
        data = db.query(ModelLevel2).field("value").eq().value(200).exec()
        assert len(data) == 2
        assert Model.compare(data[0], ModelLevel2.create({
            'id': 1,
            'value': 200,
            'level3_id': 3,
            'level3': ModelLevel3.create({
                'id': 3,
                'value': 300
            })
        }))
        assert Model.compare(data[1], ModelLevel2.create({
            'id': 22,
            'value': 200,
            'level3_id': 3,
            'level3': ModelLevel3.create({
                'id': 3,
                'value': 300
            })
        }))
        # also check they reference the same level3 object since it would be pulled from the cache
        assert data[0].level3 is data[1].level3

    def test_multiple_fk_three_deep(self, tmpdir):
        f1 = tmpdir.join(ModelLevel1.__csv_file__)
        f1.write("""id,value,level2_id
1,100,2
11,100,22
111,100100100,222
""")
        f2 = tmpdir.join(ModelLevel2.__csv_file__)
        f2.write("""id,value,level3_id
2,200,3
22,200200,3
222,200200200,333
""")
        f3 = tmpdir.join(ModelLevel3.__csv_file__)
        f3.write("""id,value
3,300
33,300300
333,300300300
""")

        db = CsvDatabase(tmpdir)
        data = db.query(ModelLevel1).field('value').eq().value(100).exec()
        assert len(data) == 2
        (l1, l2) = data
        assert Model.compare(l1, ModelLevel1.create({
            'id': 1,
            'value': 100,
            'level2_id': 2,
            'level2': ModelLevel2.create({
                'id': 2,
                'value': 200,
                'level3_id': 3,
                'level3': ModelLevel3.create({
                    'id': 3,
                    'value': 300
                })
            })
        }))
        assert Model.compare(l2, ModelLevel1.create({
            'id': 11,
            'value': 100,
            'level2_id': 22,
            'level2': ModelLevel2.create({
                'id': 22,
                'value': 200200,
                'level3_id': 3,
                'level3': ModelLevel3.create({
                    'id': 3,
                    'value': 300,
                })
            }),
        }))
        # check that the level3 reference is to the same object thereby confirming the object was not reloaded but
        # instead pulled from the cache.
        assert l1.level2.level3 is l2.level2.level3

    def test_hierarchical_models(self, tmpdir):
        f1 = tmpdir.join(Person.__csv_file__)
        f1.write("""id,last_name,first_name,parent_id
1,Smith,Craig,2
2,Smith,Elizabeth,3
3,Harris,Joesph,3
""")
        db = CsvDatabase(tmpdir)
        people = db.query(Person).field('id').eq().value(1).exec()
        grand_father = Person()
        grand_father.id = 3
        grand_father.last_name = 'Harris'
        grand_father.first_name = 'Joesph'
        grand_father.parent_id = 3
        grand_father.parent = grand_father
        assert Model.compare(people[0],
                             Person.create({'id': 1, 'last_name': 'Smith', 'first_name': 'Craig',
                                            'parent_id': 2,
                                            'parent': Person.create(
                                                {'id': 2, 'last_name': 'Smith', 'first_name': 'Elizabeth',
                                                 'parent_id': grand_father.id,
                                                 'parent': grand_father})}))
