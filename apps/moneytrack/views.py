from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import HttpResponse
from .models import Income, Expense, Account
from django.contrib.auth.mixins import LoginRequiredMixin
from decimal import Decimal

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
            account = Account.objects.create(user=request.user, bank_name=bank_name, balance=Decimal('0'))
        else:
            account = get_object_or_404(Account, id=account_id, user=request.user)

        amount = Decimal(request.POST.get('amount'))
        date = request.POST.get('date')
        category = request.POST.get('category')
        description = request.POST.get('description')

        # 新增收入
        Income.objects.create(
            account=account,
            amount=amount,
            date=date,
            category=category,
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
            account = Account.objects.create(user=request.user, bank_name=bank_name, balance=Decimal('0'))
        else:
            account = get_object_or_404(Account, id=account_id, user=request.user)

        amount = Decimal(request.POST.get('amount'))
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
        Account.objects.create(user=request.user, bank_name=bank_name, balance=Decimal('0'))
        return redirect('moneytrack:account_list')


# 編輯收入
class EditIncomeView(LoginRequiredMixin, View):
    def get(self, request, pk):
        income = get_object_or_404(Income, pk=pk, account__user=request.user)
        accounts = Account.objects.filter(user=request.user)
        return render(request, 'moneytrack/edit_income.html', {'income': income, 'accounts': accounts})

    def post(self, request, pk):
        income = get_object_or_404(Income, pk=pk, account__user=request.user)
        old_amount = income.amount
        old_account = income.account
        new_account = get_object_or_404(Account, id=request.POST.get('account'), user=request.user)

        # 更新內容
        income.account = new_account
        income.amount = Decimal(request.POST.get('amount'))
        income.date = request.POST.get('date')
        income.category = request.POST.get('category')
        income.description = request.POST.get('description')
        income.save()

        # 更新帳戶餘額（收入相反邏輯）
        if old_account == new_account:
            # 同一帳戶 → 調整差額
            diff = income.amount - old_amount  # 收入增加 -> 餘額應增加
            new_account.balance += diff
            new_account.save()
        else:
            # 換帳戶 → 從舊帳戶扣回，再加到新帳戶
            old_account.balance -= old_amount
            old_account.save()
            new_account.balance += income.amount
            new_account.save()

        return redirect('moneytrack:finance_list')


# 刪除收入
class DeleteIncomeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        income = get_object_or_404(Income, pk=pk, account__user=request.user)
        account = income.account
        account.balance -= income.amount  # 收入刪除 → 餘額減少
        account.save()
        income.delete()
        return redirect('moneytrack:finance_list')


# 編輯支出
class EditExpenseView(LoginRequiredMixin, View):
    def get(self, request, pk):
        expense = get_object_or_404(Expense, pk=pk, account__user=request.user)
        accounts = Account.objects.filter(user=request.user)
        payment_methods = ["現金", "信用卡", "銀行轉帳", "悠遊卡"]  # ⭐ 加這行

        return render(request, 'moneytrack/edit_expense.html', {
            'expense': expense,
            'accounts': accounts,
            'payment_methods': payment_methods,  # ⭐ 傳給前端
        })

    def post(self, request, pk):
        expense = get_object_or_404(Expense, pk=pk, account__user=request.user)
        old_amount = expense.amount
        old_account = expense.account  # 原帳戶

        new_account = get_object_or_404(Account, id=request.POST.get('account'), user=request.user)

        # 更新內容
        expense.account = new_account
        expense.amount = Decimal(request.POST.get('amount'))
        expense.date = request.POST.get('date')
        expense.category = request.POST.get('category')
        expense.description = request.POST.get('description')
        expense.payment_method = request.POST.get('payment_method')
        expense.save()

        # === 更新帳戶餘額 ===
        if old_account == new_account:
            # 沒換帳戶：支出變少 → 餘額增加
            diff = old_amount - expense.amount
            new_account.balance += diff
            new_account.save()
        else:
            # 換帳戶：舊帳戶加回舊金額，新帳戶扣新金額
            old_account.balance += old_amount
            old_account.save()
            new_account.balance -= expense.amount
            new_account.save()

        return redirect('moneytrack:finance_list')


# 刪除支出
class DeleteExpenseView(LoginRequiredMixin, View):
    def post(self, request, pk):
        expense = get_object_or_404(Expense, pk=pk, account__user=request.user)
        account = expense.account
        account.balance += expense.amount  # 回復餘額
        account.save()
        expense.delete()
        return redirect('moneytrack:finance_list')


# 編輯帳戶
class EditAccountView(LoginRequiredMixin, View):
    def get(self, request, pk):
        account = get_object_or_404(Account, pk=pk, user=request.user)
        return render(request, 'moneytrack/edit_account.html', {'account': account})

    def post(self, request, pk):
        account = get_object_or_404(Account, pk=pk, user=request.user)
        account.bank_name = request.POST.get('bank_name')
        account.save()
        return redirect('moneytrack:account_list')


# 刪除帳戶
class DeleteAccountView(LoginRequiredMixin, View):
    def post(self, request, pk):
        account = get_object_or_404(Account, pk=pk, user=request.user)
        # 刪除帳戶前，刪掉其收入與支出記錄
        Income.objects.filter(account=account).delete()
        Expense.objects.filter(account=account).delete()
        account.delete()
        return redirect('moneytrack:account_list')
