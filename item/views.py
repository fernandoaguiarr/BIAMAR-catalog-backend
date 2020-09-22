import copy
import re
from uuid import uuid4

from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ObjectDoesNotExist, FieldError, ValidationError
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Photo, Item, Brand, Season, Type, TypePhoto, Color, Group, Sku
from .serializers import PhotoSerializer, ItemSerializer, BrandSerializer, SeasonSerializer, TypeSerializer, \
    TypePhotoSerializer, SkuSerializer, GroupSerializer


class PhotoModelPermission(permissions.DjangoModelPermissions):

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)  # you need deepcopy when you inherit a dictionary type
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']
        self.perms_map['POST'] = ['%(app_label)s.add_%(model_name)s']
        self.perms_map['PUT'] = []
        self.perms_map['PATCH'] = ['%(app_label)s.change_%(model_name)s']
        self.perms_map['DELETE'] = []


class CustomDjangoModelPermission(permissions.DjangoModelPermissions):

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)  # you need deepcopy when you inherit a dictionary type
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']
        self.perms_map['POST'] = []
        self.perms_map['PUT'] = []
        self.perms_map['PATCH'] = []
        self.perms_map['DELETE'] = []


class PhotoViewSet(viewsets.ViewSet):

    def group_is_valid(self, group):
        # Validate group pattern
        regex = re.compile("^(0{2}[0-9]{4})")
        return bool(regex.search(group))

    def storage_save(self, file_name, file, search=False):
        storage = FileSystemStorage()

        # Search if file exist
        if search and storage.exists(file_name):
            storage.delete(file_name)

        # Save file on /media/photos
        storage.save(file_name, file)

    def get_permissions(self):
        return [IsAuthenticated(), PhotoModelPermission()]

    # PhotoModelPermission require this method
    def get_queryset(self):
        return Photo.objects.all()

    def list(self, request):
        # Query Params supported
        list_fields = ['group__id__icontains', 'type', 'color', 'preview']

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
                        if 'preview' == key:
                            if filters[key].lower() == 'true':
                                filters[key] = True
                            elif filters[key].lower() == 'false':
                                filters[key] = False
                            else:
                                raise ValueError

                    # Raise ValueError if it was not possible convert
                    except ValueError:
                        return Response(status.HTTP_401_UNAUTHORIZED)

                # Raise StopIteration if lambda function return is None
                except StopIteration:
                    return Response(status.HTTP_401_UNAUTHORIZED)

            # After serialization of query_params run query and group by 'items__group'
            queryset = queryset.filter(**filters).annotate(dCount=Count('group'))
            serializer = PhotoSerializer(queryset, many=True)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        else:
            serializer = PhotoSerializer(queryset, many=True)
            return Response(status=status.HTTP_200_OK, data=serializer.data)

    def create(self, request):
        # Params supported
        list_fields = ['group__id', 'color__id', 'type__id', 'preview', 'file']

        queryset = self.get_queryset()
        params = request.data
        filters = {}

        # Try serialize and validate data
        try:
            if 'group' not in params:
                if self.group_is_valid(params['group']):
                    raise ValidationError("group field is not valid")
                raise FieldError("group field does not exist or is invalid")

            if 'color' not in params:
                raise FieldError("color field does not exist")

            if 'type' not in params:
                raise FieldError("type photo field does not exist")

            if 'file' not in params:
                raise FieldError("file field does not exist")

            if 'preview' not in params:
                raise FieldError("preview field does not exist")

            for item in params:
                # Return the list_field item that have substring item
                key = next(filter(lambda k: item in k, list_fields))
                filters = {**filters, **{key: params[item]}}

        except ValidationError as error:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=str(error))

        except FieldError as error:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=str(error))

        except StopIteration:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Some field is invalid")

        file = params['file']
        preview = params['preview']

        try:
            # Delete keys file and preview
            del filters['file'], filters['preview']
            if queryset.filter(**filters).exists():
                return Response(status=status.HTTP_200_OK,
                                data="photo alteready exist. You should try PATCH method to update")
            else:
                raise ObjectDoesNotExist
        except ObjectDoesNotExist:
            try:
                # Try get color, group and type photo from database
                color = Color.objects.get(id=filters['color__id'])
                group = Group.objects.get(id=filters['group__id'])
                type_photo = TypePhoto.objects.get(id=int(filters['type__id']))

                # Generate file name based on group id, color id and type photo id
                file_name = "photos/{}.jpg".format(uuid4().hex)

                # Save photo in /media/photos
                self.storage_save(file=file, file_name=file_name)
                photo = Photo(color=color, group=group, type=type_photo,
                              preview=True if preview.lower() == 'true' else False)

                photo.path.name = file_name
                photo.save()

                return Response(status=status.HTTP_200_OK)

            except ObjectDoesNotExist:
                return Response(data="Group {} or color/{} or type/{} does not exist".format(filters['group__id'],
                                                                                             filters['color__id'],
                                                                                             filters['type__id']))

    def partial_update(self, request, pk=None):
        # Params supported
        list_fields = ['color__id', 'type__id', 'preview', 'file']

        # Search photos that group is equal pk
        queryset = (self.get_queryset()).filter(group=pk)
        params = request.data
        filters = {}

        try:
            if not queryset.exists():
                raise ObjectDoesNotExist
            else:
                # Try serialize and validate data
                try:
                    if 'color' not in params:
                        raise FieldError("color field does not exist")

                    if 'type' not in params:
                        raise FieldError("type photo field does not exist")

                    if 'file' not in params:
                        raise FieldError("file field does not exist")

                    if 'preview' not in params:
                        raise FieldError("preview field does not exist")

                    for item in params:
                        # Return the list_field item that have substring item
                        key = next(filter(lambda k: item in k, list_fields))
                        filters = {**filters, **{key: params[item]}}

                except FieldError as error:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data=str(error))

                except StopIteration:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data="Some field is invalid")

                preview = filters['preview']
                file = filters['file']

                # Delete keys file and preview from filters dict
                del filters['file'], filters['preview']

                # Try to get object based on filters dict, if not succeed return http error 404
                # Change preview value if preview value is different than old value
                queryset = get_object_or_404(Photo, **filters)
                queryset.preview = preview if preview != queryset.preview else queryset.preview

                # Delete old image and save the new one
                # Save object changes
                self.storage_save(file_name=queryset.path.name, file=file, search=True)
                queryset.save()

                return Response(status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data="Group does not exist")

    def destroy(self, request, pk=None):
        try:
            queryset = (self.get_queryset()).get(id=pk)
            queryset.delete()

            return Response(status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class GroupViewSet(viewsets.ViewSet):

    def group_by(self, groups):
        res = {}
        for d in groups:
            res.setdefault(d['id'], []).append(d['photo_group__path'])

        groups_list = []
        for key in res.keys():
            paths = res[key]
            if paths[0] is None:
                paths.pop(0)

            groups_list.append({'id': key, 'paths': paths})

        return groups_list

    def get_permissions(self):
        return [IsAuthenticated(), CustomDjangoModelPermission()]

    # CustomDjangoModelPermission require this method
    def get_queryset(self):
        return Group.objects.all()

    def list(self, request):

        # Query Params supported
        list_fields = ['id__icontains', 'item_group__brand__id', 'item_group__season__id',
                       'item_group__type__id', 'photo_group__preview']

        queryset = self.get_queryset()
        query_params = request.query_params

        filters = {}
        preview = None

        if query_params:
            for item in query_params:
                try:
                    # Return the list_field item that have substring item
                    key = next(filter(lambda k: item in k, list_fields))
                    filters = {**filters, **{key: query_params[item]}}

                    # Convert filters dict values to correct types
                    try:
                        if 'photo_group__preview' == key:
                            if filters[key].lower() == 'true':
                                filters[key] = True
                            elif filters[key].lower() == 'false':
                                filters[key] = False
                            else:
                                raise ValueError

                        if 'photo_group__preview' in filters:
                            preview = {'photo_group__preview': filters['photo_group__preview']}
                            del filters['photo_group__preview']

                    # Raise ValueError if it was not possible convert
                    except ValueError:
                        return Response(status.HTTP_401_UNAUTHORIZED)

                # Raise StopIteration if lambda function return is None
                except StopIteration:
                    return Response(status.HTTP_401_UNAUTHORIZED)
            # queryset = queryset.filter(**filters).values('id', 'photo_group__path', 'photo_group__preview')

            if preview is not None:
                q1 = Q(**preview)
                q2 = Q(photo_group=None)
                queryset = queryset.filter(q1 | q2, **filters).values('id', 'photo_group__path',
                                                                      'photo_group__preview').distinct()
            else:
                queryset = queryset.filter(**filters).values('id', 'photo_group__path',
                                                             'photo_group__preview').distinct()

            serializer = GroupSerializer(queryset, many=True)
            groups = self.group_by(serializer.data)

            return Response(status=status.HTTP_200_OK, data=groups)
        else:
            serializer = GroupSerializer(queryset.values('id', 'photo_group__path'), many=True)
            groups = self.group_by(serializer.data)

            return Response(status=status.HTTP_200_OK, data=groups)


class ItemViewSet(viewsets.ViewSet):

    def get_permissions(self):
        return [IsAuthenticated(), CustomDjangoModelPermission()]

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


class SkuViewSet(viewsets.ViewSet):
    def get_permissions(self):
        return [IsAuthenticated(), CustomDjangoModelPermission()]

    # ItemModelPermission require this method
    def get_queryset(self):
        return Sku.objects.all()

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        regex = re.compile("^(0{2}[0-9]{4})")

        # if item id validation fails raise ValueError exception
        try:
            if bool(regex.search(pk)):
                queryset = queryset.filter(item_id__group=pk)
                serializer = SkuSerializer(queryset, many=True)
                return Response(status=status.HTTP_200_OK, data=serializer.data)
            else:
                raise ValueError

        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class BrandViewSet(viewsets.ReadOnlyModelViewSet):

    def get_permissions(self):
        return [IsAuthenticated(), CustomDjangoModelPermission()]

    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class SeasonViewSet(viewsets.ReadOnlyModelViewSet):

    def get_permissions(self):
        return [IsAuthenticated(), CustomDjangoModelPermission()]

    queryset = Season.objects.all()
    serializer_class = SeasonSerializer


class TypeViewSet(viewsets.ReadOnlyModelViewSet):

    def get_permissions(self):
        return [IsAuthenticated(), CustomDjangoModelPermission()]

    queryset = Type.objects.all()
    serializer_class = TypeSerializer


class TypePhotoViewSet(viewsets.ReadOnlyModelViewSet):
    def get_permissions(self):
        return [IsAuthenticated(), CustomDjangoModelPermission()]

    queryset = TypePhoto.objects.all()
    serializer_class = TypePhotoSerializer
