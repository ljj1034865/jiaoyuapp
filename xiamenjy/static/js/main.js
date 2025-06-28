// 显示提示框
function showToast(title, message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastTitle = document.getElementById('toast-title');
    const toastMessage = document.getElementById('toast-message');
    
    // 设置标题和内容
    toastTitle.textContent = title;
    toastMessage.textContent = message;
    
    // 设置样式
    toast.classList.remove('bg-primary', 'bg-success', 'bg-danger', 'bg-warning');
    switch(type) {
        case 'success':
            toast.classList.add('bg-success');
            break;
        case 'danger':
            toast.classList.add('bg-danger');
            break;
        case 'warning':
            toast.classList.add('bg-warning');
            break;
        default:
            toast.classList.add('bg-primary');
    }
    
    // 显示提示框
    const toastInstance = new bootstrap.Toast(toast);
    toastInstance.show();
}

// 登出功能
document.getElementById('logoutBtn')?.addEventListener('click', async () => {
    try {
        const response = await fetch('/api/logout', {
            method: 'POST',
            credentials: 'include'
        });
        
        const data = await response.json();
        if (data.success) {
            showToast('已退出', '您已成功退出登录', 'success');
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);
        } else {
            showToast('退出失败', '退出登录时出错', 'danger');
        }
    } catch (error) {
        console.error('退出登录错误:', error);
        showToast('退出失败', '网络请求失败，请重试', 'danger');
    }
});

// 复制功能
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('copy-btn') || e.target.closest('.copy-btn')) {
        const btn = e.target.closest('.copy-btn');
        const content = btn.dataset.content || '';
        
        if (content) {
            navigator.clipboard.writeText(content).then(() => {
                showToast('复制成功', '内容已复制到剪贴板', 'success');
            }).catch(err => {
                console.error('复制失败:', err);
                showToast('复制失败', '无法复制内容，请重试', 'danger');
            });
        }
    }
});