import pytest
from dataclasses import dataclass

from django.contrib.auth import get_user_model

from rest_framework.test import APIClient

User = get_user_model()

logs: list[str] = []


@pytest.fixture(autouse=True, scope="session")
def clear_logs():
    from datetime import datetime

    logs.append(f"Logs cleared at {datetime.now().microsecond}s")
    print(f"Logs before clearing: {logs}")

    yield
    # logs.append(f"Logs were cleared.")
    # print(f"Logs after clearing: {logs}")
    logs.clear()


@dataclass
class Settings:
    debug: bool
    jwt_secret: str
    allowed_hosts: list[str]


@pytest.fixture(scope="session")
def settings() -> Settings:
    """Fixture that provides application settings."""

    return Settings(
        debug=False,
        jwt_secret="super-secret-key",
        allowed_hosts=["localhost", "api.example.com"],
    )


@pytest.fixture
def enable_debug_mode(settings: Settings):
    """
    Temporarily enables debug=True.
    Based on the settings fixture.
    """
    old_value: bool = settings.debug
    settings.debug = True
    print(f"Debug mode enabled: {settings.debug}")

    # Everything before yield = setup
    yield settings

    # Everything after yield = teardown
    settings.debug = old_value
    print(f"Debug mode restored to: {settings.debug}")


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def main_user(db):
    return User.object.create_user(
        full_name="alpha_user", email="alpha@example.com", password="pwd123"
    )


@pytest.fixture
def second_user(db):
    return User.objects.create_user(
        full_name="beta_user", email="beta@example.com", password="pwd321"
    )


@pytest.fixture
def auth_main(client, main_user):
    client.force_authenticate(main_user)
    return client


@pytest.fixture
def auth_secondary(client, second_user):
    client.force_authenticate(second_user)
    return client


@pytest.fixture
def sample_course(main_user):
    from apps.education.models import Course

    return Course.objects.create(
        title="Djangorlar", description="Basic Intro Course", owner=main_user
    )
