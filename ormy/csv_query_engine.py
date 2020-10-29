import csv
import os

from ormy.query_engine import *
import logging

log = logging.getLogger(__name__)


class CsvQueryEngine(QueryEngine):
    def __init__(self, path):
        super().__init__()
        self.path = path

    def convert_row_to_class_instance(self, model, row_data):
        field_data = self.convert_columns_to_fields(model, row_data)
        model_instance = model()
        for item in field_data.items():
            k, v = item
            setattr(model_instance, k, v)
        return model_instance

    @staticmethod
    def convert_columns_to_fields(model, row_data):
        data = {}
        for column in model.columns:
            if column.file_column_name in row_data:
                data[column.field] = column.column_type.cast(row_data[column.file_column_name])
            else:
                log.warning('column %s not present in row..skipping' % column.file_column_name)

        return data

    def _run(self, expr, context: ExprContext):
        # TODO: if not moved into the Expr tree, could move to QueryEngine and only have platform dependent
        #   operations here.
        if isinstance(expr, QueryExpr):
            # TODO: check for limit and sort
            return self.load(expr, context)
        elif issubclass(type(expr), CompExpr):
            return expr.perform_compare(self._run(expr.left, context), self._run(expr.right, context))
        elif isinstance(expr, FieldExpr):
            return getattr(context.model_data, expr.field)
        elif isinstance(expr, ValueExpr):
            return expr.value
        elif isinstance(expr, AndExpr):
            return self._run(expr.left, context) and self._run(expr.right, context)
        elif isinstance(expr, OrExpr):
            return self._run(expr.left, context) or self._run(expr.right, context)
        else:
            raise QueryEngineException("trying to execute unknown expr type '%s'" % expr.__name_)

    def process_csv_file(self, model, filter_expr: Expr, context: ExprContext):
        file = os.path.join(self.path, model.__csv_file__)
        model_instances = []
        with open(file, newline='') as f:
            # TODO: array reader or hash reader?
            #  - array reader might be faster
            #  - hash reader requires header row and easy to ignore columns
            reader = csv.DictReader(f)
            for row_data in reader:
                context.model_data = self.convert_row_to_class_instance(model, row_data)
                if filter_expr == self._TRUE or self._run(filter_expr, context):
                    model_instances.append(context.model_data)

        return model_instances

    def load(self, query_expr, context: ExprContext):
        model_instances = self.process_csv_file(query_expr.model, query_expr.left, context)
        return model_instances
