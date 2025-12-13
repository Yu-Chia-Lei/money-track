    // 更新 JS 邏輯以匹配新的 ID
    const accountSelect = document.getElementById('expense_account');
    const newAccountInput = document.getElementById('new_expense_account_name');
    accountSelect.addEventListener('change', function() {
        newAccountInput.style.display = this.value === 'new' ? 'block' : 'none';
    });