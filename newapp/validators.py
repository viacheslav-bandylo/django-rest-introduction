from rest_framework import serializers


def validate_title_length(value):
    if len(value) < 10:
        raise serializers.ValidationError("Title must be at least 10 characters long.")
