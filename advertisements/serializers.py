from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from advertisements.models import Advertisement, AdvertisementStatusChoices, FavoriteAdvertisement


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class FavoritesSerializer(serializers.ModelSerializer):
    """Сериализатор для m2m таблицы избранных статей"""

    user = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = FavoriteAdvertisement
        fields = "__all__"

    def create(self, validated_data):
        """Метод для создания"""

        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""

    creator = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'description', 'creator',
                  'status', 'created_at', )

    def create(self, validated_data):
        """Метод для создания"""

        # Простановка значения поля создатель по-умолчанию.
        # Текущий пользователь является создателем объявления
        # изменить или переопределить его через API нельзя.
        # обратите внимание на `context` – он выставляется автоматически
        # через методы ViewSet.
        # само поле при этом объявляется как `read_only=True`
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""

        open_count = self.Meta.model.objects.filter(creator=self.context["request"].user,
                                                    status=AdvertisementStatusChoices.OPEN).count()
        if open_count > 9 and self.context["request"].method == 'POST':
            raise ValidationError("Count open advertisement > 10")

        return data
