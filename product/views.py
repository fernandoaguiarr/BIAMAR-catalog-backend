from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Photo, Item
from .serializers import PhotoSerializer


# Create your views here.

@api_view(['GET', 'POST'])
def photo_list(request):
    if request.method == 'GET':
        filters = request.query_params
        # for key in filters.keys:

        return Response(filters.keys())
        # return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        return Response(status=status.HTTP_400_BAD_REQUEST)
