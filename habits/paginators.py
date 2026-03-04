from rest_framework.pagination import PageNumberPagination


class HabitsPagination(PageNumberPagination):
    """Пагинатор привычек"""

    page_size = 5
    max_page_size = 100
