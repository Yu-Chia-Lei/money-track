// ==========================================
// 1. 工具函式與切換邏輯 (保留原本的)
// ==========================================

// 帳戶選擇控制邏輯
function setupAccountSelect(selectId, newInputId) {
    const selectElement = document.getElementById(selectId);
    const newInputElement = document.getElementById(newInputId);

    if (selectElement && newInputElement) {
        selectElement.addEventListener('change', function() {
            newInputElement.style.display = this.value === 'new' ? 'block' : 'none';
        });
        if (selectElement.value === 'new') {
            newInputElement.style.display = 'block';
        }
    }
}

// 取得全域元素
const btnSwitchExpense = document.getElementById('btn-switch-expense');
const btnSwitchIncome = document.getElementById('btn-switch-income');
const expenseForm = document.getElementById('expenseForm');
const incomeForm = document.getElementById('incomeForm');
const transactionModalElement = document.getElementById('transactionModal');

function switchToExpense() {
    if (btnSwitchExpense) btnSwitchExpense.classList.add('switch-active');
    if (btnSwitchIncome) btnSwitchIncome.classList.remove('switch-active');
    if (expenseForm) expenseForm.style.display = 'block';
    if (incomeForm) incomeForm.style.display = 'none';
    
    const expAmt = document.getElementById('expense_amount');
    const incAmt = document.getElementById('income_amount');
    if (expAmt) expAmt.classList.add('text-danger');
    if (incAmt) incAmt.classList.remove('text-success');
}

function switchToIncome() {
    if (btnSwitchIncome) btnSwitchIncome.classList.add('switch-active');
    if (btnSwitchExpense) btnSwitchExpense.classList.remove('switch-active');
    if (expenseForm) expenseForm.style.display = 'none';
    if (incomeForm) incomeForm.style.display = 'block';
    
    const expAmt = document.getElementById('expense_amount');
    const incAmt = document.getElementById('income_amount');
    if (expAmt) expAmt.classList.remove('text-danger');
    if (incAmt) incAmt.classList.add('text-success');
}

if (btnSwitchExpense) btnSwitchExpense.addEventListener('click', switchToExpense);
if (btnSwitchIncome) btnSwitchIncome.addEventListener('click', switchToIncome);


