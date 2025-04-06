from typing import Dict, List

from py_magister.core import check_permission
from py_magister.core.check_permission.utils import has_direct_relations
from py_magister.core.schema_access import NamespaceRelation, SchemaResource
from py_magister.core.utils import filter_relation_subject, get_relations_config
from py_magister.models import RelationTupleField


def has_inherited_subject_permission(
    schema: Dict[str, SchemaResource],
    namespace: str,
    object_id: str,
    userset_namespace: str,
    permission: str,
    subject_id: str,
) -> bool:
    """
    Determines whether a subject has permission through inherited direct subjects.

    This function checks if the subject has permission via an inherited relation,
    where a parent entity grants permissions to its children through a specified
    inheritance structure.

    Example:
        InheritedPermission + DirectSubject: read parent->read

    Args:
        schema (Dict[str, SchemaResource]): The schema defining resource relationships.
        namespace (str): The namespace of the resource being checked.
        object_id (str): The ID of the object being accessed.
        userset_namespace (str): The userset namespace defining the subject group.
        permission (str): The permission being checked.
        subject_id (str): The subject ID whose permission is being verified.

    Returns:
        bool: True if the subject has inherited permission, False otherwise.
    """
    relations = get_relations_config(schema, namespace, permission, is_inherited=True)

    for relation in relations:
        relation_name, inherited_permission = relation.split("->")

        subject_namespaces = get_subject_namespaces(schema, namespace, relation_name)

        for subject in subject_namespaces:
            related_resources = fetch_related_resources(
                namespace, subject.namespace, object_id, relation_name
            )

            if any(
                check_permission.has_permission(
                    schema,
                    subject.namespace,
                    rel_obj,
                    userset_namespace,
                    inherited_permission,
                    subject_id,
                )
                for rel_obj in related_resources
            ):
                return True

    return False


def get_subject_namespaces(
    schema: Dict[str, SchemaResource], namespace: str, relation_name: str
) -> tuple[NamespaceRelation, ...]:
    """
    Retrieves the subject namespaces for a given relation.

    Args:
        schema (Dict[str, SchemaResource]): The schema defining resource relationships.
        namespace (str): The namespace of the resource being checked.
        relation_name (str): The relation name to filter.

    Returns:
        List[NamespaceRelation]: A list of namespace relations.
    """
    direct_subjects = filter_relation_subject(schema, namespace, relation_name)
    linked_subjects = (
        filter_relation_subject(schema, namespace, relation_name, True) or []
    )

    return direct_subjects + tuple(
        NamespaceRelation(namespace=ns.namespace.split("#")[0])
        for ns in linked_subjects
    )


def fetch_related_resources(
    namespace: str, subject_namespace: str, object_id: str, relation_name: str
) -> List[str]:
    """
    Fetches related resources for a given namespace and relation.

    Args:
        namespace (str): The namespace of the resource being checked.
        subject_namespace (str): The subject namespace associated with the relation.
        object_id (str): The ID of the object being accessed.
        relation_name (str): The relation to filter.

    Returns:
        List[str]: A list of related resource IDs.
    """
    return list(
        has_direct_relations(
            namespace, subject_namespace, object_id, None, relation_name
        ).values_list(RelationTupleField.USERSET_SUBJECT_ID, flat=True)
    )
