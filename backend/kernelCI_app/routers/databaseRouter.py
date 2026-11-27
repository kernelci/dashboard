class DatabaseRouter:
    """
    A router to control all database operations on models in the
    kernelCI_app application.
    """

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == "default":
            return True
        if app_label == "kernelCI_app":
            return db == "dashboard_db"
        return False