// ==========================================
// 2. 主程式執行區 (DOMContentLoaded)
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    
    // 1. 初始化帳戶選擇器
    setupAccountSelect('expense_account_select', 'new_expense_account_name');
    setupAccountSelect('income_account_select', 'new_income_account_name');

    // 2. Modal 初始化
    let modalInstance = null;
    if (transactionModalElement) {
        modalInstance = bootstrap.Modal.getOrCreateInstance(transactionModalElement);
        
        const closeButtons = transactionModalElement.querySelectorAll('[data-bs-dismiss="modal"]');
        closeButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                modalInstance.hide();
            });
        });

        const urlParams = new URLSearchParams(window.location.search);
        const modalParam = urlParams.get('modal');

        if (modalParam === 'income') {
            switchToIncome();
            modalInstance.show();
        } else if (modalParam === 'expense' || urlParams.has('modal')) {
            switchToExpense();
            modalInstance.show();
        }

        transactionModalElement.addEventListener('hidden.bs.modal', function () {
            switchToExpense();
            if (expenseForm) expenseForm.reset();
            if (incomeForm) incomeForm.reset();
            // 重設日期為今天
            const today = new Date().toISOString().split('T')[0];
            document.querySelectorAll('input[type="date"]').forEach(input => input.value = today);
        });
    }

    // ==========================================
    // [新增] 3. 處理篩選表單 (AJAX 讀取列表)
    // ==========================================
    const filterForm = document.querySelector('form[method="get"]');
    
    // 封裝載入資料的邏輯，方便重複呼叫
    const loadTransactions = () => {
        if (!filterForm) return;
        
        const formData = new FormData(filterForm);
        const params = new URLSearchParams(formData).toString();
        const apiUrl = "/moneytrack/api/transactions/filter/"; 

        sendRequest({
            url: `${apiUrl}?${params}`,
            method: "GET",
            showLoadingOverlay: true, // 建議你的 sendRequest 支援這個，或手動加 loading
            onSuccess: (response) => {
                if (response.status === 'success') {
                    renderTable(response.transactions);
                    // 更新網址但不刷新 (Optional)
                    // window.history.pushState({}, "", `${window.location.pathname}?${params}`);
                }
            }
        });
    };

    if (filterForm) {
        // 監聽篩選按鈕
        filterForm.addEventListener("submit", function (e) {
            e.preventDefault();
            loadTransactions();
        });

        // [關鍵] 頁面載入後，自動觸發一次查詢，填滿表格
        loadTransactions();
    }

    // ==========================================
    // [新增] 4. 處理新增表單 (AJAX 新增)
    // ==========================================
    // 將兩個新增表單整合處理
    [expenseForm, incomeForm].forEach(form => {
        if (!form) return;
        form.addEventListener("submit", function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            
            sendRequest({
                url: form.action, // 使用 form 上的 action 屬性
                method: "POST",
                data: formData,
                showLoadingOverlay: true,
                onSuccess: (response) => {
                    if (response.status === 'success') {
                        // 1. 關閉 Modal
                        if (modalInstance) modalInstance.hide();
                        // 2. 重新載入表格 (呼叫剛剛定義的 loadTransactions)
                        //    這樣做的好處是會依照目前的篩選條件重新抓資料，確保排序正確
                        loadTransactions(); 
                        // 3. 提示成功 (選用)
                        // alert(response.message);
                    } else {
                        alert(response.message || "新增失敗");
                    }
                },
                onError: (err) => alert("新增失敗，請檢查資料")
            });
        });
    });

    // ==========================================
    // 5. AJAX 刪除功能 (事件委派)
    // ==========================================
    document.body.addEventListener('click', function(e) {
        const btn = e.target.closest('.btn-delete-ajax');
        
        if (btn) {
            e.preventDefault();
            
            const url = btn.dataset.url;
            const type = btn.dataset.type || '記錄';
            const row = btn.closest('tr');

            if (!confirm(`確定要刪除這筆${type}嗎？此操作無法復原。`)) return;

            if (typeof sendRequest === 'function') {
                sendRequest({
                    url: url,
                    method: "POST",
                    onSuccess: (res) => {
                        if (res.status === 'success') {
                            row.style.transition = "all 0.1s ease";
                            row.style.opacity = "0";
                            setTimeout(() => {
                                row.remove();
                                // 如果刪除後變空了，可以檢查並顯示「無資料」提示
                                const tbody = document.getElementById("transaction-list-body");
                                if (tbody && tbody.children.length === 0) {
                                    renderTable([]); // 呼叫 renderTable 顯示空狀態
                                }
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
        }
    });

});

// ==========================================
// [新增] 6. 渲染表格函數 (Render Function)
// ==========================================
function renderTable(dataList) {
    const tbody = document.getElementById("transaction-list-body");
    if (!tbody) return;

    tbody.innerHTML = '';

    // 無資料處理
    if (!dataList || dataList.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center py-5 text-muted">
                    <i class="fa-solid fa-magnifying-glass mb-2 fs-4"></i>
                    <p class="mb-0">沒有符合條件的記錄</p>
                </td>
            </tr>`;
        return;
    }

    // 產生 HTML
    const htmlRows = dataList.map(item => {
        const isIncome = item.type === 'income';
        
        // 樣式設定
        const badgeClass = isIncome 
            ? 'badge rounded-pill bg-success bg-opacity-10 text-success' 
            : 'badge rounded-pill bg-danger bg-opacity-10 text-danger';
        const amountClass = isIncome ? 'text-success' : 'text-danger';
        const sign = isIncome ? '+' : '-';
        const deleteTypeText = isIncome ? '收入' : '支出';
        
        // 支付方式 icon
        let paymentHtml = '-';
        if (!isIncome && item.payment_method && item.payment_method !== '-') {
            paymentHtml = `<span><i class="fa-regular fa-credit-card me-1"></i>${item.payment_method}</span>`;
        }

        // 金額格式化 (1,000.00)
        const formattedAmount = new Intl.NumberFormat('en-US').format(item.amount);

        // 使用 Template Literal 生成 HTML
        return `
            <tr>
                <td class="ps-4 text-secondary">${item.date}</td>
                <td><span class="${badgeClass}">${item.category}</span></td>
                <td>${item.account_name}</td>
                <td class="text-muted small">${item.description}</td>
                <td class="text-muted small">${paymentHtml}</td>
                <td class="text-end fw-bold">
                    <span class="${amountClass}">${sign}${formattedAmount}</span>
                </td>
                <td class="text-center">
                    <a href="${item.edit_url}" class="btn btn-sm btn-link text-warning p-0 mx-1" title="編輯">
                        <i class="fa-solid fa-pen"></i>
                    </a>
                    <button type="button" 
                            class="btn btn-sm btn-link text-danger p-0 mx-1 btn-delete-ajax"
                            data-url="${item.delete_url}"
                            data-type="${deleteTypeText}"
                            title="刪除">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');

    tbody.innerHTML = htmlRows;
}