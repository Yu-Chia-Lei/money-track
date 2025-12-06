"""
Celery 任務定義

這裡定義所有 library app 的背景任務
"""
import csv
import os
from datetime import datetime
from celery import shared_task
from django.conf import settings
from django.contrib.auth.models import User


@shared_task(bind=True)
def export_expense_to_csv(self, user: User):
    """
    匯出書籍列表為 CSV 檔案

    Args:
        self: Celery task instance（因為 bind=True）
        user: 發起請求的使用者

    Returns:
        dict: 包含檔案路徑和訊息
    """
    # 這裡必須在函數內 import，避免 Django 尚未初始化
    from apps.moneytrack.models.expense import Expense

    print(f"[Task] 開始匯出支出報表，任務 ID: {self.request.id}")

    # 1. 查詢所有支出
    expense = Expense.objects.filter(account__user=user).all()
    total_expense = expense.count()

    print(f"[Task] 共有 {total_expense} 筆支出要匯出給 {user.username}")

    # 2. 建立匯出目錄（如果不存在）
    export_dir = os.path.join(settings.BASE_DIR, 'exports')
    os.makedirs(export_dir, exist_ok=True)

    # 3. 產生檔案名稱（包含時間戳記）
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'books_export_{timestamp}.csv'
    filepath = os.path.join(export_dir, filename)

    # 4. 寫入 CSV 檔案
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)

        # 寫入標題列
        writer.writerow(['ID', '金額', '日期', '分類', '描述', '支付方式'])

        # 寫入資料列
        for expense in expense:
            writer.writerow([
                expense.id,
                expense.amount,
                expense.date,
                expense.category,
                expense.description,
                expense.payment_method,
            ])

    print(f"[Task] 匯出完成：{filepath}")

    # 5. 發送 WebSocket 通知
    notify_export_complete(user.id, filename)

    return {
        'status': 'success',
        'filename': filename,
        'total_expense': total_expense,
        'message': f'成功匯出 {total_expense} 筆支出',
    }


def notify_export_complete(user: User, filename: str):
    """
    透過 WebSocket 通知使用者匯出完成

    Args:
        user: 使用者
        filename: 匯出的檔案名稱
    """
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    channel_layer = get_channel_layer()

        # 發送到 moneytrack_updates 群組
    async_to_sync(channel_layer.group_send)(
        'moneytrack_updates',
        {
            'type': 'moneytrack_update',
            'action': 'export_complete',
            'message': f'{user.username} 的報表匯出完成！檔案：{filename}',
        }
    )

    print(f"[Task] 已發送 WebSocket 通知給 {user.username}")
