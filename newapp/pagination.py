from rest_framework.pagination import CursorPagination, PageNumberPagination
from rest_framework.response import Response


class CustomCursorPagination(CursorPagination):
    page_size = 5
    ordering = '-price'  # Укажите поле, которое существует в модели, например, 'price'


class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'page': self.page.number,
            'previous': None if not self.page.has_previous() else self.page.previous_page_number(),
            'next': None if not self.page.has_next() else self.page.next_page_number(),
            'previous_link': self.get_previous_link(),
            'next_link': self.get_next_link(),
            'results': data
        })
