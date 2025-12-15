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

    // ==========================================
    // # AJAX 刪除功能
    // ==========================================
    // 使用事件委派 (Event Delegation) 監聽 body，這樣可以處理動態產生的元素，也能減少監聽器數量
    document.body.addEventListener('click', function(e) {
        // 檢查被點擊的元素是否包含 'btn-delete-ajax' class
        if (e.target && e.target.classList.contains('btn-delete-ajax')) {
            e.preventDefault();
            
            const btn = e.target;
            const url = btn.dataset.url;
            const type = btn.dataset.type || '記錄';
            const row = btn.closest('tr'); // 找到按鈕所在的該行表格

            if (!confirm(`確定要刪除這筆${type}嗎？此操作無法復原。`)) return;

            // 呼叫 utils.js 中的 sendRequest
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
                            
                            // 3. (選用) 可以在這裡檢查表格是否為空，若為空顯示 "目前沒有紀錄"
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


        }
    });

    const modal = new bootstrap.Modal(document.getElementById('transactionModal'));

    // 1. 點擊「新增」：清空表單
    document.getElementById('btn-open-add-modal').addEventListener('click', () => {
        document.getElementById('expenseForm').reset();
        document.getElementById('incomeForm').reset();
        document.getElementById('expense_id').value = ''; // 清空 ID 表示是新增模式
        document.getElementById('income_id').value = '';
        document.getElementById('transactionModalLabel').textContent = '新增一筆記錄';
        // 確保可以切換類型
        document.getElementById('btn-switch-expense').disabled = false;
        document.getElementById('btn-switch-income').disabled = false;
    });

    // 2. 點擊「編輯」：撈資料填表單 (事件委派)
    document.body.addEventListener('click', (e) => {
        if (e.target && e.target.classList.contains('btn-edit-record')) {
            const id = e.target.dataset.id;
            const type = e.target.dataset.type;
            
            document.getElementById('transactionModalLabel').textContent = '編輯記錄';
            
            // 透過 AJAX 抓資料
            sendRequest({
                url: `/moneytrack/api/transaction/${type}/${id}/`,
                method: 'GET',
                onSuccess: (res) => {
                    const data = res.data;
                    if (type === 'expense') {
                        switchToExpense(); // 切換到支出 Tab
                        document.getElementById('expense_id').value = data.id;
                        document.getElementById('expense_amount').value = data.amount;
                        // ... (回填其他欄位: date, category, description, account ...)
                        // 注意 account select 的值要對應 option value
                        document.getElementById('expense_account_select').value = data.account_id; 
                    } else {
                        switchToIncome(); // 切換到收入 Tab
                        document.getElementById('income_id').value = data.id;
                        document.getElementById('income_amount').value = data.amount;
                        // ... (回填其他欄位)
                        document.getElementById('income_account_select').value = data.account_id;
                    }
                    // 編輯模式下，鎖定類型切換比較安全
                    document.getElementById('btn-switch-expense').disabled = true;
                    document.getElementById('btn-switch-income').disabled = true;
                    
                    modal.show();
                }
            });
        }
    });

    // 3. 表單提交：AJAX 送出
    function handleForm(e, type) {
        e.preventDefault();
        const form = e.target;
        const id = form.querySelector('input[name="id"]').value;
        const isEdit = !!id;
        
        let url = isEdit 
            ? `/moneytrack/api/${type}/edit/${id}/` 
            : `/moneytrack/api/${type}/add/`;

        const formData = new FormData(form);

        sendRequest({
            url: url,
            method: 'POST',
            data: formData,
            onSuccess: (res) => {
                modal.hide();
                // 這裡你需要寫一段 JS 把回傳的 res.data 生成 HTML
                // 如果是編輯(isEdit)，就 replaceWith() 原本的 <tr id="...">
                // 如果是新增，就 prepend() 到表格最前面
                updateTable(res.data, isEdit); 
                alert(res.message);
            }
        });
    }

    document.getElementById('expenseForm').addEventListener('submit', (e) => handleForm(e, 'expense'));
    document.getElementById('incomeForm').addEventListener('submit', (e) => handleForm(e, 'income'));

});

// Helper: 更新表格畫面 (你可以自己美化這段 HTML 生成邏輯)
function updateTable(data, isEdit) {
    const rowId = `row-${data.type}-${data.id}`;
    let html = `<tr id="${rowId}">
        <td>${data.account_name}</td>
        <td>${data.amount}</td>
        <td>${data.date}</td>
        <td>${data.category}</td>
        <td>${data.description}</td>
        ${data.type === 'expense' ? `<td>${data.payment_method}</td>` : ''}
        <td>
            <button class="btn btn-sm btn-warning btn-edit-record" data-id="${data.id}" data-type="${data.type}">編輯</button>
            <button class="btn btn-sm btn-danger btn-delete-ajax" data-url="/moneytrack/api/${data.type}/delete/${data.id}/">刪除</button>
        </td>
    </tr>`;

    if (isEdit) {
        const oldRow = document.getElementById(rowId);
        if (oldRow) oldRow.outerHTML = html;
    } else {
        const tableId = data.type === 'expense' ? 'expense-list' : 'income-list';
        document.querySelector(`#${tableId} tbody`).insertAdjacentHTML('afterbegin', html);
    }
}