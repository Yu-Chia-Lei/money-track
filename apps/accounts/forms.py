from django import forms
from .models import User

class ReminderSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['is_reminder_on', 'reminder_time']
        widgets = {
        'is_reminder_on': forms.CheckboxInput(attrs={
        'class': 'form-check-input',
        'role': 'switch',
        }),
        'reminder_time': forms.TimeInput(attrs={
        # 這裡一定要加上 time-picker-input 類別
        'class': 'form-control time-picker-input', 
        'type': 'time',
        'step': '60', # 這行沒加，上下鍵就不能按分鐘調整
        }),
}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_reminder_on'].label = "啟用每日提醒"
        self.fields['reminder_time'].label = "設定提醒時間"