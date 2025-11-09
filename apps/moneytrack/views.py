from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse
from .models import Income, Expense

class HelloWorldView(View):
    def get(self, request):
        return HttpResponse("Hello, World!")

class FinanceListView(View):
    def get(self, request):
        incomes = Income.objects.all()
        expenses = Expense.objects.all()
        return render(request, 'moneytrack/finance_list.html', {
            'incomes': incomes,
            'expenses': expenses
        })

        
class AddIncomeView(View):
    def post(self, request):
        amount = request.POST.get('income_amount')
        date = request.POST.get('income_date')
        description = request.POST.get('income_description')
        if amount and date:
            Income.objects.create(amount=amount, date=date, description=description)
        return redirect('moneytrack:finance_list')


class AddExpenseView(View):
    def post(self, request):
        amount = request.POST.get('expense_amount')
        date = request.POST.get('expense_date')
        description = request.POST.get('expense_description')
        if amount and date:
            Expense.objects.create(amount=amount, date=date, description=description)
        return redirect('moneytrack:finance_list')