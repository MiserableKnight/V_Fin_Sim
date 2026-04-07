/**
 * Apple-inspired Interactions
 * 滚动动画 · 平滑过渡 · 细腻交互
 */

(function() {
    'use strict';

    // ============================================
    // SCROLL REVEAL ANIMATION (滚动显示动画)
    // ============================================
    class ScrollReveal {
        constructor(options = {}) {
            this.threshold = options.threshold || 0.1;
            this.rootMargin = options.rootMargin || '0px 0px -50px 0px';
            this.elements = [];
            this.init();
        }

        init() {
            // Create intersection observer
            this.observer = new IntersectionObserver(
                (entries) => this.handleIntersection(entries),
                {
                    threshold: this.threshold,
                    rootMargin: this.rootMargin
                }
            );

            // Observe all reveal elements
            this.refresh();

            // Initial check for elements already in view
            this.checkInitial();
        }

        refresh() {
            // Disconnect previous observations
            this.observer.disconnect();

            // Find all elements to reveal
            const elements = document.querySelectorAll('.apple-scroll-reveal');
            elements.forEach(el => this.observer.observe(el));
            this.elements = Array.from(elements);
        }

        handleIntersection(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');

                    // Optional: unobserve after revealing
                    // this.observer.unobserve(entry.target);
                }
            });
        }

        checkInitial() {
            const elements = document.querySelectorAll('.apple-scroll-reveal');
            elements.forEach(el => {
                const rect = el.getBoundingClientRect();
                if (rect.top < window.innerHeight - 100) {
                    el.classList.add('visible');
                }
            });
        }
    }

    // ============================================
    // GLASS NAVIGATION (毛玻璃导航)
    // ============================================
    class GlassNav {
        constructor() {
            this.nav = document.querySelector('.apple-nav');
            this.scrollThreshold = 10;
            this.lastScrollY = 0;
            this.init();
        }

        init() {
            if (!this.nav) return;

            window.addEventListener('scroll', () => this.handleScroll(), { passive: true });
            this.handleScroll(); // Initial check
        }

        handleScroll() {
            const scrollY = window.scrollY;

            // Add/remove scrolled class
            if (scrollY > this.scrollThreshold) {
                this.nav.classList.add('scrolled');
            } else {
                this.nav.classList.remove('scrolled');
            }

            this.lastScrollY = scrollY;
        }
    }

    // ============================================
    // SMOOTH SCROLL (平滑滚动)
    // ============================================
    class SmoothScroll {
        constructor() {
            this.init();
        }

        init() {
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', (e) => this.handleClick(e));
            });
        }

        handleClick(e) {
            const anchor = e.currentTarget;
            const href = anchor.getAttribute('href');

            // Skip empty or external links
            if (!href || href === '#' || href.startsWith('#!')) return;

            const target = document.querySelector(href);
            if (!target) return;

            e.preventDefault();
            this.scrollTo(target);
        }

        scrollTo(target, offset = 60) {
            const targetPosition = target.getBoundingClientRect().top + window.scrollY - offset;

            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    }

    // ============================================
    // PARALLAX EFFECT (视差效果)
    // ============================================
    class Parallax {
        constructor(options = {}) {
            this.speed = options.speed || 0.5;
            this.elements = [];
            this.init();
        }

        init() {
            window.addEventListener('scroll', () => this.handleScroll(), { passive: true });
            this.refresh();
        }

        refresh() {
            this.elements = Array.from(document.querySelectorAll('[data-parallax]'));
        }

        handleScroll() {
            const scrollY = window.scrollY;

            this.elements.forEach(el => {
                const speed = parseFloat(el.dataset.parallax) || this.speed;
                const yPos = -(scrollY * speed);
                el.style.transform = `translateY(${yPos}px)`;
            });
        }
    }

    // ============================================
    // METRIC COUNTER ANIMATION (数字计数动画)
    // ============================================
    class CounterAnimation {
        constructor(options = {}) {
            this.duration = options.duration || 1000;
            this.init();
        }

        init() {
            const counters = document.querySelectorAll('[data-count]');
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.animate(entry.target);
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.5 });

            counters.forEach(counter => observer.observe(counter));
        }

        animate(element) {
            const target = parseFloat(element.dataset.count);
            const startTime = performance.now();
            const startValue = 0;
            const hasDecimal = target % 1 !== 0;

            const update = (currentTime) => {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / this.duration, 1);

                // Easing function (easeOutExpo)
                const eased = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);

                const current = startValue + (target - startValue) * eased;

                element.textContent = hasDecimal ? current.toFixed(1) : Math.round(current);

                if (progress < 1) {
                    requestAnimationFrame(update);
                } else {
                    element.textContent = hasDecimal ? target.toFixed(1) : target;
                }
            };

            requestAnimationFrame(update);
        }
    }

    // ============================================
    // CARD HOVER EFFECT (卡片悬停效果)
    // ============================================
    class CardHover {
        constructor() {
            this.init();
        }

        init() {
            const cards = document.querySelectorAll('.apple-card, .apple-metric, .apple-threshold-card');

            cards.forEach(card => {
                card.addEventListener('mousemove', (e) => this.handleMouseMove(e, card));
                card.addEventListener('mouseleave', (e) => this.handleMouseLeave(e, card));
            });
        }

        handleMouseMove(e, card) {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const rotateX = (y - centerY) / 20;
            const rotateY = (centerX - x) / 20;

            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
        }

        handleMouseLeave(e, card) {
            card.style.transform = '';
        }
    }

    // ============================================
    // LOADING STATE (加载状态)
    // ============================================
    class LoadingState {
        constructor() {
            this.loadingElements = new Set();
            this.init();
        }

        init() {
            // Create loading overlay if it doesn't exist
            this.createOverlay();
        }

        createOverlay() {
            let overlay = document.querySelector('.apple-loading-overlay');
            if (!overlay) {
                overlay = document.createElement('div');
                overlay.className = 'apple-loading-overlay';
                overlay.innerHTML = `
                    <div class="apple-loading-spinner">
                        <div class="spinner-blade"></div><div class="spinner-blade"></div>
                        <div class="spinner-blade"></div><div class="spinner-blade"></div>
                        <div class="spinner-blade"></div><div class="spinner-blade"></div>
                        <div class="spinner-blade"></div><div class="spinner-blade"></div>
                        <div class="spinner-blade"></div><div class="spinner-blade"></div><div class="spinner-blade"></div><div class="spinner-blade"></div>
                    </div>
                `;
                document.body.appendChild(overlay);
            }
        }

        show() {
            const overlay = document.querySelector('.apple-loading-overlay');
            if (overlay) {
                overlay.classList.add('active');
            }
        }

        hide() {
            const overlay = document.querySelector('.apple-loading-overlay');
            if (overlay) {
                overlay.classList.remove('active');
            }
        }
    }

    // ============================================
    // TOOLTIP (工具提示)
    // ============================================
    class Tooltip {
        constructor() {
            this.tooltip = null;
            this.init();
        }

        init() {
            document.querySelectorAll('[data-tooltip]').forEach(el => {
                el.addEventListener('mouseenter', (e) => this.show(e));
                el.addEventListener('mouseleave', () => this.hide());
            });
        }

        show(e) {
            const text = e.target.dataset.tooltip;

            this.tooltip = document.createElement('div');
            this.tooltip.className = 'apple-tooltip';
            this.tooltip.textContent = text;
            document.body.appendChild(this.tooltip);

            const rect = e.target.getBoundingClientRect();
            this.tooltip.style.left = rect.left + (rect.width / 2) - (this.tooltip.offsetWidth / 2) + 'px';
            this.tooltip.style.top = rect.top - this.tooltip.offsetHeight - 8 + 'px';

            requestAnimationFrame(() => {
                this.tooltip.classList.add('visible');
            });
        }

        hide() {
            if (this.tooltip) {
                this.tooltip.classList.remove('visible');
                setTimeout(() => {
                    if (this.tooltip && this.tooltip.parentNode) {
                        this.tooltip.parentNode.removeChild(this.tooltip);
                    }
                    this.tooltip = null;
                }, 200);
            }
        }
    }

    // ============================================
    // STATUS INDICATOR (状态指示器)
    // ============================================
    class StatusIndicator {
        constructor(element, options = {}) {
            this.element = element;
            this.value = options.value || 0;
            this.max = options.max || 100;
            this.thresholds = options.thresholds || [33, 66];
            this.labels = options.labels || ['低', '中', '高'];
            this.render();
        }

        render() {
            const percentage = Math.min((this.value / this.max) * 100, 100);
            let status = 'healthy';

            if (percentage >= this.thresholds[1]) {
                status = 'critical';
            } else if (percentage >= this.thresholds[0]) {
                status = 'warning';
            }

            this.element.innerHTML = `
                <div class="apple-status-indicator">
                    <div class="status-bar">
                        <div class="status-fill status-${status}" style="width: ${percentage}%"></div>
                    </div>
                    <div class="status-label">${this.labels[this.getStatusIndex(percentage)]}</div>
                </div>
            `;
        }

        getStatusIndex(percentage) {
            if (percentage >= this.thresholds[1]) return 2;
            if (percentage >= this.thresholds[0]) return 1;
            return 0;
        }

        update(value) {
            this.value = value;
            this.render();
        }
    }

    // ============================================
    // INITIALIZATION (初始化)
    // ============================================
    const AppleUI = {
        scrollReveal: null,
        glassNav: null,
        smoothScroll: null,
        parallax: null,
        counterAnimation: null,
        cardHover: null,
        loadingState: null,
        tooltip: null,

        init() {
            // Initialize all modules
            this.scrollReveal = new ScrollReveal();
            this.glassNav = new GlassNav();
            this.smoothScroll = new SmoothScroll();
            this.counterAnimation = new CounterAnimation({ duration: 1500 });
            this.cardHover = new CardHover();
            this.loadingState = new LoadingState();
            this.tooltip = new Tooltip();

            // Listen for DOM changes
            this.observeChanges();

            // Expose StatusIndicator
            this.StatusIndicator = StatusIndicator;

            console.log('Apple UI initialized');
        },

        observeChanges() {
            // Re-initialize scroll reveal when DOM changes
            const observer = new MutationObserver(() => {
                if (this.scrollReveal) {
                    this.scrollReveal.refresh();
                }
            });

            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        },

        refresh() {
            if (this.scrollReveal) {
                this.scrollReveal.refresh();
            }
        }
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => AppleUI.init());
    } else {
        AppleUI.init();
    }

    // Expose globally
    window.AppleUI = AppleUI;

})();
