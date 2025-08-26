from rest_framework import serializers

from user.models import ExpendUser


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = ExpendUser
        fields = '__all__'
