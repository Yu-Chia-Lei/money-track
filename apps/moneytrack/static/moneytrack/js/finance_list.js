/**
 * apps/moneytrack/static/moneytrack/js/finance_list.js
 * * 功能：
 * 1. 處理收入/支出表單的 AJAX 提交
 * 2. 處理「帳戶」下拉選單的切換邏輯 (顯示/隱藏新帳戶輸入框)
 * 3. 即時更新介面 (餘額、新增的表格列)
 */

document.addEventListener('DOMContentLoaded', () => {
    // --------------------------------------------------
    // 1. 初始化帳戶選擇器 (切換 "新帳戶" 輸入框)
    // --------------------------------------------------
    // 對應 HTML 中的 ID
    setupAccountSelect('income_account', 'new_income_account_name');
    setupAccountSelect('expense_account', 'new_expense_account_name');

    // --------------------------------------------------
    // 2. 初始化 AJAX 表單提交
    // --------------------------------------------------
    // 參數: (Form ID, Table Body ID, 是否為收入)
    setupAjaxForm('income-form', 'income-table-body', true);
    setupAjaxForm('expense-form', 'expense-table-body', false);
});


// ==================================================
//  核心功能函數
// ==================================================

/**
 * 設定帳戶選擇控制邏輯
 * 當選擇 "new" 時，顯示輸入框，否則隱藏
 */
function setupAccountSelect(selectId, newInputId) {
    const selectElement = document.getElementById(selectId);
    const newInputElement = document.getElementById(newInputId);

    if (selectElement && newInputElement) {
        selectElement.addEventListener('change', function() {
            newInputElement.style.display = this.value === 'new' ? 'block' : 'none';
        });
        
        // 初始化檢查 (防止重新整理後狀態跑掉)
        if (selectElement.value === 'new') {
            newInputElement.style.display = 'block';
        }
    }
}

/**
 * 設定 AJAX 表單提交
 * @param {string} formId 表單 ID
 * @param {string} tbodyId 表格 Body ID
 * @param {boolean} isIncome 是否為收入 (影響金額顏色與顯示方式)
 */
function setupAjaxForm(formId, tbodyId, isIncome) {
    const form = document.getElementById(formId);
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault(); // 阻止傳統頁面跳轉

        const formData = new FormData(form);
        const accountVal = formData.get('account'); // 檢查是否選了 "新增帳戶"

        // 使用 utils.js 的 sendRequest
        sendRequest({
            url: form.action, // 使用 form 標籤上的 action 屬性 (API URL)
            method: 'POST',
            data: formData,
            showLoadingOverlay: false, // 若您有實作 loading 動畫可設為 true
            onSuccess: (response) => {
                if (response.success) {
                    // 特殊情況：如果是創建了「新帳戶」
                    // 為了讓另一個表單的下拉選單也同步更新，最簡單的方式是重新整理頁面
                    if (accountVal === 'new') {
                        alert(response.message + "\n(頁面將重新載入以更新帳戶列表)");
                        window.location.reload();
                        return;
                    }

                    // 1. 更新畫面上的餘額
                    updateBalance(response.data.account_id, response.data.new_balance);

                    // 2. 動態新增一行到表格
                    // 我們需要帳戶名稱來顯示，先從 select 選單中抓取目前的文字
                    const selectEl = form.querySelector('select[name="account"]');
                    const accountName = selectEl ? selectEl.options[selectEl.selectedIndex].text : '-';
                    
                    addTableRow(tbodyId, response.data, accountName, isIncome);

                    // 3. 重置表單
                    form.reset();
                    
                    // 4. 把日期設回今天 (因為 reset 會清空所有欄位)
                    const dateInput = form.querySelector('input[name="date"]');
                    if(dateInput) dateInput.value = new Date().toISOString().split('T')[0];

                    // 可選：顯示成功提示
                    // alert(response.message); 

                } else {
                    // 後端回傳 success: False
                    alert('操作失敗: ' + (response.message || '未知錯誤'));
                }
            },
            onError: (err) => {
                console.error(err);
                // utils.js 通常會處理錯誤提示，這裡做一個保險
                alert('連線錯誤或伺服器異常，請稍後再試。');
            }
        });
    });
}

/**
 * 更新指定帳戶的餘額顯示
 * 尋找帶有 data-account-id="..." 的元素
 */
function updateBalance(accountId, newBalance) {
    // 這裡對應 HTML: <span class="account-balance" data-account-id="1">
    const balanceElements = document.querySelectorAll(`.account-balance[data-account-id="${accountId}"]`);
    
    balanceElements.forEach(el => {
        // 做一個簡單的視覺回饋 (紅色閃爍)
        el.style.transition = "color 0.2s";
        el.style.color = "red";
        el.textContent = newBalance;
        
        setTimeout(() => {
            el.style.color = ""; // 恢復原色
        }, 1000);
    });
}

/**
 * 動態新增一行到表格頂部
 */
function addTableRow(tbodyId, data, accountName, isIncome) {
    const tbody = document.getElementById(tbodyId);
    if (!tbody) return;

    // 移除 "目前沒有紀錄" 的空行 (如果有的話)
    const emptyRow = tbody.querySelector('.empty-row');
    if (emptyRow) emptyRow.remove();

    const tr = document.createElement('tr');
    tr.className = "table-success"; // Bootstrap 綠色背景，作為新增提示效果

    // 根據是否為收入，決定金額樣式
    const amountClass = isIncome ? 'text-success fw-bold' : 'text-danger fw-bold';
    
    // 編輯按鈕的連結 (暫時使用 JS 拼接，注意：若 URL 結構改變這裡也要改)
    // 假設 URL 模式為 /moneytrack/finance/income/123/edit/
    // 這裡只是一個權宜之計，為了讓新增的行也有編輯按鈕
    const typeStr = isIncome ? 'income' : 'expense';
    const editUrl = `/moneytrack/finance/${typeStr}/${data.id}/edit/`; 

    // 依據 HTML 表格欄位順序組裝: 日期 | 金額 | 摘要 | 操作
    tr.innerHTML = `
        <td>${data.date}</td>
        <td class="${amountClass}">${data.amount}</td>
        <td>${data.category || ''} - ${accountName}</td>
        <td>
            <a href="${editUrl}" class="btn btn-sm btn-link p-0">編輯</a>
        </td>
    `;

    // 插入到表格最前面 (tbody 的第一個子元素之前)
    tbody.insertBefore(tr, tbody.firstChild);

    // 1秒後移除高亮背景
    setTimeout(() => {
        tr.classList.remove('table-success');
    }, 1000);
}