from functools import reduce
from typing import Dict, Optional, List, Any, Union

from django.db.models import QuerySet, Subquery

from py_magister.core.models import LookupSubjectsRequest
from py_magister.core.schema_access import SchemaResource
from py_magister.core.utils import (
    union_querysets,
    is_recursive_relation,
    get_tree_relations_for_perm,
    filter_relation_tuple,
    _process_direct_relation,
)
from py_magister.models import RelationTupleField


def fetch_subjects_direct_rel_queryset(
    schema: Dict[str, SchemaResource], request: LookupSubjectsRequest
) -> Optional[QuerySet]:
    """
    Constructs and returns a queryset of subjects that have direct permissions
    corresponding to the provided lookup request.

    This function retrieves all possible relationship definitions for the given
    permission and namespace. For each relationship path (tree relation), it
    fetches subjects via `fetch_subjects_single_rel`, then accumulates them into
    a combined list of querysets. It finally unions any valid querysets into one.

    Args:
        schema (Dict[str, SchemaResource]): The schema defining resource relationships.
        request (LookupSubjectsRequest): Contains the target namespace, permission,
            userset namespace, and object ID(s) for which subjects are being fetched.

    Returns:
        Optional[QuerySet]: A unified queryset of subjects that directly match the
        provided permission criteria, or None if no valid subjects are found.
    """
    rels = get_tree_relations_for_perm(
        schema, request.namespace, request.userset_namespace, request.permission
    )
    queries = [
        fetch_subjects_single_rel(
            schema, request.userset_namespace, tree_rel, request.target_object
        )
        for tree_rel in rels
    ]
    valid_queries = [q for q in queries if q]
    flatten_queries = (
        reduce(lambda x, y: x.extend(y) or x, valid_queries) if valid_queries else None
    )
    return union_querysets(flatten_queries) if flatten_queries else None


def fetch_subjects_single_rel(
    schema: Dict[str, SchemaResource],
    target_namespace: str,
    relationship_paths: List[Any],
    object_constraint: Optional[Union[str, Subquery, QuerySet, list]] = None,
) -> List[QuerySet]:
    """
    Determines whether a subject (e.g., user) has permission in a specific namespace
    (e.g., target_namespace) by evaluating a list of relationship paths.
    Each path is composed of steps that either handle direct or recursive relationships.

    Args:
        schema (Dict[str, SchemaResource]): The schema definition mapping namespaces
        to their resources.
        target_namespace (str): The namespace (e.g., "user") we ultimately want to
        check.
        relationship_paths (List[Any]): A collection of possible paths
        (lists of tuples). Each tuple is (current_namespace, current_relation,
        next_namespace, next_relation?), describing how to expand relationships or
        permissions at each step.
        object_constraint (Optional[Union[str, Subquery, QuerySet, list]]): An optional
        This may be updated/expanded at each step.

    Returns:
        bool: True if the subject has permission based on at least one of the paths,
        False otherwise.
    """

    # --- HELPER FUNCTIONS ---

    def _process_recursive_relation(
        rel_tuple: tuple,
        current_subquery: Optional[Union[str, QuerySet, list]],
        rel_path: list,
    ) -> QuerySet:
        """
        Handles the logic for a single recursive relationship rel_tuple:
          1) Resolve IDs from the existing subquery (if any),
          2) Union them with newly resolved IDs,
          3) If it's the last rel_tuple and the target_namespace is reachable,
          apply a final filter.
        """
        current_ns, current_rel, next_ns, next_rel = rel_tuple

        # If no existing sub-query, resolve fresh from subject_id
        if not current_subquery:
            updated_queryset = resolve_recursive_rel(
                current_ns, current_rel, object_constraint
            )
        else:
            if new_queryset := resolve_recursive_rel(
                current_ns, current_rel, next_rel, current_subquery
            ):
                updated_queryset = new_queryset
            else:
                updated_queryset = current_subquery

        # Check if this rel_tuple is the last in the rel_path AND target_namespace
        # is reachable
        is_last_step = (rel_tuple == rel_path[-1]) and (
            target_namespace
            in [ns.namespace for ns in schema[current_ns].relations[current_rel]]
        )
        if is_last_step:
            updated_queryset = filter_relation_tuple(
                current_ns,
                current_rel,
                target_namespace,
                object_filter=updated_queryset,
            )

        return updated_queryset

    # --- MAIN LOOP ---
    queries = []
    for path in relationship_paths:
        current_queryset = None
        for step in path:
            new_object_constraint = (
                object_constraint if current_queryset is None else current_queryset
            )
            if is_recursive_relation(step):
                # Process recursive
                current_queryset = _process_recursive_relation(
                    step, new_object_constraint, path
                )
            else:
                # Process direct
                current_queryset = _process_direct_relation(step, new_object_constraint)
            if isinstance(current_queryset, QuerySet):
                current_queryset = current_queryset.values_list(
                    RelationTupleField.USERSET_SUBJECT_ID, flat=True
                )

        if current_queryset:
            queries.append(current_queryset)

    return queries


def resolve_recursive_rel(
    ns: str, rel, usr_rel: str, object_filter: Optional[str | QuerySet] = None
) -> QuerySet:
    ids = set()
    if isinstance(object_filter, QuerySet):
        object_filter = Subquery(object_filter)

    def resolve(object_id):
        for sg in filter_relation_tuple(
            ns, rel, ns, object_filter=object_id, usr_rel=usr_rel
        ).values_list(RelationTupleField.USERSET_SUBJECT_ID, flat=True):
            if sg not in ids:
                ids.add(sg)
                resolve(sg)

    resolve(object_filter)
    return (
        filter_relation_tuple(ns, rel, ns, object_filter=ids, usr_rel=usr_rel)
        .values_list(RelationTupleField.USERSET_SUBJECT_ID, flat=True)
        .union(
            filter_relation_tuple(
                ns, rel, ns, object_filter=object_filter, usr_rel=usr_rel
            ).values_list(RelationTupleField.USERSET_SUBJECT_ID, flat=True)
        )
    )
