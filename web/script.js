document.addEventListener('DOMContentLoaded', () => {
    // 1. 封装「获取元素 + 绑定跳转」的函数
    function bindLoginButton(buttonId, targetUrl) {
        const button = document.getElementById(buttonId);
        if (!button) {
            console.error(`⚠️ 未找到元素：${buttonId}，请检查 HTML 的 id 是否正确`);
            return; // 元素不存在就跳过，避免报错
        }

        button.addEventListener('click', () => {
            // 2. 跳转前显示「加载中」提示（可选，提升体验）
            const loading = document.createElement('div');
            loading.style.position = 'fixed';
            loading.style.top = '50%';
            loading.style.left = '50%';
            loading.style.transform = 'translate(-50%, -50%)';
            loading.style.padding = '20px 40px';
            loading.style.background = 'rgba(0,0,0,0.8)';
            loading.style.color = 'white';
            loading.style.fontSize = '16px';
            loading.style.borderRadius = '8px';
            loading.innerText = '跳转中...';
            document.body.appendChild(loading);

            // 3. 延迟 300ms 跳转（让用户看到加载提示）
            setTimeout(() => {
                window.location.href = targetUrl;
            }, 300);
        });
    }

    // 4. 调用函数，绑定三个登录按钮
    bindLoginButton('user-login', '/');
    bindLoginButton('caregiver-login', 'caregiver-login.html');
    bindLoginButton('admin-login', 'admin-login.html');
});