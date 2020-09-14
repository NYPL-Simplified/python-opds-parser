import collections


class RegistryItem(object):
    """Represents a single metadata registry item (collection role, media type, etc.)"""

    def __init__(self, key):
        """Initializes a new instance of RegistryItem class

        :param key: Unique identifier of this registry item
        :type key: basestring
        """
        self._key = key

    @property
    def key(self):
        """Returns a unique identifier of this registry item

        :return: Unique identifier of this registry item
        :rtype: basestring
        """
        return self._key


class Registry(collections.MutableMapping):
    """Represents a collection of registry items with a particular type (collection roles, media types, etc.)"""

    def __init__(self, items=None):
        """Initializes a new instance of Registry class

        :param items: (Optional) collection of registry items. Note that all items have to be RegistryItem descendants
        :type items: List[RegistryItems]
        """
        self._items = {}

        if items:
            self._add_items(items)

    def __setitem__(self, key, value):
        """Adds a new item to the registry

        :param key: Unique identifier of the item
        :type key: basestring

        :param value: Registry item
        :type value: RegistryItem
        """
        if not isinstance(value, RegistryItem):
            raise ValueError('Registry item must have RegistryItem type')

        self._items[key] = value

    def __delitem__(self, key):
        """Removes the item from the registry

        :param key: Unique identifier of the item
        :type key: basestring
        """
        del self._items[key]

    def __getitem__(self, key):
        """Returns an item from the registry by its key or raises a KeyError if it doesn't exist

        :param key: Unique identifier of the item
        :type key: basestring

        :return: Registry item
        :rtype: RegistryItem
        """
        return self._items[key]

    def __iter__(self):
        """Returns an iterator of all the registry items

        :return: Iterator of the registry items
        :rtype: Iterator[RegistryItem]
        """
        return self._items.itervalues()

    def __len__(self):
        """Returns a number of items in the registry

        :return: Number of items in the registry
        :rtype: int
        """
        return len(self._items)

    def _add_items(self, items):
        """Adds new items to the registry. Note that all the items must be RegistryItem descendants

        :param items: New registry items
        :type items: List[RegistryItem]
        """
        for item in items:
            if not isinstance(item, RegistryItem):
                raise ValueError('Registry item must have RegistryItem type')

            self._items[item.key] = item


class MediaType(RegistryItem):
    """Represents a media type registry item"""


class RWPMMediaTypesRegistry(Registry):
    """Registry containing media types mentioned in the RWPM spec"""

    # https://github.com/readium/webpub-manifest#4-media-type
    MANIFEST = MediaType(key='application/webpub+json')

    # https://github.com/readium/webpub-manifest#6-table-of-contents
    HTML = MediaType(key='text/html')
    CSS = MediaType(key='text/css')

    # https://github.com/readium/webpub-manifest#7-cover
    JPEG = MediaType(key='image/jpeg')
    PNG = MediaType(key='image/png')
    GIF = MediaType(key='image/gif')
    WEBP = MediaType(key='image/webp')
    SVG = MediaType(key='image/svg')
    SVG_XML = MediaType(key='image/svg+xml')

    # https://github.com/readium/webpub-manifest#9-package
    WEB_PUBLICATION_PACKAGE = MediaType('application/webpub+zip')
    EPUB_PUBLICATION_PACKAGE = MediaType('application/epub+zip')

    CORE_TYPES = [
        MANIFEST,
        HTML,
        CSS,
        JPEG,
        PNG,
        GIF,
        WEBP,
        SVG,
        SVG_XML,
        WEB_PUBLICATION_PACKAGE,
        EPUB_PUBLICATION_PACKAGE
    ]

    def __init__(self):
        """Initializes a new instance of RWPMMediaTypesRegistry class"""
        super(RWPMMediaTypesRegistry, self).__init__(self.CORE_TYPES)


class LinkRelation(RegistryItem):
    """Represents a link relation registry item"""


class RWPMLinkRelationsRegistry(Registry):
    """Registry containing link relations mentioned in the RWPM spec
    (https://github.com/readium/webpub-manifest/blob/master/relationships.md)
    """

    ALTERNATE = LinkRelation(key='alternate')
    CONTENTS = LinkRelation(key='contents')
    COVER = LinkRelation(key='cover')
    MANIFEST = LinkRelation(key='manifest')
    SEARCH = LinkRelation(key='search')
    SELF = LinkRelation(key='self')

    CORE_LINK_RELATIONS = [
        ALTERNATE,
        CONTENTS,
        COVER,
        MANIFEST,
        SEARCH,
        SELF
    ]

    def __init__(self):
        """Initializes a new instance of RWPMLinkRelationsRegistry class"""
        super(RWPMLinkRelationsRegistry, self).__init__(self.CORE_LINK_RELATIONS)


class CollectionRole(RegistryItem):
    """Represents a collection role registry item"""

    def __init__(self, key, compact, required):
        """Initializes a new instance of CollectionRole class

        :param key: Name of the collection
        :type key: basestring

        :param compact: Boolean value indicating whether the collection shall be compact
        :type compact: bool

        :param required: Boolean value indicating whether the collection is required
        :type required: bool
        """
        super(CollectionRole, self).__init__(key)

        self._compact = compact
        self._required = required

    @property
    def compact(self):
        """Returns the boolean value indicating whether the collection shall be compact

        :return: Boolean value indicating whether the collection shall be compact
        :rtype: bool
        """
        return self._compact

    @property
    def required(self):
        """Returns the boolean value indicating whether the collection is required

        :return: Boolean value indicating whether the collection is required
        :rtype: bool
        """
        return self._required


class RWPMCollectionRolesRegistry(Registry):
    """Registry of containing collection roles defined in the RWPM spec"""

    READING_ORDER = CollectionRole(key='readingOrder', compact=True, required=True)
    RESOURCES = CollectionRole(key='resources', compact=True, required=False)
    TOC = CollectionRole(key='toc', compact=True, required=False)

    GUIDED = CollectionRole(key='guided', compact=True, required=False)
    LANDMARKS = CollectionRole(key='landmarks', compact=True, required=False)
    LOA = CollectionRole(key='loa', compact=True, required=False)
    LOI = CollectionRole(key='loi', compact=True, required=False)
    LOT = CollectionRole(key='lot', compact=True, required=False)
    LOV = CollectionRole(key='lov', compact=True, required=False)
    PAGE_LIST = CollectionRole(key='pageList', compact=True, required=False)

    CORE_ROLES = [
        READING_ORDER,
        RESOURCES,
        TOC
    ]

    EXTENSIONS = [
        GUIDED,
        LANDMARKS,
        LOA,
        LOI,
        LOT,
        LOV,
        PAGE_LIST
    ]

    def __init__(self):
        """Initializes a new instance of RWPMCollectionRolesRegistry class"""
        super(RWPMCollectionRolesRegistry, self).__init__(self.CORE_ROLES + self.EXTENSIONS)
