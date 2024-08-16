from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid
from django.db import transaction


class BaseUUIDModel(models.Model):
    """Abstract base model providing a UUID as the primary key."""
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_("UUID"))

    class Meta:
        abstract = True


class AuditModel(BaseUUIDModel):
    """Provides automatic timestamps for model creation and updates."""
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        abstract = True


class ActiveStatusModel(BaseUUIDModel):
    """Tracks whether an object is active or not."""
    is_active = models.BooleanField(default=True, verbose_name=_("Active Status"))

    class Meta:
        abstract = True


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(delete_at__isnull=True)


class SoftDeleteModel(BaseUUIDModel):
    """Implements soft deletion functionality."""
    deleted = models.DateTimeField(blank=True, null=True, default=None, verbose_name=_("Deleted At"), editable=False)
    active_objects = SoftDeleteManager()  # Default manager
    objects = models.Manager()  # Access to all objects, including logically deleted ones

    def mark_deleted(self, user=None):
        if not self.deleted:
            self.deleted = timezone.now()
            self.save()

    def restore(self, user=None):
        if self.deleted:
            self.deleted = None
            self.save()

    @transaction.atomic
    def permanently_delete(self, user=None):
        super().delete()

    def delete(self, using=None, keep_parents=False, hard=False):
        if hard:
            self.permanently_delete()
        else:
            self.mark_deleted()

    class Meta:
        abstract = True


class ComprehensiveModel(AuditModel, ActiveStatusModel, SoftDeleteModel):
    """Combines audit, active status, and soft delete functionalities."""

    class Meta:
        abstract = True


class TrackableModel(AuditModel, SoftDeleteModel):
    """Combines audit and soft delete functionalities."""

    class Meta:
        abstract = True
