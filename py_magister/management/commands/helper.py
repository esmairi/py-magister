import json

from py_magister.access_manager import AccessManager


def get_access_manager(schema: str) -> AccessManager:
    json_schema = json.load(open(schema))
    return AccessManager(json_schema)


def parse_perm_string(perm_string: str):
    """
    Parses a string of the form:
        "namespace:object_id#relation@subject_namespace:subject_id"

    Returns a tuple: (namespace, object_id, relation, subject_ns, subject_id)
    """
    # Example: "document:doc1#reader@user:user42"
    # 1) Split around '#' to separate resource part from relation@subject
    #    => "document:doc1" and "reader@user:user42"
    try:
        resource_part, relation_part = perm_string.split("#", 1)
    except ValueError:
        raise ValueError("Missing '#' separator.")

    # resource_part => "document:doc1"
    # relation_part => "reader@user:user42"

    # 2) For resource_part, split by ':' => namespace, object_id
    try:
        namespace, object_id = resource_part.split(":", 1)
    except ValueError:
        raise ValueError("Resource part must be 'namespace:object_id'.")

    # 3) For relation_part, split by '@' => "reader" and "user:user42"
    try:
        rel, subject_part = relation_part.split("@", 1)
    except ValueError:
        raise ValueError("Relation part must contain '@' after '#'.")

    # 4) For subject_part, split by ':' => subject_namespace, subject_id
    try:
        subject_ns, sub_id = subject_part.split(":", 1)
    except ValueError:
        raise ValueError("Subject part must be 'subject_namespace:subject_id'.")
    sub_rel = None
    if sub_id.split("#") == 2:
        sub_id, sub_rel = sub_id.split("#")
    return namespace, object_id, rel, subject_ns, sub_id, sub_rel
