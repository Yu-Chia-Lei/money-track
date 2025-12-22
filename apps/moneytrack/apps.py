from django.apps import AppConfig


class MoneytrackConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.moneytrack'

    def ready(self):
        # 載入 models 以確保訊號被註冊
        import apps.moneytrack.models.account
