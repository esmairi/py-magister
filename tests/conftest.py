from typing import Dict

import pytest

from py_magister.models import RelationTuple


def get_rt(data: dict) -> RelationTuple:
    return RelationTuple(**data)


@pytest.fixture
def doc1_user1_dict() -> Dict:
    return {
        "namespace": "document",
        "object_id": "doc1",
        "relation": "reader",
        "userset_namespace": "user",
        "userset_subject_id": "u1",
    }


@pytest.fixture
def doc2_user1_dict() -> Dict:
    return {
        "namespace": "document",
        "object_id": "doc1",
        "relation": "reader",
        "userset_namespace": "user",
        "userset_subject_id": "u1",
    }


@pytest.fixture
def doc1_user1() -> RelationTuple:
    return get_rt(
        {
            "namespace": "document",
            "object_id": "doc1",
            "relation": "editor",
            "userset_namespace": "user",
            "userset_subject_id": "u1",
        }
    )


@pytest.fixture
def doc2_user1() -> RelationTuple:
    return get_rt(
        {
            "namespace": "document",
            "object_id": "doc2",
            "relation": "editor",
            "userset_namespace": "user",
            "userset_subject_id": "u1",
        }
    )


@pytest.fixture
def doc1_user2() -> RelationTuple:
    return get_rt(
        {
            "namespace": "document",
            "object_id": "doc1",
            "relation": "editor",
            "userset_namespace": "user",
            "userset_subject_id": "u2",
        }
    )


@pytest.fixture
def doc2_user2() -> RelationTuple:
    return get_rt(
        {
            "namespace": "document",
            "object_id": "doc2",
            "relation": "owner",
            "userset_namespace": "user",
            "userset_subject_id": "u2",
        }
    )


@pytest.fixture
def file1_doc1() -> RelationTuple:
    return get_rt(
        {
            "namespace": "file",
            "object_id": "file1",
            "relation": "parent",
            "userset_namespace": "document",
            "userset_subject_id": "doc1",
        }
    )


@pytest.fixture
def file2_doc1() -> RelationTuple:
    return get_rt(
        {
            "namespace": "file",
            "object_id": "file2",
            "relation": "parent",
            "userset_namespace": "document",
            "userset_subject_id": "doc1",
        }
    )


@pytest.fixture
def group1_user1() -> RelationTuple:
    return get_rt(
        {
            "namespace": "group",
            "object_id": "group1",
            "relation": "member",
            "userset_namespace": "user",
            "userset_subject_id": "u1",
        }
    )


@pytest.fixture
def group2_user1() -> RelationTuple:
    return get_rt(
        {
            "namespace": "group",
            "object_id": "group2",
            "relation": "member",
            "userset_namespace": "user",
            "userset_subject_id": "u1",
        }
    )


@pytest.fixture
def doc1_group1() -> RelationTuple:
    return get_rt(
        {
            "namespace": "document",
            "object_id": "doc1",
            "relation": "reader",
            "userset_namespace": "group",
            "userset_subject_id": "group1",
            "userset_relation": "member",
        }
    )


@pytest.fixture
def group1_team1() -> RelationTuple:
    return get_rt(
        {
            "namespace": "group",
            "object_id": "group1",
            "relation": "member",
            "userset_namespace": "team",
            "userset_subject_id": "team1",
            "userset_relation": "belongs",
        }
    )


@pytest.fixture
def team1_user1() -> RelationTuple:
    return get_rt(
        {
            "namespace": "team",
            "object_id": "team1",
            "relation": "belongs",
            "userset_namespace": "user",
            "userset_subject_id": "u1",
        }
    )


@pytest.fixture
def group1_group2() -> RelationTuple:
    return get_rt(
        {
            "namespace": "group",
            "object_id": "group1",
            "relation": "member",
            "userset_namespace": "group",
            "userset_subject_id": "group2",
            "userset_relation": "member",
        }
    )
