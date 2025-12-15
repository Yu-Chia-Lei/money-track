// ==========================================
// 1. 工具函式與切換邏輯
// ==========================================

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

// 取得全域元素 (放在外面是為了讓全域都能存取，但要在函式內檢查是否存在)
const btnSwitchExpense = document.getElementById('btn-switch-expense');
const btnSwitchIncome = document.getElementById('btn-switch-income');
const expenseForm = document.getElementById('expenseForm');
const incomeForm = document.getElementById('incomeForm');
const transactionModalElement = document.getElementById('transactionModal');

function switchToExpense() {
    // 視覺切換
    if (btnSwitchExpense) btnSwitchExpense.classList.add('switch-active');
    if (btnSwitchIncome) btnSwitchIncome.classList.remove('switch-active');
    
    // 表單內容切換
    if (expenseForm) expenseForm.style.display = 'block';
    if (incomeForm) incomeForm.style.display = 'none';
    
    // 金額顏色
    const expAmt = document.getElementById('expense_amount');
    const incAmt = document.getElementById('income_amount');
    if (expAmt) expAmt.classList.add('text-danger');
    if (incAmt) incAmt.classList.remove('text-success');
}

function switchToIncome() {
    // 視覺切換
    if (btnSwitchIncome) btnSwitchIncome.classList.add('switch-active');
    if (btnSwitchExpense) btnSwitchExpense.classList.remove('switch-active');
    
    // 表單內容切換
    if (expenseForm) expenseForm.style.display = 'none';
    if (incomeForm) incomeForm.style.display = 'block';
    
    // 金額顏色
    const expAmt = document.getElementById('expense_amount');
    const incAmt = document.getElementById('income_amount');
    if (expAmt) expAmt.classList.remove('text-danger');
    if (incAmt) incAmt.classList.add('text-success');
}

// 綁定切換按鈕事件
if (btnSwitchExpense) btnSwitchExpense.addEventListener('click', switchToExpense);
if (btnSwitchIncome) btnSwitchIncome.addEventListener('click', switchToIncome);


// ==========================================
// 2. 主程式執行區 (DOMContentLoaded)
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    
    // 1. 初始化帳戶選擇器
    setupAccountSelect('expense_account_select', 'new_expense_account_name');
    setupAccountSelect('income_account_select', 'new_income_account_name');

    // 2. Modal 初始化與事件處理 (核心修復部分)
    if (transactionModalElement) {
        // [關鍵修改] 使用 getOrCreateInstance 避免重複初始化導致按鈕失效
        const modal = bootstrap.Modal.getOrCreateInstance(transactionModalElement);
        
        // [關鍵修改] 強制幫所有關閉按鈕 (X 和 關閉) 綁定隱藏事件
        const closeButtons = transactionModalElement.querySelectorAll('[data-bs-dismiss="modal"]');
        closeButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault(); // 防止預設行為衝突
                modal.hide();       // 手動呼叫關閉
            });
        });

        // 處理 URL 參數自動開啟 Modal
        const urlParams = new URLSearchParams(window.location.search);
        const modalParam = urlParams.get('modal');

        if (modalParam === 'income') {
            switchToIncome();
            modal.show();
        } else if (modalParam === 'expense') {
            switchToExpense();
            modal.show();
        } else if (urlParams.has('modal')) {
            switchToExpense();
            modal.show();
        }

        // Modal 關閉後的清理工作
        transactionModalElement.addEventListener('hidden.bs.modal', function () {
            // 重設為支出表單 (預設狀態)
            switchToExpense();
            // 清除表單內容
            if (expenseForm) expenseForm.reset();
            if (incomeForm) incomeForm.reset();
        });
    }

    // ==========================================
    // # AJAX 刪除功能
    // ==========================================
    document.body.addEventListener('click', function(e) {
        // 檢查被點擊的元素是否包含 'btn-delete-ajax' class
        // (如果是點擊到 icon <i>，使用 closest 往上找按鈕)
        const btn = e.target.closest('.btn-delete-ajax');
        
        if (btn) {
            e.preventDefault();
            
            const url = btn.dataset.url;
            const type = btn.dataset.type || '記錄';
            const row = btn.closest('tr'); // 找到按鈕所在的該行表格

            if (!confirm(`確定要刪除這筆${type}嗎？此操作無法復原。`)) return;

            // 檢查 sendRequest 是否存在 (定義在 utils.js)
            if (typeof sendRequest === 'function') {
                sendRequest({
                    url: url,
                    method: "POST",
                    onSuccess: (res) => {
                        if (res.status === 'success') {
                            // 1. 動畫效果 (淡出)
                            row.style.transition = "all 0.2s ease";
                            row.style.opacity = "0";
                            
                            setTimeout(() => {
                                // 2. 實際移除 DOM
                                row.remove();
                            }, 500);
                        } else {
                            alert(res.message || "刪除失敗");
                        }
                    },
                    onError: (err) => {
                        console.error(err);
                        alert("發生錯誤，請稍後再試。");
                    }
                });
            } else {
                console.error("錯誤: utils.js 未載入，找不到 sendRequest 函式");
                alert("系統錯誤：無法發送請求");
            }
        }
    });

});