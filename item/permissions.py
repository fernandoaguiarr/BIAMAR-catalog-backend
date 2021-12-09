import copy

from rest_framework import permissions


class DefaultViewSetPermission(permissions.DjangoModelPermissions):
    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)
        self.perms_map['GET'] = ['%(app_label)s.get_%(model_name)s_api']
        self.perms_map['POST'] = []
        self.perms_map['PUT'] = []
        self.perms_map['PATCH'] = []
        self.perms_map['DELETE'] = []

