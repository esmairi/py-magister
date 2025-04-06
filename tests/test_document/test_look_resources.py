from tests.test_document.base_document_test import BaseDocumentTest


class TestLookupRes1DirectRelDocument(BaseDocumentTest):
    def test_look_resources_1_direct_rel(self, doc1_user1):
        self.access_manager_test.create_bulk([doc1_user1])

        res1 = self.access_manager_test.lookup_resources(
            "document", "read", "user", "u1"
        )
        res2 = self.access_manager_test.lookup_resources(
            "document", "write", "user", "u1"
        )
        res3 = self.access_manager_test.lookup_resources(
            "document", "manage", "user", "u1"
        )
        res4 = self.access_manager_test.lookup_resources(
            "document", "manage", "user", "u2"
        )
        self.dj_tester.assertQuerySetEqual(res1, ["doc1"], ordered=False)
        self.dj_tester.assertQuerySetEqual(res2, ["doc1"], ordered=False)
        self.dj_tester.assertQuerySetEqual(res3, [], ordered=False)
        self.dj_tester.assertQuerySetEqual(res4, [], ordered=False)


class TestLookupRes2DirectRelDocument(BaseDocumentTest):
    def test_look_resources_2_direct_rel(self, doc1_user1, doc2_user1):
        self.access_manager_test.create_bulk([doc1_user1, doc2_user1])

        res1 = self.access_manager_test.lookup_resources(
            "document", "read", "user", "u1"
        )
        res2 = self.access_manager_test.lookup_resources(
            "document", "read", "user", "u2"
        )
        self.dj_tester.assertQuerySetEqual(res1, ["doc1", "doc2"], ordered=False)
        self.dj_tester.assertQuerySetEqual(res2, [], ordered=False)


class TestLookupResLinkedRelDocumentDeep1(BaseDocumentTest):
    def test_look_resources_linked_rel_deep1(self, doc1_group1, group1_user1):
        self.access_manager_test.create_bulk([doc1_group1, group1_user1])

        res1 = self.access_manager_test.lookup_resources(
            "document", "read", "user", "u1"
        )
        res2 = self.access_manager_test.lookup_resources(
            "document", "write", "user", "u1"
        )
        res3 = self.access_manager_test.lookup_resources(
            "document", "manage", "user", "u1"
        )
        res4 = self.access_manager_test.lookup_resources(
            "document", "manage", "user", "u2"
        )

        self.dj_tester.assertQuerySetEqual(res1, ["doc1"], ordered=False)
        self.dj_tester.assertQuerySetEqual(res2, [], ordered=False)
        self.dj_tester.assertQuerySetEqual(res3, [], ordered=False)
        self.dj_tester.assertQuerySetEqual(res4, [], ordered=False)


class TestLookupResInheritRelDocument(BaseDocumentTest):
    def test_look_sub_inherit_rel_1(self, file1_doc1, doc1_user1):
        self.access_manager_test.create_bulk([file1_doc1, doc1_user1])
        res1 = self.access_manager_test.lookup_resources("file", "read", "user", "u1")
        res2 = self.access_manager_test.lookup_resources("file", "read", "user", "u2")
        self.dj_tester.assertQuerySetEqual(res1, ["file1"], ordered=False)
        self.dj_tester.assertQuerySetEqual(res2, [], ordered=False)

    def test_look_resources_inherit_rel_2(self, file1_doc1, file2_doc1, doc1_user1):
        self.access_manager_test.create_bulk([file1_doc1, file2_doc1, doc1_user1])
        res1 = self.access_manager_test.lookup_resources("file", "read", "user", "u1")
        res2 = self.access_manager_test.lookup_resources("file", "read", "user", "u2")
        self.dj_tester.assertQuerySetEqual(res1, ["file1", "file2"], ordered=False)
        self.dj_tester.assertQuerySetEqual(res2, [], ordered=False)
