from multipledispatch import dispatch

from webpub_manifest_parser.core.ast import (
    Collection,
    CollectionList,
    CompactCollection,
    Link,
    LinkList,
    Manifestlike,
    Metadata,
    PresentationMetadata,
)
from webpub_manifest_parser.core.errors import BaseSemanticError
from webpub_manifest_parser.odl.ast import ODLLicense
from webpub_manifest_parser.odl.registry import ODLMediaTypesRegistry
from webpub_manifest_parser.opds2.ast import (
    OPDS2Feed,
    OPDS2FeedMetadata,
    OPDS2Publication,
)
from webpub_manifest_parser.opds2.registry import OPDS2LinkRelationsRegistry
from webpub_manifest_parser.opds2.semantic import OPDS2SemanticAnalyzer
from webpub_manifest_parser.utils import encode, first_or_default

MUST_CONTAIN_PUBLICATIONS = BaseSemanticError(
    "ODL Feed must contain publications subcollection"
)

MUST_NOT_CONTAIN_GROUPS_FACETS_NAVIGATION = BaseSemanticError(
    "ODL Feed must not contain groups, facets, navigation"
)

MUST_CONTAIN_EITHER_LICENSES_OR_OA_ACQUISITION_LINK = BaseSemanticError(
    "ODL publication must contain either contain a licenses subcollection or "
    "an Open-Access Acquisition Link (http://opds-spec.org/acquisition/open-access)"
)

MUST_CONTAIN_SELF_LINK_TO_LICENSE_INFO_DOCUMENT = BaseSemanticError(
    "ODL License must contain a self link to the License Info Document"
)

MUST_CONTAIN_CHECKOUT_LINK_TO_LICENSE_STATUS_DOCUMENT = BaseSemanticError(
    "ODL License must contain a checkout link to the License Status Document"
)


class ODLSemanticAnalyzer(OPDS2SemanticAnalyzer):
    """ODL 2.0 semantic analyzer."""

    @dispatch(Manifestlike)
    def visit(self, node):
        """Perform semantic analysis of the manifest node.

        :param node: Manifest-like node
        :type node: Manifestlike
        """
        super(ODLSemanticAnalyzer, self).visit(node)

    @dispatch(Metadata)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the feed's metadata.

        :param node: Feed's metadata
        :type node: OPDS2FeedMetadata
        """
        super(ODLSemanticAnalyzer, self).visit(node)

    @dispatch(PresentationMetadata)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the feed's metadata.

        :param node: Feed's metadata
        :type node: PresentationMetadata
        """

    @dispatch(OPDS2Feed)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the OPDS 2.0 publication.

        :param node: OPDS 2.0 publication
        :type node: OPDS2Feed
        """
        self._logger.debug(u"Started processing {0}".format(encode(node)))

        super(ODLSemanticAnalyzer, self).visit(node)

        if not node.publications:
            raise MUST_CONTAIN_PUBLICATIONS

        if node.groups or node.facets or node.navigation:
            raise MUST_NOT_CONTAIN_GROUPS_FACETS_NAVIGATION

        self._logger.debug(u"Finished processing {0}".format(encode(node)))

    @dispatch(OPDS2FeedMetadata)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the feed's metadata.

        :param node: Feed's metadata
        :type node: OPDS2FeedMetadata
        """
        super(ODLSemanticAnalyzer, self).visit(node)

    @dispatch(OPDS2Publication)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the OPDS 2.0 publication.

        :param node: OPDS 2.0 publication
        :type node: OPDS2Publication
        """
        self._logger.debug(u"Started processing {0}".format(encode(node)))

        if not node.licenses:
            for link in node.links:
                if OPDS2LinkRelationsRegistry.OPEN_ACCESS.key in link.rels:
                    break

                raise MUST_CONTAIN_EITHER_LICENSES_OR_OA_ACQUISITION_LINK

        self._logger.debug(u"Finished processing {0}".format(encode(node)))

    @dispatch(LinkList)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the list of links.

        :param node: Manifest's metadata
        :type node: LinkList
        """
        super(ODLSemanticAnalyzer, self).visit(node)

    @dispatch(Link)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the link node.

        :param node: Link node
        :type node: Link
        """
        super(ODLSemanticAnalyzer, self).visit(node)

    @dispatch(CollectionList)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the list of sub-collections.

        :param node: CollectionList node
        :type node: CollectionList
        """
        super(ODLSemanticAnalyzer, self).visit(node)

    @dispatch(CompactCollection)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the compact collection node.

        :param node: Collection node
        :type node: CompactCollection
        """
        super(ODLSemanticAnalyzer, self).visit(node)

    @dispatch(Collection)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the collection node.

        :param node: Collection node
        :type node: Collection
        """
        super(ODLSemanticAnalyzer, self).visit(node)

    @dispatch(ODLLicense)  # noqa: F811
    def visit(self, node):  # pylint: disable=E0102
        """Perform semantic analysis of the ODL license node.

        :param node: ODLLicense node
        :type node: ODLLicense
        """
        self_link = first_or_default(
            node.links.get_by_rel(OPDS2LinkRelationsRegistry.SELF.key)
        )

        if (
            not self_link
            or self_link.type != ODLMediaTypesRegistry.ODL_LICENSE_INFO_DOCUMENT.key
        ):
            raise MUST_CONTAIN_SELF_LINK_TO_LICENSE_INFO_DOCUMENT

        borrow_link = first_or_default(
            node.links.get_by_rel(OPDS2LinkRelationsRegistry.BORROW.key)
        )

        if (
            not borrow_link
            or borrow_link.type != ODLMediaTypesRegistry.ODL_LICENSE_STATUS_DOCUMENT.key
        ):
            raise MUST_CONTAIN_CHECKOUT_LINK_TO_LICENSE_STATUS_DOCUMENT
