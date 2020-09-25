"""Implementation of APIs for app users."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_condition import And

from users.permissions import IsAdmin
from users import serializers
from users.models import User


def get_permissions(instance):
    """Specifies permission for various methods in the ViewSet."""
    try:
        return [
            permission()
            for permission in instance.permission_classes_by_action[instance.action]
        ]
    except KeyError:
        return [permission() for permission in instance.permission_classes]


class CustomizedTokenObtainPairView(TokenObtainPairView):
    """
    Accepts username and password credentials from user and returns an access and refresh JSON web\
    token pair to prove the authentication of those credentials.
    """

    serializer_class = serializers.CustomizedTokenObtainPairSerializer


class CustomizedTokenRefreshView(TokenRefreshView):
    """
    Takes a refresh type JSON web token and returns an access type JSON web
    token if the refresh token is valid.
    """

    serializer_class = serializers.CustomizedTokenRefreshSerializer


class LogoutView(APIView):
    """View to logout of the application by blacklisting refresh_token.

    Note: Flush blacklisted token daily by using
    `rest_framework_simplejwt.token_blacklist.management.commands.flushexpiredtokens`.
    """

    def post(self, request):
        """Blacklists refresh token. That token cannot be used to
        fetch access_token after this request.
        """
        try:
            token = RefreshToken(request.data.get("refresh"))
        except TokenError as token_error:
            return Response(
                {"errors": token_error.args}, status=status.HTTP_400_BAD_REQUEST
            )

        # handling for case value of `refresh` is `null` in request
        if token.get("user_id"):
            token.blacklist()
            return Response(
                {"message": "Logout successful."}, status=status.HTTP_200_OK
            )

        return Response(
            {"errors": ("Logout failed.",)}, status=status.HTTP_400_BAD_REQUEST
        )


class ChangePassword(APIView):
    """View to allow user to change password."""

    def post(self, request):
        """Changes user password."""
        serializer = serializers.ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            if request.user.check_password(serializer.validated_data.get("password")):
                request.user.set_password(serializer.validated_data.get("new_password"))
                request.user.default_password_flag = False
                request.user.save()
                return Response({"message": "Password changed successfully."})
            return Response(
                {"errors": ("Wrong password.",)}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )


class UserViewSet(viewsets.ModelViewSet):
    """
    create:
    Create a new User.
    * Requires token authentication.
    * Only admin users are able to access this view.

    list:
    Return a list of all existing users.
    * Requires token authentication.
    * Only admin users are able to access this view.

    retrieve:
    Return the details of the given user.
    * Requires token authentication.
    * Only admin users are able to access this view.
    """

    serializer_class = serializers.UserSerializer
    queryset = User.objects.all()

    permission_classes_by_action = {
        "create": [And(IsAuthenticated, IsAdmin)],  # post
        "list": [And(IsAuthenticated, IsAdmin)],  # get
        "retrieve": [And(IsAuthenticated, IsAdmin)],  # get
        "user_activation": [And(IsAuthenticated, IsAdmin)],  # post
        "user_deactivation": [And(IsAuthenticated, IsAdmin)],  # post
    }

    # override `get_permissions` in ViewSet to improve readability of permissions
    get_permissions = get_permissions

    def list(self, request, *args, **kwargs):
        all_users = User.objects.all()
        serializer = serializers.UserSerializer(instance=all_users, many=True)

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        try:
            elem = User.objects.get(username=kwargs.get("pk"))
        except User.DoesNotExist:
            return Response(
                {"error": "No such user exist"}, status=status.HTTP_404_NOT_FOUND
            )
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        result = dict()
        result["id"] = elem.id
        result["username"] = elem.username
        result["state"] = elem.state
        result["roles"] = elem.roles

        return Response(result)

    @action(
        methods=["post"], detail=True, url_path="activate", url_name="user_activation"
    )
    def user_activation(self, request, pk, *args, **kwargs):
        """Activates an user to enable interaction with application."""
        try:
            user = User.objects.get(username=pk)
        except User.DoesNotExist:
            return Response(
                {"error": "No such user exist"}, status=status.HTTP_404_NOT_FOUND
            )
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # activate the user
        if user.state == "D":
            user.state = "A"
            user.save()

            return Response({"message": "User activated."}, status=status.HTTP_200_OK)
        return Response(
            {"error": "Can't activate a user in state other than 'Deactivated'"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        methods=["post"],
        detail=True,
        url_path="deactivate",
        url_name="user_deactivation",
    )
    def user_deactivation(self, request, pk, *args, **kwargs):
        """Deactivates an user to disable interaction with application."""
        try:
            user = User.objects.get(username=pk)
        except User.DoesNotExist:
            return Response(
                {"error": "No such user exist"}, status=status.HTTP_404_NOT_FOUND
            )
        except KeyError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if "A" not in user.roles:
            # deactivate the user
            if user.state == "A":
                user.state = "D"
                user.save()
                return Response(
                    {"message": "User deactivated."}, status=status.HTTP_200_OK
                )
        else:
            # disallow the deactivation of a user with Admin role
            return Response(
                {"error": "Can't deactivate a user with 'Admin' role."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"error": "Can't deactivate a user in state other than 'Activated'"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # unsupported actions
    def partial_update(self, request, *args, **kwargs):
        return Response(
            {"error": "method not supported"}, status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request, *args, **kwargs):
        return Response(
            {"error": "method not supported"}, status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        return Response(
            {"error": "method not supported"}, status=status.HTTP_400_BAD_REQUEST
        )
