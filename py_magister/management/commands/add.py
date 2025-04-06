from django.core.management.base import BaseCommand

from py_magister.management.commands.helper import parse_perm_string, get_access_manager
from py_magister.models import RelationTuple


class Command(BaseCommand):
    help = "Add one or more relations to the RelationTuple model."

    def add_arguments(self, parser):
        """
        Define how the user provides new relations.
        You can do it in multiple ways:
         1) Single or multiple arguments like
         "namespace:object_id#relation@userset_namespace:subject_id"
         2) A file path to read a bulk list from
         3) JSON or CSV data, etc.
        """
        parser.add_argument("--schema", type=str, help="Schema json path")
        parser.add_argument(
            "relation",
            type=str,
            help=(
                "One or more relation specifications (e.g.,"
                " 'document:doc1#reader@user:user42')."
            ),
        )
        # Alternatively, you could use a --file argument to load from a file.

    def handle(self, *args, **options):
        schema_path = options.get("schema")
        relation = options.get("relation")
        try:
            ns, obj_id, rel, userset_ns, subject_id, userset_rel = parse_perm_string(
                relation
            )
            #  Create a new RelationTuple record
            relation_tuple = RelationTuple(
                namespace=ns,
                object_id=obj_id,
                relation=rel,
                userset_namespace=userset_ns,
                userset_subject_id=subject_id,
                userset_relation=userset_rel,
            )
            manager = get_access_manager(schema_path)
            manager.create_bulk([relation_tuple])
            self.stdout.write(self.style.SUCCESS("[SUCCESS] created new relation"))

        except ValueError as e:
            self.stderr.write(
                self.style.ERROR(f"Skipping invalid relation '{relation}': {e}")
            )
