from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import HttpResponse, JsonResponse
from .models import Income, Expense, Account
from django.contrib.auth.mixins import LoginRequiredMixin
from decimal import Decimal
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth, TruncDay, TruncWeek
from django.utils import timezone
import datetime
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from operator import attrgetter
from django.urls import reverse


# ==========================================
# 1. 獨立的資料處理函數 (共用邏輯)
# ==========================================
def get_filtered_transactions(user, get_params):
    """
    接收 user 和 GET 參數，回傳篩選並排序後的交易物件列表
    """
    start_date = get_params.get('start_date')
    end_date = get_params.get('end_date')
    filter_type = get_params.get('type', 'all')  # all, income, expense

    # 1. 建立基礎 QuerySet
    incomes = Income.objects.filter(account__user=user)
    expenses = Expense.objects.filter(account__user=user)

    # 2. 日期篩選
    if start_date:
        incomes = incomes.filter(date__gte=start_date)
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        incomes = incomes.filter(date__lte=end_date)
        expenses = expenses.filter(date__lte=end_date)

    # 3. 類型篩選與合併
    results = []
    
    # 處理收入
    if filter_type in ['all', 'income']:
        for i in incomes:
            i.record_type = 'income'  # 標記類型，方便後續分辨
        results.extend(list(incomes))
        
    # 處理支出
    if filter_type in ['all', 'expense']:
        for e in expenses:
            e.record_type = 'expense' # 標記類型
        results.extend(list(expenses))

    # 4. 排序 (由新到舊)
    results.sort(key=attrgetter('date'), reverse=True)
    
    return results


# 2. 頁面渲染 View
class FinanceListView(LoginRequiredMixin, View):
    def get(self, request):
        # 這裡不再呼叫 get_filtered_transactions
        # 我們只準備篩選表單需要的預設值 (例如預設顯示本月)
        
        # (選擇性) 如果你想讓表單預設有值，可以在這裡準備
        # start_date = ... 
        
        context = {
            # 'transactions': ...  <-- 這行刪除！不要傳資料給模板
            'accounts': Account.objects.filter(user=request.user),
            
            # 保留表單預設值 (選擇性，看你想不想在後端控制預設日期)
            'filter_type': 'all',
            'start_date': request.GET.get('start_date', ''),
            'end_date': request.GET.get('end_date', ''),
        }
        return render(request, 'moneytrack/finance_list.html', context)

# ==========================================
# 3. API View (負責 AJAX 篩選，回傳 JSON)
# ==========================================
class TransactionFilterApiView(LoginRequiredMixin, View):
    def get(self, request):
        # 1. 呼叫共用函數取得物件列表
        transactions = get_filtered_transactions(request.user, request.GET)
        
        # 2. 將物件轉換成 JSON 格式 (Serialization)
        data_list = []
        for t in transactions:
            # 判斷是收入還是支出 (透過 helper function 標記的 record_type)
            is_income = (t.record_type == 'income')
            
            # 生成前端需要的資料結構
            item = {
                'id': t.id,
                'date': t.date.strftime('%Y-%m-%d'), # 日期轉字串
                'category': t.category,
                'account_name': t.account.bank_name,
                'description': t.description or "-",
                'amount': float(t.amount), # Decimal 轉 float
                'type': t.record_type,     # 'income' 或 'expense'
                
                # 支出才有 payment_method，收入沒有則給 '-'
                'payment_method': getattr(t, 'payment_method', '-'),
                
                # 在後端先生成好 URL，這樣 JS 就不用自己組字串
                'edit_url': reverse(f'moneytrack:edit_{t.record_type}', args=[t.id]),
                # 假設你的刪除 URL 是 delete_income_ajax / delete_expense_ajax
                'delete_url': reverse(f'moneytrack:delete_{t.record_type}_ajax', args=[t.id]),
            }
            data_list.append(item)

        # 3. 回傳 JSON
        return JsonResponse({'status': 'success', 'transactions': data_list})


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
        # account.balance += amount
        # account.save()

        return JsonResponse({
            'status': 'success',
            'message': '收入新增成功',
        })


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
        # account.balance -= amount
        # account.save()

        return JsonResponse({
            'status': 'success',
            'message': '支出新增成功',
        })


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
    login_url = '/accounts/login/' # 如果沒有登入，則跳轉到登入頁面
    
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

        if mode == 'week':
            # 週視圖：顯示「最近 12 週」
            start_date = today - datetime.timedelta(weeks=12)
            trunc_func = TruncWeek('date')
            date_format = '%Y-%m-%d'
        else: 
            # (預設) 月視圖：顯示「最近 12 個月」
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
        
        payment_stats = expenses.values('payment_method').annotate(count=Count('id')).order_by('-count')

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
                'data': [float(item['count']) for item in payment_stats]
            }
        }
        
        return JsonResponse(data)


# ==========================================
# # AJAX API 端點
# ==========================================

@login_required
@require_POST
def delete_expense_ajax(request, pk):
    """
    非同步刪除支出，並回補帳戶餘額
    """
    expense = get_object_or_404(Expense, pk=pk, account__user=request.user)
    
    try:
        # 1. 處理餘額回補
        account = expense.account
        account.balance += expense.amount
        account.save()
        
        # 2. 刪除
        expense.delete()
        
        return JsonResponse({'status': 'success', 'message': '支出已刪除'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
@require_POST
def delete_income_ajax(request, pk):
    """
    非同步刪除收入，並扣除帳戶餘額
    """
    income = get_object_or_404(Income, pk=pk, account__user=request.user)
    
    try:
        # 1. 處理餘額扣除
        account = income.account
        account.balance -= income.amount
        account.save()
        
        # 2. 刪除
        income.delete()
        
        return JsonResponse({'status': 'success', 'message': '收入已刪除'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


class DeleteAccountAjaxView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            account = get_object_or_404(Account, pk=pk, user=request.user)
            account.delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
