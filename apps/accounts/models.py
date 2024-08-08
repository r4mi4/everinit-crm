from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .constants import RESERVED_ROLES
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from ..common.models import AuditModel


class Role(models.Model):
    """
    Model representing a user role in the system.
    """
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Role Code"),
        help_text=_("Unique code for the role.")
    )
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Role Name"),
        help_text=_("Unique name for the role.")
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Description"),
        help_text=_("Optional description for the role.")
    )

    def __str__(self):
        return self.name

    def clean(self):
        """
        Ensure that reserved role codes are not used.
        Raises:
            ValidationError: If the role code is reserved.
        """
        if self.is_reserved():
            raise ValidationError(
                _("The code '%(code)s' is reserved and cannot be used.") % {'code': self.code}
            )

    def save(self, *args, **kwargs):
        """
        Save the role instance to the database, ensuring reserved codes are not changed.
        Raises:
            ValidationError: If an attempt is made to change a reserved role's code.
        """

        self._check_reserved_code_change()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Delete the role instance, ensuring reserved roles are not deleted.
        Raises:
            ValidationError: If an attempt is made to delete a reserved role.
        """
        self._check_reserved_deletion()
        super().delete(*args, **kwargs)

    def is_reserved(self):
        """
        Check if the role's code is reserved.
        Returns:
            bool: True if the role's code is reserved, False otherwise.
        """
        return self.code in RESERVED_ROLES

    def _check_reserved_code_change(self):
        """
        Check if a reserved role's code is being changed.
        Raises:
            ValidationError: If a reserved role's code is being changed.
        """
        if self.pk:  # If the role already exists
            original_code = Role.objects.values_list('code', flat=True).get(pk=self.pk)
            if original_code != self.code and original_code in RESERVED_ROLES:
                raise ValidationError(
                    _("The code '%(code)s' is reserved and cannot be changed.") % {'code': self.code}
                )

    def _check_reserved_deletion(self):
        """
        Check if a reserved role is being deleted.
        Raises:
            ValidationError: If a reserved role is being deleted.
        """
        if self.is_reserved():
            raise ValidationError(
                _("The role with code '%(code)s' is reserved and cannot be deleted.") % {'code': self.code}
            )


class ContactNumber(models.Model):
    """
    Model to store phone numbers associated with a contact.
    """
    phone = models.CharField(
        max_length=15,
        verbose_name=_("Phone"),
        help_text=_("Phone number of the contact.")
    )

    class Meta:
        verbose_name = _("Phone Number")
        verbose_name_plural = _("Phone Numbers")

    def __str__(self):
        return self.phone


class ContactInfo(models.Model):
    """
    Model to store contact information of an Entity.
    """
    email = models.EmailField(
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("Email"),
        help_text=_("Email address of the contact.")
    )
    picture = models.ImageField(
        upload_to='contact_pictures/',
        blank=True,
        null=True,
        verbose_name=_("Profile Picture"),
        help_text=_("Profile picture of the contact.")
    )
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Address"),
        help_text=_("Address of the contact.")
    )
    phone_numbers = models.ManyToManyField(
        ContactNumber,
        related_name='contact_infos',
        blank=True,
        verbose_name=_("Phone Numbers"),
        help_text=_("Phone numbers associated with the contact.")
    )

    class Meta:
        verbose_name = _("Contact Info")
        verbose_name_plural = _("Contact Infos")

    def __str__(self):
        return f"{self.email or 'No Email'} - {self.phone_numbers.first() or'No Phone'}"


class EntityType(models.Model):
    """
    Model to store the type of entity (e.g., Person, Company).

    Attributes:
        name (str): The name of the entity type.
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Entity Type"),
        help_text=_("The type of the entity (e.g., Person, Company).")
    )

    class Meta:
        verbose_name = _("Entity Type")
        verbose_name_plural = _("Entity Types")

    def __str__(self):
        return self.name


class EntityUsageLog(models.Model):
    """
    Model to log usage and activities of entities.
    """
    user = models.ForeignKey(
        'CustomUser',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("User"),
        help_text=_("User who performed the action.")
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_("Content Type"),
        help_text=_("The type of the content object.")
    )
    object_id = models.PositiveIntegerField(
        verbose_name=_("Object ID"),
        help_text=_("ID of the related object.")
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    action = models.CharField(
        max_length=255,
        verbose_name=_("Action"),
        help_text=_("Description of the action performed.")
    )
    timestamp = models.DateTimeField(
        verbose_name=_("Timestamp"),
        help_text=_("The time when the action was performed.")
    )
    entity = models.ForeignKey(
        'Entity',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Entity"),
        help_text=_("The entity related to the action.")
    )
    context = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Context"),
        help_text=_("Additional context for the action.")
    )

    class Meta:
        verbose_name = _("Entity Usage Log")
        verbose_name_plural = _("Entity Usage Logs")
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.content_type.app_label}.{self.content_type.model} {self.object_id} - {self.action} at {self.timestamp}"


class Entity(AuditModel):
    """
    Base model to store information about an entity (e.g., Person, Company).
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_("Name"),
        help_text=_("The name of the entity.")
    )
    entity_type = models.ForeignKey(
        EntityType,
        on_delete=models.CASCADE,
        verbose_name=_("Entity Type"),
        help_text=_("The type of the entity.")
    )
    contact_info = models.OneToOneField(
        ContactInfo,
        on_delete=models.CASCADE,
        verbose_name=_("Contact Info"),
        help_text=_("Contact information for the entity.")
    )
    additional_info = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_("Additional Info"),
        help_text=_("Additional information about the entity.")
    )
    related_entities = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        verbose_name=_("Related Entities"),
        help_text=_("Entities related to this entity.")
    )
    date_joined = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("Date Joined"),
        help_text=_("The date the entity joined.")
    )
    roles = models.ManyToManyField(
        Role,
        through='RoleAssignment',
        verbose_name=_("Roles"),
        help_text=_("Roles assigned to the entity.")
    )

    class Meta:
        verbose_name = _("Entity")
        verbose_name_plural = _("Entities")

    def __str__(self):
        return self.name


class RoleAssignment(models.Model):
    """
    Model to assign roles to entities.
    """
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        verbose_name=_("Entity"),
        help_text=_("The entity to which the role is assigned.")
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        verbose_name=_("Role"),
        help_text=_("The role assigned to the entity.")
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Assigned At"),
        help_text=_("The date and time when the role was assigned.")
    )

    def __str__(self):
        return f"{self.entity.name} has role {self.role.name}"


class CustomUser(AbstractUser):
    """
    Custom user model to include an entity relationship.
    """
    entity = models.ForeignKey(
        Entity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Entity"),
        help_text=_("The entity associated with this user.")
    )

    def __str__(self):
        return f"{self.username} ({self.email})"
