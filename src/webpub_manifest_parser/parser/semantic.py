import logging

from multipledispatch import dispatch

from webpub_manifest_parser.ast import (
    Collection,
    CollectionList,
    Link,
    LinksList,
    Manifestlike,
    Metadata,
    Visitor,
)
from webpub_manifest_parser.registry import (
    RWPMCollectionRolesRegistry,
    RWPMLinkRelationsRegistry,
)
from webpub_manifest_parser.utils import first_or_default


class SemanticError(Exception):
    """Exception raised in the case of any semantic errors."""


MISSING_TYPE_METADATA_ERROR = SemanticError(
    "Manifest's metadata does not contain @type property"
)
MISSING_TITLE_METADATA_ERROR = SemanticError(
    "RWPM Manifest's metadata does not contain title property"
)

MISSING_SELF_LINK_ERROR = SemanticError("Required self link is missing")
WRONG_SELF_LINK_HREF_FORMAT = SemanticError(
    "Self link's href must be an absolute URI to the canonical location of the manifest"
)


class CollectionWrongFormatError(SemanticError):
    """Exception raised in the case when collection's format (compact, full) doesn't not conform with its role."""

    def __init__(self, collection, inner_exception=None):
        """Initialize a new instance of CollectionWrongFormat class.

        :param collection: Collection with a wrong format
        :type collection: python_rwpm_parser.ast.Collection

        :param inner_exception: (Optional) inner exception
        :type inner_exception: Optional[Exception]
        """
        message = "Collection {0} must be {1} but it is not".format(
            collection.role.key, "compact" if collection.role.compact else "full"
        )

        super(CollectionWrongFormatError, self).__init__(
            collection, message, inner_exception
        )

        self._collection = collection

    @property
    def collection(self):
        """Return a collection with a wrong format.

        :return: Collection with a wrong format
        :rtype: python_rwpm_parser.ast.Collection
        """
        return self._collection


class MissingCollectionError(SemanticError):
    """Exception raised when a required sub-collection is missing."""

    def __init__(self, collection_role, inner_exception=None):
        """Initialize a new instance of CollectionWrongFormat class.

        :param collection_role: Role of the required collection
        :type collection_role: python_rwpm_parser.registry.CollectionRole

        :param inner_exception: (Optional) inner exception
        :type inner_exception: Optional[Exception]
        """
        super(MissingCollectionError, self).__init__(
            collection_role,
            "Required sub-collection {0} is missing".format(collection_role.key),
            inner_exception,
        )


class LinkWrongFormatError(SemanticError):
    """Exception raised in the case of a link having a wrong format."""

    def __init__(self, link, message, inner_exception=None):
        """Initialize a new instance of LinkWrongFormatError class.

        :param link: Link with a wrong format
        :type link: python_rwpm_parser.ast.Link

        :param message: Error message
        :type message: basestring

        :param inner_exception: (Optional) inner exception
        :type inner_exception: Optional[Exception]
        """
        super(LinkWrongFormatError, self).__init__(message, inner_exception)

        self._link = link

    @property
    def link(self):
        """Return a link with a wrong format.

        :return: Link with a wrong format
        :rtype: python_rwpm_parser.ast.Link
        """
        return self._link


class MissingLinkTypeError(LinkWrongFormatError):
    """Exception raised when a link does not have type."""

    def __init__(self, link, inner_exception=None):
        """Initialize a new instance of MissingLinkTypeError class.

        :param link: Link with a wrong format
        :type link: python_rwpm_parser.ast.Link

        :param inner_exception: (Optional) inner exception
        :type inner_exception: Optional[Exception]
        """
        super(MissingLinkTypeError, self).__init__(
            link, "Link {0} does not have type".format(link), inner_exception
        )


class UnknownLinkTypeError(LinkWrongFormatError):
    """Exception raised when a link has an unknown (not registered) type."""

    def __init__(self, link, inner_exception=None):
        """Initialize a new instance of UnknownLinkTypeError class.

        :param link: Link with a wrong format
        :type link: python_rwpm_parser.ast.Link

        :param inner_exception: (Optional) inner exception
        :type inner_exception: Optional[Exception]
        """
        super(UnknownLinkTypeError, self).__init__(
            link,
            "Link {0} has unknown (not registered) type {1}".format(link, link.type),
            inner_exception,
        )


