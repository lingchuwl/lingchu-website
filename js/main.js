// 零初科技网站主JavaScript文件

document.addEventListener('DOMContentLoaded', function() {
    console.log('零初科技网站已加载');
    
    // 平滑滚动
    initSmoothScroll();
    
    // 导航栏效果
    initNavbar();
    
    // 动画效果
    initAnimations();
    
    // 表单处理
    initForms();
    
    // 统计功能
    initStats();
});

// 平滑滚动功能
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                const navbarHeight = document.querySelector('.navbar').offsetHeight;
                const targetPosition = targetElement.offsetTop - navbarHeight;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
                
                // 更新URL（不刷新页面）
                history.pushState(null, null, targetId);
            }
        });
    });
}

// 导航栏效果
function initNavbar() {
    const navbar = document.querySelector('.navbar');
    let lastScroll = 0;
    
    // 滚动时隐藏/显示导航栏
    window.addEventListener('scroll', function() {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll <= 0) {
            navbar.style.transform = 'translateY(0)';
            return;
        }
        
        if (currentScroll > lastScroll && currentScroll > 100) {
            // 向下滚动，隐藏导航栏
            navbar.style.transform = 'translateY(-100%)';
        } else {
            // 向上滚动，显示导航栏
            navbar.style.transform = 'translateY(0)';
        }
        
        lastScroll = currentScroll;
    });
    
    // 移动端菜单切换
    const menuToggle = document.querySelector('.menu-toggle');
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            const navLinks = document.querySelector('.nav-links');
            navLinks.classList.toggle('active');
            this.classList.toggle('active');
        });
    }
}

// 动画效果
function initAnimations() {
    // 观察器配置
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // 观察需要动画的元素
    document.querySelectorAll('.card, .feature-item, .demo-module').forEach(el => {
        observer.observe(el);
    });
}

// 表单处理
function initForms() {
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // 获取表单数据
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);
            
            // 简单验证
            if (!data.name || !data.email || !data.message) {
                showAlert('请填写所有必填字段', 'error');
                return;
            }
            
            // 模拟提交
            showAlert('提交中...', 'info');
            
            setTimeout(() => {
                showAlert('感谢您的咨询！我们将尽快与您联系。', 'success');
                contactForm.reset();
            }, 1500);
        });
    }
    
    // 试用申请表单
    const trialForm = document.getElementById('trial-form');
    if (trialForm) {
        trialForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const company = this.querySelector('input[name="company"]').value;
            const email = this.querySelector('input[name="email"]').value;
            
            if (!company || !email) {
                showAlert('请填写公司名称和邮箱', 'error');
                return;
            }
            
            showAlert(`已收到 ${company} 的试用申请，我们将发送确认邮件至 ${email}`, 'success');
            this.reset();
        });
    }
}

// 统计功能
function initStats() {
    // 模拟实时数据更新
    const statElements = document.querySelectorAll('.stat-value');
    if (statElements.length > 0) {
        setInterval(() => {
            statElements.forEach(stat => {
                const current = parseFloat(stat.textContent);
                if (!isNaN(current)) {
                    // 轻微随机变化
                    const change = (Math.random() - 0.5) * 0.1;
                    const newValue = Math.max(0, Math.min(100, current + change));
                    stat.textContent = newValue.toFixed(2) + (stat.textContent.includes('%') ? '%' : '');
                }
            });
        }, 5000);
    }
    
    // 页面访问统计
    const pageViews = localStorage.getItem('lingchu_page_views') || 0;
    localStorage.setItem('lingchu_page_views', parseInt(pageViews) + 1);
    
    // 显示访问次数（仅开发模式）
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        console.log(`页面访问次数: ${parseInt(pageViews) + 1}`);
    }
}

// 工具函数：显示提示
function showAlert(message, type = 'info') {
    // 移除现有提示
    const existingAlert = document.querySelector('.alert');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    // 创建新提示
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    alert.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'error' ? '#f44336' : type === 'success' ? '#4caf50' : '#2196f3'};
        color: white;
        border-radius: 5px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 9999;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(alert);
    
    // 3秒后自动移除
    setTimeout(() => {
        alert.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => alert.remove(), 300);
    }, 3000);
}

// 添加CSS动画
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .menu-toggle {
        display: none;
    }
    
    @media (max-width: 768px) {
        .menu-toggle {
            display: block;
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
        }
        
        .nav-links {
            position: fixed;
            top: 60px;
            left: 0;
            right: 0;
            background: var(--primary-color);
            flex-direction: column;
            padding: 1rem;
            transform: translateY(-100%);
            transition: transform 0.3s;
        }
        
        .nav-links.active {
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(style);

// 导出函数供其他脚本使用
window.Lingchu = {
    showAlert: showAlert,
    initSmoothScroll: initSmoothScroll
};