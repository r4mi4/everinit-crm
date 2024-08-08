from django.utils.translation import gettext_lazy as _

ROLE_WAREHOUSE_MANAGER = 'ROLE_WAREHOUSE_MANAGER'
ROLE_SELLER = 'ROLE_SELLER'
ROLE_CUSTOMER = 'ROLE_CUSTOMER'

# Define reserved role codes
RESERVED_ROLES = {
    ROLE_WAREHOUSE_MANAGER: _("Warehouse Manager"),
    ROLE_SELLER: _("Seller"),
    ROLE_CUSTOMER: _("Customer"),
    # Add other reserved roles here
}


