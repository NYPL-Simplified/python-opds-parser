from abc import ABCMeta, abstractmethod

from python_rwpm_parser.parser.semantic import RWPMSemanticAnalyzer
from python_rwpm_parser.parser.syntax import RWPMSyntaxAnalyzer
from python_rwpm_parser.registry import RWPMMediaTypesRegistry, RWPMLinkRelationsRegistry, RWPMCollectionRolesRegistry


class Parser(object):
    def __init__(self, syntax_analyzer, semantic_analyzer):
        """Initializes a new instance of Parser class

        :param syntax_analyzer: Syntax analyzer
        :type syntax_analyzer: syntax.SyntaxAnalyzer

        :param semantic_analyzer: Semantic analyser
        :type semantic_analyzer: semantic.SemanticAnalyzer
        """
        self._syntax_analyzer = syntax_analyzer
        self._semantic_analyzer = semantic_analyzer

    def parse(self, input_file_path):
        """Parses the input file and returns a validated AST object

        :param input_file_path: Full path to the file containing RWPM-compatible document
        :type input_file_path: basestring

        :return: Validated manifest-like object
        :rtype: python_rwpm_parser.ast.Manifestlike
        """
        manifest = self._syntax_analyzer.analyze(input_file_path)
        manifest.accept(self._semantic_analyzer)

        return manifest


class ParserFactory(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def create(self):
        raise NotImplementedError()


class RWPMParserFactory(ParserFactory):
    def create(self):
        media_types_registry = RWPMMediaTypesRegistry()
        link_relations_registry = RWPMLinkRelationsRegistry()
        collection_roles_registry = RWPMCollectionRolesRegistry()
        syntax_analyzer = RWPMSyntaxAnalyzer(collection_roles_registry)
        semantic_analyzer = RWPMSemanticAnalyzer(
            media_types_registry, link_relations_registry, collection_roles_registry)
        parser = Parser(syntax_analyzer, semantic_analyzer)

        return parser
