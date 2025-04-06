from typing import Optional, Dict

from django.db.models import Subquery, QuerySet

from py_magister.core.lookup_resources.lookup_resources_direct_rel import (
    fetch_resources_direct_rel,
)
from py_magister.core.schema_access import SchemaResource, NamespaceRelation
from py_magister.core.utils import (
    union_querysets,
    get_relations_config,
    filter_relation_tuple,
)
from py_magister.models import RelationTupleField


def fetch_resources_inherit_rel(
    schema: Dict[str, SchemaResource], ns: str, perm: str, uns: str, subj: str
) -> Optional[QuerySet]:
    """
    Retrieves inherited relations from the relations configuration and generates
    associated queries.

    Args:
        schema (Dict[str, SchemaResource]): The schema of resources with defined
        relations.
        ns (str): The namespace for the resources.
        perm (str): The type of permission used to retrieve the relations.
        uns (str): The user or other identifier to filter resources.
        subj: The subject for which the relations need to be retrieved.

    Returns:
        QuerySet or None: A combined query set for all the inherited relations,
        or None if no queries are generated.
    """
    inherit_relations = get_relations_config(schema, ns, perm, True)

    if not inherit_relations:
        return None  # Avoid unnecessary processing if no inherited relations are found

    queries = [
        process_inherit_relation(schema, ns, base_rel, inherit_perm, uns, subj)
        for base_rel, inherit_perm in (rel.split("->") for rel in inherit_relations)
    ]
    valid_queries = [q for q in queries if q]
    return union_querysets(valid_queries) if valid_queries else None


def process_inherit_relation(
    schema: Dict[str, SchemaResource],
    ns: str,
    base_rel: str,
    inherit_perm: str,
    uns: str,
    subj: str,
) -> Optional[QuerySet]:
    """
    Processes a single inherited relation and generates the related queries.

    Args:
        schema: The schema of resources.
        ns (str): The namespace for the resources.
        base_rel (str): The base relation to process.
        inherit_perm (str): The inherited permission to apply.
        uns (str): The user or other identifier.
        subj: The subject to process the relation for.

    Returns:
        QuerySet or None: A combined query set for the inherited relation,
        or None if no queries are generated.
    """
    queries = [
        generate_inherit_relation_query(
            schema, ns, base_rel, subject_ns, inherit_perm, uns, subj
        )
        for subject_ns in schema[ns].relations[base_rel]
    ]
    valid_queries = [q for q in queries if q]
    return union_querysets([q for q in queries if q]) if valid_queries else None


def generate_inherit_relation_query(
    schema: Dict[str, SchemaResource],
    ns: str,
    base_rel: str,
    subject_ns: NamespaceRelation,
    inherit_perm: str,
    uns: str,
    subj: str,
) -> Optional[QuerySet]:
    """
    Generates a query for a single subject relation based on inherited permissions.

    Args:
        schema: The schema of resources.
        ns (str): The namespace for the resources.
        base_rel (str): The base relation to generate the query for.
        subject_ns: The subject namespace.
        inherit_perm (str): The inherited permission to apply.
        uns (str): The user or other identifier.
        subj: The subject to process the relation for.

    Returns:
        QuerySet or None: The query for the inherited relation,
        or None if no query is generated.
    """
    related_resources = filter_relation_tuple(
        ns, base_rel, subject_ns.namespace
    ).values_list(RelationTupleField.USERSET_SUBJECT_ID, flat=True)

    query = fetch_resources_direct_rel(
        schema, subject_ns.namespace, inherit_perm, uns, subj, related_resources
    )

    return (
        filter_relation_tuple(
            ns,
            base_rel,
            subject_ns.namespace,
            subject_filter=Subquery(
                query.values_list(RelationTupleField.OBJECT_ID, flat=True)
            ),
        )
        if query
        else None
    )
