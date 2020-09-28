import inspect
from abc import ABCMeta, abstractmethod

import six


@six.add_metaclass(ABCMeta)
class HasProperties(object):
    """Interface representing class containing ObjectProperty meta-properties."""

    @abstractmethod
    def get_setting_value(self, setting_name, default_value=None):
        """Return the setting's value.

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
        """Set the setting's value.

        :param setting_name: Name of the setting
        :type setting_name: string

        :param setting_value: New value of the setting
        :type setting_value: Any
        """
        raise NotImplementedError()


class ObjectProperty(object):
    """Class representing object property, storing property's metadata and its value."""

    def __init__(self, key, _format, required, default_value=None):
        """Initialize a new instance of ObjectProperty class.

        :param key: Property's key
        :type key: basestring

        :param _format: Property's format
        :type key: Type

        :param required: Boolean value indicating whether the property is required or not
        :type required: bool

        :param default_value: Property's default value
        :type default_value: Any
        """
        self._key = key
        self._format = _format
        self._required = required
        self._default_value = default_value

    def __get__(self, owner_instance, owner_type):
        """Return the property's value.

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
            raise Exception("owner must be an instance of HasProperties type")

        return owner_instance.get_setting_value(self._key, self._default_value)

    def __set__(self, owner_instance, value):
        """Set the property's value.

        :param owner_instance: Instance of the owner, class having instance of ObjectProperty as an attribute
        :type owner_instance: Optional[HasProperties]

        :param value: New setting's value
        :type value: Any
        """
        if not isinstance(owner_instance, HasProperties):
            raise Exception("owner must be an instance HasProperties type")

        return owner_instance.set_setting_value(self._key, value)

    @property
    def key(self):
        """Return the property's key.

        :return: Property's key
        :rtype: basestring
        """
        return self._key

    @property
    def format(self):
        """Return the property's format.

        :return: Setting's format
        :rtype: Type
        """
        return self._format

    @property
    def required(self):
        """Return a boolean value indicating whether this property is required or not.

        :return: Boolean value indicating whether this property is required or not.
        :rtype: bool
        """
        return self._required

    @property
    def default_value(self):
        """Return the property's default value.

        :return: Property's default value.
        :rtype: bool
        """
        return self._default_value


class PropertiesGrouping(HasProperties):
    """Group of properties."""

    def __init__(self):
        """Initialize a new instance of PropertiesGrouping class."""
        self._values = {}

    def get_setting_value(self, setting_name, default_value=None):
        """Return the setting's value.

        :param setting_name: Setting's name
        :type setting_name: basestring

        :param default_value: Setting's default value
        :type default_value: Any
        """
        return self._values.get(setting_name, default_value)

    def set_setting_value(self, setting_name, setting_value):
        """Set the setting's value.

        :param setting_name: Setting's name
        :type setting_name: basestring

        :param setting_value: New setting's value
        :type setting_value: Any
        """
        self._values[setting_name] = setting_value

    @staticmethod
    def get_class_properties(klass):
        """Return a list of 2-tuples containing information ConfigurationMetadata properties in the specified class.

        :param klass: Class
        :type klass: type

        :return: List of 2-tuples containing information ConfigurationMetadata properties in the specified class
        :rtype: List[Tuple[string, ConfigurationMetadata]]
        """
        members = inspect.getmembers(klass)
        object_properties = []

        for _, member in members:
            if isinstance(member, ObjectProperty):
                object_properties.append(member)

        return object_properties
