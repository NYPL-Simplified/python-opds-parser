import datetime
import logging
import os
from unittest import TestCase

from webpub_manifest_parser.core.ast import CompactCollection, PresentationMetadata
from webpub_manifest_parser.opds2.ast import OPDS2FeedMetadata
from webpub_manifest_parser.opds2.parsers import OPDS2DocumentParserFactory
from webpub_manifest_parser.opds2.registry import (
    OPDS2LinkRelationsRegistry,
    OPDS2MediaTypesRegistry,
)
from webpub_manifest_parser.utils import first_or_default


class OPDS2Parser(TestCase):
    def test(self):
        # Arrange
        logging._defaultFormatter = logging.Formatter(u"%(message)s")

        parser_factory = OPDS2DocumentParserFactory()
        parser = parser_factory.create()
        input_file_path = os.path.join(
            os.path.dirname(__file__), "../../files/opds2/test.json"
        )

        # Act
        feed = parser.parse_file(input_file_path)

        # Assert
        self.assertIsInstance(feed.metadata, OPDS2FeedMetadata)
        self.assertEqual(feed.metadata.title, "Example listing publications")

        self.assertIsInstance(feed.links, list)
        self.assertEqual(1, len(feed.links))
        [manifest_link] = feed.links
        self.assertEqual(manifest_link.rel[0], OPDS2LinkRelationsRegistry.SELF.key)
        self.assertEqual(manifest_link.href, "http://example.com/new")
        self.assertEqual(manifest_link.type, OPDS2MediaTypesRegistry.OPDS_FEED.key)

        self.assertIsInstance(feed.publications, list)
        self.assertEqual(1, len(feed.publications))
        [publication] = feed.publications

        self.assertIsInstance(publication.metadata, PresentationMetadata)
        self.assertEqual("http://schema.org/Book", publication.metadata.type)
        self.assertEqual("Moby-Dick", publication.metadata.title)
        self.assertEqual("Herman Melville", publication.metadata.author)
        self.assertEqual("urn:isbn:978031600000X", publication.metadata.identifier)
        self.assertEqual("en", publication.metadata.language)
        self.assertEqual(
            datetime.datetime(2015, 9, 29, 17, 0, 0), publication.metadata.modified
        )

        self.assertIsInstance(publication.links, list)
        self.assertEqual(len(publication.links), 2)

        publication_self_link = first_or_default(
            publication.links.get_by_rel(OPDS2LinkRelationsRegistry.SELF.key)
        )
        self.assertEqual(
            OPDS2LinkRelationsRegistry.SELF.key, publication_self_link.rel[0]
        )
        self.assertEqual(
            "http://example.org/publication.json", publication_self_link.href
        )
        self.assertEqual(
            OPDS2MediaTypesRegistry.OPDS_PUBLICATION.key, publication_self_link.type
        )

        publication_acquisition_link = first_or_default(
            publication.links.get_by_rel(OPDS2LinkRelationsRegistry.OPEN_ACCESS.key)
        )
        self.assertEqual(
            OPDS2LinkRelationsRegistry.OPEN_ACCESS.key,
            publication_acquisition_link.rel[0],
        )
        self.assertEqual(
            "http://example.org/file.epub", publication_acquisition_link.href
        )
        self.assertEqual(
            OPDS2MediaTypesRegistry.EPUB_PUBLICATION_PACKAGE.key,
            publication_acquisition_link.type,
        )

        self.assertIsInstance(publication.images, CompactCollection)
        self.assertIsInstance(publication.images.links, list)
        self.assertEqual(3, len(publication.images.links))

        jpeg_cover_link = first_or_default(
            publication.images.links.get_by_href("http://example.org/cover.jpg")
        )
        self.assertEqual([], jpeg_cover_link.rel)
        self.assertEqual("http://example.org/cover.jpg", jpeg_cover_link.href)
        self.assertEqual(OPDS2MediaTypesRegistry.JPEG.key, jpeg_cover_link.type)
        self.assertEqual(1400, jpeg_cover_link.height)
        self.assertEqual(800, jpeg_cover_link.width)

        small_jpeg_cover_link = first_or_default(
            publication.images.links.get_by_href("http://example.org/cover-small.jpg")
        )
        self.assertEqual(
            "http://example.org/cover-small.jpg", small_jpeg_cover_link.href
        )
        self.assertEqual(OPDS2MediaTypesRegistry.JPEG.key, small_jpeg_cover_link.type)
        self.assertEqual(700, small_jpeg_cover_link.height)
        self.assertEqual(400, small_jpeg_cover_link.width)

        svg_cover_link = first_or_default(
            publication.images.links.get_by_href("http://example.org/cover.svg")
        )
        self.assertEqual(svg_cover_link.href, "http://example.org/cover.svg")
        self.assertEqual(svg_cover_link.type, OPDS2MediaTypesRegistry.SVG_XML.key)
