from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Photo, Item, Collection
from .serializers import PhotoSerializer, ItemSerializer, CollectionSerializer, GenericSerializer


# Create your views here.

# @api_view(['GET'])
# def photo_list(request):
#     filters = request.query_params
#     if filters:
#         query_filter = {el: {'id': int(filters[el])} for el in list(filters.keys())}
#         if 'id' in filters:
#             del query_filter['id']
#             query_filter['id__contains'] = filters['id']
#         item = Item.objects.filter(**query_filter).values('id')
#
#         if not item:
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#         else:
#             id = []
#             for x in item:
#                 id.append(x['id'].split(" ")[2])
#
#             item = Photo.objects.filter(id__in=id)
#             serializer = PhotoSerializer(item, many=True)
#
#     else:
#         item = Photo.objects.all()
#         serializer = PhotoSerializer(item, many=True)
#
#     return Response(status=status.HTTP_200_OK, data=serializer.data)
#
#
# @api_view(['GET'])
# def photo_detail(request, id):
#     try:
#         photo = Photo.objects.get(id__contains=id)
#         serializer = PhotoSerializer(photo)
#         return Response(status=status.HTTP_200_OK, data=serializer.data)
#
#     except Photo.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)

class PhotoViewSet(viewsets.ViewSet):
    def list(self, request):
        filters = request.query_params
        print(filters)
        if filters:
            query_filter = {el: {'id': int(filters[el])} for el in list(filters.keys())}
            if 'id' in filters:
                del query_filter['id']
                query_filter['id__contains'] = filters['id']
            queryset = Item.objects.filter(**query_filter).values('id')

            if not queryset:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                id = []
                for x in queryset:
                    id.append(x['id'].split(" ")[2])

                queryset = Photo.objects.filter(id__in=id)
                serializer = PhotoSerializer(queryset, many=True)

        else:
            queryset = Photo.objects.all()
            serializer = PhotoSerializer(queryset, many=True)

        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Photo.objects.all()
        photo = get_object_or_404(queryset, id=pk)
        serializer = PhotoSerializer(photo)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class ItemViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        if Item.objects.filter(id__contains=pk):
            queryset = Item.objects.filter(id__contains=pk)
            serializer = ItemSerializer(queryset, many=True)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class FilterViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Item.objects.values_list('collection', flat=True).distinct()
        collection_serializer = CollectionSerializer(queryset, many=True)

        queryset = Item.objects.values_list('brand', flat=True).distinct()
        brand_filters = GenericSerializer(queryset, many=True)

        queryset = Item.objects.values_list('type', flat=True).distinct()
        type_filters = GenericSerializer(queryset, many=True)

        return Response(status=status.HTTP_200_OK,
                        data={'collection': collection_serializer.data, 'brand': brand_filters.data,
                              'type': type_filters.data})

# @api_view(['GET'])
# def filters_list(request):
#     filters = Item.objects.values_list('collection', flat=True).distinct()
#     collection_serializer = CollectionSerializer(filters, many=True)
#
#     filters = Item.objects.values_list('brand', flat=True).distinct()
#     brand_filters = GenericSerializer(filters, many=True)
#
#     filters = Item.objects.values_list('type', flat=True).distinct()
#     type_filters = GenericSerializer(filters, many=True)
#
#     return Response(status=status.HTTP_200_OK,
#                     data={'collection': collection_serializer.data, 'brand': brand_filters.data,
#                           'type': type_filters.data})
#     # data= collection_serializer.data
