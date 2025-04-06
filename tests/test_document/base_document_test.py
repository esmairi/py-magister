import json
from django.test import TestCase

import pytest

from py_magister.access_manager import AccessManager
from tests.test_settings import BASE_DIR


@pytest.mark.django_db(transaction=False)
class BaseDocumentTest:
    json_schema = json.load(open(BASE_DIR / "tests" / "test_document" / "schema.json"))
    access_manager_test = AccessManager(json_schema)
    dj_tester = TestCase()
