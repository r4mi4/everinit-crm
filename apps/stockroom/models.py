from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from apps.common.models import ComprehensiveModel, TrackableModel


class Warehouse(ComprehensiveModel):
    """Model representing a warehouse."""
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sub_warehouse',
        verbose_name=_("Sub Warehouse"),
    )
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Name"))
    location = models.TextField(blank=True, null=True, verbose_name=_("Location"))
    manager = models.ForeignKey(
        'accounts.Entity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_warehouses',
        verbose_name=_("Manager")
    )

    def __str__(self):
        """String representation of the warehouse."""
        return self.name


class WarehousePartner(ComprehensiveModel):
    """Model representing a partner in a warehouse."""
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='warehouse_partners',
        verbose_name=_("Warehouse")
    )
    entity = models.ForeignKey(
        'accounts.Entity',
        on_delete=models.CASCADE,
        related_name='warehouse_partnerships',
        verbose_name=_("Entity")
    )
    share_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("Share Percentage")
    )

    def __str__(self):
        """String representation of the warehouse partner."""
        return _("{person_name} - {warehouse_name}").format(
            person_name=self.entity.name,
            warehouse_name=self.warehouse.name
        )

    class Meta:
        unique_together = ('warehouse', 'entity')
        verbose_name = _("Warehouse Partner")
        verbose_name_plural = _("Warehouse Partners")


class ProductCategory(ComprehensiveModel):
    """Model representing a category of products."""
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories',
        verbose_name=_("Parent Category"),
    )
    name = models.CharField(max_length=200, unique=True, verbose_name=_("Category Name"))
    image = models.ImageField(
        upload_to='category_images/',
        null=True,
        blank=True,
        verbose_name=_("Image")
    )
    category_status = models.BooleanField(
        default=True,
        verbose_name=_("Category Status")
    )
    descriptions = models.TextField(
        verbose_name=_("Category Descriptions"),
        null=True,
        blank=True
    )

    def __str__(self):
        """String representation of the product category."""
        return self.name

    class Meta:
        verbose_name = _("Product Category")
        verbose_name_plural = _("Product Categories")


class Product(ComprehensiveModel):
    """Model representing a product."""
    name = models.CharField(max_length=200, verbose_name=_("Product Name"))
    sku = models.CharField(max_length=100, unique=True, verbose_name=_("SKU"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name=_("Category")
    )
    is_divisible = models.BooleanField(default=True, verbose_name=_("Is Divisible"))

    def __str__(self):
        """String representation of the product."""
        return self.name


class SharedAttributes(ComprehensiveModel):
    """Model representing shared attributes across product attributes."""
    attributes = models.JSONField(verbose_name=_("Shared Attributes"))

    def __str__(self):
        """String representation of the shared attributes."""
        attributes_display = " / ".join([f"{key}: {value}" for key, value in self.attributes.items()])
        return f"Shared Attributes: {attributes_display}"

    class Meta:
        verbose_name = _("Shared Attributes")
        verbose_name_plural = _("Shared Attributes")


class ProductAttributes(ComprehensiveModel):
    """Model for storing product attributes as JSON."""
    shared_attributes = models.ForeignKey(
        SharedAttributes,
        on_delete=models.CASCADE,
        related_name='related_product_attributes',
        verbose_name=_("Shared Attributes")
    )
    attributes = models.JSONField(blank=True, null=True, verbose_name=_("Attributes"))

    def __str__(self):
        """String representation of the attributes."""
        return _("Attributes")


class Inventory(ComprehensiveModel):
    """Model representing the inventory of a product in a warehouse."""
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='warehouse_inventories',
        verbose_name=_("Warehouse")
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_inventories',
        verbose_name=_("Product")
    )
    attributes = models.ForeignKey(
        ProductAttributes,
        on_delete=models.CASCADE,
        related_name='attribute_inventories',
        verbose_name=_("Product Attributes")
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Quantity"))

    class Meta:
        unique_together = ('warehouse', 'product', 'attributes')
        verbose_name = _("Inventory")
        verbose_name_plural = _("Inventories")

    def __str__(self):
        """String representation of the inventory."""
        return _("{product_name} - {quantity}").format(product_name=self.product.name, quantity=self.quantity)

    def clean(self):
        """Custom validation to ensure correct inventory quantity and uniqueness."""
        if not self.product.is_divisible and not self.quantity.is_integer():
            raise ValidationError(_("This product does not support decimal quantities."))

        if Inventory.objects.filter(
                warehouse=self.warehouse,
                product=self.product,
                attributes=self.attributes
        ).exclude(id=self.id).exists():
            raise ValidationError(_("An inventory with these attributes already exists in the warehouse."))


class Stocktaking(TrackableModel):
    """Model representing a stocktaking event in a warehouse."""
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='stocktakings',
        verbose_name=_("Warehouse")
    )
    date = models.DateTimeField(verbose_name=_("Date"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notes"))

    def __str__(self):
        """String representation of the stocktaking event."""
        return _("{warehouse_name} - {date}").format(warehouse_name=self.warehouse.name, date=self.date)


class StocktakingItem(TrackableModel):
    """Model representing an item checked during stocktaking."""
    stocktaking = models.ForeignKey(
        Stocktaking,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_("Stocktaking")
    )
    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        related_name='stocktaking_items',
        verbose_name=_("Inventory")
    )
    recorded_quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Recorded Quantity"))
    counted_quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Counted Quantity"))

    def __str__(self):
        """String representation of the stocktaking item."""
        return _("{product_name} - {counted_quantity}").format(
            product_name=self.inventory.product.name,
            counted_quantity=self.counted_quantity
        )

    def discrepancy(self):
        """Calculate the discrepancy between recorded and counted quantity."""
        return self.counted_quantity - self.recorded_quantity

    class Meta:
        unique_together = ('stocktaking', 'inventory')
        verbose_name = _("Stocktaking Item")
        verbose_name_plural = _("Stocktaking Items")


class InventoryHistory(TrackableModel):
    """Model representing the history of changes in inventory."""
    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name=_("Inventory")
    )
    change_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Change Date"))
    change_type = models.CharField(
        max_length=50,
        choices=(
            ('transfer_out', _("Transfer Out")),
            ('transfer_in', _("Transfer In")),
        ),
        verbose_name=_("Change Type")
    )
    change_quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Change Quantity"))
    related_inventory = models.ForeignKey(
        Inventory,
        on_delete=models.SET_NULL,
        related_name='related_transfers',
        null=True,
        blank=True,
        verbose_name=_("Related Inventory")
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notes"))

    def __str__(self):
        """String representation of the inventory history entry."""
        return _("{inventory} - {change_type}").format(inventory=self.inventory, change_type=self.change_type)

    class Meta:
        verbose_name = _("Inventory History")
        verbose_name_plural = _("Inventory Histories")


