from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from users.models import User
from rest_framework import serializers

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = [
            'id',
            'email',
            'password',
            'first_name',
            'last_name',
            'address',
            'phone_number'
        ]


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = User
        ref_name = 'CustomUser'
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'address',
            'phone_number',
            'balance',
            'role'
        ]
        read_only_fields = ['balance', 'role']


class UserRoleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'role']
        read_only_fields = ['id', 'email']