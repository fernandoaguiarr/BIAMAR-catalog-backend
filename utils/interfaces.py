from rest_framework.exceptions import NotFound

from django.core.exceptions import ObjectDoesNotExist


class CustomViewSet:
    def __init__(self, filters: dict):
        self.filters = filters

    def get_filter_object(self, query_params: dict):
        queryset_filter = {}
        for obj in query_params.items():
            if obj[0] in self.filters:
                try:
                    query = {self.filters[obj[0]]['query_key']: obj[1]}
                    queryset_filter[obj[0]] = self.filters[obj[0]]['klass'].objects.get(**query)
                except ObjectDoesNotExist:
                    raise NotFound()
        return queryset_filter
