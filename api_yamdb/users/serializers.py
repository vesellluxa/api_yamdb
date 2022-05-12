from rest_framework import serializers
from .models import YamDBUser
from rest_framework.exceptions import ValidationError
from django.db import transaction
from django.db import models


class ConfirmCodeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150, required=True)
    confirmation_code = serializers.CharField(max_length=100, required=True)

    class Meta:
        model = YamDBUser
        fields = (
            'username', 'confirmation_code'
        )


class AdminSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = YamDBUser
        fields = (
            'username', 'email', 'role', 'bio', 'first_name', 'last_name'
        )

    def validate(self, data):
        email = self.initial_data.get('email')
        username = self.initial_data.get('username')
        if YamDBUser.objects.filter(email=email).exists():
            raise ValidationError('email must be unique!')
        if YamDBUser.objects.filter(username=username).exists():
            raise ValidationError('username must be unique!')
        if username == 'me':
            raise ValidationError('this username is already registered')
        return data


class UserSerializer(AdminSerializer):

    @transaction.atomic
    def create(self, validated_data):
        user = self.Meta.model.objects.create_user(**validated_data)
        user.send_confirmation_code()
        return user
