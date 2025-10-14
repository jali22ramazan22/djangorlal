from django.views import View
from django.http.response import JsonResponse
from datetime import datetime


class BaseAPIView(View):

    def json_response(self, data, status=200):
        return JsonResponse(data, status=status, safe=False)

    def error_response(self, message, status=400):
        return self.json_response({"error": message}, status=status)

    def parse_date(self, date_str):
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None
