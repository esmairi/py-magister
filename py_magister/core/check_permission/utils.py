from django.db.models import QuerySet

from py_magister.models import RelationTuple, RelationTupleField


def has_direct_relations(
    namespace: str,
    userset_namespace: str,
    object_id: str | None,
    subject_id: str | None,
    relation: str,
    userset_relation: str = None,
) -> QuerySet:
    """
    Checks if at least one direct relations exists.

    group#member has relation writer

    :param namespace: The resource namespace.
    :param userset_namespace: The userset namespace.
    :param object_id: The target object ID.
    :param subject_id: The subject ID.
    :param relation: The set of relations to check.
    :param userset_relation:
    :return: True if any relation exists, False otherwise.

    """
    relation_query = {
        RelationTupleField.NAMESPACE: namespace,
        RelationTupleField.USERSET_NAMESPACE: userset_namespace,
        RelationTupleField.RELATION: relation,
        RelationTupleField.USERSET_RELATION: userset_relation,
    }
    if object_id:
        if isinstance(object_id, list):
            relation_query[f"{RelationTupleField.OBJECT_ID}__in"] = object_id
        else:
            relation_query[RelationTupleField.OBJECT_ID] = object_id

    if subject_id:
        if isinstance(subject_id, list):
            relation_query[f"{RelationTupleField.USERSET_SUBJECT_ID}__in"] = subject_id
        else:
            relation_query[RelationTupleField.USERSET_SUBJECT_ID] = subject_id
    return RelationTuple.objects.filter(**relation_query)
