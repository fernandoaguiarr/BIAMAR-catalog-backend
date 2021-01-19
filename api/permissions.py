import copy

from rest_framework import permissions


class DefaultViewSetPermission(permissions.DjangoModelPermissions):

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)  # you need deepcopy when you inherit a dictionary type
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']
        self.perms_map['POST'] = []
        self.perms_map['PUT'] = []
        self.perms_map['PATCH'] = []
        self.perms_map['DELETE'] = []


class PhotoViewSetPermission(permissions.DjangoModelPermissions):

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)  # you need deepcopy when you inherit a dictionary type
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']
        self.perms_map['POST'] = ['%(app_label)s.add_%(model_name)s']
        self.perms_map['PUT'] = []
        self.perms_map['PATCH'] = ['%(app_label)s.change_%(model_name)s']
        self.perms_map['DELETE'] = []


class GroupViewSetPermission(permissions.DjangoModelPermissions):

    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)  # you need deepcopy when you inherit a dictionary type
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s', '%(app_label)s.view_group']
        self.perms_map['POST'] = []
        self.perms_map['PUT'] = []
        self.perms_map['PATCH'] = []
        self.perms_map['DELETE'] = []
