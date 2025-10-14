from django.db.models import QuerySet
from django.http.response import JsonResponse
from django.forms.models import model_to_dict
from datetime import date, datetime


class PaginatedMixin:

    def paginate_queryset(self, queryset: QuerySet, page_size=20):
        if queryset.exists() and not hasattr(queryset.first(), "to_json"):
            raise TypeError("Not Serializeable")

        try:
            page = int(self.request.GET.get("page", 1))
        except ValueError:
            page = 1

        page = max(1, page)

        total_count = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size

        page_items = queryset[start:end]
        deserialized_query_set = [obj.to_json() for obj in page_items]

        return {
            "data": deserialized_query_set,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "has_next": end < total_count,
                "has_prev": page > 1,
            },
        }

    def paginate_queryset_list(self, queryset_list, page_size=20):
        if queryset_list and not hasattr(queryset_list[0], "to_json"):
            raise TypeError("Not Serializeable")

        try:
            page = int(self.request.GET.get("page", 1))
        except ValueError:
            page = 1

        page = max(1, page)
        total_count = len(queryset_list)
        start = (page - 1) * page_size
        end = start + page_size

        page_items = queryset_list[start:end]
        deserialized_data = [obj.to_json() for obj in page_items]

        return {
            "data": deserialized_data,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "has_next": end < total_count,
                "has_prev": page > 1,
            },
        }


class JSONSerializerInstanceMixin:

    def to_json(self) -> dict:
        dict_obj = model_to_dict(self)

        for key, value in dict_obj.items():
            if isinstance(value, (date, datetime)):
                dict_obj[key] = value.isoformat()

        return dict_obj
