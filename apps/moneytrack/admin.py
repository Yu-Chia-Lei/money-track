from django.contrib import admin
from .models import Income, Expense, Account

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['date', 'amount', 'description', 'category']
    list_filter = ['date']
    search_fields = ['description']

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['date', 'amount', 'description', 'category', 'payment_method']
    list_filter = ['date']
    search_fields = ['description']


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['bank_name', 'balance']
    list_filter = ['bank_name']
    search_fields = ['bank_name']
