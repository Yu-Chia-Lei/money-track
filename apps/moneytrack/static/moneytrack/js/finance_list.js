// 帳戶選擇控制邏輯：新帳戶輸入框的顯示/隱藏
function setupAccountSelect(selectId, newInputId) {
    const selectElement = document.getElementById(selectId);
    const newInputElement = document.getElementById(newInputId);

    if (selectElement && newInputElement) {
        selectElement.addEventListener('change', function() {
            newInputElement.style.display = this.value === 'new' ? 'block' : 'none';
        });
         // 初始化時檢查一次
        if (selectElement.value === 'new') {
            newInputElement.style.display = 'block';
        }
    }
}


// 模態框中的收入/支出切換邏輯
const btnSwitchExpense = document.getElementById('btn-switch-expense');
const btnSwitchIncome = document.getElementById('btn-switch-income');
const expenseForm = document.getElementById('expenseForm');
const incomeForm = document.getElementById('incomeForm');
const transactionModalElement = document.getElementById('transactionModal');

function switchToExpense() {
    // 視覺切換
    btnSwitchExpense.classList.add('switch-active');
    btnSwitchIncome.classList.remove('switch-active');
    // 表單內容切換
    expenseForm.style.display = 'block';
    incomeForm.style.display = 'none';
    // 金額顏色
    document.getElementById('expense_amount').classList.add('text-danger');
    document.getElementById('income_amount').classList.remove('text-success');
}

function switchToIncome() {
    // 視覺切換
    btnSwitchIncome.classList.add('switch-active');
    btnSwitchExpense.classList.remove('switch-active');
    // 表單內容切換
    expenseForm.style.display = 'none';
    incomeForm.style.display = 'block';
    // 金額顏色
    document.getElementById('expense_amount').classList.remove('text-danger');
    document.getElementById('income_amount').classList.add('text-success');
}

btnSwitchExpense.addEventListener('click', switchToExpense);
btnSwitchIncome.addEventListener('click', switchToIncome);

// 2. 主程式執行區 (DOMContentLoaded)
document.addEventListener('DOMContentLoaded', () => {
    // 1. 初始化帳戶選擇器
    setupAccountSelect('expense_account_select', 'new_expense_account_name');
    setupAccountSelect('income_account_select', 'new_income_account_name');

    // ---------------- [新增這一段] ----------------
    // 設定「支出」表單的鎖定邏輯
    // 請將 'expense_payment_method' 換成您 HTML 中「支出-支付方式」的真實 ID
    //setupPaymentLock('expense_payment_method', 'expense_account_select'); 

    // 設定「收入」表單的鎖定邏輯 (如果收入也需要此功能)
    // 請將 'income_payment_method' 換成您 HTML 中「收入-支付方式」的真實 ID
    // setupPaymentLock('income_payment_method', 'income_account_select');
    // ---------------------------------------------
    
    // 2. 頁面載入時自動彈出 Modal
    const urlParams = new URLSearchParams(window.location.search);
    const modalParam = urlParams.get('modal');

    if (transactionModalElement) {
        const modal = new bootstrap.Modal(transactionModalElement);
        
        // 根據 URL 參數決定切換模式並打開 Modal
        if (modalParam === 'income') {
            switchToIncome();
            modal.show();
        } else if (modalParam === 'expense') {
            switchToExpense();
            modal.show();
        } else if (urlParams.has('modal')) {
            // 如果沒有指定 income/expense，預設彈出並停留在支出模式 (如圖)
            switchToExpense();
            modal.show();
        }

        // Modal 關閉時的清理和重設邏輯
        transactionModalElement.addEventListener('hidden.bs.modal', function () {
            // 重設為支出表單 (預設狀態)
            switchToExpense();
            // 清除表單內容
            expenseForm.reset();
            incomeForm.reset();

        });
    }
});