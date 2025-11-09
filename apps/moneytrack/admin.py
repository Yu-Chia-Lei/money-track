from django.contrib import admin
from .models import Income, Expense

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['date', 'amount', 'description']
    list_filter = ['date']
    search_fields = ['description']

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['date', 'amount', 'description']
    list_filter = ['date']
    search_fields = ['description']

