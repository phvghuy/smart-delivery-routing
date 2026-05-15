from smart_delivery_routing.application.services import AuthService, AuthToken
from smart_delivery_routing.infrastructure.supabase.repositories.auth import sign_in, sign_out


class SupabaseAuthService(AuthService):
    def sign_in(self, email: str, password: str) -> AuthToken:
        result = sign_in(email, password)
        role = result.user.app_metadata.get("role", "")
        return AuthToken(access_token=result.session.access_token, role=role)

    def sign_out(self, token: str) -> None:
        sign_out(token)
