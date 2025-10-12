from django.http.response import JsonResponse, HttpResponse
from django.http.request import HttpRequest
from django.core.serializers import serialize

from apps.db.models import JiraUser, Company


def response_with_all_queryset(model) -> JsonResponse:
    data = serialize("python", model.objects.all())
    simplified = [{"id": item["pk"], **item["fields"]} for item in data]
    return JsonResponse(simplified, safe=False)


def get_users(request: HttpRequest) -> HttpResponse:
    return response_with_all_queryset(JiraUser)


def get_companies(request: HttpRequest) -> HttpResponse:
    return response_with_all_queryset(Company)
