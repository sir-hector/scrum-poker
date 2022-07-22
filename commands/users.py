from users import user_service
from users.exceptions import RegisterException, LoginException


def register(db, login, password):
    if not user_service.validate_login(login):
        raise RegisterException("Wrong data")

    if not user_service.validate_password(password):
        raise RegisterException("Wrong data")

    if not user_service.has_user(db, login):
        raise RegisterException("Existing user")

    user_service.create_user(db, login, password)


def login_user(db, login, password):
    if user_service.has_user(db, login):
        raise RegisterException("No existing user")

    if not user_service.login_user(db, login, password):
        raise LoginException("wrong_credentials")

    return user_service.login_user(db, login, password)