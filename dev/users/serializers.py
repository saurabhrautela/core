"""Serializers to control input and output of APIs."""
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from users import models
from users import validators


class UserSerializer(serializers.ModelSerializer):
    """Serializer for `User` model."""

    password = serializers.CharField(
        required=True, style={"input_type": "password"}, write_only=True
    )
    roles = serializers.CharField(max_length=2, validators=[validators.roles])

    class Meta:
        model = get_user_model()
        fields = ["id", "username", "password", "email", "roles", "state"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        """Creates a user and adds it to the database."""
        user = models.User(
            username=validated_data["username"],
            email=validated_data["email"],
            roles=validated_data["roles"],
        )
        if len(validated_data["password"]) > settings.MAX_PASSWORD_LENGTH:
            truncated_password = validated_data["password"][
                : settings.MAX_PASSWORD_LENGTH
            ]
        else:
            truncated_password = validated_data["password"]

        user.set_password(truncated_password)
        user.save()

        return user

    def update(self, instance, validated_data):
        """Method not needed."""
        raise NotSupportedException


class CustomizedTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Modified serializer for obtaining JWT tokens to add validation for user state."""

    @classmethod
    def get_token(cls, user):
        # check if user is in active state to login
        if not user.state == "A":
            raise PermissionDenied(
                detail="Your account is deactivated. Contact support."
            )
        if not user.default_password_flag:
            raise PermissionDenied(detail="Please change your password.")

        token = super(CustomizedTokenObtainPairSerializer, cls).get_token(user)

        token["username"] = user.username
        token["roles"] = user.roles

        return token

    def create(self, validated_data):
        """Method not needed."""
        raise NotImplemented

    def update(self, instance, validated_data):
        """Method not needed."""
        raise NotImplemented


class CustomizedTokenRefreshSerializer(TokenRefreshSerializer):
    """Modified serializer for using refresh token to add validation for user state."""

    def validate(self, attrs):
        refresh = RefreshToken(attrs["refresh"])

        user_model = get_user_model()

        if not user_model.objects.get(id=refresh.get("user_id")).state == "A":
            raise PermissionDenied(
                detail="Your account is deactivated. Contact support."
            )

        data = {"access": str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    # Attempt to blacklist the given refresh token
                    refresh.blacklist()
                except AttributeError:
                    # If blacklist app not installed, `blacklist` method will
                    # not be present
                    pass

            refresh.set_jti()
            refresh.set_exp()

            data["refresh"] = str(refresh)

        return data

    def create(self, validated_data):
        """Method not needed."""
        raise NotImplemented

    def update(self, instance, validated_data):
        """Method not needed."""
        raise NotImplemented


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for ChangePasswordView."""

    password = serializers.CharField(
        required=True,
        style={"input_type": "password"},
        write_only=True,
        min_length=settings.MIN_PASSWORD_LENGTH,
    )
    new_password = serializers.CharField(
        required=True,
        style={"input_type": "password"},
        write_only=True,
        min_length=settings.MIN_PASSWORD_LENGTH,
    )

    class Meta:
        model = get_user_model()
        fields = ["password", "new_password"]

    def create(self, validated_data):
        """Method not needed."""
        raise NotImplemented

    def update(self, instance, validated_data):
        """Method not needed."""
        raise NotImplemented
