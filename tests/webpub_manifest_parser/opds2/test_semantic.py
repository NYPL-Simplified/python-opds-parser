from unittest import TestCase

from nose.tools import assert_raises, eq_
from parameterized import parameterized

from webpub_manifest_parser.core.ast import (
    Collection,
    CollectionList,
    Link,
    LinkList,
    PresentationMetadata,
)
from webpub_manifest_parser.opds2.ast import OPDS2Feed, OPDS2Publication
from webpub_manifest_parser.opds2.registry import (
    OPDS2CollectionRolesRegistry,
    OPDS2LinkRelationsRegistry,
    OPDS2MediaTypesRegistry,
)
from webpub_manifest_parser.opds2.semantic import (
    MISSING_ACQUISITION_LINK,
    MISSING_NAVIGATION_LINK_TITLE_ERROR,
    MISSING_REQUIRED_FEED_SUB_COLLECTIONS,
    OPDS2SemanticAnalyzer,
)
from webpub_manifest_parser.rwpm.registry import RWPMLinkRelationsRegistry


class SemanticAnalyzerTest(TestCase):
    @parameterized.expand(
        [
            (
                "when_feed_does_not_contain_neither_publications_nor_navigation_nor_groups",
                OPDS2Feed(
                    metadata=PresentationMetadata("test"),
                    links=LinkList(
                        [
                            Link(
                                href="http://example.com",
                                rel=[RWPMLinkRelationsRegistry.SELF.key],
                            )
                        ]
                    ),
                ),
                MISSING_REQUIRED_FEED_SUB_COLLECTIONS,
            ),
            (
                "when_navigation_link_does_not_contain_title",
                OPDS2Feed(
                    metadata=PresentationMetadata("test"),
                    links=LinkList(
                        [
                            Link(
                                href="http://example.com",
                                rel=[RWPMLinkRelationsRegistry.SELF.key],
                            )
                        ]
                    ),
                    navigation=Collection(
                        links=LinkList([Link(href="http://example.com")])
                    ),
                ),
                MISSING_NAVIGATION_LINK_TITLE_ERROR,
            ),
            (
                "when_publication_does_not_contain_acquisition_link",
                OPDS2Feed(
                    metadata=PresentationMetadata("test"),
                    links=LinkList(
                        [
                            Link(
                                href="http://example.com",
                                rel=[RWPMLinkRelationsRegistry.SELF.key],
                            )
                        ]
                    ),
                    publications=CollectionList(
                        [
                            OPDS2Publication(
                                links=LinkList([Link(href="http://example.com")])
                            )
                        ]
                    ),
                ),
                MISSING_ACQUISITION_LINK,
            ),
        ]
    )
    def test_semantic_analyzer_raises_error(self, _, manifest, expected_error):
        # Arrange
        media_types_registry = OPDS2MediaTypesRegistry()
        link_relations_registry = OPDS2LinkRelationsRegistry()
        collection_roles_registry = OPDS2CollectionRolesRegistry()
        semantic_analyzer = OPDS2SemanticAnalyzer(
            media_types_registry, link_relations_registry, collection_roles_registry
        )

        # Act
        with assert_raises(expected_error.__class__) as assert_raises_context:
            semantic_analyzer.visit(manifest)

        # Assert
        eq_(str(assert_raises_context.exception), str(expected_error))

    def test_semantic_analyzer_does_correctly_processes_valid_ast(self):
        # Arrange
        manifest = OPDS2Feed(
            metadata=PresentationMetadata("test"),
            links=LinkList(
                [
                    Link(
                        href="http://example.com",
                        rel=[RWPMLinkRelationsRegistry.SELF.key],
                    )
                ]
            ),
            publications=CollectionList(
                [
                    OPDS2Publication(
                        links=LinkList(
                            [
                                Link(
                                    href="http://example.com",
                                    rel=[OPDS2LinkRelationsRegistry.ACQUISITION.key],
                                )
                            ]
                        )
                    )
                ]
            ),
        )
        media_types_registry = OPDS2MediaTypesRegistry()
        link_relations_registry = OPDS2LinkRelationsRegistry()
        collection_roles_registry = OPDS2CollectionRolesRegistry()
        semantic_analyzer = OPDS2SemanticAnalyzer(
            media_types_registry, link_relations_registry, collection_roles_registry
        )

        # Act
        semantic_analyzer.visit(manifest)
