from django.http.response import JsonResponse
from django.core.serializers import serialize


def serialize_and_simplify(queryset) -> JsonResponse:
    data = serialize("python", queryset)
    simplified = [{"id": item["pk"], **item["fields"]} for item in data]
    return JsonResponse(simplified, safe=False)
