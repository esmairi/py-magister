from tests.test_document.base_document_test import BaseDocumentTest


class TestLookSubj1DirectRelDocument(BaseDocumentTest):
    def test_look_subj_1_direct_rel(self, doc1_user1):
        self.access_manager_test.create_bulk([doc1_user1])

        res1 = self.access_manager_test.lookup_subjects(
            doc1_user1.namespace,
            "read",
            doc1_user1.userset_namespace,
            doc1_user1.object_id,
        )
        res2 = self.access_manager_test.lookup_subjects(
            doc1_user1.namespace,
            "write",
            doc1_user1.userset_namespace,
            doc1_user1.object_id,
        )
        res3 = self.access_manager_test.lookup_subjects(
            doc1_user1.namespace,
            "manage",
            doc1_user1.userset_namespace,
            doc1_user1.object_id,
        )
        res4 = self.access_manager_test.lookup_subjects(
            doc1_user1.namespace, "manage", doc1_user1.userset_namespace, "u2"
        )
        self.dj_tester.assertQuerySetEqual(res1, ["u1"], ordered=False)
        self.dj_tester.assertQuerySetEqual(res2, ["u1"], ordered=False)
        self.dj_tester.assertQuerySetEqual(res3, [], ordered=False)
        self.dj_tester.assertQuerySetEqual(res4, [], ordered=False)


class TestLookSubj2DirectRelDocument(BaseDocumentTest):
    def test_look_subj_2_direct_rel(self, doc1_user1, doc1_user2):
        self.access_manager_test.create_bulk([doc1_user1, doc1_user2])

        res1 = self.access_manager_test.lookup_subjects(
            doc1_user1.namespace,
            "read",
            doc1_user1.userset_namespace,
            doc1_user1.object_id,
        )
        res2 = self.access_manager_test.lookup_subjects(
            doc1_user1.namespace,
            "write",
            doc1_user1.userset_namespace,
            doc1_user1.object_id,
        )
        res3 = self.access_manager_test.lookup_subjects(
            doc1_user1.namespace,
            "manage",
            doc1_user1.userset_namespace,
            doc1_user1.object_id,
        )
        res4 = self.access_manager_test.lookup_subjects(
            doc1_user1.namespace, "manage", doc1_user1.userset_namespace, "u2"
        )
        self.dj_tester.assertQuerySetEqual(res1, ["u1", "u2"], ordered=False)
        self.dj_tester.assertQuerySetEqual(res2, ["u1", "u2"], ordered=False)
        self.dj_tester.assertQuerySetEqual(res3, [], ordered=False)
        self.dj_tester.assertQuerySetEqual(res4, [], ordered=False)


class TestLookSubjLinkedRelDocumentDeep1(BaseDocumentTest):
    def test_look_subj_linked_rel_deep1(self, doc1_group1, group1_user1):
        self.access_manager_test.create_bulk([doc1_group1, group1_user1])

        res1 = self.access_manager_test.lookup_subjects(
            doc1_group1.namespace,
            "read",
            group1_user1.userset_namespace,
            doc1_group1.object_id,
        )
        res2 = self.access_manager_test.lookup_subjects(
            doc1_group1.namespace,
            "write",
            group1_user1.userset_namespace,
            doc1_group1.object_id,
        )
        res3 = self.access_manager_test.lookup_subjects(
            doc1_group1.namespace,
            "manage",
            group1_user1.userset_namespace,
            doc1_group1.object_id,
        )
        res4 = self.access_manager_test.lookup_subjects(
            doc1_group1.namespace, "manage", group1_user1.userset_namespace, "doc2"
        )
        self.dj_tester.assertQuerySetEqual(res1, ["u1"], ordered=False)
        self.dj_tester.assertQuerySetEqual(res2, [], ordered=False)
        self.dj_tester.assertQuerySetEqual(res3, [], ordered=False)
        self.dj_tester.assertQuerySetEqual(res4, [], ordered=False)


class TestLookSubjLinkedRelDocumentDeep2(BaseDocumentTest):
    def test_has_perm_linked_rel_deep2(self, doc1_group1, group1_team1, team1_user1):
        self.access_manager_test.create_bulk([doc1_group1, group1_team1, team1_user1])

        res1 = self.access_manager_test.lookup_subjects(
            "document", "read", "user", "doc1"
        )
        res2 = self.access_manager_test.lookup_subjects(
            "document", "read", "user", "doc2"
        )
        self.dj_tester.assertQuerySetEqual(res1, ["u1"], ordered=False)
        self.dj_tester.assertQuerySetEqual(res2, [], ordered=False)


class TestLookSubjLinkedRelDocumentRecursive(BaseDocumentTest):
    def test_has_perm_linked_rel_recursive_deep1(
        self, doc1_group1, group1_group2, group2_user1
    ):
        self.access_manager_test.create_bulk([doc1_group1, group1_group2, group2_user1])

        res1 = self.access_manager_test.lookup_subjects(
            "document", "read", "user", "doc1"
        )
        res2 = self.access_manager_test.lookup_subjects(
            "document", "read", "user", "doc2"
        )
        self.dj_tester.assertQuerySetEqual(res1, ["u1"], ordered=False)
        self.dj_tester.assertQuerySetEqual(res2, [], ordered=False)


class TestLookSubjInheritRelDocument(BaseDocumentTest):
    def test_look_sub_inherit_rel_1(self, file1_doc1, doc1_user1):
        self.access_manager_test.create_bulk([file1_doc1, doc1_user1])
        res1 = self.access_manager_test.lookup_subjects("file", "read", "user", "file1")
        res2 = self.access_manager_test.lookup_subjects("file", "read", "user", "file2")
        self.dj_tester.assertQuerySetEqual(res1, ["u1"], ordered=False)
        self.dj_tester.assertQuerySetEqual(res2, [], ordered=False)

    def test_look_subj_inherit_rel_2(self, file1_doc1, doc1_user1, doc1_user2):
        self.access_manager_test.create_bulk([file1_doc1, doc1_user1, doc1_user2])
        res1 = self.access_manager_test.lookup_subjects("file", "read", "user", "file1")
        res2 = self.access_manager_test.lookup_subjects("file", "read", "user", "file2")
        self.dj_tester.assertQuerySetEqual(res1, ["u1", "u2"], ordered=False)
        self.dj_tester.assertQuerySetEqual(res2, [], ordered=False)
