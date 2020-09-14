import os
from unittest import TestCase

from nose.tools import eq_

from python_rwpm_parser.ast import RWPMManifest
from python_rwpm_parser.parser.parser import RWPMParserFactory
from python_rwpm_parser.registry import (RWPMCollectionRolesRegistry,
                                         RWPMLinkRelationsRegistry,
                                         RWPMMediaTypesRegistry)


class RWPMParserTest(TestCase):
    def test(self):
        parser_factory = RWPMParserFactory()
        parser = parser_factory.create()
        input_file_path = os.path.join(os.path.dirname(__file__), '../files/rwpm/spec_example.json')
        manifest = parser.parse(input_file_path)

        eq_(manifest.context is not None, True)
        eq_(manifest.context, RWPMManifest.DEFAULT_CONTEXT)

        eq_(manifest.metadata is not None, True)
        eq_(manifest.metadata['@type'], 'http://schema.org/Book')

        eq_(len(manifest.links), 3)
        eq_(manifest.links[0].rel, RWPMLinkRelationsRegistry.SELF.key)
        eq_(manifest.links[0].href, 'https://example.com/manifest.json')
        eq_(manifest.links[0].type, 'application/webpub+json')

        eq_(manifest.links[1].rel, RWPMLinkRelationsRegistry.ALTERNATE.key)
        eq_(manifest.links[1].href, 'https://example.com/publication.epub')
        eq_(manifest.links[1].type, 'application/epub+zip')

        eq_(manifest.links[2].rel, RWPMLinkRelationsRegistry.SEARCH.key)
        eq_(manifest.links[2].href, 'https://example.com/search{?query}')
        eq_(manifest.links[2].type, 'text/html')
        eq_(manifest.links[2].templated, True)

        eq_(len(manifest.sub_collections), 2)
        eq_(manifest.sub_collections[0].role.key, RWPMCollectionRolesRegistry.READING_ORDER.key)
        eq_(len(manifest.sub_collections[0].links), 2)
        eq_(manifest.sub_collections[0].links[0].href, 'https://example.com/c001.html')
        eq_(manifest.sub_collections[0].links[0].type, RWPMMediaTypesRegistry.HTML.key)
        eq_(manifest.sub_collections[0].links[0].title, 'Chapter 1')

        eq_(manifest.sub_collections[0].links[1].href, 'https://example.com/c002.html')
        eq_(manifest.sub_collections[0].links[1].type, RWPMMediaTypesRegistry.HTML.key)
        eq_(manifest.sub_collections[0].links[1].title, 'Chapter 2')

        eq_(manifest.sub_collections[1].role.key, RWPMCollectionRolesRegistry.RESOURCES.key)
        eq_(len(manifest.sub_collections[1].links), 5)
        eq_(manifest.sub_collections[1].links[0].rel, RWPMLinkRelationsRegistry.COVER.key)
        eq_(manifest.sub_collections[1].links[0].href, 'https://example.com/cover.jpg')
        eq_(manifest.sub_collections[1].links[0].type, RWPMMediaTypesRegistry.JPEG.key)
        eq_(manifest.sub_collections[1].links[0].height, 600)
        eq_(manifest.sub_collections[1].links[0].width, 400)

        eq_(manifest.sub_collections[1].links[1].href, 'https://example.com/style.css')
        eq_(manifest.sub_collections[1].links[1].type, RWPMMediaTypesRegistry.CSS.key)

        eq_(manifest.sub_collections[1].links[2].href, 'https://example.com/whale.jpg')
        eq_(manifest.sub_collections[1].links[2].type, RWPMMediaTypesRegistry.JPEG.key)

        eq_(manifest.sub_collections[1].links[3].href, 'https://example.com/boat.svg')
        eq_(manifest.sub_collections[1].links[3].type, RWPMMediaTypesRegistry.SVG_XML.key)

        eq_(manifest.sub_collections[1].links[4].href, 'https://example.com/notes.html')
        eq_(manifest.sub_collections[1].links[4].type, RWPMMediaTypesRegistry.HTML.key)
