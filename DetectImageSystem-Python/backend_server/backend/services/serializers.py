from abc import ABC

from django.contrib.auth.models import User, Group
from rest_framework import serializers


class PredictImageSerializer(serializers.Serializer, ABC):
    url = serializers.CharField(max_length=500)
    label = serializers.CharField(max_length=5, default='')

    def validate(self, data):
        # other wise you can set default value of age here,
        if data.get('label', None) is None:   # true only when age = serializer.IntergerField(required=False)
            data['label'] = ''
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


# Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'])
        return user
