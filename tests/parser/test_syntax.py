from unittest import TestCase

from nose.tools import assert_raises, eq_
from parameterized import parameterized
from pyfakefs.fake_filesystem_unittest import Patcher

from webpub_manifest_parser.ast import Link, Metadata, RWPMManifest
from webpub_manifest_parser.parser.syntax import (
    MISSING_CONTEXT_ERROR,
    MISSING_LINKS_ERROR,
    MISSING_METADATA_ERROR,
    MissingPropertyError,
    MissingSubCollectionError,
    RWPMSyntaxAnalyzer,
    UnknownCollectionRolesError,
)
from webpub_manifest_parser.registry import (
    Registry,
    RWPMCollectionRolesRegistry,
    RWPMLinkRelationsRegistry,
    RWPMMediaTypesRegistry,
)

RWPM_MANIFEST_WITHOUT_CONTEXT = """
{
}
"""

RWPM_MANIFEST_WITHOUT_METADATA = """
{
    "@context": "https://readium.org/webpub-manifest/context.jsonld",
    
    "links": [
        {"rel": "self", "href": "https://example.com/manifest.json", "type": "application/webpub+json"}
    ]  
}
"""

RWPM_MANIFEST_WITHOUT_LINKS = """
{
    "@context": "https://readium.org/webpub-manifest/context.jsonld",
    
    "metadata": {
        "@type": "http://schema.org/Book",
        "title": "Moby-Dick",
        "author": "Herman Melville",
        "identifier": "urn:isbn:978031600000X",
        "language": "en",
        "modified": "2015-09-29T17:00:00Z"
    }
}
"""

RWPM_MANIFEST_WITH_MISSING_LINK_PROPERTY = """
{
    "@context": "https://readium.org/webpub-manifest/context.jsonld",

    "metadata": {
        "@type": "http://schema.org/Book",
        "title": "Moby-Dick",
        "author": "Herman Melville",
        "identifier": "urn:isbn:978031600000X",
        "language": "en",
        "modified": "2015-09-29T17:00:00Z"
    },

    "links": [
        {"rel": "self", "type": "application/webpub+json"}
    ]
}
"""

RWPM_MANIFEST_WITH_MISSING_SUB_COLLECTION = """
{
    "@context": "https://readium.org/webpub-manifest/context.jsonld",

    "metadata": {
        "@type": "http://schema.org/Book",
        "title": "Moby-Dick",
        "author": "Herman Melville",
        "identifier": "urn:isbn:978031600000X",
        "language": "en",
        "modified": "2015-09-29T17:00:00Z"
    },

    "links": [
        {"rel": "self", "href": "https://example.com/manifest.json", "type": "application/webpub+json"}
    ]
}
"""

RWPM_MANIFEST_WITH_UNKNOWN_SUB_COLLECTION = """
{
    "@context": "https://readium.org/webpub-manifest/context.jsonld",

    "metadata": {
        "@type": "http://schema.org/Book",
        "title": "Moby-Dick",
        "author": "Herman Melville",
        "identifier": "urn:isbn:978031600000X",
        "language": "en",
        "modified": "2015-09-29T17:00:00Z"
    },

    "links": [
        {"rel": "self", "href": "https://example.com/manifest.json", "type": "application/webpub+json"}
    ],

    "unknownSubCollection": [
        {"href": "https://example.com/c001.html", "type": "text/html", "title": "Chapter 1"}
    ]
}
"""

RWPM_MANIFEST = """
{
    "@context": "https://readium.org/webpub-manifest/context.jsonld",

    "metadata": {
        "@type": "http://schema.org/Book",
        "title": "Moby-Dick",
        "author": "Herman Melville",
        "identifier": "urn:isbn:978031600000X",
        "language": "en",
        "modified": "2015-09-29T17:00:00Z"
    },

    "links": [
        {"rel": "self", "href": "https://example.com/manifest.json", "type": "application/webpub+json"}
    ],

    "readingOrder": [
        {"href": "https://example.com/c001.html", "type": "text/html", "title": "Chapter 1"}
    ]
}
"""


