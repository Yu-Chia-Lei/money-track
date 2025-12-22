from django.db import models
# from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# -----------------------
# 帳戶模型
# -----------------------

class Account(models.Model):
    """帳戶"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='accounts')
    bank_name = models.CharField(max_length=50)  # 例如：現金、中信銀行
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = '帳戶'
        verbose_name_plural = '帳戶'

    def __str__(self):
        return f"{self.bank_name}（餘額：{self.balance}）"

@receiver(post_save, sender=User)
def create_user_default_account(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance, bank_name='現金', balance=0)