from tests.test_document.base_document_test import BaseDocumentTest


class TestHasPermissionDirectRelDocument(BaseDocumentTest):
    def test_has_perm_direct_rel(self, doc1_user1):
        self.access_manager_test.create_bulk([doc1_user1])

        assert self.access_manager_test.has_permission(
            doc1_user1.namespace,
            doc1_user1.object_id,
            doc1_user1.userset_namespace,
            "read",
            doc1_user1.userset_subject_id,
        )
        assert not self.access_manager_test.has_permission(
            doc1_user1.namespace,
            "doc2",
            doc1_user1.userset_namespace,
            "read",
            doc1_user1.userset_subject_id,
        )

        assert not self.access_manager_test.has_permission(
            doc1_user1.namespace,
            doc1_user1.object_id,
            doc1_user1.userset_namespace,
            "write",
            "u2",
        )


class TestHasPermissionLinkedRelDocument(BaseDocumentTest):
    def test_has_perm_linked_rel_deep1(self, doc1_group1, group1_user1):
        self.access_manager_test.create_bulk([doc1_group1, group1_user1])

        assert self.access_manager_test.has_permission(
            "document", "doc1", "user", "read", "u1"
        )
        assert not self.access_manager_test.has_permission(
            "document", "doc2", "user", "read", "u1"
        )
        assert not self.access_manager_test.has_permission(
            "document", "doc1", "user", "read", "u2"
        )

    def test_has_perm_linked_rel_deep2(self, doc1_group1, group1_team1, team1_user1):
        self.access_manager_test.create_bulk([doc1_group1, group1_team1, team1_user1])

        assert self.access_manager_test.has_permission(
            "document", "doc1", "user", "read", "u1"
        )
        assert not self.access_manager_test.has_permission(
            "document", "doc2", "user", "read", "u1"
        )
        assert not self.access_manager_test.has_permission(
            "document", "doc1", "user", "read", "u2"
        )

    def test_has_perm_linked_rel_recursive_deep1(
        self, doc1_group1, group1_group2, group2_user1
    ):
        self.access_manager_test.create_bulk([doc1_group1, group1_group2, group2_user1])

        assert self.access_manager_test.has_permission(
            "document", "doc1", "user", "read", "u1"
        )
        assert not self.access_manager_test.has_permission(
            "document", "doc2", "user", "read", "u1"
        )
        assert not self.access_manager_test.has_permission(
            "document", "doc1", "user", "read", "u2"
        )


class TestHasPermissionInheritRelDocument(BaseDocumentTest):
    def test_has_perm_inherit_rel(self, file1_doc1, doc1_user1):
        self.access_manager_test.create_bulk([file1_doc1, doc1_user1])

        assert self.access_manager_test.has_permission(
            "file", "file1", "user", "read", "u1"
        )
        assert not self.access_manager_test.has_permission(
            "file", "file2", "user", "read", "u1"
        )
        assert not self.access_manager_test.has_permission(
            "file", "file1", "user", "read", "u2"
        )
