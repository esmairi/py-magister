from typing import Dict, List, Optional
from django.db.models import QuerySet

from py_magister.core import (
    has_permission,
    fecth_object_relations,
    fetch_resources,
    fetch_resources_query,
    fetch_subjects,
    fetch_subjects_query,
    LookupSubjectsRequest,
    LookupResourcesRequest,
    RelationshipWriter,
    SchemaResource,
    AccessControlSchema,
)
from py_magister.models import RelationTuple


class AccessManager:
    """
    A class responsible for managing access control relationships between resources
    within a given schema.

    The `AccessManager` facilitates operations such as creating, querying, and managing
    access control relationships between resources defined in the schema. It uses a
    `RelationshipWriter` to handle the creation of relationships and queries related
    to these relationships. The schema defines how resources are structured,
    related, and the permissions associated with those relationships.

    Example schema:
        schema = {
            "user": {},
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

    Attributes:
        schema (Dict[str, SchemaResource]): A dictionary mapping resource names to
            `SchemaResource` objects defining the relationships, permissions, and
             structure for each resource.
        writer (RelationshipWriter): A writer instance responsible for performing
             operations such as creating or querying relationship records based
             on the schema.

    Methods:
        __init__(schema: Dict): Initializes the `AccessManager` with the provided schema

        create_from_dict(relationship_dict: Dict) -> QuerySet: Creates relationships
            from a dictionary representation and returns a `QuerySet` of created
            relationships.

        create_bulk(relationships: List[RelationTuple]) -> QuerySet: Creates multiple
            relationships in bulk from a list of `RelationTuple` instances and returns a
            `QuerySet` of the created relationships.

        has_permission(
            namespace: str,
            object_id: str,
            userset_namespace: str,
             permission: str,
            subject_id: str) -> bool: Checks if a subject has a specific permission on
                a given object in the specified namespace and userset.

        lookup_subjects(
            namespace: str,
            permission: str,
            userset_namespace: str,
            object_id: str | List[str],
            only_query: bool = False) -> QuerySet | List[str]: Looks up subjects based
                on the provided namespace, permission, userset namespace, and object
                ID(s).
                Can either return a query for the subjects or the resolved subjects,
                depending on the value of `only_query`.

        lookup_resources(
            namespace: str,
            permission: str,
            userset_namespace: str,
            subject: str | List[str], only_query: bool = False
        ) -> QuerySet | List[Resource]: Looks up resources based on the provided
                namespace, permission, userset namespace, and subject(s).
                Can either return a query for the resources or the resolved resources,
                depending on the value of `only_query`.
        lookup_resource_relations
    """

    schema: Dict[str, SchemaResource]
    writer: RelationshipWriter

    def __init__(self, schema: Dict):
        """
        Initializes the AccessManager with a provided schema and sets up the writer for
         relationship operations.

        Args:
            schema (Dict): A dictionary representing the schema that defines how
                            resources are structured and related.
                            The schema will be used to initialize an
                            `AccessControlSchema` instance, which is then
                            used to configure the `AccessManager`.

        Example:
            schema = {
                "user": {},
                "document": {
                    "relations": {
                    "owner": ["user"],
                    "editor": ["user"],
                    "reader": ["user", "group#member"],
                    "parent": ["document"]
                    }
                    "permissions": {
                    "read": ["owner", "editor", "reader", "parent->read"],
                    "write": ["owner", "editor", "parent->editor"]
                    }
                }
            }
            access_manager = AccessManager(schema)
        """
        self.schema = AccessControlSchema.from_dict(schema).schema
        self.writer = RelationshipWriter(self.schema)

    def create_from_dict(self, relationship_dict: Dict) -> QuerySet:
        """
        Creates relationships from a dictionary representation and returns a QuerySet
         of the created relationships.

        This method delegates the actual creation logic to the writer's
         `create_from_dict` method and returns a QuerySet containing the created
          relationship objects.

        Args:
            relationship_dict (Dict): A dictionary containing the data for creating
                                      relationships.
                                      The structure and required fields of this
                                      dictionary depend on the specific
                                      implementation of the `create_from_dict`
                                      method in the writer.

        Returns:
            QuerySet: A QuerySet containing the created relationships.
            The exact contents of the QuerySet depend on the underlying model
            and database operations.

        Example:
            relationship_data = {
                'namespace': 'document',
                'object_id': 'object_123',
                'relation': 'editor',
                'userset_namespace': 'user',
                'userset_subject_id': 'user_456'
            }

            # Create the relationship from the dictionary and get the QuerySet
            created_relationships = create_from_dict(relationship_data)

            # The created_relationships is a QuerySet containing the created
            #  relationship(s).
        """
        return self.writer.create_from_dict(relationship_dict)

    def create_bulk(self, relationships: List[RelationTuple]) -> QuerySet:
        """
        Creates multiple relationships in bulk from a list of `RelationTuple` instances
        and returns a QuerySet of the created relationships.

        This method delegates the bulk creation logic to the writer’s `create_bulk`
        method, which processes the list of `RelationTuple` instances and inserts them
        into the database in a single operation. The method then returns a `QuerySet`
        containing the created relationships.

        Args:
            relationships (List[RelationTuple]): A list of `RelationTuple` instances
                                                 representing the relationships to be
                                                 created.
                                                 Each `RelationTuple` should contain
                                                 the necessary fields and data required
                                                 for creating individual relationship
                                                 records.

        Returns:
            QuerySet: A QuerySet containing the created relationships. The exact
                      contents of the QuerySet depend on the underlying model and
                      database operations. The QuerySet may represent multiple created
                      relationship records.

        Example:
            # Assuming `relation_1` and `relation_2` are valid RelationTuple instances
            bulk_created_relationships = create_bulk([relation_1, relation_2])

            # `bulk_created_relationships` is a QuerySet containing the newly created
            # relationships.
        """
        return self.writer.create_bulk(relationships)

    def has_permission(
        self,
        namespace: str,
        object_id: str,
        userset_namespace: str,
        permission: str,
        subject_id: str,
    ) -> bool:
        """
        Checks if a subject has a specific permission on a given object in the
        specified namespace and userset.

        This method calls the underlying `has_permission` function to perform the check
         and returns the result.

        Args:
            namespace (str): The namespace where the object resides.
            object_id (str): The ID of the object for which the permission is being
            checked.
            userset_namespace (str): The namespace of the userset that is being
            evaluated for permission.
            permission (str): The permission type (e.g., "read", "write", etc.)
            that is being checked.
            subject_id (str): The ID of the subject (e.g., user) whose permission is
            being checked.

        Returns:
            bool: Returns `True` if the subject has the specified permission on the
            object in the given namespace;  otherwise, returns `False`.

        Example:
            # Check if a user has read permission on a document

            has_read_permission = has_permission(
                namespace="document",
                object_id="document_123",
                userset_namespace="user",
                permission="read",
                subject_id="user_456"
            )
            # Returns True or False based on the permission check.
        """
        return has_permission(
            self.schema, namespace, object_id, userset_namespace, permission, subject_id
        )

    def lookup_subjects(
        self,
        namespace: str,
        permission: str,
        userset_namespace: str,
        object_id: str | List[str],
        only_query: bool = False,
    ) -> Optional[QuerySet | list]:
        """
        Looks up subjects based on provided namespace, permission, userset namespace,
        and object ID.
        The function can either return a query for the subjects or the resolved
        subjects, depending on the value of the `only_query` flag.

        Args:
            namespace (str): The namespace of the subject for which permissions are
            being queried.

            permission (str): The permission to be checked for the given subjects.

            userset_namespace (str): The namespace of the userset involved in the
            permission query.

            object_id (str | List[str]): The object ID(s) associated with the
            permission check. This can be a single string representing one object ID
            or a list of object IDs.

            only_query (bool, optional): A flag indicating whether to return just the
             query (`True`) or the actual subjects (`False`). Defaults to `False`,
             which returns the resolved subjects.

        Returns:
            QuerySet | List[Subject] | None:
            - If `only_query` is `True`, returns a query for subjects that can be used
             to fetch the relevant records.
            - If `only_query` is `False`, returns the resolved list of subjects based on
             the provided parameters.
            - Returns `None` if no subjects or query are found.

        Example:

            subjects = lookup_subjects(
                namespace="document",
                permission="read",
                userset_namespace="user",
                object_id="document_123"
            )
            # Returns resolved subjects for the given query parameters.

        """
        rq = LookupSubjectsRequest(
            namespace=namespace,
            permission=permission,
            userset_namespace=userset_namespace,
            target_object=object_id,
        )
        if only_query:
            return fetch_subjects_query(self.schema, rq)
        return fetch_subjects(self.schema, rq)

    def lookup_resources(
        self,
        namespace: str,
        permission: str,
        userset_namespace: str,
        subject: str | List[str],
        only_query: bool = False,
    ) -> Optional[QuerySet | list]:
        """
        Looks up resources based on the provided namespace, permission,
         userset namespace, and subject(s).
        The function can either return a query for the resources or the resolved
        resources, depending on the value of the `only_query` flag.

        Args:
            namespace (str): The namespace of the resources for which permission is
            being checked.
            permission (str): The permission to be checked for the given resources
             (e.g., "read", "write").
            userset_namespace (str): The namespace of the userset that the resources
             belong to.
            subject (str | List[str]): The subject(s) for which the resource permissions
             are being checked.
             This can be a single subject ID (string) or a list of subject IDs.
            only_query (bool, optional): A flag indicating whether to return just
                                         the query (`True`) or
                                         the actual resolved resources (`False`).
                                         Defaults to `False`,
                                        which returns the resolved resources.

        Returns:
            QuerySet | List[Resource] | None:
            - If `only_query` is `True`, returns a query for the resources that can be
                used to fetch the relevant records.
            - If `only_query` is `False`, returns the resolved list of resources based
                on the provided parameters.
            - Returns `None` if no resources or query are found.

        Example:
            # Retrieve resources based on the provided subject

            resources = lookup_resources(
                namespace="document",
                permission="read",
                userset_namespace="user",
                subject="user_123"
            )
            # Returns resolved resources for the given subject.

        """
        rq = LookupResourcesRequest(
            namespace=namespace,
            permission=permission,
            userset_namespace=userset_namespace,
            subject=subject,
        )
        if only_query:
            return fetch_resources_query(self.schema, rq)
        return fetch_resources(self.schema, rq)

    def lookup_resource_relations(
        self,
        namespace: str,
        relation: str,
        userset_namespace: str,
        object_filter: str | List[str],
        userset_relation: Optional[str] = None,
        only_query: bool = False,
    ) -> QuerySet:
        """
        Looks up resource relations for a given namespace and relation, optionally
        returning either the raw query or the values in dictionary form.

        This method wraps the `lookup_object_relation` utility to filter `RelationTuple`
        records matching the provided namespace, relation, userset namespace, and an
        optional userset relation (e.g., “member”). By default, it returns the records'
        values as dictionaries. Setting `only_query` to True returns the underlying
        QuerySet object instead.

        Args:
            namespace (str): The resource namespace to search (e.g., "document").
            relation (str): The specific relation to filter by (e.g., "owner", "editor")
            userset_namespace (str): The namespace of the subject set (e.g., "user").
            object_filter (Union[str, List[str]]): A single object ID or a list of IDs
            used to constrain the lookup.
            userset_relation (Optional[str]): An additional relation within the
            userset namespace (e.g., "member") for further filtering. Defaults to None.
            only_query (bool): If True, returns the raw QuerySet. Otherwise, returns the
                query results as a list of dictionaries. Defaults to False.

        Returns:
            QuerySet | List[dict]: A QuerySet if `only_query` is True; otherwise, a list
             of dictionaries representing the matching relation tuples.
        """
        query = fecth_object_relations(
            namespace, relation, userset_namespace, object_filter, userset_relation
        )
        if only_query:
            return query
        return query.values()
