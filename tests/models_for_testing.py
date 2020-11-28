from ormy.column import Column, IntegerColumnType, PrimaryKey, StringColumnType, FloatColumnType, ForeignKey, \
    DateColumnType
from ormy.model import Model

TIME_STR = '2020-08-19 17:44:49.732176'


class IntSingle(Model):
    columns = [
        Column('value', IntegerColumnType())
    ]


class FloatSingle(Model):
    columns = [
        Column('value', FloatColumnType())
    ]


class StringSingle(Model):
    columns = [
        Column('value', StringColumnType())
    ]


class DateSingle(Model):
    columns = [
        Column('value', DateColumnType(TIME_STR))
    ]


class AllValueTypes(Model):
    ALL_VALUE_TYPES_FORMAT_STR = "%Y-%m-%d %H:%M:%S.%f"

    __csv_file__ = 'all-value-types.csv'
    columns = [
        Column('int_col', IntegerColumnType()),
        Column('float_col', FloatColumnType()),
        Column('string_col', StringColumnType()),
        Column('date_col', DateColumnType(ALL_VALUE_TYPES_FORMAT_STR))
    ]


class ModelLevel3(Model):
    __csv_file__ = "model_level3.csv"
    columns = [
        Column('id', IntegerColumnType(), key=PrimaryKey()),
        Column('value', IntegerColumnType())

    ]


class ModelLevel2(Model):
    __csv_file__ = "model_level2.csv"
    columns = [
        Column('id', IntegerColumnType(), key=PrimaryKey()),
        Column('value', IntegerColumnType()),
        Column('level3_id', IntegerColumnType(), key=ForeignKey('id', ModelLevel3), object_field='level3')

    ]


class ModelLevel1(Model):
    __csv_file__ = "model_level1.csv"
    columns = [
        Column('id', IntegerColumnType(), key=PrimaryKey()),
        Column('value', IntegerColumnType()),
        Column('level2_id', IntegerColumnType(), key=ForeignKey('id', ModelLevel2), object_field='level2')
    ]


class Person(Model):
    __csv_file__ = "people.csv"

    columns = [
        Column('id', IntegerColumnType(), key=PrimaryKey()),
        Column('last_name', StringColumnType()),
        Column('first_name', StringColumnType()),
    ]


# TODO: here's the remedy to the class in a class reference problem.
Person.columns.append(
    Column('parent_id', IntegerColumnType(), key=ForeignKey('id', Person), object_field='parent'))


class Manufacturer(Model):
    __csv_file__ = 'manufacturers.csv'
    columns = [
        Column('manufacturer_id', StringColumnType(), key=PrimaryKey()),
        Column('description', StringColumnType()),
        Column('contact_id', IntegerColumnType(), key=ForeignKey('person_id', Person), object_field='contact')
    ]


class Product(Model):
    __csv_file__ = "products.csv"
    columns = [
        Column('product_id', IntegerColumnType(), key=PrimaryKey()),
        Column('manufacturer_id', StringColumnType(), key=ForeignKey('manufacturer_id', Manufacturer),
               object_field='manufacturer'),
        Column('description', StringColumnType()),
        Column('unit_cost', FloatColumnType()),
        Column('in_stock_count', IntegerColumnType()),
    ]


class Order(Model):
    __csv_file__ = "orders.csv"
    columns = [
        Column('order_id', IntegerColumnType(), key=PrimaryKey()),
        Column('person_id', IntegerColumnType(), key=ForeignKey('person_id', Person), object_field='person'),
        Column('product_id', IntegerColumnType(), key=ForeignKey('product_id', Product), object_field='product'),
        Column('quantity', IntegerColumnType()),
        Column('total', IntegerColumnType())
    ]


def generate_order_data(tmpdir):
    f1 = tmpdir.join(Person.__csv_file__)
    f1.write("""person_id,last_name,first_name
1,Smith,Eric
2,Smith,Craig
3,Smith,Caron
4,Fader,Jack
5,O'Hearn,Amie
""")
    f2 = tmpdir.join(Order.__csv_file__)
    f2.write("""order_id,person_id,product_id,quantity,total
1,1,1,10,100
2,4,1,2,20
3,2,2,3,15
""")
    f3 = tmpdir.join(Product.__csv_file__)
    f3.write("""product_id,manufacturer_id,description,unit_cost,in_stock_count
1,1,funny hats,10.00,10
2,2,beer,7.00,100
""")

    f4 = tmpdir.join(Manufacturer.__csv_file__)
    f4.write("""manufacturer_id,description,contact_id
1,Craig Corp.,2
2,Eric Inc.,1
""")
