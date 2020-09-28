from unittest import TestCase

from nose.tools import assert_raises, eq_
from parameterized import parameterized

from webpub_manifest_parser.ast import Collection, Link, Metadata, RWPMManifest
from webpub_manifest_parser.parser.semantic import (
    MISSING_SELF_LINK_ERROR,
    MISSING_TITLE_METADATA_ERROR,
    MISSING_TYPE_METADATA_ERROR,
    WRONG_SELF_LINK_HREF_FORMAT,
    CollectionWrongFormatError,
    MissingCollectionError,
    MissingLinkTypeError,
    RWPMSemanticAnalyzer,
    UnknownLinkTypeError,
)
from webpub_manifest_parser.registry import (
    CollectionRole,
    Registry,
    RWPMCollectionRolesRegistry,
    RWPMLinkRelationsRegistry,
    RWPMMediaTypesRegistry,
)


class SemanticAnalyzerTest(TestCase):
    @parameterized.expand(
        [
            ("when_@type_is_missing", {}, [], MISSING_TYPE_METADATA_ERROR),
            (
                "when_title_is_missing",
                {"@type": "http://schema.org/Book"},
                [],
                MISSING_TITLE_METADATA_ERROR,
            ),
            (
                "when_self_link_is_missing",
                {"@type": "http://schema.org/Book", "title": "Test"},
                [],
                MISSING_SELF_LINK_ERROR,
            ),
            (
                "when_self_link_href_has_wrong_format",
                {"@type": "http://schema.org/Book", "title": "Test"},
                [Link(rel=RWPMLinkRelationsRegistry.SELF.key, href="www.example.org")],
                WRONG_SELF_LINK_HREF_FORMAT,
            ),
        ]
    )
    def test_semantic_analyzer_raises_error(self, _, metadata, links, expected_error):
        # Arrange
        manifest = RWPMManifest()
        manifest.context = RWPMManifest.DEFAULT_CONTEXT
        manifest.metadata = Metadata(metadata)
        manifest.links.extend(links)
        media_types_registry = Registry()
        link_relations_registry = Registry()
        collection_roles_registry = Registry()
        semantic_analyzer = RWPMSemanticAnalyzer(
            media_types_registry, link_relations_registry, collection_roles_registry
        )

        # Act
        with assert_raises(expected_error.__class__) as assert_raises_context:
            semantic_analyzer.visit(manifest)

        # Assert
        eq_(str(assert_raises_context.exception), str(expected_error))

    @parameterized.expand(
        [
            (
                "links_without_types",
                [Link(href="https://example.com/c001.html")],
                MissingLinkTypeError,
            ),
            (
                "links_with_unknown_type",
                [Link(href="https://example.com/c001.html", _type="text/unknown")],
                UnknownLinkTypeError,
            ),
        ]
    )
    def test_semantic_analyzer_raises_error_when_compact_collection_has(
        self, _, links, expected_error
    ):
        # Arrange
        reading_order_sub_collection = Collection(
            RWPMCollectionRolesRegistry.READING_ORDER
        )
        reading_order_sub_collection.links.extend(links)

        self_link = Link(
            rel=RWPMLinkRelationsRegistry.SELF.key, href="https://example.org"
        )

        manifest = RWPMManifest()
        manifest.context = RWPMManifest.DEFAULT_CONTEXT
        manifest.metadata = Metadata(
            {"@type": "http://schema.org/Book", "title": "Test"}
        )
        manifest.links.append(self_link)
        manifest.sub_collections.append(reading_order_sub_collection)

        media_types_registry = Registry()
        link_relations_registry = Registry()
        collection_roles_registry = Registry(
            [RWPMCollectionRolesRegistry.READING_ORDER]
        )
        semantic_analyzer = RWPMSemanticAnalyzer(
            media_types_registry, link_relations_registry, collection_roles_registry
        )

        # Act, assert
        with assert_raises(expected_error):
            semantic_analyzer.visit(manifest)

    def test_semantic_analyzer_raises_error_when_compact_collection_is_not_compact(
        self,
    ):
        # Arrange
        sub_collection_link_type = RWPMMediaTypesRegistry.HTML
        sub_collection_link = Link(
            href="https://example.org/index.html", _type=sub_collection_link_type.key
        )
        compact_collection_role = RWPMCollectionRolesRegistry.READING_ORDER
        compact_sub_collection = Collection(compact_collection_role)
        compact_sub_collection.metadata = Metadata()
        compact_sub_collection.links.append(sub_collection_link)

        self_link = Link(
            rel=RWPMLinkRelationsRegistry.SELF.key, href="https://example.org"
        )

        manifest = RWPMManifest()
        manifest.context = RWPMManifest.DEFAULT_CONTEXT
        manifest.metadata = Metadata(
            {"@type": "http://schema.org/Book", "title": "Test"}
        )
        manifest.links.append(self_link)
        manifest.sub_collections.append(compact_sub_collection)

        media_types_registry = Registry([sub_collection_link_type])
        link_relations_registry = Registry()
        collection_roles_registry = Registry([compact_collection_role])
        semantic_analyzer = RWPMSemanticAnalyzer(
            media_types_registry, link_relations_registry, collection_roles_registry
        )

        # Act, assert
        with assert_raises(CollectionWrongFormatError):
            semantic_analyzer.visit(manifest)

    def test_semantic_analyzer_raises_error_when_full_collection_is_not_full(self):
        # Arrange
        full_collection_role = CollectionRole("dummy", False, True)
        full_sub_collection = Collection(full_collection_role)

        self_link = Link(
            rel=RWPMLinkRelationsRegistry.SELF.key, href="https://example.org"
        )

        manifest = RWPMManifest()
        manifest.context = RWPMManifest.DEFAULT_CONTEXT
        manifest.metadata = Metadata(
            {"@type": "http://schema.org/Book", "title": "Test"}
        )
        manifest.links.append(self_link)
        manifest.sub_collections.append(full_sub_collection)

        media_types_registry = Registry()
        link_relations_registry = Registry()
        collection_roles_registry = Registry([full_collection_role])
        semantic_analyzer = RWPMSemanticAnalyzer(
            media_types_registry, link_relations_registry, collection_roles_registry
        )

        # Act, assert
        with assert_raises(CollectionWrongFormatError):
            semantic_analyzer.visit(manifest)

    def test_semantic_analyzer_raises_error_required_sub_collection_is_missing(self):
        # Arrange
        required_collection_role = CollectionRole("dummy", True, True)

        self_link = Link(
            rel=RWPMLinkRelationsRegistry.SELF.key, href="https://example.org"
        )

        manifest = RWPMManifest()
        manifest.context = RWPMManifest.DEFAULT_CONTEXT
        manifest.metadata = Metadata(
            {"@type": "http://schema.org/Book", "title": "Test"}
        )
        manifest.links.append(self_link)

        media_types_registry = Registry()
        link_relations_registry = Registry()
        collection_roles_registry = Registry([required_collection_role])
        semantic_analyzer = RWPMSemanticAnalyzer(
            media_types_registry, link_relations_registry, collection_roles_registry
        )

        # Act, assert
        with assert_raises(MissingCollectionError):
            semantic_analyzer.visit(manifest)

    def test_semantic_analyzer_does_correctly_processes_valid_ast(self):
        reading_order_sub_collection = Collection(
            RWPMCollectionRolesRegistry.READING_ORDER
        )
        reading_order_sub_collection.links.append(
            Link(
                href="https://example.com/text.html",
                _type=RWPMMediaTypesRegistry.HTML.key,
            )
        )

        self_link = Link(
            rel=RWPMLinkRelationsRegistry.SELF.key,
            href="https://example.com/manifest.json",
        )

        manifest = RWPMManifest()
        manifest.context = RWPMManifest.DEFAULT_CONTEXT
        manifest.metadata = Metadata(
            {"@type": "http://schema.org/Book", "title": "Test"}
        )
        manifest.links.append(self_link)
        manifest.sub_collections.append(reading_order_sub_collection)

        media_types_registry = Registry([RWPMMediaTypesRegistry.HTML])
        link_relations_registry = Registry()
        collection_roles_registry = Registry(
            [RWPMCollectionRolesRegistry.READING_ORDER]
        )
        semantic_analyzer = RWPMSemanticAnalyzer(
            media_types_registry, link_relations_registry, collection_roles_registry
        )

        # Act
        semantic_analyzer.visit(manifest)
