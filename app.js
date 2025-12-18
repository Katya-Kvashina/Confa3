// app.js - Основная клиентская логика приложения

class F1App {
    constructor() {
        this.init();
    }

    init() {
        // Инициализация всех модулей
        this.initNotifications();
        this.initCountdown();
        this.initInteractiveElements();
        this.initLazyLoading();
        this.initFormValidation();
        this.initStatistics();
        this.initGalleryLightbox();
        this.initMobileOptimizations();
        this.initPerformanceMonitoring();
    }

    initNotifications() {
        const notificationBell = document.querySelector('.notification-bell');
        const notificationCount = document.querySelector('.notification-count');
        
        if (notificationBell) {
            notificationBell.addEventListener('click', (e) => {
                e.stopPropagation();
                const dropdown = document.querySelector('.notification-dropdown');
                dropdown.classList.toggle('show');
                
                // Сброс счетчика уведомлений
                if (notificationCount) {
                    notificationCount.textContent = '0';
                    notificationCount.style.display = 'none';
                }
            });
            
            // Закрытие при клике вне уведомлений
            document.addEventListener('click', () => {
                const dropdown = document.querySelector('.notification-dropdown');
                dropdown.classList.remove('show');
            });
        }
    }

    initCountdown() {
        // Следующий Гран-при - Бахрейн 11 марта 2025
        const nextRaceDate = new Date('2025-03-11T16:00:00').getTime();
        
        const updateCountdown = () => {
            const now = new Date().getTime();
            const timeLeft = nextRaceDate - now;
            
            if (timeLeft > 0) {
                const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
                const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);
                
                // Обновляем элементы с countdown
                document.querySelectorAll('.countdown').forEach(element => {
                    element.innerHTML = `
                        <div class="countdown-item">
                            <span class="countdown-value">${days}</span>
                            <span class="countdown-label">дней</span>
                        </div>
                        <div class="countdown-item">
                            <span class="countdown-value">${hours}</span>
                            <span class="countdown-label">часов</span>
                        </div>
                        <div class="countdown-item">
                            <span class="countdown-value">${minutes}</span>
                            <span class="countdown-label">минут</span>
                        </div>
                        <div class="countdown-item">
                            <span class="countdown-value">${seconds}</span>
                            <span class="countdown-label">секунд</span>
                        </div>
                    `;
                });
            } else {
                document.querySelectorAll('.countdown').forEach(element => {
                    element.innerHTML = '<span style="color: var(--primary-color); font-weight: bold;">ГОНКА НАЧАЛАСЬ!</span>';
                });
            }
        };
        
        // Создаем счетчик, если его нет на странице
        if (!document.querySelector('.countdown')) {
            const countdownElement = document.createElement('div');
            countdownElement.className = 'countdown';
            countdownElement.style.cssText = `
                display: flex;
                gap: 10px;
                justify-content: center;
                margin: 20px 0;
                padding: 15px;
                background: var(--secondary-color);
                color: white;
                border-radius: var(--border-radius);
                font-family: monospace;
                font-size: 1.2rem;
            `;
            
            // Добавляем на главную страницу в герой-секцию
            const heroSection = document.querySelector('.hero-section .hero-content');
            if (heroSection) {
                heroSection.appendChild(countdownElement);
            }
        }
        
