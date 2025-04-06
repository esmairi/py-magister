from typing import Dict, List

from django.db import transaction
from django.db.models import QuerySet

from py_magister.core.exceptions import NamespaceNotFoundError, RelationNotFoundError
from py_magister.core.schema_access import SchemaResource
from py_magister.models import RelationTuple, RelationTupleField


class RelationshipWriter:
    schema: Dict[str, SchemaResource]

    def __init__(self, schema: Dict[str, SchemaResource]):
        self.schema = schema

    def create_from_dict(self, relation_tuple_dict: Dict) -> QuerySet:
        return RelationTuple.objects.get_or_create(
            **relation_tuple_dict,
        )

    def create_bulk(self, relation_tuples: List[RelationTuple]) -> QuerySet:
        [self.check_relashionship(rel) for rel in relation_tuples]
        with transaction.atomic():
            return RelationTuple.objects.bulk_create(
                relation_tuples, ignore_conflicts=True
            )

    def create_bulk_from_dict(self, relation_tuple_dict: List[Dict]):
        relationships = [
            self.__get_relation_tuple_from_dict(relationship_dict)
            for relationship_dict in relation_tuple_dict
        ]
        return self.create_bulk(relationships)

    def __get_relation_tuple_from_dict(
        self, relation_tuple_dict: Dict
    ) -> RelationTuple:
        return RelationTuple(
            namespace=relation_tuple_dict.get(RelationTupleField.NAMESPACE),
            relation=relation_tuple_dict.get(RelationTupleField.RELATION),
            object_id=relation_tuple_dict.get(RelationTupleField.OBJECT_ID),
            userset_namespace=relation_tuple_dict.get(
                RelationTupleField.USERSET_NAMESPACE
            ),
            userset_subject_id=relation_tuple_dict.get(
                RelationTupleField.USERSET_SUBJECT_ID
            ),
            userset_relation=relation_tuple_dict.get(
                RelationTupleField.USERSET_RELATION
            )
            or None,
        )

    def check_relashionship(self, relation_tuple: RelationTuple):
        """

        :param relation_tuple:
        :return:
        """
        ns_config = self.schema.get(relation_tuple.namespace)
        if not ns_config:
            raise NamespaceNotFoundError(relation_tuple.namespace)
        relation_namespaces = ns_config.relations.get(relation_tuple.relation)
        if relation_tuple.relation not in ns_config.relations:
            raise RelationNotFoundError(
                relation_tuple.namespace, relation_tuple.namespace
            )
        for rel_ns in relation_namespaces:
            rel_ns_name = rel_ns.namespace
            rel_linked_to = rel_ns.linked_to
            if not self.schema.get(rel_ns.namespace):
                raise NamespaceNotFoundError(rel_ns.namespace)
            if (
                rel_linked_to
                and rel_linked_to not in self.schema.get(rel_ns.namespace).relations
            ):
                raise RelationNotFoundError(rel_ns_name, rel_linked_to)
