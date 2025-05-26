class HistoryDBRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'game' and model._meta.model_name == 'gamehistory':
            return 'history_db'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'game' and model._meta.model_name == 'gamehistory':
            return 'history_db'
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'game' and model_name == 'gamehistory':
            return db == 'history_db'
        return None