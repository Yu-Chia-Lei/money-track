from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import HttpResponse
from .models import Income, Expense, Account
from django.contrib.auth.mixins import LoginRequiredMixin

# class HelloWorldView(View):
#     def get(self, request):
#         return HttpResponse("Hello, World!")

class FinanceListView(LoginRequiredMixin, View):
    def get(self, request):
        # 只抓登入使用者的帳戶
        accounts = Account.objects.filter(user=request.user)
        
        # 收入、支出按帳戶分組
        incomes = Income.objects.filter(account__in=accounts).order_by('-date')
        expenses = Expense.objects.filter(account__in=accounts).order_by('-date')

        return render(request, 'moneytrack/finance_list.html', {
            'accounts': accounts,
            'incomes': incomes,
            'expenses': expenses
        })


class AddIncomeView(LoginRequiredMixin, View):
    def post(self, request):
        account_id = request.POST.get('account')
        if account_id == 'new':
            # 使用者新增帳戶
            bank_name = request.POST.get('new_account_name')
            account = Account.objects.create(user=request.user, bank_name=bank_name, balance=0)
        else:
            account = get_object_or_404(Account, id=account_id, user=request.user)

        amount = float(request.POST.get('amount'))
        date = request.POST.get('date')
        description = request.POST.get('description')

        # 新增收入
        Income.objects.create(
            account=account,
            amount=amount,
            date=date,
            description=description
        )

        # 更新帳戶餘額
        account.balance += amount
        account.save()

        return redirect('moneytrack:finance_list')


class AddExpenseView(LoginRequiredMixin, View):
    def post(self, request):
        account_id = request.POST.get('account')
        if account_id == 'new':
            # 使用者新增帳戶
            bank_name = request.POST.get('new_account_name')
            account = Account.objects.create(user=request.user, bank_name=bank_name, balance=0)
        else:
            account = get_object_or_404(Account, id=account_id, user=request.user)

        amount = float(request.POST.get('amount'))
        date = request.POST.get('date')
        category = request.POST.get('category')
        description = request.POST.get('description')
        payment_method = request.POST.get('payment_method')

        # 新增支出
        Expense.objects.create(
            account=account,
            amount=amount,
            date=date,
            category=category,
            description=description,
            payment_method=payment_method
        )

        # 扣除帳戶餘額
        account.balance -= amount
        account.save()

        return redirect('moneytrack:finance_list')


class AccountListView(LoginRequiredMixin, View):
    def get(self, request):
        accounts = Account.objects.filter(user=request.user)
        return render(request, 'moneytrack/account_list.html', {'accounts': accounts})


class AddAccountView(LoginRequiredMixin, View):
    def post(self, request):
        # 獨立新增帳戶
        bank_name = request.POST.get('bank_name')
        Account.objects.create(user=request.user, bank_name=bank_name, balance=0)
        return redirect('moneytrack:finance_list')
