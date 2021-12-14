import copy

from rest_framework import permissions


class ImageViewSetPermission(permissions.DjangoModelPermissions):
    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']
        self.perms_map['POST'] = ['%(app_label)s.add_%(model_name)s']
        self.perms_map['PUT'] = []
        self.perms_map['PATCH'] = []
        self.perms_map['DELETE'] = []
