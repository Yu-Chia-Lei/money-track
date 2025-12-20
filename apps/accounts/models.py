from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    自訂使用者模型
    繼承 AbstractUser,保留所有內建欄位並新增額外欄位
    """

    # 新增的自訂欄位
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='電話號碼'
    )

    avatar = models.URLField(
        blank=True,
        null=True,
        verbose_name='頭像網址'
    )

    bio = models.TextField(
        blank=True,
        max_length=500,
        verbose_name='個人簡介'
    )

    # --- 新增的提醒相關欄位 ---
    is_reminder_on = models.BooleanField(
        default=False,
        verbose_name='是否開啟記帳提醒'
    )

    reminder_time = models.TimeField(
        blank=True,
        null=True,
        verbose_name='提醒時間'
    )

    class Meta:
        verbose_name = '使用者'
        verbose_name_plural = '使用者'

    def __str__(self):
        return self.username

