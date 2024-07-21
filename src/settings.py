from envparse import Env


env = Env()

ASYNC_DATABASE_URL = env.str("ASYNC_DATABASE_URL", default="sqlite+aiosqlite:///test_db_sqlite.sqlite")
APP_PORT = env.int("APP_PORT", default=40610)

# AUTH
AUTH_SECRET_KEY: str = env.str("AUTH_SECRET_KEY", default="secret_key")
AUTH_ALGORITHM: str = env.str("AUTH_ALGORITHM", default="HS256")
AUTH_ACCESS_TOKEN_EXPIRE_MINUTES: int = env.int("ACCESS_TOKEN_EXPIRE_MINUTES", default=30)
AUTH_REFRESH_TOKEN_EXPIRE_MINUTES: int = env.int("REFRESH_TOKEN_EXPIRE_MINUTES", default=4 * 7 * 24 * 60)

# test envs
# TEST_DATABASE_URL = env.str(
#     "TEST_DATABASE_URL",
#     default="postgresql+asyncpg://postgres_test:postgres_test@0.0.0.0:5433/postgres_test",
# )  # connect string for the test database