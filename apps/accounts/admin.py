from django.contrib import admin
from .models import (
    Entity,
    Role,
    RoleAssignment,
    ContactInfo,
    ContactNumber,
    EntityType,
    CustomUser,
    Tag,
    EntityRelationship
)
from reversion.admin import VersionAdmin


@admin.register(Entity)
class EntityAdmin(VersionAdmin):
    """Admin interface for managing Entity records."""
    list_display = ('name', 'entity_type', 'date_joined')
    search_fields = ('name', 'entity_type__name')
    list_filter = ('entity_type', 'date_joined')
    filter_horizontal = ('roles', 'related_entities',)
    raw_id_fields = ('contact_info',)
    autocomplete_fields = ('entity_type', 'roles', 'related_entities')


@admin.register(Role)
class RoleAdmin(VersionAdmin):
    """Admin interface for managing Role records."""
    list_display = ('code', 'name', 'description')
    search_fields = ('code', 'name')


@admin.register(RoleAssignment)
class RoleAssignmentAdmin(VersionAdmin):
    """Admin interface for managing RoleAssignment records."""
    list_display = ('entity', 'role', 'assigned_at')
    list_filter = ('role', 'entity')
    search_fields = ('entity__name', 'role__name')
    autocomplete_fields = ('entity', 'role')
    readonly_fields = ('assigned_at',)


@admin.register(ContactInfo)
class ContactInfoAdmin(VersionAdmin):
    """Admin interface for managing ContactInfo records."""
    list_display = ('email', 'address')
    search_fields = ('email', 'phone_numbers__phone')
    filter_horizontal = ('phone_numbers',)


@admin.register(ContactNumber)
class ContactNumberAdmin(VersionAdmin):
    """Admin interface for managing ContactNumber records."""
    list_display = ('phone',)
    search_fields = ('phone',)


@admin.register(EntityType)
class EntityTypeAdmin(VersionAdmin):
    """Admin interface for managing EntityType records."""
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """Admin interface for managing CustomUser records."""
    list_display = ('username', 'email', 'entity')
    search_fields = ('username', 'email')
    list_filter = ('entity',)
    autocomplete_fields = ('entity',)


@admin.register(Tag)
class TagAdmin(VersionAdmin):
    """Admin interface for managing Tag records."""
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(EntityRelationship)
class EntityRelationshipAdmin(admin.ModelAdmin):
    """Admin interface for managing EntityRelationship records."""
    list_display = ('from_entity', 'to_entity', 'relationship_type')
    search_fields = ('from_entity__name', 'to_entity__name', 'relationship_type')
    autocomplete_fields = ('from_entity', 'to_entity')
    list_filter = ('relationship_type',)
