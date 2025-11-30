from conftest import auth_main, client

from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_403_FORBIDDEN,
)


def test_courses_list_ok(auth_main):
    response: Response = auth_main.get("/api/education/v1/courses")
    assert response.status_code == HTTP_200_OK


def test_course_list_no_auth(client):
    response: Response = client.get("/api/education/v1/courses")
    assert response.status_code == HTTP_401_UNAUTHORIZED


def test_course_creation(auth_main):
    payload = {"title": "New course", "description": "some description"}
    response: Response = auth_main.post("/api/education/v1/courses", payload)
    assert response.status_code == HTTP_201_CREATED
    assert response.data["title"] == payload["title"]


def test_course_creation_bad_data(auth_main):
    payload = {"title": "", "description": "some description"}
    response: Response = auth_main.post("/api/education/v1/courses", payload)
    assert response.status_code == HTTP_400_BAD_REQUEST


def test_get_single_course(auth_main, sample_course):
    response = auth_main.get(f"/api/education/v1/courses/{sample_course.id}")
    assert response.status_code == HTTP_200_OK


def test_get_unknown_course(auth_main):
    response = auth_main.get(f"/api/education/v1/courses/9191")
    assert response.status_code == HTTP_404_NOT_FOUND


def test_edit_course(auth_main, sample_course):
    new_data = {"title": "Reworked", "description": "Reworked details"}
    response = auth_main.put(f"/api/education/v1/courses/{sample_course.id}", new_data)
    assert response.status_code == HTTP_200_OK
    assert response.data["title"] == new_data["title"]
    assert response.data["description"] == new_data["description"]


def test_edit_course_invalid(auth_main, sample_course):
    new_data = {"title": "", "description": "Still Valid"}
    response = auth_main.put(f"/api/education/v1/courses/{sample_course.id}", new_data)
    assert response.status_code == HTTP_400_BAD_REQUEST


def test_edit_course_wrong_owner(auth_secondary, sample_course):
    patch_data = {"title": "Try Edit", "description": "Still Valid"}
    response = auth_main.put(
        f"/api/education/v1/courses/{sample_course.id}", patch_data
    )
    assert response.status_code == HTTP_403_FORBIDDEN


def test_remove_course(auth_main, sample_course):
    response = auth_main.delete(f"/api/education/v1/courses/{sample_course.id}")
    assert response.status_code == HTTP_200_OK


def test_enable_course(auth_main, sample_course):
    response = auth_main.post(f"/api/education/v1/courses/{sample_course.id}/activate")
    assert response.status_code == HTTP_200_OK

    sample_course.refresh_from_db()
    assert sample_course.is_active is True


def test_disable_course(auth_main, sample_course):
    response = auth_main.post(
        f"/api/education/v1/courses/{sample_course.id}/deactivate"
    )
    assert response.status_code == HTTP_200_OK

    sample_course.refresh_from_db()
    assert sample_course.is_active is False


def test_enable_course_not_owner(auth_secondary, sample_course):
    response = auth_main.post(f"/api/education/v1/courses/{sample_course.id}/activate")
    assert response.status_code == HTTP_403_FORBIDDEN


def test_lessons_list(auth_main, sample_course):
    response = auth_main.post(f"/api/education/v1/courses/{sample_course.id}/lessons")
    assert response.status_code == HTTP_200_OK
