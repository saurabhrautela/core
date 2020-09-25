"""Permissions to control access to APIs for users."""
from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """For Admins"""

    def has_permission(self, request, view=None):
        """Checks if the user has admin privileges."""
        return "A" in request.user.roles


class IsUser(permissions.BasePermission):
    """For User"""

    def has_permission(self, request, view=None):
        """Checks if the user has user privileges."""
        return "U" in request.user.roles
