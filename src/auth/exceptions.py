from fastapi import HTTPException
from starlette import status


# TODO Arrange better format for exceptions


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
)

incorrect_username_or_password = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect username or password",
)

jwt_exception = Exception('jwt_exception')
cannot_create_refresh_token = Exception('cannot_create_refresh_token')
cannot_create_access_token = Exception('cannot_create_access_token')

user_is_none = Exception('user_is_none')