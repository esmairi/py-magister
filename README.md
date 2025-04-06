# py_magister Django App Documentation

## Overview

`py_magister` is a Django application designed to provide comprehensive access control by managing relationships between subjects (users, groups) and resources (documents, objects). It offers a schema-based approach to defining and enforcing permissions, simplifying relationship management and permission checks.


### Why This Module?

In many authorization systems, you must **first** send a request to the authorization service to retrieve all resource IDs a user can access, **then** do a join or filter in your local database. This approach quickly becomes cumbersome and inefficient when the data set is large, because:

1. You might end up fetching **thousands or millions** of resource IDs from an external service.
2. Performing a join or filter on your database with such a large in-memory list is expensive and complicated.

**This module** solves that problem by returning a **Django QuerySet** for authorized resources, rather than a flat list of IDs. Because it’s a QuerySet, you can **chain** additional filters, joins, or annotations in Python—without manually handling huge ID lists. This means you can write queries like:



```python
from py_magister.access_manager import AccessManager
access_manager = AccessManager(schema)

authorized_resources = access_manager.get_authorized_resources(lookup_resources('document',  'read', 'user', 'u1'))

# Now chain additional filters/joins in Django ORM, e.g.:
results = (
    YourResourceModel.objects.filter(pk__in=Subquery(authorized_resources))
)
```


## Key Features

- **Schema-Based Access Control:** Clearly defines resources, relationships, and permissions.
- **Efficient Relationship Management:** Supports creation, querying, and bulk operations for resource-subject relationships.
- **Role-Based Permission Handling:** Dynamically manages permissions based on user roles and defined relationships.
- **Optimized Queries:** Facilitates quick permission checks for both direct and inherited permissions.


---

## Installation

Install the package directly from Git using pip:

```bash
pip install py_magister
```
Add my_module to your INSTALLED_APPS in settings.py:
````python
INSTALLED_APPS = [
    # ...
    'py_magister',
]
````

Run migrations to apply any database changes

```bash
python manage.py migrate
```



---

## Schema Definition Example

This system is built on the concept of a **schema**, which defines:

- **Resource Types** (namespaces): The entities like users, groups, documents.
- **Relations**: How these entities relate to each other.
- **Permissions**: High-level access control derived from one or more relations.

Example:

```json
{
  "user": {},
  "group": {"relations": {"member": ["user"]}},
  "document": {
    "relations": {
      "owner": ["user"],
      "editor": ["user"],
      "reader": ["user", "group#member"],
      "parent": ["document"]
    },
    "permissions": {
      "read": ["owner", "editor", "reader", "parent->read"],
      "write": ["owner", "editor", "parent->editor"]
    }
  }
}
```

### Schema Explanation

#### 1. Resource: user
    The user namespace represents individual users.

    It has no internal relations defined within the schema.

    Users can be assigned as owner, editor, or reader in the context of a document.

    Users can also be members of groups (through the group#member relation).


#### 2. Resource: group

    member relation: connects users to a group.

    Any user linked via group:team#member@user:alice means "Alice is a member of team".

    This allows permissions to be assigned to a group (e.g., reader), and then inherited by all group members.




#### 3. Resource: document
Relations

    owner: a user who fully controls the document.

    editor: a user with write access.

    reader: can be a direct user or a group member (group#member), giving groups read access.

    parent: points to another document, enabling permission inheritance.

Permissions

    read permission is granted to:

        Users assigned as owner, editor, or reader.

        Any user with read permission on a parent document (parent->read).

    write permission is granted to:

        Users assigned as owner or editor.

        Any user who is an editor on a parent document (parent->editor).

    If a document doc2 has a parent doc1, and doc1 grants read or editor access to a user, then doc2 also inherits those permissions.
    This enables deeply nested documents or resources to share hierarchical access control without duplicating assignments.





# CLI Commands

Manage relations and check permissions using Django management commands. Each command accepts a **schema file** and a **single string argument** that encodes your resource and subject in the format:


For instance:
- `document:doc1#owner@user:user1`
- `document:doc1#read@user:user1`

---

#### 1. Adding a Relation

Use the `add` command to insert a new relationship into your system. For example:

```bash
python ./manage.py add --schema tests/test_document/schema.json document:doc1#owner@user:user1
```

#### 2. Check permission
Use the permission command to verify whether a given subject has a certain permission on a resource:

```bash
python ./manage.py permission --schema tests/test_document/schema.json document:doc1#read@user:user1
```







##  Class: `AccessManager`

### Initialization

Instantiate the AccessManager with a schema:

```python
from py_magister.access_manager import AccessManager
access_manager = AccessManager(schema)
```

### Available Methods

Creates relationships from a dictionary representation:

#### `create_from_dict(relationship_dict: Dict) -> QuerySet`

Bulk creates multiple relationships:

#### `create_bulk(relationships: List[RelationTuple]) -> QuerySet`

Checks if a subject has specific permission:

#### `has_permission(namespace: str, object_id: str, userset_namespace: str, permission: str, subject_id: str) -> bool`

Looks up subjects associated with permissions:
#### `lookup_subjects(namespace: str, permission: str, userset_namespace: str, object_id: Union[str, List[str]], only_query: bool = False) -> Union[QuerySet, List[str]]`

Retrieves resources accessible by subjects:
#### `lookup_resources(namespace: str, permission: str, userset_namespace: str, subject: Union[str, List[str]], only_query: bool = False) -> Union[QuerySet, List[str]]`

Retrieves resource relations:
#### `lookup_resource_relations(namespace: str, relation: str, userset_namespace: str, object_filter: str | List[str], userset_relation: Optional[str] = None, only_query: bool = False)`


---

## Data Model: `RelationTuple`

Represents the relationship between subjects and resources.


| Field                | Type                            | Description                                       |
|----------------------|---------------------------------|---------------------------------------------------|
| `namespace`          | `CharField(100)`                | Namespace of the relationship (e.g., document)    |
| `object_id`          | `CharField(100)`                | Resource identifier (e.g., doc1)                  |
| `relation`           | `CharField(100)`                | Type of relation (e.g., owner, editor, reader)    |
| `userset_namespace`  | `CharField(100)`                | Namespace for the userset (e.g., user)            |
| `userset_subject_id` | `CharField(100, nullable=True)` | Identifier for subject or group                   |
| `userset_relation`   | `CharField(100, nullable=True)` | Relation within the userset (e.g., admin, member) |




## Usage Examples

### Creating Relationships

```python
from py_magister.models import RelationTuple
relationship1 = RelationTuple(namespace="user", object_id="doc1", relation="owner", userset_namespace="user", userset_subject_id="user123")
relationship2 = RelationTuple(namespace="document", object_id="doc1", relation="reader", userset_namespace="group", userset_subject_id="group1", userset_relation="member")

# Single creation
access_manager.create(relationship1)

# Bulk creation
access_manager.create_bulk([relationship1, relationship2])
```

### Checking Permissions

```python
if access_manager.has_permission("document", "doc1", "user", "read", "user123"):
    print("User has permission to read the document.")
else:
    print("User does not have permission to read the document.")
```

### Lookup Subjects

```python
subjects = access_manager.lookup_subjects("document", "read", "user", "doc1")
# subjects   =    ["u1", "u2"]

```

### Lookup Resources

```python
res = access_manager.lookup_resources("document", "read", "user", "user123")
# res   =    ["doc1"]

```

### Looks up resource relations

```python
res = access_manager.lookup_resource_relations("document", "reader", "user", "doc1")

```


### More Examples
**Note:** For additional usage examples and reference implementations, please check the `tests/` folder in this repository.


## License

This project is licensed under the MIT License.
