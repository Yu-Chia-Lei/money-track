from django.db import models
from .account import Account
# -----------------------
# 收入模型
# -----------------------
class Income(models.Model):
    """收入"""
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='incomes', null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    category = models.CharField(max_length=30, blank=True)  # 可選分類
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = '收入'
        verbose_name_plural = '收入'

    def __str__(self):
        return f"{self.category}：{self.amount}元"

    def save(self, *args, **kwargs):
        is_new = self._state.adding  # 判斷是否第一次新增
        super().save(*args, **kwargs)
        if is_new:
            self.account.balance += self.amount
            self.account.save()