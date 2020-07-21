import json
import re

from django.db.models import Count
from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import Photo, Item, Brand, Season, Type
from .serializers import PhotoSerializer, ItemSerializer, BrandSerializer, SeasonSerializer, TypeSerializer


class PhotoViewSet(viewsets.ViewSet):

    # PhotoModelPermission require this method
    def get_queryset(self):
        return Photo.objects.all()

    def list(self, request):
        # Query Params supported
        list_fields = ['items__group__icontains', 'items__brand__id', 'items__season__id', 'item__type__id', 'preview']

        queryset = self.get_queryset()
        query_params = request.query_params

        filters = {}
        if query_params:
            for item in query_params:
                try:
                    # Return the list_field item that have substring item
                    key = next(filter(lambda k: item in k, list_fields))
                    filters = {**filters, **{key: query_params[item]}}

                    # Convert filters dict values to correct types
                    try:
                        if 'id' in key:
                            filters[key] = int(filters[key])
                        elif 'preview' == key:
                            if filters[key].lower() == 'true':
                                filters[key] = True
                            elif filters[key].lower() == 'false':
                                filters[key] = False
                            else:
                                raise ValueError

                    # Raise ValueError if it was not possible convert
                    except ValueError:
                        return Response(status.HTTP_401_UNAUTHORIZED)

                # Raise StopIteration if lambdas function return is None
                except StopIteration:
                    return Response(status.HTTP_401_UNAUTHORIZED)

            # After serialization of query_params run query and group by 'items__group'
            queryset = queryset.filter(**filters).annotate(dcount=Count('items__group'))
            serializer = PhotoSerializer(queryset, many=True)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        else:
            serializer = PhotoSerializer(queryset, many=True)
            return Response(status=status.HTTP_200_OK, data=serializer.data)


class ItemViewSet(viewsets.ViewSet):

    # ItemModelPermission require this method
    def get_queryset(self):
        return Item.objects.all()

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        regex = re.compile("^(0{2}[0-9]{4})")

        # if item id validation fails raise ValueError exception
        try:
            if bool(regex.search(pk)):
                queryset = queryset.filter(group=pk)
                serializer = ItemSerializer(queryset, many=True)
                return Response(status=status.HTTP_200_OK, data=serializer.data)

            else:
                raise ValueError

        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class SeasonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer


class TypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Type.objects.all()
    serializer_class = TypeSerializer

