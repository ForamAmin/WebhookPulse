from src.services.auth_service import login_user, register_user


def register(
    email: str,
    password: str,
    company_name: str,
):
    return register_user(
        email=email,
        password=password,
        company_name=company_name,
    )


def login(
    email: str,
    password: str,
):
    return login_user(
        email=email,
        password=password,
    )