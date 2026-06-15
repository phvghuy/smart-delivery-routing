from supabase import Client
from ecom_logistics.auth.application.services import AuthService, AuthToken


class SupabaseAuthService(AuthService):
    def __init__(self, client: Client) -> None:
        self._client = client

    def sign_in(self, email: str, password: str) -> AuthToken:
        result = self._client.auth.sign_in_with_password({"email": email, "password": password})
        if not result.user or not result.session:
            raise ValueError("Invalid credentials")
        role = result.user.app_metadata.get("role", "")
        return AuthToken(access_token=result.session.access_token, role=role)

    def sign_out(self, token: str) -> None:  # token unused: Supabase SDK signs out current session
        self._client.auth.sign_out()

    def get_user_role(self, access_token: str) -> str | None:
        response = self._client.auth.get_user(access_token)
        if not response or not response.user:
            return None
        return response.user.app_metadata.get("role")

    def get_user_id(self, access_token: str) -> str:
        response = self._client.auth.get_user(access_token)
        if not response or not response.user:
            raise ValueError("Invalid token")
        return str(response.user.id)
