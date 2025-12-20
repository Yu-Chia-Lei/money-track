import csv
import os
from datetime import datetime
from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from operator import attrgetter
import time


@shared_task(bind=True)
def export_transactions_to_csv(self, user_id, start_date=None, end_date=None, filter_type='all'):
    """背景執行：根據篩選條件匯出 CSV 並回傳下載網址"""
    User = get_user_model()
    user = User.objects.get(id=user_id)
    
    from apps.moneytrack.models import Income, Expense

    # 1. 執行篩選邏輯 (與你的 API 保持同步)
    incomes = Income.objects.filter(account__user=user)
    expenses = Expense.objects.filter(account__user=user)

    if start_date:
        incomes = incomes.filter(date__gte=start_date)
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        incomes = incomes.filter(date__lte=end_date)
        expenses = expenses.filter(date__lte=end_date)

    results = []
    if filter_type in ['all', 'income']:
        for i in incomes: i.record_type = '收入'; results.append(i)
    if filter_type in ['all', 'expense']:
        for e in expenses: e.record_type = '支出'; results.append(e)

    # 排序 (日期由新到舊)
    results.sort(key=attrgetter('date'), reverse=True)

    # 2. 存到 Media 目錄
    relative_path = 'exports'
    export_dir = os.path.join(settings.MEDIA_ROOT, relative_path)
    os.makedirs(export_dir, exist_ok=True)

    filename = f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    filepath = os.path.join(export_dir, filename)

    # 3. 寫入 CSV (utf-8-sig 確保 Excel 不亂碼)
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['日期', '類型', '分類', '金額', '帳戶', '備註', '支付方式'])
        for t in results:
            writer.writerow([
                t.date, t.record_type, t.category, t.amount,
                t.account.bank_name, t.description or "-",
                getattr(t, 'payment_method', '-')
            ])

    # 4. 回傳給 Celery Result (這會被後端 API 抓到)
    file_url = f"{settings.MEDIA_URL}{relative_path}/{filename}"
    return {'file_url': file_url}


@shared_task
def cleanup_old_reports():
    """自動清理超過 1 小時的舊報表"""
    #print("===== [Celery Beat] 開始掃描過期報表 =====")
    export_dir = os.path.join(settings.MEDIA_ROOT, 'exports')
    
    # 檢查資料夾是否存在
    if not os.path.exists(export_dir):
        return "資料夾不存在，無需清理。"

    now = time.time()
    # 3600 秒 = 1 小時
    cutoff = now - 3600

    deleted_count = 0
    for filename in os.listdir(export_dir):
        file_path = os.path.join(export_dir, filename)
        
        # 只處理檔案且判斷修改時間是否早於 cutoff
        if os.path.isfile(file_path):
            if os.path.getmtime(file_path) < cutoff:
                os.remove(file_path)
                deleted_count += 1
    
    return f"清理完成，共刪除 {deleted_count} 個過期報表。"