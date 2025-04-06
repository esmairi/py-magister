from typing import List, Optional

from django.db.models import QuerySet

from py_magister.core.utils import filter_relation_tuple


def fecth_object_relations(
    namespace: str,
    relation: str,
    userset_namespace: str,
    object_filter: str | List[str],
    userset_relation: Optional[str] = None,
) -> QuerySet:
    """
    Retrieves a queryset of relation tuples based on the provided namespace, relation,
    userset namespace, and object filter. An optional userset relation can also be
    applied.

    This function wraps `filter_relation_tuple` to filter the `RelationTuple` model for
    entries matching the given criteria. It returns all tuples where the object
    ID matches the `object_filter` (one or more IDs) and the relationship is defined by
    the specified `relation` and `userset_relation` within the given `namespace` and
    `userset_namespace`.

    Args:
        namespace (str): The namespace defining the resource type (e.g., "document").
        relation (str): The relation name (e.g., "owner", "editor") indicating how the
            subject relates to the resource.
        userset_namespace (str): The namespace of the subject set (e.g., "user").
        object_filter (Union[str, List[str]]): A single object ID or a list of
        object IDs to filter on.
        userset_relation (Optional[str]): An optional relation within the
        userset namespace (e.g., "member"), allowing further restriction on subject
        relationships.

    Returns:
        QuerySet: A Django QuerySet of matching `RelationTuple` entries, or an empty
        QuerySet if no tuples match the criteria.
    """
    return filter_relation_tuple(
        namespace,
        relation,
        userset_namespace,
        userset_relation,
        object_filter=object_filter,
    )
