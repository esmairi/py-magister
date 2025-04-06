from django.core.management.base import BaseCommand, CommandError

from py_magister.management.commands.helper import parse_perm_string, get_access_manager


class Command(BaseCommand):
    help = (
        "Check permission using a single argument like"
        " 'document:doc1#reader@user:user1'"
    )

    def add_arguments(self, parser):
        """Define command arguments (optional)."""
        parser.add_argument("--schema", type=str, help="Schema json path")
        parser.add_argument(
            "perm_string",
            type=str,
            help=(
                "Combined string in format"
                " 'namespace:object_id#relation@subject_namespace:subject_id'"
            ),
        )

    def handle(self, *args, **options):
        """Logic for the command execution."""
        schema_path = options.get("schema")
        perm_string = options.get("perm_string")

        try:
            (
                namespace,
                object_id,
                permission,
                subject_ns,
                subject_id,
                _,
            ) = parse_perm_string(perm_string)
        except ValueError as e:
            raise CommandError(f"Invalid format: {e}")
        self.stdout.write(f"Namespace: {namespace}")
        self.stdout.write(f"Object ID: {object_id}")
        self.stdout.write(f"Permission: {permission}")
        self.stdout.write(f"Subject NS: {subject_ns}")
        self.stdout.write(f"Subject ID: {subject_id}")
        manager = get_access_manager(schema_path)
        has_perm = manager.has_permission(
            namespace, object_id, subject_ns, permission, subject_id
        )
        if has_perm:
            self.stdout.write(
                self.style.SUCCESS(
                    f"[PASS] Subject '{subject_id}' HAS '{permission}' permission on"
                    f" '{object_id}' (namespace '{namespace}')"
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"[FAIL] Subject '{subject_id}' does NOT have '{permission}'"
                    f" permission on '{object_id}' (namespace '{namespace}')"
                )
            )
