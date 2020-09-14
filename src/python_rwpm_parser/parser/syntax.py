import json
import logging
from abc import ABCMeta, abstractmethod

from python_rwpm_parser.ast import Collection, Link, Metadata, RWPMManifest
from python_rwpm_parser.errors import BaseError
from python_rwpm_parser.metadata import ObjectMetadata


class ParsingError(BaseError):
    """Raised in the case of parsing errors"""


class MissingPropertyError(ParsingError):
    """Raised in the case of a missing required property"""

    def __init__(self, cls, object_property, inner_exception=None):
        """Initializes a new instance of MissingPropertyError class

        :param cls: Object's class where the missing property is defined
        :type cls: Type

        :param object_property: Missing property
        :type object_property: python_rwpm_parser.metadata.ObjectProperty

        :param inner_exception: (Optional) inner exception
        :type inner_exception: Optional[Exception]
        """
        super(MissingPropertyError, self).__init__(
            '{0}\'s required property {1} is missing'.format(cls, object_property.key),
            inner_exception
        )

        self._cls = cls
        self._object_property = object_property

    @property
    def cls(self):
        """Returns the object's class where the missing property is defined

        :return: Object's class where the missing property is defined
        :rtype: Type
        """
        return self._cls

    @property
    def object_property(self):
        """Returns the missing property

        :return: Missing property
        :rtype: python_rwpm_parser.metadata.ObjectProperty
        """
        return self._object_property


class MissingSubCollectionError(ParsingError):
    """Raised in the case of a missing required sub-collection"""

    def __init__(self, sub_collection_role, inner_exception=None):
        """Initializes a new instance of MissingSubCollectionError class

        :param sub_collection_role: Missing sub-collection's role
        :type sub_collection_role: python_rwpm_parser.registry.CollectionRole

        :param inner_exception: (Optional) inner exception
        :type inner_exception: Optional[Exception]
        """
        super(MissingSubCollectionError, self).__init__(
            'Required sub-collection {0} is missing'.format(sub_collection_role.key),
            inner_exception
        )

        self._sub_collection_role = sub_collection_role

    @property
    def sub_collection_role(self):
        """Returns the role of the missing sub-collection

        :return: Role of the missing sub-collection
        :rtype: python_rwpm_parser.registry.CollectionRole
        """
        return self._sub_collection_role


class UnknownCollectionRolesError(ParsingError):
    """Raised when non-registered collections roles are found in the document"""

    def __init__(self, unknown_sub_collection_keys, inner_exception=None):
        """Initializes a new instance of UnknownCollectionRolesError class

        :param unknown_sub_collection_keys: List of sub-collection keys
            which are present in the document but not registered
        :type unknown_sub_collection_keys: List[basestring]

        :param inner_exception: (Optional) inner exception
        :type inner_exception: Optional[Exception]
        """
        unknown_sub_collection_keys = list(unknown_sub_collection_keys)

        super(UnknownCollectionRolesError, self).__init__(
            'The following sub-collection keys are not registered: {0}'.format(unknown_sub_collection_keys),
            inner_exception
        )

        self._not_registered_sub_collection_keys = list(unknown_sub_collection_keys)

    @property
    def unknown_sub_collection_keys(self):
        """Returns the list of sub-collection keys which are present in the document but not registered

        :return: List of sub-collection keys which are present in the document but not registered
        :rtype: List[basestring]
        """
        return self._not_registered_sub_collection_keys


class WrongFormatError(ParsingError):
    """Raised in the case of wrong format"""


MISSING_CONTEXT_ERROR = WrongFormatError('Manifest does not contain context')
MISSING_METADATA_ERROR = WrongFormatError('Manifest does not contain metadata')
MISSING_LINKS_ERROR = WrongFormatError('Collection does not contain links')
INCORRECT_LINKS_FORMAT_ERROR = WrongFormatError('Links list has an incorrect format')


