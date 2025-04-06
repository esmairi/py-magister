class NamespaceNotFoundError(Exception):
    """Raised when the given namespace does not exist."""

    def __init__(self, namespace: str):
        super().__init__(f"Namespace '{namespace}' not found.")


class RelationNotFoundError(Exception):
    """Raised when the given relation does not exist within a namespace."""

    def __init__(self, namespace: str, relation: str):
        super().__init__(f"Relation '{relation}' not found in namespace '{namespace}'.")