class RWPMSyntaxAnalyzerTest(TestCase):
    @parameterized.expand(
        [
            (
                "when_manifest_does_not_contain_context",
                RWPM_MANIFEST_WITHOUT_CONTEXT,
                MISSING_CONTEXT_ERROR,
            ),
            (
                "when_manifest_does_not_contain_metadata",
                RWPM_MANIFEST_WITHOUT_METADATA,
                MISSING_METADATA_ERROR,
            ),
            (
                "when_manifest_does_not_contain_links",
                RWPM_MANIFEST_WITHOUT_LINKS,
                MISSING_LINKS_ERROR,
            ),
        ]
    )
    def test_syntax_analyzer_raises_correct_format_errors(
        self, _, rwpm_manifest_content, expected_error
    ):
        # Arrange
        collection_roles_registry = Registry()
        syntax_analyzer = RWPMSyntaxAnalyzer(collection_roles_registry)
        expected_error_class = (
            expected_error.__class__
            if isinstance(expected_error, Exception)
            else expected_error
        )
        expected_error_message = (
            str(expected_error) if isinstance(expected_error, Exception) else None
        )
        input_file_path = "/tmp/rwpm.jsonld"

        with Patcher() as patcher:
            patcher.fs.create_file(input_file_path, contents=rwpm_manifest_content)

            # Act
            with assert_raises(expected_error_class) as assert_raises_context:
                syntax_analyzer.analyze(input_file_path)

            # Assert
            if expected_error_message:
                eq_(str(assert_raises_context.exception), expected_error_message)

    def test_syntax_analyzer_raises_missing_property_error(self):
        # Arrange
        collection_roles_registry = Registry()
        syntax_analyzer = RWPMSyntaxAnalyzer(collection_roles_registry)
        input_file_path = "/tmp/rwpm.jsonld"

        with Patcher() as patcher:
            patcher.fs.create_file(
                input_file_path, contents=RWPM_MANIFEST_WITH_MISSING_LINK_PROPERTY
            )

            # Act
            with assert_raises(MissingPropertyError) as assert_raises_context:
                syntax_analyzer.analyze(input_file_path)

            # Assert
            eq_(assert_raises_context.exception.cls, Link)
            eq_(assert_raises_context.exception.object_property, Link.href)

    def test_syntax_analyzer_raises_missing_sub_collection(self):
        # Arrange
        missing_sub_collection_role = RWPMCollectionRolesRegistry.READING_ORDER
        collection_roles_registry = Registry(
            [missing_sub_collection_role, RWPMCollectionRolesRegistry.PAGE_LIST]
        )
        syntax_analyzer = RWPMSyntaxAnalyzer(collection_roles_registry)
        input_file_path = "/tmp/rwpm.jsonld"

        with Patcher() as patcher:
            patcher.fs.create_file(
                input_file_path, contents=RWPM_MANIFEST_WITH_MISSING_SUB_COLLECTION
            )

            # Act
            with assert_raises(MissingSubCollectionError) as assert_raises_context:
                syntax_analyzer.analyze(input_file_path)

            # Assert
            eq_(
                assert_raises_context.exception.sub_collection_role,
                missing_sub_collection_role,
            )

    def test_syntax_analyzer_raises_unknown_collection_error(self):
        # Arrange
        collection_roles_registry = Registry()
        syntax_analyzer = RWPMSyntaxAnalyzer(collection_roles_registry)
        input_file_path = "/tmp/rwpm.jsonld"

        with Patcher() as patcher:
            patcher.fs.create_file(
                input_file_path, contents=RWPM_MANIFEST_WITH_UNKNOWN_SUB_COLLECTION
            )

            # Act
            with assert_raises(UnknownCollectionRolesError) as assert_raises_context:
                syntax_analyzer.analyze(input_file_path)

            # Assert
            eq_(
                assert_raises_context.exception.unknown_sub_collection_keys,
                ["unknownSubCollection"],
            )

    def test_syntax_analyzer_returns_ast(self):
        # Arrange
        sub_collection_role = RWPMCollectionRolesRegistry.READING_ORDER
        collection_roles_registry = Registry([sub_collection_role])
        syntax_analyzer = RWPMSyntaxAnalyzer(collection_roles_registry)
        input_file_path = "/tmp/rwpm.jsonld"

        with Patcher() as patcher:
            patcher.fs.create_file(input_file_path, contents=RWPM_MANIFEST)

            # Act
            result = syntax_analyzer.analyze(input_file_path)

            # Assert
            eq_(isinstance(result, RWPMManifest), True)
            eq_(result.context, "https://readium.org/webpub-manifest/context.jsonld")

            eq_(isinstance(result.metadata, Metadata), True)
            eq_(
                result.metadata,
                {
                    "@type": "http://schema.org/Book",
                    "title": "Moby-Dick",
                    "author": "Herman Melville",
                    "identifier": "urn:isbn:978031600000X",
                    "language": "en",
                    "modified": "2015-09-29T17:00:00Z",
                },
            )

            eq_(len(result.links), 1)
            [link] = result.links
            eq_(link.rel, RWPMLinkRelationsRegistry.SELF.key)
            eq_(link.href, "https://example.com/manifest.json")
            eq_(link.type, RWPMMediaTypesRegistry.MANIFEST.key)

            eq_(len(result.sub_collections), 1)
            [sub_collection] = result.sub_collections
            eq_(sub_collection.role, sub_collection_role)

            eq_(len(sub_collection.links), 1)
            [sub_collection_link] = sub_collection.links
            eq_(sub_collection_link.href, "https://example.com/c001.html")
            eq_(sub_collection_link.type, RWPMMediaTypesRegistry.HTML.key)
            eq_(sub_collection_link.title, "Chapter 1")
