import csv
import logging
import os

from ormy.query_engine import *

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
        assert len(model_instance.__dict__) == len(
            model.columns), "the number attributes (%d) of instance does not match the number of columns (%d) in model '%s'" % (
            len(model_instance.__dict__), len(model.columns), model.__name__)
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
        elif isinstance(expr, LambdaExpr):
            return expr.func(self._run(expr.left, context))
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
        entities = self.process_csv_file(query_expr.model, query_expr.left, context)

        # TODO: this is not specific to the CsvQueryEngine, but abstract across all engines.
        #   Move traversal of the AST into QueryEngine, similarly call a load method in QE which calls platform-specific
        #   load in CQE which returns data to QE which scans for foreign keys in QE since this is a platform-independent
        #   action. The FK scan traverses the schema doing loads using load from QE and CEQ recursively. Refactor this.
        fk_key_columns = query_expr.model.get_fk_columns()
        if fk_key_columns:
            self.load_with_foreign_entities(entities, fk_key_columns)

        return entities

    def load_with_foreign_entities(self, entities_to_patch, fk_columns):
        # gather FK ids from current models, and loop through the FK models and
        # and load only matching object instances

        # entity_cache = {}
        for fk_column in fk_columns:
            self.load_fk_entities_work(fk_column, entities_to_patch)

    def load_fk_entities_work(self, fk_column, entities_to_patch, entity_cache: dict = None):
        assert fk_column.has_fk(), "column '%s' does not have a foreign key" % fk_column.field

        fk_ids = [getattr(instance, fk_column.field) for instance in entities_to_patch]

        if entity_cache is None:
            entity_cache = {}

        # - construct a filter based on the id's in entities_to_patch and in the cache
        # - load the entities for that model with the filter
        # - update the cache
        # - patch the entities_to_patch by referencing the corresponding object in the cache
        fk_model = fk_column.key.model
        fk_object_field = fk_column.object_field
        field_in_fk_model = fk_column.key.field
        fk_field = fk_column.field

        # TODO: assumes a flat hierarchy of model names. Not sure if this is right or wrong...
        # NOTE: the cache_key has to be a combination of the model name and the key in the FK model because
        #   the FK doesn't have to point to the PK, just a unique key in that other model.
        cache_key = fk_model.__name__ + '.' + field_in_fk_model
        if cache_key not in entity_cache:
            entity_cache[cache_key] = {}
        cache = entity_cache[cache_key]

        # filter func that loaded entity is in originating fk list but not in cache
        def filter_entities(val):
            return val in fk_ids and val not in cache

        field_expr = FieldExpr(field_in_fk_model)
        lambda_expr = LambdaExpr(filter_entities, field_expr)
        new_entities = self.process_csv_file(fk_model, lambda_expr, ExprContext())

        # TODO: What if fk_field value (in the child) is None? Should that be allowed? Yes but should be
        #  configurable. Without extra code what's the behavior here?

        for entity in new_entities:
            cache[getattr(entity, field_in_fk_model)] = entity
        for patch in entities_to_patch:
            setattr(patch, fk_object_field, cache[getattr(patch, fk_field)])

        if len(new_entities) > 0:
            for c in fk_model.get_fk_columns():
                self.load_fk_entities_work(c, new_entities, entity_cache)