        // Обновляем каждую секунду
        updateCountdown();
        setInterval(updateCountdown, 1000);
    }

    initInteractiveElements() {
        // Анимация кнопок
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('mousedown', () => {
                btn.style.transform = 'scale(0.95)';
            });
            
            btn.addEventListener('mouseup', () => {
                btn.style.transform = '';
            });
            
            btn.addEventListener('mouseleave', () => {
                btn.style.transform = '';
            });
        });

        // Интерактивные карточки
        document.querySelectorAll('.card, .news-card, .page-card').forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-10px)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = '';
            });
        });

        // Параллакс эффект для герой-секции
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const heroSection = document.querySelector('.hero-section');
            if (heroSection) {
                const rate = scrolled * -0.5;
                heroSection.style.backgroundPositionY = `${rate}px`;
            }
        });
    }

    initLazyLoading() {
        // Lazy loading для изображений
        const images = document.querySelectorAll('img[data-src], img[src*="нтернет-ресурсы"]');
        
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    const src = img.getAttribute('data-src') || img.src;
                    
                    // Загружаем изображение
                    img.src = src;
                    img.classList.add('loaded');
                    
                    // Убираем observer после загрузки
                    observer.unobserve(img);
                }
            });
        }, {
            rootMargin: '50px',
            threshold: 0.1
        });

        images.forEach(img => {
            // Добавляем placeholder
            if (!img.hasAttribute('data-src')) {
                img.setAttribute('data-src', img.src);
                img.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200"%3E%3Crect width="300" height="200" fill="%23f0f0f0"/%3E%3Ctext x="50%" y="50%" font-family="Arial" font-size="14" fill="%23999" text-anchor="middle" dy=".3em"%3EЗагрузка...%3C/text%3E%3C/svg%3E';
            }
            imageObserver.observe(img);
        });
    }

    initFormValidation() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                let isValid = true;
                const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
                
                inputs.forEach(input => {
                    if (!input.value.trim()) {
                        isValid = false;
                        input.style.borderColor = 'var(--primary-color)';
                        
                        // Создаем сообщение об ошибке
                        const errorMsg = document.createElement('div');
                        errorMsg.className = 'error-message';
                        errorMsg.textContent = 'Это поле обязательно для заполнения';
                        errorMsg.style.cssText = `
                            color: var(--primary-color);
                            font-size: 0.8rem;
                            margin-top: 5px;
                        `;
                        
                        // Удаляем старое сообщение
                        const oldError = input.nextElementSibling;
                        if (oldError && oldError.className === 'error-message') {
                            oldError.remove();
                        }
                        
                        input.parentNode.insertBefore(errorMsg, input.nextSibling);
                    } else {
                        input.style.borderColor = '';
                        const errorMsg = input.nextElementSibling;
                        if (errorMsg && errorMsg.className === 'error-message') {
                            errorMsg.remove();
                        }
                    }
                });
                
                if (!isValid) {
                    e.preventDefault();
                    this.showToast('Пожалуйста, заполните все обязательные поля');
                }
            });
        });
    }

    initStatistics() {
        // Динамическое обновление статистики
        const updateStats = () => {
            // Здесь можно добавить загрузку реальных данных через API
            const stats = {
                nextRace: 'Бахрейн',
                daysLeft: 45,
                activeUsers: 1243,
                topDriver: 'Макс Ферстаппен'
            };
            
            document.querySelectorAll('.stats-item').forEach(item => {
                const statType = item.getAttribute('data-stat');
                if (stats[statType]) {
                    item.textContent = stats[statType];
                }
            });
        };
        
        // Обновляем статистику каждые 5 минут
        updateStats();
        setInterval(updateStats, 300000);
    }

    initGalleryLightbox() {
        const galleryItems = document.querySelectorAll('.gallery-item');
        
        galleryItems.forEach(item => {
            item.addEventListener('click', () => {
                const imgSrc = item.querySelector('img').src;
                const title = item.querySelector('h3')?.textContent || '';
                
                this.openLightbox(imgSrc, title);
            });
        });
        
        // Закрытие по ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeLightbox();
            }
        });
    }

    openLightbox(imgSrc, title) {
        const lightbox = document.createElement('div');
        lightbox.id = 'lightbox';
        lightbox.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.9);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        
        lightbox.innerHTML = `
            <div class="lightbox-content" style="max-width: 90%; max-height: 90%; position: relative;">
                <img src="${imgSrc}" alt="${title}" style="max-width: 100%; max-height: 100%;">
                <div style="color: white; text-align: center; margin-top: 10px;">${title}</div>
                <button class="lightbox-close" style="position: absolute; top: -40px; right: 0; background: none; border: none; color: white; font-size: 2rem; cursor: pointer;">×</button>
            </div>
        `;
        
        document.body.appendChild(lightbox);
        
        // Анимация появления
        setTimeout(() => {
            lightbox.style.opacity = '1';
        }, 10);
        
        // Закрытие
        lightbox.querySelector('.lightbox-close').addEventListener('click', () => {
            this.closeLightbox();
        });
        
        lightbox.addEventListener('click', (e) => {
            if (e.target === lightbox) {
                this.closeLightbox();
            }
        });
    }

    closeLightbox() {
        const lightbox = document.getElementById('lightbox');
        if (lightbox) {
            lightbox.style.opacity = '0';
            setTimeout(() => {
                lightbox.remove();
            }, 300);
        }
    }

    initMobileOptimizations() {
        // Оптимизация для мобильных устройств
        if ('ontouchstart' in window) {
            // Увеличиваем области клика для сенсорных устройств
            document.querySelectorAll('button, a').forEach(element => {
                element.style.minHeight = '44px';
                element.style.minWidth = '44px';
                element.style.padding = '12px';
            });
            
            // Отключаем hover-эффекты на мобильных
            document.body.classList.add('touch-device');
        }
        
        // Определяем тип устройства
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        
        if (isMobile) {
            // Оптимизация для медленных сетей
            this.enableDataSaverMode();
        }
    }

    enableDataSaverMode() {
        const dataSaver = localStorage.getItem('data-saver') === 'true';
        
        if (dataSaver || navigator.connection?.saveData) {
            // Отключаем тяжелые анимации
            document.body.classList.add('data-saver');
            
            // Заменяем GIF на статические изображения
            document.querySelectorAll('img[src$=".gif"]').forEach(img => {
                const staticSrc = img.src.replace('.gif', '.jpg');
                img.src = staticSrc;
            });
        }
    }

    initPerformanceMonitoring() {
        // Мониторинг производительности
        if ('performance' in window) {
            window.addEventListener('load', () => {
                const timing = performance.timing;
                const loadTime = timing.loadEventEnd - timing.navigationStart;
                
                console.log(`Время загрузки страницы: ${loadTime}ms`);
                
                // Отправляем метрики (в реальном приложении отправляем на сервер)
                if (loadTime > 3000) {
                    console.warn('Медленная загрузка страницы');
                }
            });
        }
        
        // Предзагрузка критических ресурсов
        this.preloadCriticalResources();
    }

    preloadCriticalResources() {
        const criticalResources = [
            'index.css',
            'theme.js',
            'app.js'
        ];
        
        criticalResources.forEach(resource => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.href = resource;
            link.as = resource.endsWith('.css') ? 'style' : 'script';
            document.head.appendChild(link);
        });
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%) translateY(100px);
            background: ${type === 'error' ? 'var(--primary-color)' : 'var(--secondary-color)'};
            color: white;
            padding: 12px 24px;
            border-radius: var(--border-radius);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 10000;
            transition: transform 0.3s ease;
            max-width: 80%;
            text-align: center;
        `;
        
        document.body.appendChild(toast);
        
        // Анимация появления
        setTimeout(() => {
            toast.style.transform = 'translateX(-50%) translateY(0)';
        }, 10);
        
        // Автоматическое скрытие
        setTimeout(() => {
            toast.style.transform = 'translateX(-50%) translateY(100px)';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// Инициализация приложения
document.addEventListener('DOMContentLoaded', () => {
    window.f1App = new F1App();
});

// Service Worker для PWA
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js').then(registration => {
            console.log('ServiceWorker зарегистрирован:', registration);
        }).catch(error => {
            console.log('Ошибка регистрации ServiceWorker:', error);
        });
    });
}

// Обработка офлайн-режима
window.addEventListener('online', () => {
    window.f1App?.showToast('Соединение восстановлено', 'info');
});

window.addEventListener('offline', () => {
    window.f1App?.showToast('Работаем в офлайн-режиме', 'error');
});