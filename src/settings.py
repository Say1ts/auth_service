"""File with settings and configs for the project"""
from envparse import Env

env = Env()

###########################################################
#                       AUTH MODULE                       #
###########################################################

AUTH_DATABASE_URL = env.str(
    "REAL_DATABASE_URL",
    default="postgresql+asyncpg://postgres:postgres@localhost:5432/postgres",
)  # connect string for the real database
AUTH_APP_PORT = env.int("APP_PORT", default=40610)

# AUTH
AUTH_SECRET_KEY: str = env.str("SECRET_KEY", default="secret_key")
AUTH_ALGORITHM: str = env.str("ALGORITHM", default="HS256")
AUTH_ACCESS_TOKEN_EXPIRE_MINUTES: int = env.int("ACCESS_TOKEN_EXPIRE_MINUTES", default=30)

# test envs
# TEST_DATABASE_URL = env.str(
#     "TEST_DATABASE_URL",
#     default="postgresql+asyncpg://postgres_test:postgres_test@0.0.0.0:5433/postgres_test",
# )  # connect string for the test database
