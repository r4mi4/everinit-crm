from django.db import models
from django.utils.translation import gettext_lazy as _


class AuditModel(models.Model):
    """
    Abstract base class for models with created and updated timestamps.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        abstract = True
