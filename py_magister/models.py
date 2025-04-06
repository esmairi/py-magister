from enum import StrEnum

from django.db.models import UniqueConstraint, CharField, Manager, Model


class RelationTupleField(StrEnum):
    NAMESPACE = "namespace"
    OBJECT_ID = "object_id"
    RELATION = "relation"
    USERSET_NAMESPACE = "userset_namespace"
    USERSET_SUBJECT_ID = "userset_subject_id"
    USERSET_RELATION = "userset_relation"


class RelationTuple(Model):
    objects = Manager()
    namespace: str = CharField(max_length=100)
    object_id: str = CharField(max_length=100)
    relation: str = CharField(max_length=100)

    userset_namespace: str = CharField(max_length=100)
    userset_subject_id: str = CharField(max_length=100)
    userset_relation: str = CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.object_id} - {self.relation} {self.userset_subject_id}"

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=[
                    RelationTupleField.NAMESPACE,
                    RelationTupleField.OBJECT_ID,
                    RelationTupleField.RELATION,
                    RelationTupleField.USERSET_NAMESPACE,
                    RelationTupleField.USERSET_SUBJECT_ID,
                    RelationTupleField.USERSET_RELATION,
                ],
                name="unique_relation_tuple_constraint",
            )
        ]
