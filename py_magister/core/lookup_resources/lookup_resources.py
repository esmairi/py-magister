from typing import Dict, Optional, List

from django.db.models import QuerySet

from py_magister.core.lookup_resources.lookup_resources_direct_rel import (
    fetch_resources_direct_rel,
)
from py_magister.core.lookup_resources.lookup_resources_inherit_rel import (
    fetch_resources_inherit_rel,
)
from py_magister.core.models import LookupResourcesRequest
from py_magister.core.schema_access import SchemaResource
from py_magister.core.utils import union_querysets
from py_magister.models import RelationTupleField


def fetch_resources_query(
    schema: Dict[str, SchemaResource],
    lookup_request: LookupResourcesRequest,
) -> Optional[QuerySet]:
    """
    Retrieves a combined queryset of resources that match direct or inherited
    relationships based on the provided lookup request.

    This function delegates resource fetching to separate mechanisms for direct and
    inherited relationships, then unions all resulting querysets into one, if any.
    If no resources match, it returns None.

    Args:
        schema (Dict[str, SchemaResource]): The schema defining resource relationships.
        lookup_request (LookupResourcesRequest): The request containing namespace,
        permission, userset namespace, and the subject (user or group) for which
        resources are being fetched.

    Returns:
        Optional[QuerySet]: A unified queryset of matching resources if any exist,
        otherwise None.
    """
    queries = [
        query
        for query in (
            fetch_resources_direct_rel(
                schema,
                lookup_request.namespace,
                lookup_request.permission,
                lookup_request.userset_namespace,
                lookup_request.subject,
            ),
            fetch_resources_inherit_rel(
                schema,
                lookup_request.namespace,
                lookup_request.permission,
                lookup_request.userset_namespace,
                lookup_request.subject,
            ),
        )
        if query
    ]
    return union_querysets(queries) if queries else None


def fetch_resources(
    schema: Dict[str, SchemaResource], lookup_request: LookupResourcesRequest
) -> Optional[QuerySet[List[str]]]:
    """
    Retrieves a flattened list of resource IDs for the given lookup request.

    This function delegates the query building to `fetch_resources_query`, and if any
    resources match the direct or inherited relationships, it returns a queryset
    of resource IDs. If no matching query is found, it returns None.

    Args:
        schema (Dict[str, SchemaResource]): The schema defining resource relationships.
        lookup_request (LookupResourcesRequest): The request specifying which namespace,
            permission, userset namespace, and subject to query.

    Returns:
        Optional[QuerySet[List[str]]]: A queryset of resource IDs, or None if no
        resources match.
    """
    queryset = fetch_resources_query(schema, lookup_request)
    return (
        queryset.values_list(RelationTupleField.OBJECT_ID, flat=True)
        if queryset
        else None
    )
