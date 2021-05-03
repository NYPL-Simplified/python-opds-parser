from webpub_manifest_parser.core.ast import (
    ArrayOfCollectionsProperty,
    ArrayOfLinksProperty,
    Collection,
    Node,
)
from webpub_manifest_parser.core.parsers import TypeParser
from webpub_manifest_parser.core.properties import (
    ArrayOfStringsProperty,
    ArrayProperty,
    BooleanProperty,
    DateOrTimeProperty,
    NumberProperty,
    TypeProperty,
    URIProperty,
)
from webpub_manifest_parser.opds2.ast import (
    OPDS2Feed,
    OPDS2Group,
    OPDS2Price,
    OPDS2Publication,
)
from webpub_manifest_parser.opds2.registry import OPDS2CollectionRolesRegistry


class ODLLicenseTerms(Node):
    """ODL license terms & conditions."""

    checkouts = NumberProperty("checkouts", required=False)
    expires = DateOrTimeProperty("expires", required=False)
    concurrency = NumberProperty("concurrency", required=False)
    length = NumberProperty("length", required=False)


class ODLLicenseProtection(Node):
    """ODL license protection information."""

    formats = ArrayOfStringsProperty("format", required=False)
    devices = NumberProperty("devices", required=False)
    copy_allowed = BooleanProperty("copy", required=False)
    print_allowed = BooleanProperty("print", required=False)
    tts_allowed = BooleanProperty("tts", required=False)


class ODLLicenseMetadata(Node):
    """ODL license metadata."""

    identifier = URIProperty("identifier", required=True)
    formats = ArrayOfStringsProperty("format", required=True)
    created = DateOrTimeProperty("created", required=True)
    terms = TypeProperty(
        "terms",
        required=False,
        nested_type=ODLLicenseTerms,
    )
    protection = TypeProperty(
        "protection",
        required=False,
        nested_type=ODLLicenseProtection,
    )
    price = TypeProperty(
        "price",
        required=False,
        nested_type=OPDS2Price,
    )
    source = URIProperty("source", required=False)


class ODLLicense(Collection):
    """ODL license subcollection."""

    metadata = TypeProperty("metadata", required=True, nested_type=ODLLicenseMetadata)


class ODLPublication(OPDS2Publication):
    """ODL publication."""

    links = ArrayOfLinksProperty(key="links", required=False)

    licenses = ArrayProperty(
        "licenses",
        required=False,
        item_parser=TypeParser(ODLLicense),
    )


class ODLGroup(OPDS2Group):
    """ODL group."""

    publications = ArrayOfCollectionsProperty(
        "publications",
        required=False,
        role=OPDS2CollectionRolesRegistry.PUBLICATIONS,
        collection_type=ODLPublication,
    )


class ODLFeed(OPDS2Feed):
    """ODL feed."""

    publications = ArrayOfCollectionsProperty(
        "publications",
        required=False,
        role=OPDS2CollectionRolesRegistry.PUBLICATIONS,
        collection_type=ODLPublication,
    )
    groups = ArrayOfCollectionsProperty(
        "groups",
        required=False,
        role=OPDS2CollectionRolesRegistry.GROUPS,
        collection_type=ODLGroup,
    )
