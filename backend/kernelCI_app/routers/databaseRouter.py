class DatabaseRouter:
    """
    A router to control all database operations on models in the
    kernelCI_app application.
    """

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == "default":
            return app_label != "kernelCI_cache"
        if model_name in ["notificationscheckout", "notificationsissue"]:
            return db == "notifications"
        if model_name in ["checkoutscache"]:
            return db == "cache"
        if hints.get("run_always", False):
            return app_label == "kernelCI_cache"
        if app_label == "kernelCI_app":
            return db == "dashboard_db"

        # Default False return to prevent duplication of schema.
        # If new model is added, it will not be migrated to any database.
        # To create new model schema, add it to the logic as above.
        return False
