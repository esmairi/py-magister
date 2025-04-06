from typing import Dict, Optional, List

from django.db.models import QuerySet

from py_magister.core.lookup_subjects.lookup_subjects_inherit_rel import (
    fetch_subjects_inherited_rel_queryset,
)
from py_magister.core.lookup_subjects.lookup_subjects_direct_rel import (
    fetch_subjects_direct_rel_queryset,
)
from py_magister.core.models import LookupSubjectsRequest
from py_magister.core.schema_access import SchemaResource
from py_magister.core.utils import union_querysets
from py_magister.models import RelationTupleField


def fetch_subjects_query(
    schema: Dict[str, SchemaResource], lookup_request: LookupSubjectsRequest
) -> Optional[QuerySet]:
    """
    Constructs a queryset to retrieve subjects with direct, linked, or inherited
    permissions.

    This function aggregates different permission sources (direct, linked,
    and inherited) to form a unified queryset representing all relevant subjects.

    Args:
        schema (Dict[str, SchemaResource]): The schema defining resource relationships.
        lookup_request (LookupSubjectsRequest): The request containing namespace,
        permission, userset namespace, and target object details.

    Returns:
        QuerySet or None: A combined queryset of subjects with permissions,
         or None if no matches are found.
    """
    queries = [
        query
        for query in (
            fetch_subjects_direct_rel_queryset(schema, lookup_request),
            fetch_subjects_inherited_rel_queryset(schema, lookup_request),
        )
        if query
    ]
    return union_querysets(queries) if queries else None


def fetch_subjects(
    schema: Dict[str, SchemaResource], lookup_request: LookupSubjectsRequest
) -> Optional[QuerySet[List[str]]]:
    """
    Retrieves a queryset of lists of subject IDs based on the given schema and lookup
    request.

    This function executes a query to find the subjects corresponding to the provided
     schema and lookup request and returns a queryset of lists containing subject IDs,
     or an empty queryset if no subjects are found.

    Args:
        schema (Dict[str, SchemaResource]): The schema defining resource relationships.
        lookup_request (LookupSubjectsRequest): The request containing namespace,
        permission, userset namespace, and target object details.

    Returns:
        QuerySet[List[str]]: A queryset of lists of  subject IDs, or an empty queryset
        if no subjects are found.
    """
    queryset = fetch_subjects_query(schema, lookup_request)
    return (
        queryset.values_list(RelationTupleField.USERSET_SUBJECT_ID, flat=True)
        if queryset
        else None
    )
