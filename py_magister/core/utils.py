from typing import Dict, List, Optional, Set, Union

from django.db.models import QuerySet, Subquery

from py_magister.core.schema_access import NamespaceRelation, SchemaResource
from py_magister.models import RelationTupleField, RelationTuple


def filter_relation_subject(
    schema: Dict[str, SchemaResource],
    namespace: str,
    relation: str,
    is_linked: bool = False,
) -> tuple[NamespaceRelation, ...]:
    """
    Filters subjects based on whether they are linked (have an optional relation) or not

    :param schema: The schema dictionary containing resource definitions.
    :param namespace: The resource namespace to look up.
    :param relation: The relation key to retrieve subjects for.
    :param is_linked: If True, return only linked subjects (having an optional relation)
    , otherwise return unlinked ones.
    :return: A tuple of subjects matching the criteria.
    """
    relation_config = schema.get(namespace, {}).relations.get(relation, [])
    return tuple(
        subject for subject in relation_config if bool(subject.linked_to) == is_linked
    )


def get_relations_config(
    schema: Dict[str, SchemaResource],
    namespace: str,
    permission: str,
    is_inherited: bool = False,
) -> tuple[str, ...]:
    """
    Retrieve relations from the schema based on the given namespace and permission.

    :param schema: The schema dictionary containing resource definitions.
    :param namespace: The resource namespace to look up.
    :param permission: The permission key to retrieve relations for.
    :param is_inherited: If True, return only inherited relations (with '->'),
    otherwise return direct relations.
    :return: A tuple of relation strings matching the criteria.
    """
    relation_config = schema.get(namespace, {}).permissions.get(permission, []) or []
    return tuple(
        relation for relation in relation_config if ("->" in relation) == is_inherited
    )


def walk_relations(
    schema: Dict[str, SchemaResource],
    namespace,
    userset_namepace: str,
    relation,
    path=None,
) -> List[List[tuple[str, str, str, str]]]:
    """
    Recursively retrieves all possible relation paths in the schema starting from a
    given namespace and relation.

    The function explores the hierarchical structure of relations, following references
     in the format "namespace#relation".
    It returns all possible paths as lists of (namespace, relation, target) tuples.


    :param userset_namepace:
    :param schema: The schema defining namespaces, relations, and permissions.
    :param namespace: The starting namespace to explore.
    :param relation: The relation to follow from the namespace.
    :param path: The current path being explored (used for recursion).
    :return: A list of paths, where each path is a list of (namespace, relation,
    userset_namespace, userset_relation) tuples.
    """
    if path is None:
        path = []
    relations = schema[namespace].relations[relation]
    paths = []
    for rel in relations:
        next_namespace, next_relation = rel.namespace, rel.linked_to
        new_path = path + [(namespace, relation, next_namespace, next_relation)]

        if (
            next_relation
            and next_namespace in schema
            and userset_namepace != next_relation
            and next_namespace != namespace
        ):
            paths.extend(
                walk_relations(
                    schema, next_namespace, userset_namepace, next_relation, new_path
                )
            )
        else:
            paths.append(new_path)
        if next_namespace == namespace:
            path.extend([(namespace, relation, next_namespace, next_relation)])

    return paths


def is_recursive_relation(rel: tuple[str, str, str, str | None]) -> bool:
    ns, _, uns, _ = rel
    return ns == uns


def get_tree_relations_for_perm(schema, ns, un, perm):
    direct_relations = get_relations_config(schema, ns, perm)
    return [walk_relations(schema, ns, un, x) for x in direct_relations]


def get_field_filter_query(
    field: RelationTupleField, field_value: str | List[str] | QuerySet | Subquery
) -> str | None:
    if isinstance(field_value, (str, int)):
        return field
    elif isinstance(field_value, (list, set, tuple, QuerySet, Subquery)):
        return f"{field}__in"


def filter_relation_tuple(
    ns: str,
    rel: str,
    uns: str,
    usr_rel: Optional[str] = None,
    subject_filter: Optional[Union[str, QuerySet, Subquery, List[str] | Set]] = None,
    object_filter: Optional[Union[QuerySet, Subquery, List[str] | Set]] = None,
) -> QuerySet:
    """
    Constructs a QuerySet filtering RelationTuple based on the given namespace,
    relation, and filters.
    The query dict is built dynamically using get_field_filter_query().
    """
    query = {
        RelationTupleField.NAMESPACE: ns,
        RelationTupleField.RELATION: rel,
        RelationTupleField.USERSET_NAMESPACE: uns,
    }

    # Build a list of (field, value) pairs
    filters_to_apply = [
        (RelationTupleField.USERSET_SUBJECT_ID, subject_filter),
        (RelationTupleField.OBJECT_ID, object_filter),
        (RelationTupleField.USERSET_RELATION, usr_rel),
    ]

    for field, field_value in filters_to_apply:
        if field_value is not None:
            filter_key = get_field_filter_query(field, field_value)
            if filter_key:
                # If it's a QuerySet, we might convert to Subquery for IDs
                if isinstance(field_value, QuerySet):
                    field_value = Subquery(
                        field_value.values_list(RelationTupleField.OBJECT_ID, flat=True)
                    )
                query[filter_key] = field_value
    return RelationTuple.objects.filter(**query)


def _process_direct_relation(
    rel_tuple: tuple,
    current_subquery: Optional[Union[str, Subquery, QuerySet, list]],
    subject_id: str = None,
    target_namespace: str = None,
) -> QuerySet:
    current_ns, current_rel, next_ns, next_rel = rel_tuple

    return filter_relation_tuple(
        current_ns,
        current_rel,
        next_ns,
        next_rel,
        subject_filter=subject_id if next_ns == target_namespace else None,
        object_filter=(
            Subquery(current_subquery)
            if isinstance(current_subquery, QuerySet)
            else current_subquery
        ),
    )


# Lookup Subject
def union_querysets(querysets: List[QuerySet]) -> QuerySet:
    """
    Takes a list of QuerySets and returns a single QuerySet as a union of all.

    :param querysets: List of QuerySets to be combined.
    :return: A single QuerySet containing the union of all input QuerySets.
    """
    if not querysets:
        raise ValueError("length querysets must be > 0")

    return querysets[0].union(*querysets[1:])
