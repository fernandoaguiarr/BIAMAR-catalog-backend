from rest_framework.exceptions import NotFound

from django.core.exceptions import ObjectDoesNotExist


class CustomViewSet:
    def __init__(self, filters: dict):
        self.filters = filters

    @staticmethod
    def add_key_prefix(key, prefix=None):
        if prefix:
            return '{}{}'.format(prefix, key)
        return key

    @staticmethod
    def add_key_suffix(key, suffix=None):
        return '{}{}'.format(key, suffix) if suffix else key

    def get_filter_object(self, query_params: dict):
        queryset_filter = {}
        for obj in query_params.items():
            if obj[0] in self.filters:
                try:
                    prefix = suffix = None
                    try:
                        prefix = self.filters[obj[0]]['prefix']
                        suffix = self.filters[obj[0]]['suffix']
                    except KeyError:
                        pass

                    query = {self.filters[obj[0]]['query_key']: obj[1]}
                    key = self.add_key_suffix(self.add_key_prefix(obj[0], prefix), suffix)
                    queryset_filter[key] = self.filters[obj[0]]['klass'].objects.get(
                        **query)
                except ObjectDoesNotExist:
                    raise NotFound()
        return queryset_filter
