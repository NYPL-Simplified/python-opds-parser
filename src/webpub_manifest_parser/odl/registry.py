from webpub_manifest_parser.core.registry import MediaType
from webpub_manifest_parser.opds2.registry import OPDS2MediaTypesRegistry


class ODLMediaTypesRegistry(OPDS2MediaTypesRegistry):
    """Registry containing ODL 2.0 media types."""

    ODL_LICENSE_INFO_DOCUMENT = MediaType(key="application/vnd.odl.info+json")
    ODL_LICENSE_STATUS_DOCUMENT = MediaType(
        key="application/vnd.readium.license.status.v1.0+json"
    )
