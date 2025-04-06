from dataclasses import dataclass
from typing import List, Dict, Optional, TypedDict


class ResourceDefinition(TypedDict):
    relations: Dict[str, List[str]]
    permissions: Dict[str, List[str]]


SchemaDict = Dict[str, ResourceDefinition]


class NamespaceRelation:
    namespace: str
    linked_to: Optional[str] = None

    def __init__(self, namespace: str):
        """

        :param namespace:
        :return:
        """
        if "#" in namespace:
            self.namespace, self.linked_to = namespace.split("#")
        else:
            self.namespace = namespace


@dataclass
class SchemaResource:
    namespace: str
    relations: Dict[str, List[NamespaceRelation]]
    permissions: Dict[str, List[str]]


@dataclass
class AccessControlSchema:
    schema: Dict[str, SchemaResource]

    @classmethod
    def from_dict(cls, data: SchemaDict) -> "AccessControlSchema":
        schema = dict()
        for namespace in data:
            ns_config = data.get(namespace)
            relations_dict = ns_config.get("relations") if ns_config else dict()
            relations = {
                relation: [
                    NamespaceRelation(rel_namespace)
                    for rel_namespace in relations_dict[relation]
                ]
                for relation in relations_dict
            }
            schema[namespace] = SchemaResource(
                namespace=namespace,
                relations=relations,
                permissions=ns_config.get("permissions") if ns_config else dict(),
            )

        return cls(
            schema=schema,
        )
