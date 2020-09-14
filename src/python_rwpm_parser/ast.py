from abc import ABCMeta, abstractmethod

from python_rwpm_parser.metadata import (ObjectMetadata, ObjectProperty,
                                         ObjectType)
from python_rwpm_parser.registry import LinkRelation, MediaType


class Visitor(object):
    """Interface for visitors walking through AST trees"""

    __metaclass__ = ABCMeta

    @abstractmethod
    def visit(self, node):
        """Processes the specified node

        :param node: AST node
        :type node: Node
        """
        raise NotImplementedError()


class Visitable(object):
    """Interface for objects walkable by AST visitors"""

    __metaclass__ = ABCMeta

    @abstractmethod
    def accept(self, visitor):
        """Accepts the specified visitor

        :param visitor: Visitor object
        :type visitor: Visitor
        """
        raise NotImplementedError()


class Node(Visitable):
    """Base class for all AST nodes"""

    def accept(self, visitor):
        """Accepts the specified visitor

        :param visitor: Visitor object
        :type visitor: Visitor
        """
        visitor.visit(self)


class Link(Node, ObjectMetadata):
    """Represents a link to another resource"""

    href = ObjectProperty('href', ObjectType.URI, True)
    templated = ObjectProperty('templated', bool, False)
    type = ObjectProperty('type', MediaType, False)
    title = ObjectProperty('title', str, False)
    rel = ObjectProperty('rel', LinkRelation, False)
    properties = ObjectProperty('properties', LinkRelation, False)
    height = ObjectProperty('height', int, False)
    width = ObjectProperty('width', int, False)
    duration = ObjectProperty('duration', float, False)
    bitrate = ObjectProperty('bitrate', float, False)
    language = ObjectProperty('language', float, False)
    alternate = ObjectProperty('alternate', 'Link', False)
    children = ObjectProperty('children', 'Link', False)

    def __init__(
            self,
            href=None,
            templated=None,
            type=None,
            title=None,
            rel=None,
            properties=None,
            height=None,
            width=None,
            duration=None,
            bitrate=None,
            language=None,
            alternate=None,
            children=None):
        """Initializes a new instance of Link class

        :param href: Link's URL
        :type href: basestring

        :param templated: Boolean value indicating whether href is a URI template
        :type templated: bool

        :param type: Media type of the linked resource
        :type type: Union[basestring, MediaType]

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
        self.type = type
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
    """Represents a list of links"""

    def get_by_rel(self, rel):
        """Returns links with the specific relation

        :param rel: Link's relation
        :type rel: str

        :return: Links with the specified relation
        :rtype: List[Link]
        """
        return [link for link in self if link.rel == rel]


class CollectionList(Node, list):
    """Represents a list of sub-collections"""


class Metadata(Node, dict):
    """Contains manifest's metadata"""


class Collection(Node, ObjectMetadata):
    """

    "A collection is defined as a grouping of metadata, links and
    sub-collections." - RWPM

    """

    def __init__(self, role=None):
        super(Collection, self).__init__()

        self._role = role
        self._links = LinksList()
        self._metadata = None
        self._sub_collections = CollectionList()

    @property
    def role(self):
        return self._role

    @property
    def links(self):
        """Returns a list of links

        :return: List of links
        :rtype: LinksList
        """
        return self._links

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        self._metadata = value

    @property
    def sub_collections(self):
        return self._sub_collections

    @property
    def compact(self):
        return self._metadata is None and len(self._sub_collections) == 0

    @property
    def full(self):
        return self._metadata is not None and len(self._sub_collections) > 0





class Manifestlike(Collection):
    """Base class for Manifest (Readium Web Publication Manifest)
    and Feed (OPDS 2)

    An OPDS 2 feed is defined as a RWPM with enumerated exceptions.

    This class implements the behavior common to both specs.  The
    alternative is to have the Feed class subclass Manifest and then
    implement a lot of exceptions.
    """

    context = ObjectProperty('@context', str, True)


class RWPMManifest(Manifestlike):
    """A Readium Web Publication Manifest."""

    # https://github.com/readium/webpub-manifest#22-metadata
    DEFAULT_CONTEXT = "https://readium.org/webpub-manifest/context.jsonld"

    context = ObjectProperty('@context', str, True, DEFAULT_CONTEXT)
