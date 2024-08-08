from django.contrib import admin
from .models import (
    Entity,
    Role,
    RoleAssignment,
    ContactInfo,
    ContactNumber,
    EntityType,
    EntityUsageLog,
    CustomUser,
)


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    """Admin interface for managing Entity records."""
    list_display = ('name', 'entity_type', 'date_joined')
    search_fields = ('name', 'entity_type__name')
    list_filter = ('entity_type', 'date_joined')
    filter_horizontal = ('roles', 'related_entities',)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin interface for managing Role records."""
    list_display = ('code', 'name', 'description')


@admin.register(RoleAssignment)
class RoleAssignmentAdmin(admin.ModelAdmin):
    """Admin interface for managing RoleAssignment records."""
    list_display = ('entity', 'role', 'assigned_at')
    list_filter = ('role', 'entity')
    search_fields = ('entity__name', 'role__name')


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    """Admin interface for managing ContactInfo records."""
    list_display = ('email', 'address')
    search_fields = ('email', 'phone_numbers__phone')


@admin.register(ContactNumber)
class ContactNumberAdmin(admin.ModelAdmin):
    """Admin interface for managing ContactNumber records."""
    list_display = ('phone',)


@admin.register(EntityType)
class EntityTypeAdmin(admin.ModelAdmin):
    """Admin interface for managing EntityType records."""
    list_display = ('name',)


@admin.register(EntityUsageLog)
class EntityUsageLogAdmin(admin.ModelAdmin):
    """Admin interface for managing EntityUsageLog records."""
    list_display = ('user', 'content_type', 'object_id', 'action', 'timestamp', 'entity')
    list_filter = ('content_type', 'user', 'entity')
    search_fields = ('action', 'entity__name')


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """Admin interface for managing CustomUser records."""
    list_display = ('username', 'email', 'entity')
    search_fields = ('username', 'email')
    list_filter = ('entity',)
