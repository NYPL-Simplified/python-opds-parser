def first_or_default(collection, default=None):
    element = next(iter(collection), None)

    if element is None:
        element = default

    return element
