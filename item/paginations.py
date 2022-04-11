from django.core.paginator import Paginator
from django.utils.functional import cached_property
from rest_framework.pagination import PageNumberPagination


class FasterDjangoPaginator(Paginator):
    @cached_property
    def count(self):
        # only select 'id' for counting, much cheaper
        return self.object_list.values('id').count()

class GroupPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 50
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    django_paginator_class = FasterDjangoPaginator


class SkuPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 12
    page_query_param = 'page'
    page_size_query_param = 'page_size'
