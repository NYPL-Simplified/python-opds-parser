from abc import ABCMeta, abstractmethod

import six

from webpub_manifest_parser.parser.semantic import RWPMSemanticAnalyzer
from webpub_manifest_parser.parser.syntax import RWPMSyntaxAnalyzer
from webpub_manifest_parser.registry import (
    RWPMCollectionRolesRegistry,
    RWPMLinkRelationsRegistry,
    RWPMMediaTypesRegistry,
)


class Parser(object):
    """Base class for RWPM-compatible parsers."""

    def __init__(self, syntax_analyzer, semantic_analyzer):
        """Initialize a new instance of Parser class.

        :param syntax_analyzer: Syntax analyzer
        :type syntax_analyzer: syntax.SyntaxAnalyzer

        :param semantic_analyzer: Semantic analyser
        :type semantic_analyzer: semantic.SemanticAnalyzer
        """
        self._syntax_analyzer = syntax_analyzer
        self._semantic_analyzer = semantic_analyzer

    def parse(self, input_file_path):
        """Parse the input file and return a validated AST object.

        :param input_file_path: Full path to the file containing RWPM-compatible document
        :type input_file_path: basestring

        :return: Validated manifest-like object
        :rtype: python_rwpm_parser.ast.Manifestlike
        """
        manifest = self._syntax_analyzer.analyze(input_file_path)
        manifest.accept(self._semantic_analyzer)

        return manifest


@six.add_metaclass(ABCMeta)
class ParserFactory(object):
    """Base class for factories creating parsers for particular RWPM-compatible standards (for example, OPDS 2.0)."""

    @abstractmethod
    def create(self):
        """Create a new Parser instance.

        :return: Parser instance
        :rtype: Parser
        """
        raise NotImplementedError()


class RWPMParserFactory(ParserFactory):
    """Factory creating RWPM parsers."""

    def create(self):
        """Create a new RWPMParser.

        :return: RWPM parser instance
        :rtype: Parser
        """
        media_types_registry = RWPMMediaTypesRegistry()
        link_relations_registry = RWPMLinkRelationsRegistry()
        collection_roles_registry = RWPMCollectionRolesRegistry()
        syntax_analyzer = RWPMSyntaxAnalyzer(collection_roles_registry)
        semantic_analyzer = RWPMSemanticAnalyzer(
            media_types_registry, link_relations_registry, collection_roles_registry
        )
        parser = Parser(syntax_analyzer, semantic_analyzer)

        return parser
