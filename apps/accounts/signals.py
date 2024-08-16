from core.logging_config import logger
from .models import Role
from .constants import RESERVED_ROLES
from django.db.models.signals import pre_delete, post_migrate
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.apps import apps


@receiver(pre_delete, sender=Role)
def prevent_deletion_of_reserved_role(sender, instance, **kwargs):
    """
    Signal to prevent deletion of reserved roles.
    Raises:
        ValidationError: If a reserved role is being deleted.
    """
    if instance.is_reserved():
        raise ValidationError(
            _("The role with code '%(code)s' is reserved and cannot be deleted.") % {'code': instance.code}
        )


@receiver(post_migrate)
def ensure_roles_exist(sender, **kwargs):
    """
    Ensure that reserved roles are created in the database after migrations.
    Runs only for apps that have the 'manage_reserved_roles' attribute set to True in their AppConfig.
    """
    app_config = apps.get_app_config(sender.label)

    # Check if the app_config has the custom attribute 'manage_reserved_roles'
    if getattr(app_config, 'manage_reserved_roles', False):
        logger.info(f"Running post_migrate for {sender.label}: Managing reserved roles.")
        for role_code, role_name in RESERVED_ROLES.items():
            role, created = Role.objects.get_or_create(
                code=role_code,
                defaults={'name': role_name}
            )
            if created:
                logger.info(f"Created new role: {role_code}")
