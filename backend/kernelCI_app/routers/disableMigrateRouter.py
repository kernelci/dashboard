class DisableMigrateRouter:
    """
    Database router to disable migration for databases that are manually managed.
    """

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == "default":
            return False
        return True
