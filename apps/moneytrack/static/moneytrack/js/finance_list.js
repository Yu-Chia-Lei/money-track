// ==========================================
// 1. 工具函式與切換邏輯 (保留原本的)
// ==========================================

// 分類選擇器邏輯：處理點擊圖標切換 active 狀態並更新隱藏 input
function initCategoryPicker(gridId, inputId) {
    const grid = document.getElementById(gridId);
    const input = document.getElementById(inputId);
    if (!grid || !input) return;

    const items = grid.querySelectorAll('.category-item');

    items.forEach(item => {
        item.addEventListener('click', () => {
            // 移除同網格內其他項目的選取狀態
            items.forEach(i => i.classList.remove('active'));
            // 為點擊項目加上選取狀態
            item.classList.add('active');
            // 更新隱藏 input 的值以利表單送出
            input.value = item.getAttribute('data-value');
        });
    });
}

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

    // === 新增：初始化分類網格選擇器 ===
    initCategoryPicker('expense_category_grid', 'expense_category_input');
    initCategoryPicker('income_category_grid', 'income_category_input');
    // =============================

    // === 新增：支付方式選擇「現金」後自動選擇「現金帳戶」 ===
    const expensePaymentMethod = document.getElementById('expense_payment_method');
    const expenseAccountSelect = document.getElementById('expense_account_select');

    function syncCashAccount() {
        if (expensePaymentMethod && expensePaymentMethod.value === '現金') {
            for (let i = 0; i < expenseAccountSelect.options.length; i++) {
                if (expenseAccountSelect.options[i].text.includes('現金')) {
                    expenseAccountSelect.selectedIndex = i;
                    expenseAccountSelect.dispatchEvent(new Event('change')); // 隱藏「新增帳戶」輸入框
                    break;
                }
            }
        }
    }

    if (expensePaymentMethod && expenseAccountSelect) {
        expensePaymentMethod.addEventListener('change', syncCashAccount);
    }
    // =======================================================

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

        // 統一定義設定日期的邏輯
        const setTodayDate = () => {
            const today = new Date().toLocaleDateString('en-CA'); 
            document.querySelectorAll('#expense_date, #income_date').forEach(input => {
                input.value = today;
            });
        };

        // 打開時設定日期與檢查現金連動
        transactionModalElement.addEventListener('shown.bs.modal', () => {
            setTodayDate();
            syncCashAccount(); 
        });

        // 【唯一保留的關閉監聽器】重設表單、補回日期、重設分類、安全清理
        transactionModalElement.addEventListener('hidden.bs.modal', function () {
            // 1. 基本重設
            switchToExpense();
            if (expenseForm) expenseForm.reset();
            if (incomeForm) incomeForm.reset();
            setTodayDate();

            // 2. [新增] 重設分類網格的視覺狀態 (回到預設值)
            document.querySelectorAll('.category-item').forEach(item => item.classList.remove('active'));
            const defaultExpense = document.querySelector('#expense_category_grid [data-value="餐飲"]');
            const defaultIncome = document.querySelector('#income_category_grid [data-value="薪資"]');
            if (defaultExpense) defaultExpense.classList.add('active');
            if (defaultIncome) defaultIncome.classList.add('active');
            
            // 確保隱藏 input 的值也重設
            if(document.getElementById('expense_category_input')) document.getElementById('expense_category_input').value = "餐飲";
            if(document.getElementById('income_category_input')) document.getElementById('income_category_input').value = "薪資";

            // 3. 確保視窗完全關閉後，才去抓新資料
            if (typeof loadTransactions === 'function') {
                loadTransactions();
            }

            // 4. === 安全清理模式 ===
            // 檢查畫面上是否還有任何正在顯示的 Modal (避免快速連續點擊時誤刪新視窗的遮罩)
            const openedModals = document.querySelectorAll('.modal.show');
    
            if (openedModals.length === 0) {
                // 只有當「沒有」其他視窗開啟時，才移除遮罩與鎖定狀態
                document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
                document.body.classList.remove('modal-open');
                document.body.style.overflow = '';
                document.body.style.paddingRight = '';
            }
        });

        // 處理 URL 參數開啟彈窗
        const urlParams = new URLSearchParams(window.location.search);
        const modalParam = urlParams.get('modal');

        if (modalParam === 'income') {
            switchToIncome();
            modalInstance.show();
        } else if (modalParam === 'expense' || urlParams.has('modal')) {
            switchToExpense();
            modalInstance.show();
        }
    }

    // === 新增：防止「新增紀錄」按鈕連點導致動畫出錯 ===
    const btnNewRecord = document.querySelector('.btn-new-record');
    if (btnNewRecord) {
        btnNewRecord.addEventListener('click', function() {
            const self = this;
            // 暫時關閉點擊功能，避免 0.5 秒內重複觸發動畫
            self.style.pointerEvents = 'none'; 
            setTimeout(() => {
                self.style.pointerEvents = 'auto'; 
            }, 500);
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
                        // 【關鍵修改】這裡只負責關閉視窗，不要在這裡刷新列表
                        if (modalInstance) {
                            modalInstance.hide();
                        }
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

    // ==========================================
    // [新增] 6. 下載報表 (Celery + 輪詢機制)
    // ==========================================
    
    // 下載報表邏輯
    const downloadBtn = document.getElementById('btn-download-csv');

if (downloadBtn) {
    downloadBtn.addEventListener('click', function(e) {
        // 【關鍵 1】防止按鈕觸發任何表單提交或網頁跳轉行為
        e.preventDefault(); 
        e.stopPropagation();

        const type = document.getElementById('typeFilter')?.value || 'all';
        const startDate = document.getElementById('startDate')?.value || '';
        const endDate = document.getElementById('endDate')?.value || '';
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        const formData = new FormData();
        formData.append('type', type);
        formData.append('start_date', startDate);
        formData.append('end_date', endDate);
        formData.append('csrfmiddlewaretoken', csrfToken);

        // UI 狀態回饋
        const originalHTML = downloadBtn.innerHTML;
        downloadBtn.disabled = true;
        downloadBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> 正在執行任務...';

        // 1. 發送請求啟動任務
        fetch('/moneytrack/api/transactions/export/', { 
            method: 'POST', 
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                const taskId = data.task_id;
                
                // 2. 定時檢查進度
                const checkStatus = setInterval(() => {
                    fetch(`/moneytrack/api/transactions/export/status/${taskId}/`)
                    .then(r => r.json())
                    .then(res => {
                        if (res.status === 'DONE') {
                            // 【關鍵 2】一旦完成，立刻停止輪詢，防止重複觸發
                            clearInterval(checkStatus); 
                            
                            const filename = res.file_url; // 這裡拿到的是 report_xxx.csv
    
                            // 【關鍵修正】構造指向我們剛剛在 urls.py 設定的路徑
                            const downloadUrl = `/moneytrack/finance/export/download/${filename}/`;

                            const link = document.createElement('a');
                            link.href = downloadUrl; // 使用構造好的 URL
                            link.setAttribute('download', filename); 
                            document.body.appendChild(link);
                            link.click();
                            link.remove();

                            // 恢復按鈕狀態
                            downloadBtn.innerHTML = '<i class="fa-solid fa-check"></i> 下載成功';
                            downloadBtn.classList.replace('btn-outline-success', 'btn-success');

                            setTimeout(() => {
                                downloadBtn.disabled = false;
                                downloadBtn.innerHTML = originalHTML;
                                downloadBtn.classList.replace('btn-success', 'btn-outline-success');
                            }, 2000);
                        }
                    })
                    .catch(err => {
                        clearInterval(checkStatus);
                        console.error("監測出錯:", err);
                        downloadBtn.disabled = false;
                        downloadBtn.innerHTML = originalHTML;
                    });
                }, 2000);
            }
        })
        .catch(err => {
            console.error("啟動失敗:", err);
            downloadBtn.disabled = false;
            downloadBtn.innerHTML = originalHTML;
        });
    });
}
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