from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import Photo, Item
from .serializers import PhotoSerializer, ItemSerializer, CollectionSerializer, GenericSerializer


# Create your views here.
class PhotoViewSet(viewsets.ViewSet):
    def list(self, request):
        filters = request.query_params
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

                queryset = Photo.objects.filter(id__in=id).order_by('-id')
                serializer = PhotoSerializer(queryset, many=True)

        else:
            queryset = Photo.objects.all().order_by('-id')[:500]
            serializer = PhotoSerializer(queryset, many=True)

        # RETORNA AS FOTOS EM CONJUNTO COM O PREÇO
        # for item in serializer.data:
        #     prices = Item.objects.filter(id__contains=item['id']).values('price')
        #     item['price'] = Item.objects.filter(id__contains=item['id']).values('price')[0]['price']
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


class PublicPhotoViewSet(viewsets.ViewSet):
    def list(self, request):
        filters = request.query_params
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
                queryset = Photo.objects.filter(~Q(concept_photo='') | ~Q(lookbook_photo=''))
                queryset = queryset.filter(id__in=id).order_by('-id')
                serializer = PhotoSerializer(queryset, many=True)

        else:
            queryset = Photo.objects.filter(~Q(concept_photo='') | ~Q(lookbook_photo='')).order_by('-id')[:500]
            serializer = PhotoSerializer(queryset, many=True)
        if not queryset:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Photo.objects.filter(~Q(concept_photo='') | ~Q(lookbook_photo=''))
        photo = get_object_or_404(queryset, id=pk)
        serializer = PhotoSerializer(photo)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

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
