from django.core.exceptions import ImproperlyConfigured
import os


def get_env_variable(var_name, default_value=None, required=True):
    """
    Get the environment variable or return exception.

    Args:
        var_name (str): Name of the environment variable
        default_value (any): Default value if variable is not set
        required (bool): Whether the variable is required

    Returns:
        str: Value of the environment variable

    Raises:
        ImproperlyConfigured: If the variable is required but not set
    """
    value = os.getenv(var_name)
    if value is None:
        if required:
            raise ImproperlyConfigured(f"Set the {var_name} environment variable")
        return default_value
    return value
