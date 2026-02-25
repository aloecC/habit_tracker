from rest_framework.pagination import PageNumberPagination


class LocarewardPagination(PageNumberPagination):
    """Пагинатор локаций/действий/вознагграждений"""

    page_size = 5
    page_query_param = "page_size"
    max_page_size = 100
