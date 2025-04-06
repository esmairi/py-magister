from dataclasses import dataclass
from typing import Optional

from django.db.models import Subquery


@dataclass
class LookupSubjectsRequest:
    namespace: str
    permission: str
    userset_namespace: str
    target_object: Optional[str | Subquery]


@dataclass
class LookupResourcesRequest:
    namespace: str
    permission: str
    userset_namespace: str
    subject: Optional[str | Subquery]
