from django.utils.deprecation import MiddlewareMixin
from threading import local

from core.logging_config import logger

_user = local()


class UserTrackingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Save IP and device info to the request
        request.ip_address = self.get_client_ip(request)
        request.device_info = self.get_device_info(request)
        # Log the IP and device info
        logger.info(f"IP Address: {request.ip_address} - Device Info: {request.device_info}")
        # Store the user in thread-local storage
        _user.value = request.user

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_device_info(self, request):
        return request.META.get('HTTP_USER_AGENT', '')


def get_current_user():
    return getattr(_user, 'value', None)
