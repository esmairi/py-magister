from typing import Dict, Optional, List, Any, Union

from django.db.models import QuerySet, Subquery

from py_magister.core.schema_access import SchemaResource
from py_magister.core.utils import (
    is_recursive_relation,
    get_tree_relations_for_perm,
    filter_relation_tuple,
    _process_direct_relation,
)
from py_magister.models import RelationTupleField


def has_direct_linked_subject_permission(
    schema: Dict[str, SchemaResource],
    namespace: str,
    object_id: str,
    userset_namespace: str,
    permission: str,
    subject_id: str,
) -> bool:
    """
    Checks if a subject has permission through linked subjects.

    Example:
        AccessSubject + LinkedSubject: read group#member

    :param schema: The schema dictionary containing resource definitions.
    :param namespace: The resource namespace to check.
    :param object_id: The ID of the object being accessed.
    :param userset_namespace: The userset namespace defining the subject group.
    :param permission: The permission to check.
    :param subject_id: The subject ID whose permission needs verification.
    :return: True if the subject has the permission, otherwise False.
    """
    rels = get_tree_relations_for_perm(schema, namespace, userset_namespace, permission)
    return any(
        [
            check_permission(schema, userset_namespace, subject_id, tree_rel, object_id)
            for tree_rel in rels
        ]
    )


def check_permission(
    schema: Dict[str, SchemaResource],
    target_namespace: str,
    subject_id: str,
    relationship_paths: List[Any],
    object_constraint: Optional[Union[str, Subquery, QuerySet, list]] = None,
) -> bool:
    """
    Determines whether a subject (e.g., user) has permission in a specific namespace
    (e.g., target_namespace)
    by evaluating a list of relationship paths. Each path is composed of steps that
    either handle direct or recursive relationships.

    Args:
        schema (Dict[str, SchemaResource]): The schema definition mapping namespaces
        to their resources.
        target_namespace (str): The namespace (e.g., "user") we ultimately want
        to check.
        subject_id (str): The ID of the subject for which we're evaluating permission.
        relationship_paths (List[Any]): A collection of possible
        paths (lists of tuples). Each tuple is (current_namespace, current_relation,
        next_namespace, next_relation?), describing how to expand relationships or
        permissions at each step.
        object_constraint (Optional[Union[str, Subquery, QuerySet, list]]): An optional
        filter (object IDs or queryset) that constrains the current query.
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
    ) -> Any:
        """
        Handles the logic for a single recursive relationship rel_tuple:
          1) Resolve IDs from the existing subquery (if any),
          2) Union them with newly resolved IDs,
          3) If it's the last rel_tuple and the target_namespace is reachable, apply
          a final filter.
        """
        current_ns, current_rel, next_ns, next_rel = rel_tuple

        # If no existing sub-query, resolve fresh from subject_id
        if not current_subquery:
            updated_queryset = resolve_recursive_rel(
                current_ns, current_rel, subject_id
            )
        else:
            if new_queryset := resolve_recursive_rel(
                current_ns, current_rel, next_rel, current_subquery
            ):
                updated_queryset = new_queryset
            else:
                updated_queryset = current_subquery

        # Check if this rel_tuple is the last in the rel_path AND target_namespace is
        # reachable
        is_last_step = (rel_tuple == rel_path[-1]) and (
            target_namespace
            in [ns.namespace for ns in schema[current_ns].relations[current_rel]]
        )
        if is_last_step:
            updated_queryset = filter_relation_tuple(
                current_ns,
                current_rel,
                target_namespace,
                subject_filter=subject_id,
                object_filter=updated_queryset,
            )

        return updated_queryset

    def _has_results(obj: Any) -> bool:
        """Check if 'obj' is non-empty (QuerySet with results or non-empty list/set)"""
        if isinstance(obj, QuerySet):
            return obj.exists()
        return False

    # --- MAIN LOOP ---
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
                current_queryset = _process_direct_relation(
                    step, new_object_constraint, subject_id, target_namespace
                )
            if isinstance(current_queryset, QuerySet):
                current_queryset = current_queryset.values_list(
                    RelationTupleField.USERSET_SUBJECT_ID, flat=True
                )

        if _has_results(current_queryset):
            return True

    return False


def resolve_recursive_rel(
    ns: str, rel, usr_rel: str, object_filter: Optional[str | QuerySet] = None
) -> QuerySet:
    """
    Recursively resolves all subject IDs linked by a self-referential (recursive)
    relationship.

    This function starts from an initial set of object IDs (either a single ID,
    a QuerySet, or None) and explores all reachable IDs by repeatedly calling
    `filter_relation_tuple`. Each newly found ID triggers another recursive search
    until no additional IDs are discovered. Finally, it returns a union of all
    collected IDs and those found directly from the initial filter.

    Args:
        ns (str): The namespace in which the relationship is defined.
        rel (str): The relation name used to link subjects within the same namespace.
        usr_rel (str): An optional user or relation name indicating how the recursion
        links to further subjects.
        object_filter (Optional[Union[str, QuerySet]]): An initial filter that can be
         a single ID, a QuerySet of IDs, or None.

    Returns:
        QuerySet: A QuerySet of all subject IDs discovered through this recursive search
    """
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