class SemanticAnalyzer(Visitor):
    """Visitor performing semantic analysis of the RWPM-compatible documents."""

    def __init__(
        self, media_types_registry, link_relations_registry, collection_roles_registry
    ):
        """Initialize a new instance of SemanticAnalyzer.

        :param media_types_registry: Media types registry
        :type media_types_registry: python_rwpm_parser.registry.Registry

        :param link_relations_registry: Link relations registry
        :type link_relations_registry: python_rwpm_parser.registry.Registry

        :param collection_roles_registry: Collections roles registry
        :type collection_roles_registry: python_rwpm_parser.registry.Registry
        """
        self._media_types_registry = media_types_registry
        self._link_relations_registry = link_relations_registry
        self._collection_roles_registry = collection_roles_registry
        self._logger = logging.getLogger(__name__)

    @dispatch(Manifestlike)
    def visit(self, node):
        """Perform semantic analysis of the manifest node.

        :param node: Manifest-like node
        :type node: Manifestlike
        """
        self._logger.debug("Started processing {0}".format(node))

        node.metadata.accept(self)
        node.links.accept(self)

        self_link = first_or_default(
            node.links.get_by_rel(RWPMLinkRelationsRegistry.SELF.key)
        )

        if self_link is None:
            raise MISSING_SELF_LINK_ERROR

        if self_link.href is None or (
            not self_link.href.startswith("http://")
            and not self_link.href.startswith("https://")
        ):
            raise WRONG_SELF_LINK_HREF_FORMAT

        node.sub_collections.accept(self)

        self._logger.debug("Finished processing {0}".format(node))

    @dispatch(Metadata)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the manifest's metadata.

        :param node: Manifest's metadata
        :type node: Metadata
        """
        self._logger.debug("Started processing {0}".format(node))

        if "@type" not in node:
            raise MISSING_TYPE_METADATA_ERROR

        self._logger.debug("Finished processing {0}".format(node))

    @dispatch(LinksList)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the list of links.

        :param node: Manifest's metadata
        :type node: LinksList
        """
        self._logger.debug("Started processing {0}".format(node))

        for link in node:
            link.accept(self)

        self._logger.debug("Finished processing {0}".format(node))

    @dispatch(Link)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the link node.

        :param node: Link node
        :type node: Link
        """
        self._logger.debug("Started processing {0}".format(node))

        if node.type is not None and node.type not in self._media_types_registry:
            raise UnknownLinkTypeError(node)

        self._logger.debug("Finished processing {0}".format(node))

    @dispatch(CollectionList)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the list of sub-collections.

        :param node: CollectionList node
        :type node: CollectionList
        """
        self._logger.debug("Started processing {0}".format(node))

        for collection_role in self._collection_roles_registry:
            if collection_role.required:
                for sub_collection in node:
                    if sub_collection.role.key == collection_role.key:
                        sub_collection.accept(self)
                        break
                else:
                    raise MissingCollectionError(collection_role)

        self._logger.debug("Finished processing {0}".format(node))

    @dispatch(Collection)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the collection node.

        :param node: Collection node
        :type node: Collection
        """
        self._logger.debug("Started processing {0}".format(node))

        node.links.accept(self)

        if node.role.compact:
            if not node.compact:
                raise CollectionWrongFormatError(node)

            if node.role.key in [
                RWPMCollectionRolesRegistry.READING_ORDER.key,
                RWPMCollectionRolesRegistry.RESOURCES.key,
            ]:
                for link in node.links:
                    if link.type is None:
                        raise MissingLinkTypeError(link)
        else:
            if not node.full:
                raise CollectionWrongFormatError(node)

            node.metadata.accept(self)
            node.sub_collections.accept(self)

        self._logger.debug("Finished processing {0}".format(node))


class RWPMSemanticAnalyzer(SemanticAnalyzer):
    """RWPM semantic analyzer."""

    def __init__(
        self, media_types_registry, link_relations_registry, collection_roles_registry
    ):
        """Initialize a new instance of RWPMSemanticAnalyzer class.

        :param media_types_registry: Media types registry
        :type media_types_registry: python_rwpm_parser.registry.Registry

        :param link_relations_registry: Link relations registry
        :type link_relations_registry: python_rwpm_parser.registry.Registry

        :param collection_roles_registry: Collections roles registry
        :type collection_roles_registry: python_rwpm_parser.registry.Registry
        """
        super(RWPMSemanticAnalyzer, self).__init__(
            media_types_registry, link_relations_registry, collection_roles_registry
        )

        self._logger = logging.getLogger(__name__)

    @dispatch(Manifestlike)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the manifest node.

        :param node: Manifest's metadata
        :type node: Manifestlike
        """
        super(RWPMSemanticAnalyzer, self).visit(node)

    @dispatch(Metadata)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the manifest's metadata.

        :param node: Manifest's metadata
        :type node: Metadata
        """
        self._logger.debug("Started processing {0}".format(node))

        super(RWPMSemanticAnalyzer, self).visit(node)

        if "title" not in node:
            raise MISSING_TITLE_METADATA_ERROR

        self._logger.debug("Finished processing {0}".format(node))

    @dispatch(LinksList)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the list of links.

        :param node: Manifest's metadata
        :type node: LinksList
        """
        super(RWPMSemanticAnalyzer, self).visit(node)

    @dispatch(Link)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the link node.

        :param node: Link node
        :type node: Link
        """
        super(RWPMSemanticAnalyzer, self).visit(node)

    @dispatch(CollectionList)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the list of sub-collections.

        :param node: CollectionList node
        :type node: CollectionList
        """
        super(RWPMSemanticAnalyzer, self).visit(node)

    @dispatch(Collection)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the collection node.

        :param node: Collection node
        :type node: Collection
        """
        super(RWPMSemanticAnalyzer, self).visit(node)
