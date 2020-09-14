import inspect
from abc import ABCMeta, abstractmethod
from enum import Enum


class ObjectType(Enum):
    URI = 'URI'
    BOOLEAN = 'BOOLEAN'
    MIME = 'MIME'
    STRING = 'STRING'


class HasProperties(object):
    """Interface representing class containing ObjectProperty meta-properties"""

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_setting_value(self, setting_name, default_value=None):
        """Returns a settings'value

        :param setting_name: Name of the setting
        :type setting_name: string

        :param default_value: Default value
        :type default_value: Any

        :return: Setting's value
        :rtype: Any
        """
        raise NotImplementedError()

    @abstractmethod
    def set_setting_value(self, setting_name, setting_value):
        """Sets setting's value

        :param setting_name: Name of the setting
        :type setting_name: string

        :param setting_value: New value of the setting
        :type setting_value: Any
        """
        raise NotImplementedError()


class ObjectProperty(object):
    """Class representing object property, storing property's metadata and its value"""

    def __init__(self, key, _format, required, default_value=None):
        self._key = key
        self._format = _format
        self._required = required
        self._default_value = default_value

    def __get__(self, owner_instance, owner_type):
        """Returns a value of the setting

        :param owner_instance: Instance of the owner, class having instance of ObjectProperty as an attribute
        :type owner_instance: Optional[HasProperties]

        :param owner_type: Owner's class
        :type owner_type: Optional[Type]

        :return: ObjectProperty instance (when called via a static method) or
            the setting's value (when called via an instance method)
        :rtype: Union[ObjectProperty, Any]
        """
        # If owner_instance is empty, it means that this method was called via a static method
        # In this case we need to return the metadata instance itself
        if owner_instance is None:
            return self

        if not isinstance(owner_instance, HasProperties):
            raise Exception('owner must be an instance of HasProperties type')

        return owner_instance.get_setting_value(self._key, self._default_value)

    def __set__(self, owner_instance, value):
        """Updates the setting's value

        :param owner_instance: Instance of the owner, class having instance of ObjectProperty as an attribute
        :type owner_instance: Optional[HasProperties]

        :param value: New setting's value
        :type value: Any
        """
        if not isinstance(owner_instance, HasProperties):
            raise Exception('owner must be an instance HasProperties type')

        return owner_instance.set_setting_value(self._key, value)

    @property
    def key(self):
        return self._key

    @property
    def format(self):
        return self._format

    @property
    def required(self):
        return self._required

    @property
    def default_value(self):
        return self._default_value


class ObjectMetadata(HasProperties):
    def __init__(self):
        self._values = {}

    def get_setting_value(self, setting_name, default_value=None):
        return self._values.get(setting_name, default_value)

    def set_setting_value(self, setting_name, setting_value):
        self._values[setting_name] = setting_value

    @classmethod
    def get_properties(cls):
        ObjectMetadata.get_class_properties(cls)

    @staticmethod
    def get_class_properties(cls):
        """Returns a list of 2-tuples containing information ConfigurationMetadata properties in the specified class

        :param cls: Class
        :type cls: type

        :return: List of 2-tuples containing information ConfigurationMetadata properties in the specified class
        :rtype: List[Tuple[string, ConfigurationMetadata]]
        """
        members = inspect.getmembers(cls)
        object_properties = []

        for _, member in members:
            if isinstance(member, ObjectProperty):
                object_properties.append(member)

        return object_properties
