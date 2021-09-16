from rest_framework.pagination import PageNumberPagination


class GroupPagination(PageNumberPagination):
    page_size = 32
    max_page_size = 50
    page_query_param = 'page'
    page_size_query_param = 'page_size'
