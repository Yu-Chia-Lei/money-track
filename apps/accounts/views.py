from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ReminderSettingsForm

@login_required
def profile_settings(request):
    if request.method == 'POST':
        form = ReminderSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '提醒設定已更新！')
            return redirect('accounts:profile_settings')
    else:
        form = ReminderSettingsForm(instance=request.user)
    
    return render(request, 'account/profile_settings.html', {'form': form})
