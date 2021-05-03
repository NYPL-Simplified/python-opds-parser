import logging
from unittest import TestCase, skip

from parameterized import parameterized
from requests.auth import HTTPBasicAuth

from webpub_manifest_parser.odl.ast import ODLFeed
from webpub_manifest_parser.odl.parsers import ODLDocumentParserFactory


@skip("The test requires credentials to pull the feed")
class ODLIntegrationTest(TestCase):
    @parameterized.expand(
        [
            (
                "New Market OPDS 2.0 + ODL feed",
                "https://market.feedbooks.com/api/libraries/harvest.json",
                "utf-8",
                HTTPBasicAuth("*****", "*****"),
            )
        ]
    )
    def test_parse_url(self, _, url, encoding="utf-8", auth=None):
        # Arrange
        parser_factory = ODLDocumentParserFactory()
        parser = parser_factory.create()

        # Act
        try:
            feed = parser.parse_url(url, encoding, auth)
        except Exception:
            logging.exception(
                "An unexpected error occurred during parsing {0}".format(url)
            )
            raise

        # Assert
        self.assertIsInstance(feed, ODLFeed)