class SyntaxAnalyzer(object):
    """Base class for syntax analyzers checking the base grammar rules of RWPM and parsing raw JSON into AST"""

    __metaclass__ = ABCMeta

    CONTEXT = '@context'
    METADATA = 'metadata'
    LINKS = 'links'

    def __init__(self, collection_roles_registry):
        """Initializes a new instance of SyntaxParser class

        :param collection_roles_registry: Collection roles registry
        :type collection_roles_registry: python_rwpm_parser.registry.Registry
        """
        self._collection_roles_registry = collection_roles_registry
        self._logger = logging.getLogger(__name__)

    @abstractmethod
    def _create_manifest(self):
        """Creates a new manifest. The method Should be overridden in child classes

        :return: Manifest-like object
        :rtype: Manifestlike
        """
        raise NotImplementedError()

    def _parse_context(self, json_content):
        """Parses manifest's context into string

        :param json_content: Dictionary containing manifest's JSON
        :type json_content: Dict

        :return: Manifest's context
        :rtype: basestring
        """
        self._logger.debug('Started parsing manifest\'s context')

        if self.CONTEXT not in json_content:
            raise MISSING_CONTEXT_ERROR

        context = json_content[self.CONTEXT]

        self._logger.debug('Finished parsing manifest\'s context: {0}'.format(context))

        return context

    def _parse_metadata(self, json_content):
        """Parses collection's metadata into Python dictionary

        :param json_content: Dictionary containing collection's JSON
        :type json_content: Dict

        :return: Collection's metadata
        :rtype: Dict
        """
        self._logger.debug('Started parsing collection\'s metadata')

        if self.METADATA not in json_content:
            raise MISSING_METADATA_ERROR

        metadata = Metadata(json_content[self.METADATA])

        self._logger.debug('Finished parsing collection\'s metadata: {0}'.format(metadata))

        return metadata

    def _parse_object(self, json_content, cls):
        """Parses RWPM's object JSON into a corresponding AST object

        :param json_content: Dictionary containing object's JSON
        :type json_content: Dict

        :param cls: Object's class
        :type cls: Type

        :return: Node object
        :rtype: Node
        """
        self._logger.debug('Started parsing {0} object'.format(cls))

        ast_object = cls()
        ast_object_properties = ObjectMetadata.get_class_properties(cls)

        for object_property in ast_object_properties:
            property_value = json_content.get(object_property.key, None)

            self._logger.debug('Property {0} has the following value: {1}'.format(object_property.key, property_value))

            if property_value is None and object_property.default_value is not None:
                property_value = object_property.default_value

            if object_property.required and property_value is None:
                raise MissingPropertyError(cls, object_property)

            setattr(ast_object, object_property.key, property_value)

        self._logger.debug('Finished parsing {0} object: {1}'.format(cls, ast_object))

        return ast_object

    def _parse_links(self, json_content):
        """Parses links' JSON into a list of Link objects

        :param json_content: Dictionary containing collection's JSON
        :type json_content: Dict

        :return: List of Link objects
        :rtype: List[Link]
        """
        self._logger.debug('Started parsing links')

        if isinstance(json_content, dict):
            if self.LINKS not in json_content:
                raise MISSING_LINKS_ERROR

            links = json_content[self.LINKS]
        elif isinstance(json_content, list):
            links = json_content
        else:
            raise INCORRECT_LINKS_FORMAT_ERROR

        link_objects = []

        for link in links:
            self._logger.debug('Started parsing link {0}'.format(link))

            link_object = self._parse_object(link, Link)
            link_objects.append(link_object)

            self._logger.debug('Finished parsing link {0}: {1}'.format(link, link_object))

        self._logger.debug('Finished parsing links: {0}'.format(link_objects))

        return link_objects

    def _parse_collection(self, json_content, collection=None, role=None):
        """Parses collection's JSON into a Collection object

        :param json_content: Dictionary containing collection's JSON
        :type json_content: Dict

        :param collection: Optional object containing collection object. If missing, a new Collection will be created
        :type collection: Optional[Collection]

        :param role: Optional CollectionRole object (empty when the method is called for a manifest)
        :type role: CollectionRole

        :return: Collection object
        :rtype: CompactCollection
        """
        self._logger.debug('Started parsing collection {0} with role {1}'.format(collection, role))

        if collection is None:
            collection = Collection(role)

        if not role or not role.compact:
            links = self._parse_links(json_content)
            collection.links.extend(links)

            metadata = self._parse_metadata(json_content)
            collection.metadata = metadata

            sub_collection_keys = set(json_content.keys()) - {'@context', 'metadata', 'links'}

            self._logger.debug('There are following potential sub-collections: {0}'.format(sub_collection_keys))

            for collection_role in self._collection_roles_registry:
                if collection_role.key in sub_collection_keys:
                    sub_collection = self._parse_collection(
                        json_content[collection_role.key], collection=None, role=collection_role)

                    collection.sub_collections.append(sub_collection)

                    sub_collection_keys.remove(collection_role.key)
                elif collection_role.required:
                    raise MissingSubCollectionError(collection_role)

            if sub_collection_keys:
                raise UnknownCollectionRolesError(sub_collection_keys)
        else:
            links = self._parse_links(json_content)
            collection.links.extend(links)

        self._logger.debug('Finished parsing collection {0} with role {1}'.format(collection, role))

        return collection

    def _parse_manifest(self, json_content):
        """Parses manifest's JSON into manifest-like object

        :param json_content: Dictionary containing manifest's JSON
        :type json_content: Dict
        """
        self._logger.debug('Started parsing manifest')

        manifest = self._create_manifest()

        context = self._parse_context(json_content)
        manifest.context = context

        self._parse_collection(json_content, manifest)

        self._logger.debug('Finished parsing manifest')

        return manifest

    def analyze(self, input_file_path):
        """
        Parses JSON file into RWPM AST

        :param input_file_path: Full path to the file containing RWPM JSON

        :return: RWPM AST
        :rtype: ManifestLike
        """
        self._logger.debug('Started parsing input file {0}'.format(input_file_path))

        with open(input_file_path, 'r') as input_file:
            input_file_content = input_file.read()
            manifest_json = json.loads(input_file_content)
            manifest = self._parse_manifest(manifest_json)

            self._logger.debug('Finished parsing input file {0}: {1}'.format(input_file_path, manifest))

            return manifest


class RWPMSyntaxAnalyzer(SyntaxAnalyzer):
    """Syntax analyzer for RWPM grammar"""

    def _create_manifest(self):
        """Creates a new RWPM manifest

        :return: RWPM manifest
        :rtype: RWPMManifest
        """
        return RWPMManifest()
