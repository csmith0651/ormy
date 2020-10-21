import csv
import os
import logging

from ormy.datatabase import Database
from ormy.datatabase_exception import DatabaseException

log = logging.getLogger(__name__)

class CsvDatabase(Database):
    def __init__(self, path_to_database):
        super().__init__()
        self.validate_path(path_to_database)
        self.path = path_to_database

    @classmethod
    def validate_path(cls, path_to_database):
        if not os.path.isdir(path_to_database):
            raise DatabaseException("root directory '%s' does not exist" % path_to_database)

    def convert_row_to_class_instance(self, model, row_data):
        field_data = self.convert_columns_to_fields(model, row_data)
        model_instance = model()
        for item in field_data.items():
            k, v = item
            setattr(model_instance, k, v)
        return model_instance

    def convert_columns_to_fields(self, model, row_data):
        data = {}
        for column in model.columns:
            if column.file_column_name in row_data:
                data[column.field] = column.column_type.cast(row_data[column.file_column_name])
            else:
                log.warning('column %s not present in row..skipping' % column.file_column_name)

        return data

    def process_csv_file(self, model, filter_func=None):
        file = os.path.join(self.path, model.__csv_file__)
        model_instances = []
        with open(file, newline='') as f:
            # TODO: array reader or hash reader?
            #  - array reader might be faster
            #  - hash reader requires header row and easy to ignore columns
            reader = csv.DictReader(f)
            for row_data in reader:
                row_as_instance = self.convert_row_to_class_instance(model, row_data)
                if filter_func is None or filter_func(row_as_instance):
                    model_instances.append(row_as_instance)

        return model_instances

    def load_model(self, model, filter_func=None):
        model_instances = self.process_csv_file(model, filter_func)
        return model_instances
