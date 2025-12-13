from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import HttpResponse, JsonResponse
from .models import Income, Expense, Account
from django.contrib.auth.mixins import LoginRequiredMixin
from decimal import Decimal
from django.db.models import Sum
from django.db.models.functions import TruncMonth, TruncDay, TruncWeek
from django.utils import timezone
import datetime


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
        payment_methods = ["現金", "LINE Pay", "街口支付", "Apple Pay"]
        return render(request, 'moneytrack/edit_expense.html', {
            'expense': expense,
            'accounts': accounts,
            'payment_methods': payment_methods,
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

# 圖表頁面
class ChartsPageView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    
    def get(self, request):
        return render(request, 'moneytrack/charts.html')

class ChartDataAPI(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        mode = request.GET.get('mode', 'month')
        today = timezone.localdate()
        
        # 初始 QuerySet
        expenses = Expense.objects.filter(account__user=user)
        incomes = Income.objects.filter(account__user=user)
        
        # --- A. 日期篩選 (這部分邏輯不變，確保摘要數字跟圖表範圍一致) ---
        date_format = '%Y-%m'
        trunc_func = TruncMonth('date') # 預設

        if mode == 'day':
            start_date = today.replace(day=1)
            trunc_func = TruncDay('date')
            date_format = '%Y-%m-%d'
        elif mode == 'week':
            start_date = today - datetime.timedelta(weeks=12)
            trunc_func = TruncWeek('date')
            date_format = '%Y-%m-%d'
        else: # month
            start_date = today - datetime.timedelta(days=365)
            trunc_func = TruncMonth('date')
            date_format = '%Y-%m'

        # 應用篩選
        expenses = expenses.filter(date__gte=start_date)
        incomes = incomes.filter(date__gte=start_date)

        # ==========================================
        # [新增] 1. 計算摘要總金額 (Summary Totals)
        # ==========================================
        # 使用 aggregate 加總，若無資料回傳 None，需轉為 0
        total_expense = expenses.aggregate(sum=Sum('amount'))['sum'] or 0
        total_income = incomes.aggregate(sum=Sum('amount'))['sum'] or 0
        balance = total_income - total_expense

        # --- B. 聚合數據 (圖表用) ---
        trend_expenses = expenses.annotate(period=trunc_func).values('period').annotate(total=Sum('amount')).order_by('period')
        trend_incomes = incomes.annotate(period=trunc_func).values('period').annotate(total=Sum('amount')).order_by('period')
        
        category_stats = expenses.values('category').annotate(total=Sum('amount')).order_by('-total')
        
        # 帳戶餘額 (注意：帳戶餘額通常顯示「當下總資產」，不應受日期篩選影響)
        # 如果您希望顯示「該期間的帳戶變動」，邏輯會很複雜，建議維持顯示「當前總餘額」
        accounts = Account.objects.filter(user=user)
        
        payment_stats = expenses.values('payment_method').annotate(total=Sum('amount')).order_by('-total')

        # --- C. 格式化回傳 ---
        all_periods = set()
        exp_dict = {}
        inc_dict = {}
        for item in trend_expenses:
            label = item['period'].strftime(date_format)
            all_periods.add(label)
            exp_dict[label] = float(item['total'])
        for item in trend_incomes:
            label = item['period'].strftime(date_format)
            all_periods.add(label)
            inc_dict[label] = float(item['total'])
        sorted_labels = sorted(list(all_periods))

        data = {
            # [新增] 傳遞摘要數據
            'summary': {
                'income': float(total_income),
                'expense': float(total_expense),
                'balance': float(balance)
            },
            'trend': {
                'labels': sorted_labels,
                'expense': [exp_dict.get(label, 0) for label in sorted_labels],
                'income': [inc_dict.get(label, 0) for label in sorted_labels],
            },
            'category': {
                'labels': [item['category'] if item['category'] else '未分類' for item in category_stats],
                'data': [float(item['total']) for item in category_stats]
            },
            'account': {
                'labels': list(accounts.values_list('bank_name', flat=True)),
                'data': [float(b) for b in accounts.values_list('balance', flat=True)]
            },
            'payment': {
                'labels': [item['payment_method'] for item in payment_stats],
                'data': [float(item['total']) for item in payment_stats]
            }
        }
        
        return JsonResponse(data)