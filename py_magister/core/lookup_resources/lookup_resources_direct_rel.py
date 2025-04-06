from typing import Dict, Optional, List

from django.db.models import QuerySet, Subquery

from py_magister.core.schema_access import SchemaResource
from py_magister.core.utils import (
    get_relations_config,
    union_querysets,
    walk_relations,
    filter_relation_tuple,
)
from py_magister.models import RelationTupleField


def fetch_resources_direct_rel(
    schema: Dict[str, SchemaResource],
    ns: str,
    perm: str,
    uns: str,
    subj,
    object_ids=None,
) -> Optional[QuerySet]:
    """
    Retrieves relations based on the schema, namespace, permission, user identifier,
    and subject.
    Generates a list of queries to get relations from the schema.

    Args:
        schema (Dict[str, SchemaResource]): The schema of resources with defined
        relations.
        ns (str): The namespace for the resources.
        perm (str): The type of permission used to retrieve the relations.
        uns (str): The user or identifier for filtering the relations.
        subj: The subject for which the relations need to be retrieved.
        object_ids (optional): List of object IDs to filter the relations.

    Returns:
        QuerySet or None: A combined query set of the relations, or None if no queries
         are generated.
    """
    direct_relations = get_relations_config(schema, ns, perm)

    if not direct_relations:
        return None  # Avoid unnecessary processing if no direct relations are found

    queries = [
        process_relation_path(schema, ns, uns, rel, subj, object_ids)
        for rel in direct_relations
    ]
    valid_queries = [q for q in queries if q]
    return union_querysets(valid_queries) if valid_queries else None


def process_relation_path(
    schema: Dict[str, SchemaResource],
    ns: str,
    uns: str,
    rel: str,
    subj: str,
    object_ids: List[str],
) -> Optional[QuerySet]:
    """
    Processes a single relation path and generates a query for it.

    Args:
        schema: The schema of resources.
        ns (str): The namespace for the resources.
        uns (str): The user or identifier for filtering the relations.
        rel: The relation to process.
        subj: The subject for which the relation is to be retrieved.
        object_ids: The object IDs to filter the relations.

    Returns:
        QuerySet or None: The query for the relation, or None if no query is generated.
    """
    rel_paths = walk_relations(schema, ns, uns, rel)
    queries = [
        generate_tree_relation_query(subj, object_ids, rel_path)
        for rel_path in rel_paths
        if rel_path and rel_path[-1][2] == uns
    ]
    valid_queries = [q for q in queries if q]
    return union_querysets(valid_queries) if valid_queries else None


def generate_tree_relation_query(
    subj: str, object_ids: List[str], rel_path: List[tuple[str, str, str, str]]
) -> Optional[QuerySet]:
    """
    Generates a query for a specific relation path.

    Args:
        subj: The subject for which the relation is to be retrieved.
        object_ids: The object IDs to filter the relations.
        rel_path: A list representing the relation path to follow.

    Returns:
        QuerySet or None: The query for the relation path, or None if no query is
        generated.
    """
    rel_path.reverse()
    query_r = None
    for _ns, _rel, _uns, _ in rel_path:
        object_filter = (
            Subquery(object_ids) if isinstance(object_ids, QuerySet) else object_ids
        )
        query_r = filter_relation_tuple(
            _ns,
            _rel,
            _uns,
            subject_filter=(
                subj
                if not query_r
                else Subquery(query_r.values_list(RelationTupleField.OBJECT_ID))
            ),
            object_filter=object_filter,
        )
    return query_r
