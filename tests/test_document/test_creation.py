from py_magister.models import RelationTuple
from tests.test_document.base_document_test import BaseDocumentTest


class TestCreationDocument(BaseDocumentTest):
    def test_create_document(self, doc1_user1_dict):
        resource, _ = self.access_manager_test.create_from_dict(doc1_user1_dict)
        assert resource.namespace == doc1_user1_dict.get("namespace")
        assert resource.object_id == doc1_user1_dict.get("object_id")
        assert resource.relation == doc1_user1_dict.get("relation")
        assert resource.userset_namespace == doc1_user1_dict.get("userset_namespace")
        assert resource.userset_relation == doc1_user1_dict.get("userset_relation")
        assert resource.userset_subject_id == doc1_user1_dict.get("userset_subject_id")

    def test_create_bulk(self, doc1_user1_dict, doc2_user1_dict):
        res1 = RelationTuple(**doc1_user1_dict)
        res2 = RelationTuple(**doc2_user1_dict)
        obj1, obj2 = self.access_manager_test.create_bulk([res1, res2])
        for obj, res in ((obj1, res1), (obj2, res2)):
            assert obj.namespace == res.namespace
            assert obj.object_id == res.object_id
            assert obj.relation == res.relation
            assert obj.userset_namespace == res.userset_namespace
            assert obj.userset_relation == res.userset_relation
            assert obj.userset_subject_id == res.userset_subject_id
