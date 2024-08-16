from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .constants import RESERVED_ROLES

from ..common.models import ComprehensiveModel, TrackableModel


class Role(ComprehensiveModel):
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
        try:
            original_role = Role.objects.get(pk=self.pk)
            if original_role.code != self.code and original_role.code in RESERVED_ROLES:
                raise ValidationError(_("The code '%(code)s' is reserved and cannot be changed.") % {'code': self.code})
        except Role.DoesNotExist:
            # Log an error or handle the unexpected situation
            pass

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


class RoleAssignment(TrackableModel):
    """
    Model to assign roles to entities.
    """
    entity = models.ForeignKey(
        'Entity',
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


class ContactNumber(ComprehensiveModel):
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


class ContactInfo(ComprehensiveModel):
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
        return f"{self.email or 'No Email'} - {self.phone_numbers.first() or 'No Phone'}"


class RelationshipType(ComprehensiveModel):
    """
    Model representing the type of relationship between entities.
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Relationship Type"),
        help_text=_("The type of relationship (e.g., Supplier, Partner).")
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Description"),
        help_text=_("Optional description of the relationship type.")
    )

    class Meta:
        verbose_name = _("Relationship Type")
        verbose_name_plural = _("Relationship Types")
        ordering = ['name']

    def __str__(self):
        return self.name


class EntityRelationship(TrackableModel):
    """
    Model representing a relationship between two entities.
    """
    from_entity = models.ForeignKey(
        'Entity',
        on_delete=models.CASCADE,
        related_name='from_relationships',
        verbose_name=_("From Entity"),
        help_text=_("The entity from which the relationship originates.")
    )
    to_entity = models.ForeignKey(
        'Entity',
        on_delete=models.CASCADE,
        related_name='to_relationships',
        verbose_name=_("To Entity"),
        help_text=_("The entity to which the relationship points.")
    )
    relationship_type = models.ForeignKey(
        'RelationshipType',
        on_delete=models.CASCADE,
        verbose_name=_("Relationship Type"),
        help_text=_("The type of relationship between the entities.")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
        help_text=_("The timestamp when the relationship was created.")
    )

    class Meta:
        verbose_name = _("Entity Relationship")
        verbose_name_plural = _("Entity Relationships")
        unique_together = ('from_entity', 'to_entity', 'relationship_type')

    def __str__(self):
        return f"{self.from_entity.name} -> {self.to_entity.name} ({self.relationship_type.name})"


class Tag(ComprehensiveModel):
    """
    Model representing a tag used to categorize entities.
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Tag Name"),
        help_text=_("Name of the tag.")
    )

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ['name']

    def __str__(self):
        return self.name


class EntityType(ComprehensiveModel):
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


class Entity(ComprehensiveModel):
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
        through='EntityRelationship',
        symmetrical=False,
        related_name='related_to_entities',
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
    tags = models.ManyToManyField(
        'Tag',
        blank=True,
        verbose_name=_("Tags"),
        help_text=_("Tags associated with the entity for better classification.")
    )

    class Meta:
        verbose_name = _("Entity")
        verbose_name_plural = _("Entities")

    def __str__(self):
        return self.name


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

