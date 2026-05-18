from smart_delivery_routing.infrastructure.supabase.client import get_supabase_client

def sign_in(email: str, password: str) -> dict:
    return get_supabase_client().auth.sign_in_with_password({
        "email": email,
        "password": password
    })


def sign_out(access_token: str) -> None:
    get_supabase_client().auth.sign_out()


def get_user_role(access_token: str) -> str | None:
    user = get_supabase_client().auth.get_user(access_token)
    return user.user.app_metadata.get("role")


def get_user_id(access_token: str) -> str:
    user = get_supabase_client().auth.get_user(access_token)
    return str(user.user.id)