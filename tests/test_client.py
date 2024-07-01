from django_browserless import client


def test_merge_options():
    """Merge options is used the default options as its first param and options
    overrides as it second. To merge them it should:
    - Choose an overridden option over a base one.
    - Keep options in overrides that are not among the base options.
    - Handle nested options the same way.
    - For lists, append overrides elements that are not among the base options.
    """
    assert client._merge_options({"foo": "a", "bar": "b"}, {"foo": "b"}) == {
        "foo": "b",
        "bar": "b",
    }
    assert client._merge_options(
        {"foo": {"foo": "a", "bar": "b"}},
        {"foo": {"foo": "c", "baz": "d"}},
    ) == {"foo": {"foo": "c", "bar": "b", "baz": "d"}}
    assert client._merge_options({"foo": ["a", "b"]}, {"foo": ["b", "c"]}) == {
        "foo": ["a", "b", "c"]
    }
