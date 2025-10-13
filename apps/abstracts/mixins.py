from django.db.models import QuerySet
from django.http.response import JsonResponse


class PaginatedMixin:

    def paginate_queryset(self, queryset: QuerySet, page_size=20):
        try:
            page = int(self.request.GET.get("page", 1))
        except ValueError:
            page = 1

        start = (page - 1) * page_size
        end = start + page_size

        return {
            "data": queryset[start:end],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": queryset.count(),
                "has_next": end < queryset.count(),
                "has_prev": page > 1,
            },
        }
