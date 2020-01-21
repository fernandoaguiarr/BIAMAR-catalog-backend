from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Photo, Item
from .serializers import PhotoSerializer, ItemSerializer


# Create your views here.

@api_view(['GET'])
def photo_list(request):
    if request.method == 'GET':
        filters = request.query_params
        if filters:
            query_filter = {el: {'id': int(filters[el])} for el in list(filters.keys())}
            if 'id' in filters:
                del query_filter['id']
                query_filter['id__contains'] = filters['id']
            item = Item.objects.filter(**query_filter).values('id')

            if not item:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                id = []
                for x in item:
                    id.append(x['id'].split(" ")[2])

                item = Photo.objects.filter(id__in=id)
                serializer = PhotoSerializer(item, many=True)

        else:
            item = Photo.objects.all().values('id', 'front_photo')
            serializer = PhotoSerializer(item, many=True)

            # return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


@api_view(['GET'])
def item_detail(request, id):
    try:
        item = Item.objects.filter(id__contains=id)
        serializer = ItemSerializer(item, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    except Item.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
