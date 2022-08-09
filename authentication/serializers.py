import email
from rest_framework import serializers
from .models import User
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import (
    smart_str,
    force_str,
    smart_bytes,
    DjangoUnicodeDecodeError,
)
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import Util


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ["email", "username", "password"]

    def validate(self, attrs):
        email = attrs.get("email", "")
        username = attrs.get("username", "")

        if not username.isalnum():
            raise serializers.ValidationError(
                "The username should only contain alphanumeric characters"
            )
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ["token"]


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=6)
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    username = serializers.CharField(max_length=40, min_length=2, read_only=True)
    tokens = serializers.CharField(max_length=555, read_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "username", "tokens"]

    def validate(self, attrs):
        email = attrs.get("email", "")
        password = attrs.get("password", "")

        user = auth.authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed("Invalid credentials, Try again")

        if not user.is_active:
            raise AuthenticationFailed("Account disabled, contact admin")

        if not user.is_verified:
            raise AuthenticationFailed("Email is not verified")

        return {"email": user.email, "username": user.username, "tokens": user.tokens()}
        return super().validate(attrs)


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=5)

    class Meta:
        fields = ["email"]

    def validate(self, attrs):
        email = attrs["data"].get("email", "")
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uid64 = urlsafe_base64_encode(user.id)
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request=attrs["data"].get("request")).domain
            relativeLink = reverse(
                "password-reset-confirm", kwargs={"uid64": uid64, "token": token}
            )
            absurl = "http://" + current_site + relativeLink
            email_body = (
                "Hello "
                + user.username
                + ", Use link below to reset your password \n"
                + absurl
            )
            data = {
                "email_body": email_body,
                "email_subject": "Reset your password",
                "to_email": user.email,
            }

            Util.send_email(data)

        return super().validate(attrs)
