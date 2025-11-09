from django.db import models

class Expense(models.Model):
    """支出"""
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField()

    class Meta:
        verbose_name = '支出'
        verbose_name_plural = '支出'

    def __str__(self):
        return self.description