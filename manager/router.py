class MasterRouter(object):
    default_apps = (
        'admin',
        'auth',
        'contenttypes',
        'sessions',
        'messages',
    )

    def db_for_read(self, model, **hints):
        """
        Attempts to read item models go to item.
        """
        if model._meta.app_label == 'item':
            return 'item'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.default_apps:
            return 'default'
        return 'item'

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.default_apps:
            return db == 'default'
        return 'item'
