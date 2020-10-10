# ormy
Simple python ORM for self education.

# Intro

I've seen ORM systems but in general trusted their internal mechanisms. While I still do I want to dig a little deeper by implementing my own version.

# Methods

## Constructors

* Database() - A constructor the an abstract base class for all database types.
* CsvDatabase(path) - create a CSV backed ORM where each model class is annotated with additional information to locate the proper CSV file.

## Database methods
* query(Model) - returns a QueryOp instance.

## OpNode methods
* 

## QueryOp
* eval() - evaluate the query on the model specified for the query
* where(field) - select a field within the model to perform a comparison operation on. This returns a WhereOp.
* where_tag(tag) - select a collection of fields, by tag, to perform a comparison operation on. This returns a WhereTagOp.


