from rest_framework.authtoken.admin import User
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet

from advertisements.filters import AdvertisementFilter
from advertisements.models import Advertisement, FavoriteAdvertisement, AdvertisementStatusChoices
from advertisements.permissions import IsOwnerPermission, IsReadPermission
from advertisements.serializers import AdvertisementSerializer, FavoritesSerializer
from django_filters import rest_framework as filters


class AdvertisementViewSet(ModelViewSet):
    """ViewSet для объявлений."""

    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = AdvertisementFilter

    @action(
        detail=False,
        methods=["get", "post"], #  для теста хватит 2-х
        name="Get favorites Advertisement",
        url_path='favorites',
        url_name="favorites",
    )
    def favorites(self, request):
        """Метод для добавления и получения избранных статей"""

        if request.method == "GET":
            favorites = Advertisement.objects.filter(users__id__in=[request.user.id])
            serializer = AdvertisementSerializer(favorites, many=True)
            return Response(serializer.data, status=HTTP_200_OK)

        if request.method == "POST":

            serializer = FavoritesSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            if serializer.validated_data['advertisement'].creator == request.user:
                return Response("user can't add favorite her advertisement", status=HTTP_400_BAD_REQUEST)

            user = User.objects.get(id=request.user.id)
            serializer.validated_data['advertisement'].users.add(user)

            return Response('OK', status=HTTP_200_OK)

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action in ["create", "favorites"]:
            return [IsAuthenticated()]
        if self.action in ["update", "partial_update", "delete"]:
            return [IsOwnerPermission()]
        return [IsReadPermission()]

    def list(self, request, *args, **kwargs):
        """
            Изменяется из-за DRAFT, чтобы в общей выдаче списка вообще не было черновиков
            Черновики можно смотреть только владельцу напрямую через id объявления
        """
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.exclude(status=AdvertisementStatusChoices.DRAFT)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

