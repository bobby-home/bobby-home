from rest_framework import permissions
from .models import APIKey


class HasAPIAccess(permissions.BasePermission):
    message = 'Invalid or missing API Key.'

    def has_permission(self, request, view):
        api_key = request.META.get('API_KEY', '')
        return APIKey.objects.filter(key=api_key).exists()
