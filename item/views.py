# Create your views here.
import copy

import magic
from django.core.files.storage import FileSystemStorage
from rest_framework import viewsets, permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Item, Photo
from .serializers import PhotoSerializer, ItemSerializer, GenericItemSerializer


# Override default DjangoModelPermissions on PhotoViewSet
# Removes POST, PUT and DELETE options in request
# Because this methods wont be used
class PhotoModelPermission(permissions.DjangoModelPermissions):
    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)  # from EunChong's answer
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']
        self.perms_map['POST'] = []
        self.perms_map['PUT'] = []
        self.perms_map['DELETE'] = []


class PhotoViewSet(viewsets.ViewSet):

    # Override default method get_permissions to be able set customs permissions
    def get_permissions(self):
        return [IsAuthenticated(), PhotoModelPermission()]

    # PhotoModelPermission require this method
    def get_queryset(self):
        return Photo.objects.all()

    # This overridden method lists all Photo objects filtered
    def list(self, request):
        # Get all Item objects, and query params
        queryset = Item.objects.all()
        query_params = request.query_params

        # check if query_params isn't None
        if query_params:
            # create a dict with query_params
            query_filter = {el: {'id': int(query_params[el])} for el in list(query_params.keys())}

            # check if key ID exists
            # after remove this key, because 'id':{'id': 'x'} does not work. Isn't a pattern model
            # other keys like 'brand' looks like in dict 'brand': {'id': 'x'} is a pattern model
            # so the key isnt deleted.
            if 'id' in query_filter:
                del query_filter['id']

            # Use query_filter to filter queryset and select only 'id' field
            # create a list named items to save the ID without type and brand
            # Item query id pattern: 00 00 000000, item list pattern: 000000
            queryset = queryset.filter(**query_filter).values('id')
            items = []
            if 'id' in query_params:
                for item in queryset:

                    # Get 000000 in queryset
                    ref = item['id'].split(" ")[2]
                    # If query_params['id'] contains in queryset, if true append to items
                    if (query_params['id']) and (query_params['id'] in ref):
                        items.append(ref)

            # if query_params['id'] doesnt exist append all queryset in pattern in items
            else:
                for item in queryset:
                    ref = item['id'].split(" ")[2]
                    items.append(ref)

            # Set queryset to use Photo model and filter with all id's in items list
            queryset = self.get_queryset().filter(id__in=items).order_by('-id')

            # if queryset result is none, return Error 404
            if not queryset:
                return Response(status=status.HTTP_404_NOT_FOUND)

        # if query_params doesnt exist get "default" values (20 photos object)
        else:
            queryset = self.get_queryset().order_by('-id')[:20]

        # if queryset is not None, return queryset serialized
        serializer = PhotoSerializer(queryset, many=True)
        return Response(data=serializer.data)

    # This overriden method get Photo object by specific ID
    def retrieve(self, request, pk=None):
        queryset = Photo.objects.all()
        serializer = PhotoSerializer(get_object_or_404(queryset, id=pk))
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    # This overriden method is used to update photos url in Photo object
    # only update url field. Check if type of file is JPG and file size is greater than 2MB
    def partial_update(self, request, pk=None):

        def upload_file(file):
            storage.save(file.name, file)

        def check_in_memory_mime(in_memory_file):
            mime = magic.from_buffer(in_memory_file.read(), mime=True)
            return mime

        queryset = get_object_or_404(self.get_queryset(), id=pk)
        files = request.FILES.getlist('file')
        storage = FileSystemStorage()

        if files:
            for item in files:
                url = '{}{}'.format(storage.base_url, item.name)
                if check_in_memory_mime(item) == 'image/png' and item.size <= 2097152:
                    if storage.exists(item.name):
                        storage.delete(item.name)
                        upload_file(item)

                        if url in queryset.photos:
                            queryset.photos.remove(url)
                            queryset.photos.append(url)
                            queryset.save()

                    else:
                        upload_file(item)
                        queryset.photos.append(url)
                        queryset.save()
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST,
                                    data={
                                        'detail': 'Data {} is unsuported or file size is greater than 2MB. Your file size {} Bytes.'.format(
                                            check_in_memory_mime(item), item.size)})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'detail': 'Data files not set.'})
        return Response(status=status.HTTP_204_NO_CONTENT)


# Override default DjangoModelPermissions permission in ItemViewSet
# Removes POST, PATCH, DELETE options in request
# Because this methods wont be used
class ItemModelPermission(permissions.DjangoModelPermissions):
    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)  # from EunChong's answer
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']
        self.perms_map['POST'] = []
        self.perms_map['PATCH'] = []
        self.perms_map['PUT'] = []
        self.perms_map['DELETE'] = []


class ItemViewSet(viewsets.ViewSet):

    # Override default method get_permissions to be able set customs permissions
    def get_permissions(self):
        return [IsAuthenticated(), ItemModelPermission()]

    # ItemModelPermission require this method
    def get_queryset(self):
        return Item.objects.all()

    # Get all items that contains pk
    # This query_params is used to controll fields that will be returned
    # query_params['all'] == true -> local use
    # query_params['all'] == false or not exist -> remote use
    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()

        query_params = request.query_params.get('all')
        queryset = queryset.filter(id__contains=pk) if query_params else queryset.filter(
            id__contains=pk).values('id',
                                    'brand',
                                    'collection',
                                    'type',
                                    'genre')

        if not queryset:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Use GenericItemSerializer to not display price, sku and specs fields. only remote use
        # Use ItemSerializer to display all fields. only local use
        serializer = ItemSerializer(queryset, many=True) if query_params else GenericItemSerializer(queryset, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
