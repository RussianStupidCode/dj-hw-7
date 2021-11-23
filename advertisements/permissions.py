from rest_framework.permissions import BasePermission, SAFE_METHODS

from advertisements.models import AdvertisementStatusChoices


class IsOwnerPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.creator == request.user or request.user.is_staff


class IsReadPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Видеть объявление с DRAFT может только owner или admin
        if request.user.is_staff:
            return True

        if obj.status == AdvertisementStatusChoices.DRAFT and request.user == obj.creator:
            return True

        if request.method in SAFE_METHODS and obj.status != AdvertisementStatusChoices.DRAFT:
            return True

        return False