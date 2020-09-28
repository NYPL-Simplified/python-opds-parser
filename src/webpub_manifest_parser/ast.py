from abc import ABCMeta, abstractmethod

import six

from webpub_manifest_parser.metadata import ObjectProperty, PropertiesGrouping
from webpub_manifest_parser.registry import LinkRelation, MediaType


@six.add_metaclass(ABCMeta)
class Visitor(object):
    """Interface for visitors walking through abstract syntax trees (AST)."""

    @abstractmethod
    def visit(self, node):
        """Process the specified node.

        :param node: AST node
        :type node: Node
        """
        raise NotImplementedError()


@six.add_metaclass(ABCMeta)
class Visitable(object):
    """Interface for objects walkable by AST visitors."""

    @abstractmethod
    def accept(self, visitor):
        """Accept  the specified visitor.

        :param visitor: Visitor object
        :type visitor: Visitor
        """
        raise NotImplementedError()


class Node(Visitable):
    """Base class for all AST nodes."""

    def accept(self, visitor):
        """Accept the specified visitor.

        :param visitor: Visitor object
        :type visitor: Visitor
        """
        visitor.visit(self)


class Link(Node, PropertiesGrouping):
    """Link to another resource."""

    href = ObjectProperty("href", str, True)
    templated = ObjectProperty("templated", bool, False)
    type = ObjectProperty("type", MediaType, False)
    title = ObjectProperty("title", str, False)
    rel = ObjectProperty("rel", LinkRelation, False)
    properties = ObjectProperty("properties", LinkRelation, False)
    height = ObjectProperty("height", int, False)
    width = ObjectProperty("width", int, False)
    duration = ObjectProperty("duration", float, False)
    bitrate = ObjectProperty("bitrate", float, False)
    language = ObjectProperty("language", float, False)
    alternate = ObjectProperty("alternate", "Link", False)
    children = ObjectProperty("children", "Link", False)

    def __init__(  # pylint: disable=R0913
        self,
        href=None,
        templated=None,
        _type=None,
        title=None,
        rel=None,
        properties=None,
        height=None,
        width=None,
        duration=None,
        bitrate=None,
        language=None,
        alternate=None,
        children=None,
    ):
        """Initialize a new instance of Link class.

        :param href: Link's URL
        :type href: basestring

        :param templated: Boolean value indicating whether href is a URI template
        :type templated: bool

        :param _type: Media type of the linked resource
        :type _type: Union[basestring, MediaType]

        :param title: Title of the linked resource
        :type title: basestring

        :param rel: Relation between the resource and its containing collection
        :type rel: List[registry.LinkRelation]

        :param properties: Relation between the resource and its containing collection
        :type properties: object

        :param height: Height of the linked resource in pixels
        :type height: int

        :param width: Width of the linked resource in pixels
        :type width: int

        :param duration: Duration of the linked resource in seconds
        :type duration: float

        :param bitrate: Bit rate of the linked resource in kilobits per second
        :type bitrate: float

        :param language: Expected language of the linked resource
        :type language: List[basestring]

        :param alternate: Alternate resources for the linked resource
        :type alternate: List[Link]

        :param children: Resources that are children of the linked resource, in the context of a given collection role
        :type children: List[Link]
        """
        super(Link, self).__init__()

        self.href = href
        self.templated = templated
        self.type = _type
        self.title = title
        self.rel = rel
        self.properties = properties
        self.height = height
        self.width = width
        self.duration = duration
        self.bitrate = bitrate
        self.language = language
        self.alternate = alternate
        self.children = children


class LinksList(Node, list):
    """List of links."""

    def get_by_rel(self, rel):
        """Return links with the specific relation.

        :param rel: Link's relation
        :type rel: str

        :return: Links with the specified relation
        :rtype: List[Link]
        """
        return [link for link in self if link.rel == rel]


class CollectionList(Node, list):
    """List of sub-collections."""

    def get_by_role(self, role):
        """Return collections with the specific role.

        :param role: Collection's role
        :type role: basestring

        :return: Collections with the specific role
        :rtype: List[Collection]
        """
        return [collection for collection in self if collection.role.key == role]


class Metadata(Node, dict):
    """Dictionary containing manifest's metadata."""


class Collection(Node, PropertiesGrouping):
    """A collection is defined as a grouping of metadata, links and sub-collections."""

    def __init__(self, role=None):
        """Initialize a new instance of Collection class.

        :param role: Collection's role (can be empty when self is a manifest)
        :type role: Optional[CollectionRole]
        """
        super(Collection, self).__init__()

        self._role = role
        self._links = LinksList()
        self._metadata = None
        self._sub_collections = CollectionList()

    @property
    def role(self):
        """Return the collection's role.

        :return: Collection's role.
        :rtype: Optional[CollectionRole]
        """
        return self._role

    @property
    def links(self):
        """Return a list of links.

        :return: List of links
        :rtype: LinksList
        """
        return self._links

    @property
    def metadata(self):
        """Return the collection's metadata.

        :return: Collection's metadata
        :rtype: Optional[Metadata]
        """
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        """Set the collection's metadata.

        :param value: New metadata
        :type value: Metadata
        """
        self._metadata = value

    @property
    def sub_collections(self):
        """Return a list of sub-collections.

        :return: List of sub-collections.
        :rtype: CollectionList
        """
        return self._sub_collections

    @property
    def compact(self):
        """Return a boolean value indicating if this collection is compact.

        :return: Boolean value indicating if this collection is compact
        :rtype: bool
        """
        return self._metadata is None and len(self._sub_collections) == 0

    @property
    def full(self):
        """Return a boolean value indicating if this collection is full.

        :return: Boolean value indicating if this collection is full
        :rtype: bool
        """
        return self._metadata is not None and len(self._sub_collections) > 0


class Manifestlike(Collection):
    """Base class for Manifest (Readium Web Publication Manifest) and Feed (OPDS 2).

    An OPDS 2 feed is defined as a RWPM with enumerated exceptions.

    This class implements the behavior common to both specs.  The
    alternative is to have the Feed class subclass Manifest and then
    implement a lot of exceptions.
    """

    context = ObjectProperty("@context", str, True)


class RWPMManifest(Manifestlike):
    """A Readium Web Publication Manifest."""

    # https://github.com/readium/webpub-manifest#22-metadata
    DEFAULT_CONTEXT = "https://readium.org/webpub-manifest/context.jsonld"

    context = ObjectProperty("@context", str, True, DEFAULT_CONTEXT)
