def first_or_default(collection, default=None):
    """Return first element of the specified collection or the default value if the collection is empty.

    :param collection: Collection
    :type collection: Iterable

    :param default: Default value
    :type default: Any
    """
    element = next(iter(collection), None)

    if element is None:
        element = default

    return element
