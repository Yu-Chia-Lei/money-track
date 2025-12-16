document.addEventListener('DOMContentLoaded', function() {
    // 1. AJAX 刪除功能邏輯 (與 finance_list.js 類似，但為了獨立運作寫在這裡)
    document.body.addEventListener('click', function(e) {
        // 向上尋找是否有 .btn-delete-ajax
        const btn = e.target.closest('.btn-delete-ajax');
        
        if (btn) {
            e.preventDefault();
            const url = btn.dataset.url;
            const type = btn.dataset.type;
            const row = btn.closest('tr');

            if (confirm(`確定要刪除這個${type}嗎？\n注意：相關的收支紀錄可能也會受到影響！`)) {
                
                if (typeof sendRequest === 'function') {
                    sendRequest({
                        url: url,
                        method: "POST",
                        onSuccess: (res) => {
                            if (res.status === 'success') {
                                // 淡出動畫
                                row.style.transition = "all 0.3s ease";
                                row.style.backgroundColor = "#ffdddd";
                                row.style.opacity = "0";
                                setTimeout(() => row.remove(), 300);
                            } else {
                                alert("刪除失敗：" + (res.message || "未知錯誤"));
                            }
                        },
                        onError: (err) => {
                            console.error(err);
                            alert("發生錯誤，請稍後再試。");
                        }
                    });
                } else {
                    console.error("sendRequest not found");
                    // 如果 utils.js 沒載入的備案 (雖然上面有 import)
                    alert("系統錯誤：無法執行刪除");
                }
            }
        }
    });

    // 2. Modal 關閉按鈕修復 (比照 finance_list 的做法)
    const addModalEl = document.getElementById('addAccountModal');
    if (addModalEl) {
        const modal = bootstrap.Modal.getOrCreateInstance(addModalEl);
        const closeButtons = addModalEl.querySelectorAll('[data-bs-dismiss="modal"]');
        closeButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                modal.hide();
            });
        });
    }
});