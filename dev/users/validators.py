"""Validators for API data."""
from rest_framework import serializers


def roles(value):
    """Validate if the role input by the user are correct."""

    role_types = (("A", "Admin"), ("U", "User"))

    for character in value:
        if character not in [role[0] for role in role_types]:
            raise serializers.ValidationError(
                "{} is not a valid role.".format(character)
            )
