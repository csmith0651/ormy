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

## OpNode methods

Abstract class for all operations to perform on a query result.

* exec() - evaluate the entire query starting at current operation.
* eval() - a virtual method that defines the meaning of exec(). Different
  per node.
  
## ListOpResultsNode

Operations that can be performed on a list of results

* eq(value)
* lt(value)
* gt(value)
* lte(value)
* gte(value)

## QueryOp
* eval() - evaluate the query on the model specified for the query
* field(field) - select a field within the model to perform a comparison operation on. This returns a WhereOp.
  A where clause must be paired with a comparsion operator.
* field_tag(tag) - select a collection of fields, by tag, to perform a comparison operation on.
  This returns a WhereTagOp. A where_tag clause must be paired with a comparsion operator.
* limit(int) -- limit the number of results.


## Example usages

Generate data results.

* db.query(Model).exec()
* db.query(Model).field(value).exec()
* db.query(Model).field(value).COMP(value).exec()
* (DNE) db.query(Model).limit(int).exec()
* (DNE) db.query(Model).join(Model).oneq(f1,f2).exec()

Operations that generate a list result:
db.query()
db.COMP()

## Notes

The operations between query(X) and .exec() define a filter function. This filter function
is applied as the data is being loaded. In the case of `query(x).exec()` the filter function
is a NoOp, i.e. empty. In the case of query(X).field('amount').eq(50).exec() this creates
a filter function restricting the loaded data to where the amount field is 50. 




