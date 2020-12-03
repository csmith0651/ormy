# ormy
Simple python ORM for self education.

# Intro

I've seen ORM systems but in general trusted their internal mechanisms. While I still do, I want to dig a little deeper by implementing my own version.

# Methods

## Database Type Constructors

* Database() - A constructor for the abstract base class for all database types.
* CsvDatabase(path) - create a CSV backed ORM where each model class is annotated with additional information to locate the proper CSV file.

## Database methods
* query(Model) - returns a QueryOp instance.
* eval(query) - method to pass the query to the internal database engine.
* compile(query) - method to compile the query in the database engine. Returns the nodes converted to expression nodes in
  an AST.

## Query Operations

Abstract class for all operations to perform on a query result.

* exec() - evaluate the entire query starting at current operation.
* field(str) - select a field from a loaded instance of the model selected by the query method on the database. See
  `eq()` example below.
* value(constant) - a constant to compare against. See `eq()` example below.
* eq() - given a field operation prior compare to a value operation after and evaluate to true if equal. Note, currently
  other comparison operations are not implemented. Left as an exercise for the reader. e.g.
  `db.query(Model).field('id').eq().value(100).exec()`
* flambda - field lambda. Given a field operation prior passes that extracted field to the function (or lambda) specified
  as the parameter. Useful for operations that are too complicated to express using the limited operations available
  in the query methods. e.g. `db.query(Model).field('id').flambda(lambda id: id == 100).exec()`
* rlambda - record lambda. Pass a instance of the model, during loading, to the function specified as a parameter. e.g.
  `db.query(Model).rlambda(lambda rec: rec.id == 100).exec()`
* AND(), OR() - boolean operators joining to expressions together. e.g.
  `db.query(Model).field('id').eq().value(100).OR().field('name').eq().value('Craig').exec()`

## Notes

The operations between query(X) and .exec() define a filter function. This filter function
is applied as the data is being loaded. In the case of `query(x).exec()` the filter function
is a NoOp, i.e. empty. In the case of query(X).field('amount').eq(50).exec() this creates
a filter function restricting the loaded data to field the amount field is 50. 




