import os

from ormy.csv_query_engine import CsvQueryEngine
from ormy.datatabase import Database
from ormy.datatabase_exception import DatabaseException


class CsvDatabase(Database):
    def __init__(self, path_to_database):
        self.validate_path(path_to_database)
        self.path = path_to_database
        super().__init__(CsvQueryEngine(self.path))

    @classmethod
    def validate_path(cls, path_to_database):
        if not os.path.isdir(path_to_database):
            raise DatabaseException("root directory '%s' does not exist" % path_to_database)

    def __str__(self):
        return "CvsDatabase(path=%s)" % self.path
