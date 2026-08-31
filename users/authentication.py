from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class TokenVersionJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user = super().get_user(validated_token)

        token_version = validated_token.get('token_version')
        if user.token_version and token_version != user.token_version:
            raise InvalidToken('Token is no longer valid, password was changed')
        return user
