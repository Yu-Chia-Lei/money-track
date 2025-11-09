from django.db import models
from .account import Account

# -----------------------
# 支出模型
# -----------------------
class Expense(models.Model):
    """支出"""
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='expenses', null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    category = models.CharField(max_length=30, blank=True)  # 可選分類
    description = models.TextField(blank=True)
    payment_method = models.CharField(
        max_length=20,
        default='現金',
        choices=[
            ('現金', '現金'),
            ('信用卡', '信用卡'),
            ('轉帳', '轉帳'),
        ]
    )

    class Meta:
        verbose_name = '支出'
        verbose_name_plural = '支出'

    def __str__(self):
        return f"{self.category}：{self.amount}元"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            self.account.balance -= self.amount
            self.account.save()