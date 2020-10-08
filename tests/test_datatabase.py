import pytest

from ormy.datatabase import Database


def test_query():
    db = Database()
    with pytest.raises(AssertionError) as query_error:
        db.query(object)

    # should never each this
    assert True

