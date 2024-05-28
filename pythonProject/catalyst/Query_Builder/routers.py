# your_app_name/routers.py

class PostgreSQLRouter:
    """
    A router to control all database operations on models in the
    Query_Builder application.
    """

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'Query_Builder':
            return 'postgresql_db'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'Query_Builder':
            return 'postgresql_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'Query_Builder' and obj2._meta.app_label == 'Query_Builder':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'Query_Builder':
            return db == 'postgresql_db'
        return None
