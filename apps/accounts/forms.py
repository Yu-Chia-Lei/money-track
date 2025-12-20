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
                'class': 'form-control time-picker-input', 
                'type': 'time',
                'step': '60',  # <-- 必須加上這行，才能啟用上下鍵微調與箭頭
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_reminder_on'].label = "啟用每日提醒"
        self.fields['reminder_time'].label = "設定提醒時間"