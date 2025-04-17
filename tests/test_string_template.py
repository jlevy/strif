from strif.string_template import StringTemplate


def test_string_template():
    t = StringTemplate("{name} is {age} years old", ["name", "age"])
    assert t.format(name="Alice", age=30) == "Alice is 30 years old"

    t = StringTemplate("{count:3d}@{price:.2f}", [("count", int), ("price", float)])
    assert t.format(count=10, price=19.99) == " 10@19.99"

    try:
        StringTemplate("{name} {age}", ["name"])
        raise AssertionError("Should have raised ValueError")
    except ValueError as e:
        assert "Template contains unsupported variable: 'age'" in str(e)

    t = StringTemplate("{count:d}", [("count", int)])
    try:
        t.format(count="not an int")
        raise AssertionError("Should have raised ValueError")
    except ValueError as e:
        assert "Invalid type for 'count': expected int but got 'not an int' (str)" in str(e)

    assert not StringTemplate("", [])
    assert StringTemplate("not empty", [])
