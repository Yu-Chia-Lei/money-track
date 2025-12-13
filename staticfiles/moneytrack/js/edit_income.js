    // 確保原始的 JS 邏輯仍然有效
    const incomeSelect = document.getElementById('income_account');
    const newIncomeInput = document.getElementById('new_income_account_name');
    incomeSelect.addEventListener('change', function() {
        newIncomeInput.style.display = this.value === 'new' ? 'block' : 'none';
    });