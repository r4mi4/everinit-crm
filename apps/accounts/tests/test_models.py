from django.core.exceptions import ValidationError
from django.test import TestCase
from unittest.mock import patch
from apps.accounts.models import Role
from apps.accounts.constants import RESERVED_ROLES
from django.core.management import call_command


@patch.dict('apps.accounts.constants.RESERVED_ROLES', {'test_code': 'Test Role'})
class RoleModelTest(TestCase):
    """
    Test suite for the Role model.
    """

    def setUp(self):
        """
        Create a role instance for testing.
        """
        self.reserved_role_code = 'test_code'
        self.reserved_role_name = 'Test Role'
        # Create a role with reserved code
        self.existing_role = Role.objects.create(
            code=self.reserved_role_code,
            name=self.reserved_role_name
        )

    def test_create_role(self):
        """
        Test the creation of a role.
        """
        self.assertEqual(self.existing_role.code, self.reserved_role_code)
        self.assertEqual(self.existing_role.name, self.reserved_role_name)

    def test_reserved_role_creation(self):
        """
        Test that reserved roles are not allowed to be created.
        """
        # Trying to create a role with a reserved code that already exists
        new_role = Role(code=self.reserved_role_code, name='Another Test Role')
        with self.assertRaises(ValidationError):
            new_role.clean()  # Ensure the custom validation logic runs
            new_role.save()

    def test_change_reserved_role_code(self):
        """
        Test that reserved role codes cannot be changed.
        """
        self.existing_role.code = 'changed_code'
        with self.assertRaises(ValidationError):
            self.existing_role.save()

    def test_reserved_role_deletion(self):
        """
        Test that reserved roles cannot be deleted.
        """
        with self.assertRaises(ValidationError):
            self.existing_role.delete()

    def test_non_reserved_role_creation(self):
        """
        Test that non-reserved roles can be created.
        """
        role = Role.objects.create(code='non_reserved_code', name='Non Reserved Role')
        self.assertEqual(role.code, 'non_reserved_code')
        self.assertEqual(role.name, 'Non Reserved Role')

    def test_non_reserved_role_deletion(self):
        """
        Test that non-reserved roles can be deleted.
        """
        role = Role.objects.create(code='non_reserved_code', name='Non Reserved Role')
        role_id = role.id
        role.delete()
        with self.assertRaises(Role.DoesNotExist):
            Role.objects.get(id=role_id)

    def test_ensure_roles_exist_signal(self):
        """
        Test the ensure_roles_exist signal to create reserved roles.
        """
        call_command('migrate', 'accounts', verbosity=0)  # Simulate the migration command
        for role_code, role_name in RESERVED_ROLES.items():
            role = Role.objects.get(code=role_code)
            self.assertEqual(role.code, role_code)
            self.assertEqual(role.name, role_name)
