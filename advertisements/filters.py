from django_filters import rest_framework as filters, DateFromToRangeFilter, DateTimeFromToRangeFilter

from advertisements.models import Advertisement


class AdvertisementFilter(filters.FilterSet):
    created_at = DateTimeFromToRangeFilter()
    creator = filters.NumberFilter()

    class Meta:
        model = Advertisement
        fields = ["creator", "title", "created_at"]
