import os
from unittest import TestCase

from nose.tools import eq_

from webpub_manifest_parser.ast import RWPMManifest
from webpub_manifest_parser.parser.parser import RWPMParserFactory
from webpub_manifest_parser.registry import (
    RWPMCollectionRolesRegistry,
    RWPMLinkRelationsRegistry,
    RWPMMediaTypesRegistry,
)
from webpub_manifest_parser.utils import first_or_default


class RWPMParserTest(TestCase):
    def test(self):
        parser_factory = RWPMParserFactory()
        parser = parser_factory.create()
        input_file_path = os.path.join(
            os.path.dirname(__file__), "../files/rwpm/spec_example.json"
        )
        manifest = parser.parse(input_file_path)

        eq_(manifest.context is not None, True)
        eq_(manifest.context, RWPMManifest.DEFAULT_CONTEXT)

        eq_(manifest.metadata is not None, True)
        eq_(manifest.metadata["@type"], "http://schema.org/Book")

        eq_(len(manifest.links), 3)
        eq_(manifest.links[0].rel, RWPMLinkRelationsRegistry.SELF.key)
        eq_(manifest.links[0].href, "https://example.com/manifest.json")
        eq_(manifest.links[0].type, "application/webpub+json")

        eq_(manifest.links[1].rel, RWPMLinkRelationsRegistry.ALTERNATE.key)
        eq_(manifest.links[1].href, "https://example.com/publication.epub")
        eq_(manifest.links[1].type, "application/epub+zip")

        eq_(manifest.links[2].rel, RWPMLinkRelationsRegistry.SEARCH.key)
        eq_(manifest.links[2].href, "https://example.com/search{?query}")
        eq_(manifest.links[2].type, "text/html")
        eq_(manifest.links[2].templated, True)

        eq_(len(manifest.sub_collections), 2)

        reading_order_sub_collection = first_or_default(
            manifest.sub_collections.get_by_role(
                RWPMCollectionRolesRegistry.READING_ORDER.key
            )
        )
        eq_(
            reading_order_sub_collection.role.key,
            RWPMCollectionRolesRegistry.READING_ORDER.key,
        )
        eq_(len(reading_order_sub_collection.links), 2)
        eq_(reading_order_sub_collection.links[0].href, "https://example.com/c001.html")
        eq_(reading_order_sub_collection.links[0].type, RWPMMediaTypesRegistry.HTML.key)
        eq_(reading_order_sub_collection.links[0].title, "Chapter 1")

        eq_(reading_order_sub_collection.links[1].href, "https://example.com/c002.html")
        eq_(reading_order_sub_collection.links[1].type, RWPMMediaTypesRegistry.HTML.key)
        eq_(reading_order_sub_collection.links[1].title, "Chapter 2")

        resources_sub_collection = first_or_default(
            manifest.sub_collections.get_by_role(
                RWPMCollectionRolesRegistry.RESOURCES.key
            )
        )
        eq_(
            resources_sub_collection.role.key, RWPMCollectionRolesRegistry.RESOURCES.key
        )
        eq_(len(resources_sub_collection.links), 5)
        eq_(resources_sub_collection.links[0].rel, RWPMLinkRelationsRegistry.COVER.key)
        eq_(resources_sub_collection.links[0].href, "https://example.com/cover.jpg")
        eq_(resources_sub_collection.links[0].type, RWPMMediaTypesRegistry.JPEG.key)
        eq_(resources_sub_collection.links[0].height, 600)
        eq_(resources_sub_collection.links[0].width, 400)

        eq_(resources_sub_collection.links[1].href, "https://example.com/style.css")
        eq_(resources_sub_collection.links[1].type, RWPMMediaTypesRegistry.CSS.key)

        eq_(resources_sub_collection.links[2].href, "https://example.com/whale.jpg")
        eq_(resources_sub_collection.links[2].type, RWPMMediaTypesRegistry.JPEG.key)

        eq_(resources_sub_collection.links[3].href, "https://example.com/boat.svg")
        eq_(resources_sub_collection.links[3].type, RWPMMediaTypesRegistry.SVG_XML.key)

        eq_(resources_sub_collection.links[4].href, "https://example.com/notes.html")
        eq_(resources_sub_collection.links[4].type, RWPMMediaTypesRegistry.HTML.key)
