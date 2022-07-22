from users import user_service
from users.exceptions import RegisterException, LoginException


def register(session, login, password):
    if not user_service.validate_login(login):
        raise RegisterException("Wrong data")

    if not user_service.validate_password(password):
        raise RegisterException("Wrong data")

    if not user_service.has_user(session, login):
        raise RegisterException("Existing user")

    user_service.create_user(session, login, password)


def login_user(session, login, password):
    if user_service.has_user(session, login):
        raise RegisterException("No existing user")

    if not user_service.login_user(session, login, password):
        raise LoginException("wrong_credentials")

    return user_service.login_user(session, login, password)


def list_all(session):
    return user_service.find_all_users(session)
