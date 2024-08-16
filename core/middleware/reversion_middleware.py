import reversion
from django.utils.deprecation import MiddlewareMixin


class ReversionMiddleware(MiddlewareMixin):
    """
    Middleware to automatically create a revision for any POST, PUT, or DELETE request.
    This ensures that changes made to the database are tracked by django-reversion.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Wraps view execution in a reversion revision for POST, PUT, DELETE requests.
        Sets the current user as the author of the revision.
        """
        if request.method in ['POST', 'PUT', 'DELETE']:
            with reversion.create_revision():
                reversion.set_user(request.user)  # Assigns the current user to the revision
                response = view_func(request, *view_args, **view_kwargs)  # Execute the view
                return response
        else:
            return view_func(request, *view_args, **view_kwargs)

    def process_response(self, request, response):
        """
        Passes the response through without modification.
        Required by MiddlewareMixin but does not alter the response.
        """
        return response
