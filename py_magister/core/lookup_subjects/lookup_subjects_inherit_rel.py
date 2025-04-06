from typing import Dict, Optional

from django.db.models import QuerySet, Subquery

from py_magister.core.models import LookupSubjectsRequest
from py_magister.core.schema_access import SchemaResource, NamespaceRelation
from py_magister.core.utils import (
    get_relations_config,
    union_querysets,
    filter_relation_subject,
    filter_relation_tuple,
)
from py_magister.models import RelationTupleField


def fetch_subjects_inherited_rel_queryset(
    schema: Dict[str, SchemaResource], request: LookupSubjectsRequest
) -> Optional[QuerySet]:
    """
    Retrieves a queryset of inherited subject permissions based on the provided
    schema and lookup request.

    Args:
        schema (Dict[str, SchemaResource]): The schema defining resource relationships.
        request (LookupSubjectsRequest): The request containing namespace, permission,
        userset namespace, and target object details.

    Returns:
        Optional[QuerySet]: A queryset of inherited subject permissions,
        or None if no subjects are found.
    """
    relations = get_relations_config(
        schema, request.namespace, request.permission, is_inherited=True
    )

    queries = [
        fetch_subjects_single_rel(schema, request, relation) for relation in relations
    ]
    valid_queries = [q for q in queries if q]
    return union_querysets(valid_queries) if valid_queries else None


def fetch_subjects_single_rel(
    schema: Dict[str, SchemaResource], request: LookupSubjectsRequest, relation: str
):
    """
    Processes a single relation and generates a query for inherited subject permissions.

    Args:
        schema: The schema defining resource relationships.
        request: The request containing namespace, permission, userset namespace,
        and target object details.
        relation: The relation string that defines how resources are related.

    Returns:
        QuerySet or None: A queryset for the relation, or None if no query is generated.
    """
    relation_name, inherited_permission = relation.split("->")

    subject_namespaces = get_subject_namespaces(schema, request, relation_name)

    queries = [
        generate_subject_permission_query(schema, request, relation_name, subject)
        for subject in subject_namespaces
    ]
    valid_queries = [q for q in queries if q]
    return union_querysets(valid_queries) if valid_queries else None


def get_subject_namespaces(
    schema: Dict[str, SchemaResource],
    request: LookupSubjectsRequest,
    relation_name: str,
):
    """
    Retrieves a list of subject namespaces (direct and linked) based on the relation.

    Args:
        schema: The schema defining resource relationships.
        request: The request containing namespace, permission, userset namespace,
        and target object details.
        relation_name: The name of the relation to process.

    Returns:
        List: A list of subject namespaces (direct and linked).
    """
    direct_subject_namespaces = filter_relation_subject(
        schema, request.namespace, relation_name
    )

    linked_subject_namespaces = (
        filter_relation_subject(schema, request.namespace, relation_name, True) or []
    )

    return direct_subject_namespaces + tuple(
        NamespaceRelation(namespace=ns.namespace.split("#")[0])
        for ns in linked_subject_namespaces
    )


def generate_subject_permission_query(
    schema: Dict[str, SchemaResource],
    request: LookupSubjectsRequest,
    relation: str,
    subject: NamespaceRelation,
):
    """
    Generates a query for inherited subject permissions based on the subject namespace.

    Args:
        schema: The schema defining resource relationships.
        request: The request containing namespace, permission, userset namespace, and
         target object details.
        relation: The relation string that defines how resources are related.
        subject: The subject namespace to process.

    Returns:
        QuerySet or None: The generated query, or None if no query is generated.
    """
    from py_magister.core.lookup_subjects import fetch_subjects

    related_resources_query = filter_relation_tuple(
        request.namespace,
        relation,
        subject.namespace,
        object_filter=request.target_object,
    )

    if related_resources_query.exists():
        sub_request = LookupSubjectsRequest(
            namespace=subject.namespace,
            permission=request.permission,
            userset_namespace=request.userset_namespace,
            target_object=Subquery(
                related_resources_query.values_list(
                    RelationTupleField.USERSET_SUBJECT_ID, flat=True
                )
            ),
        )
        return fetch_subjects(schema, sub_request)

    return None
