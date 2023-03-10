from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from rest_framework import permissions


def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(u):
        if u.is_authenticated:
            if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
                return True
        return False

    return user_passes_test(in_groups)


class CustomPermissions(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method == 'GET' and request.user.groups.filter(name__in=['CRU', 'R', 'CR', 'CRUD']).exists():
            return True

        elif request.method == 'POST' and request.user.groups.filter(name__in=['CRU', 'CR',
                                                                               'CRUD']).exists():
            return True
        elif request.method == 'PUT' and request.user.groups.filter(name__in=['CRU',
                                                                              'CRUD']).exists():
            return True
        elif request.method == 'DELETE' and request.user.groups.filter(name='CRUD').exists():
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        elif request.method == 'GET' and request.user.groups.filter(name__in=['CRU', 'R', 'CR', 'CRUD']).exists():
            return True
        elif request.method == 'POST' and request.user.groups.filter(name__in=['CRU', 'CR', 'CRUD']).exists():
            return True
        elif request.method == 'PUT' and request.user.groups.filter(name__in=['CRU', 'CRUD']).exists():
            return True
        elif request.method == 'DELETE' and request.user.groups.filter(name='CRUD').exists():
            return True
        else:
            return False

