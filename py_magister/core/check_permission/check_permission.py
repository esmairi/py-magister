from typing import Dict

from py_magister.core.check_permission.check_inherited_subject_rel import (
    has_inherited_subject_permission,
)
from py_magister.core.check_permission.check_direct_subject_rel import (
    has_direct_linked_subject_permission,
)
from py_magister.core.schema_access import SchemaResource


def has_permission(
    schema: Dict[str, SchemaResource],
    namespace: str,
    object_id: str,
    userset_namespace: str,
    permission: str,
    subject_id,
) -> bool:
    """
    Determines whether a subject (e.g., user) has a specified permission on a given
     object within a namespace.

    This function first checks for direct or linked subject permissions, then checks
    for any inherited permissions that might apply to the subject. It returns True as
    soon as a matching permission is found through either check.

    Args:
        schema (Dict[str, SchemaResource]): The schema defining resources, relations,
        and permissions.
        namespace (str): The namespace (e.g., resource type) of the object being
        accessed.
        object_id (str): The ID of the object for which the permission is evaluated.
        userset_namespace (str): The namespace of the subject set (e.g., user, group).
        permission (str): The permission to check (e.g., "read", "write").
        subject_id (str): The ID of the subject (e.g., user ID) whose permission is
        being verified.

    Returns:
        bool: True if the subject has the specified permission on the object;
         otherwise, False.
    """
    if has_direct_linked_subject_permission(
        schema, namespace, object_id, userset_namespace, permission, subject_id
    ):
        return True
    if has_inherited_subject_permission(
        schema, namespace, object_id, userset_namespace, permission, subject_id
    ):
        return True
    return False
