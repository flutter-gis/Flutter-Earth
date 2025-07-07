/**
 * Enhanced Theme Effects v2.0
 * Advanced theming system with dynamic effects and modern animations
 */

class EnhancedThemeEffects {
    constructor() {
        this.currentTheme = 'default';
        this.themes = new Map();
        this.effects = new Map();
        this.animations = new Map();
        this.particles = [];
        this.isInitialized = false;
        
        this.initializeThemes();
        this.setupEventListeners();
        this.loadThemeFromStorage();
    }

    /**
     * Initialize available themes
     */
    initializeThemes() {
        // Default themes
        this.registerTheme('default', {
            name: 'Default',
            description: 'Clean and modern default theme',
            colors: {
                primary: '#4A90E2',
                primaryDark: '#357ABD',
                primaryLight: '#7BB3F0',
                accent: '#50C878',
                accentDark: '#3DA066',
                background: '#f8f9fa',
                backgroundDark: '#2c3e50',
                backgroundLight: '#ffffff',
                widgetBg: '#ffffff',
                widgetBgDark: '#34495e',
                widgetBorder: '#e9ecef',
                widgetBorderDark: '#4a5568',
                text: '#212529',
                textDark: '#ecf0f1',
                textSubtle: '#6c757d',
                textSubtleDark: '#bdc3c7',
                success: '#28a745',
                error: '#dc3545',
                warning: '#ffc107',
                info: '#17a2b8'
            },
            effects: {
                shadows: true,
                gradients: true,
                animations: true,
                particles: false,
                blur: false
            }
        });

        this.registerTheme('dark', {
            name: 'Dark Mode',
            description: 'Elegant dark theme for low-light environments',
            colors: {
                primary: '#64B5F6',
                primaryDark: '#42A5F5',
                primaryLight: '#90CAF9',
                accent: '#81C784',
                accentDark: '#66BB6A',
                background: '#1a1a1a',
                backgroundDark: '#0d0d0d',
                backgroundLight: '#2d2d2d',
                widgetBg: '#2d2d2d',
                widgetBgDark: '#1a1a1a',
                widgetBorder: '#404040',
                widgetBorderDark: '#2d2d2d',
                text: '#ffffff',
                textDark: '#ffffff',
                textSubtle: '#b0b0b0',
                textSubtleDark: '#808080',
                success: '#4CAF50',
                error: '#F44336',
                warning: '#FF9800',
                info: '#2196F3'
            },
            effects: {
                shadows: true,
                gradients: true,
                animations: true,
                particles: true,
                blur: true
            }
        });

        this.registerTheme('nature', {
            name: 'Nature',
            description: 'Inspired by natural landscapes and earth tones',
            colors: {
                primary: '#2E7D32',
                primaryDark: '#1B5E20',
                primaryLight: '#4CAF50',
                accent: '#8BC34A',
                accentDark: '#689F38',
                background: '#F1F8E9',
                backgroundDark: '#C5E1A5',
                backgroundLight: '#FFFFFF',
                widgetBg: '#FFFFFF',
                widgetBgDark: '#E8F5E8',
                widgetBorder: '#C8E6C9',
                widgetBorderDark: '#A5D6A7',
                text: '#2E7D32',
                textDark: '#1B5E20',
                textSubtle: '#558B2F',
                textSubtleDark: '#33691E',
                success: '#4CAF50',
                error: '#D32F2F',
                warning: '#FF8F00',
                info: '#1976D2'
            },
            effects: {
                shadows: true,
                gradients: true,
                animations: true,
                particles: true,
                blur: false
            }
        });

        this.registerTheme('ocean', {
            name: 'Ocean',
            description: 'Deep blue ocean-inspired theme',
            colors: {
                primary: '#0277BD',
                primaryDark: '#01579B',
                primaryLight: '#039BE5',
                accent: '#00BCD4',
                accentDark: '#0097A7',
                background: '#E3F2FD',
                backgroundDark: '#BBDEFB',
                backgroundLight: '#FFFFFF',
                widgetBg: '#FFFFFF',
                widgetBgDark: '#E1F5FE',
                widgetBorder: '#B3E5FC',
                widgetBorderDark: '#81D4FA',
                text: '#0277BD',
                textDark: '#01579B',
                textSubtle: '#0288D1',
                textSubtleDark: '#0277BD',
                success: '#00BCD4',
                error: '#F44336',
                warning: '#FF9800',
                info: '#2196F3'
            },
            effects: {
                shadows: true,
                gradients: true,
                animations: true,
                particles: true,
                blur: true
            }
        });

        this.registerTheme('sunset', {
            name: 'Sunset',
            description: 'Warm sunset colors and gradients',
            colors: {
                primary: '#FF5722',
                primaryDark: '#D84315',
                primaryLight: '#FF8A65',
                accent: '#FF9800',
                accentDark: '#F57C00',
                background: '#FFF3E0',
                backgroundDark: '#FFE0B2',
                backgroundLight: '#FFFFFF',
                widgetBg: '#FFFFFF',
                widgetBgDark: '#FFF8E1',
                widgetBorder: '#FFCC02',
                widgetBorderDark: '#FFB300',
                text: '#E65100',
                textDark: '#BF360C',
                textSubtle: '#F57C00',
                textSubtleDark: '#E65100',
                success: '#4CAF50',
                error: '#D32F2F',
                warning: '#FF9800',
                info: '#2196F3'
            },
            effects: {
                shadows: true,
                gradients: true,
                animations: true,
                particles: true,
                blur: false
            }
        });

        this.registerTheme('minimal', {
            name: 'Minimal',
            description: 'Clean and minimal design',
            colors: {
                primary: '#000000',
                primaryDark: '#000000',
                primaryLight: '#333333',
                accent: '#666666',
                accentDark: '#333333',
                background: '#ffffff',
                backgroundDark: '#f5f5f5',
                backgroundLight: '#ffffff',
                widgetBg: '#ffffff',
                widgetBgDark: '#f5f5f5',
                widgetBorder: '#e0e0e0',
                widgetBorderDark: '#cccccc',
                text: '#000000',
                textDark: '#000000',
                textSubtle: '#666666',
                textSubtleDark: '#999999',
                success: '#000000',
                error: '#000000',
                warning: '#000000',
                info: '#000000'
            },
            effects: {
                shadows: false,
                gradients: false,
                animations: false,
                particles: false,
                blur: false
            }
        });
    }

    /**
     * Register a new theme
     */
    registerTheme(themeId, themeData) {
        this.themes.set(themeId, {
            id: themeId,
            ...themeData
        });
    }

    /**
     * Apply theme to the application
     */
    applyTheme(themeId) {
        const theme = this.themes.get(themeId);
        if (!theme) {
            console.warn('Theme not found:', themeId);
            return;
        }

        this.currentTheme = themeId;
        this.applyColors(theme.colors);
        this.applyEffects(theme.effects);
        this.saveThemeToStorage();
        this.triggerThemeChange(themeId);
    }

    /**
     * Apply color variables
     */
    applyColors(colors) {
        const root = document.documentElement;
        
        Object.entries(colors).forEach(([key, value]) => {
            root.style.setProperty(`--${key}`, value);
        });

        // Apply dark theme class if needed
        if (colors.background === '#1a1a1a' || colors.background === '#0d0d0d') {
            document.documentElement.setAttribute('data-theme', 'dark');
        } else {
            document.documentElement.removeAttribute('data-theme');
        }
    }

    /**
     * Apply theme effects
     */
    applyEffects(effects) {
        // Enable/disable shadows
        if (effects.shadows) {
            document.body.classList.add('theme-shadows');
        } else {
            document.body.classList.remove('theme-shadows');
        }

        // Enable/disable gradients
        if (effects.gradients) {
            document.body.classList.add('theme-gradients');
        } else {
            document.body.classList.remove('theme-gradients');
        }

        // Enable/disable animations
        if (effects.animations) {
            document.body.classList.add('theme-animations');
        } else {
            document.body.classList.remove('theme-animations');
        }

        // Enable/disable particles
        if (effects.particles) {
            this.startParticles();
        } else {
            this.stopParticles();
        }

        // Enable/disable blur effects
        if (effects.blur) {
            document.body.classList.add('theme-blur');
        } else {
            document.body.classList.remove('theme-blur');
        }
    }

    /**
     * Start particle effects
     */
    startParticles() {
        if (this.particles.length > 0) return; // Already running

        const canvas = this.createParticleCanvas();
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const particleCount = 50;
        const particles = [];

        // Create particles
        for (let i = 0; i < particleCount; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                size: Math.random() * 2 + 1,
                opacity: Math.random() * 0.5 + 0.1
            });
        }

        this.particles = particles;

        // Animation loop
        const animate = () => {
            if (this.particles.length === 0) return; // Stop if particles disabled

            ctx.clearRect(0, 0, canvas.width, canvas.height);

            particles.forEach(particle => {
                // Update position
                particle.x += particle.vx;
                particle.y += particle.vy;

                // Wrap around edges
                if (particle.x < 0) particle.x = canvas.width;
                if (particle.x > canvas.width) particle.x = 0;
                if (particle.y < 0) particle.y = canvas.height;
                if (particle.y > canvas.height) particle.y = 0;

                // Draw particle
                ctx.beginPath();
                ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(74, 144, 226, ${particle.opacity})`;
                ctx.fill();
            });

            requestAnimationFrame(animate);
        };

        animate();
    }

    /**
     * Stop particle effects
     */
    stopParticles() {
        this.particles = [];
        const canvas = document.getElementById('particle-canvas');
        if (canvas) {
            canvas.remove();
        }
    }

    /**
     * Create particle canvas
     */
    createParticleCanvas() {
        // Remove existing canvas
        const existingCanvas = document.getElementById('particle-canvas');
        if (existingCanvas) {
            existingCanvas.remove();
        }

        // Create new canvas
        const canvas = document.createElement('canvas');
        canvas.id = 'particle-canvas';
        canvas.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1;
            opacity: 0.3;
        `;

        // Set canvas size
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        document.body.appendChild(canvas);

        // Handle resize
        window.addEventListener('resize', () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        });

        return canvas;
    }

    /**
     * Create animated background
     */
    createAnimatedBackground() {
        const container = document.querySelector('.theme-animated-bg');
        if (!container) return;

        // Create gradient animation
        const gradient = document.createElement('div');
        gradient.className = 'animated-gradient';
        gradient.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(-45deg, var(--primary), var(--accent), var(--primary-light), var(--accent-dark));
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            opacity: 0.1;
            pointer-events: none;
        `;

        container.appendChild(gradient);
    }

    /**
     * Add hover effects to elements
     */
    addHoverEffects() {
        const elements = document.querySelectorAll('.btn, .toolbar-item, .feature-card, .form-section');
        
        elements.forEach(element => {
            element.addEventListener('mouseenter', (e) => {
                this.createRippleEffect(e);
            });
        });
    }

    /**
     * Create ripple effect
     */
    createRippleEffect(event) {
        const element = event.currentTarget;
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;

        const ripple = document.createElement('span');
        ripple.className = 'ripple-effect';
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 0.6s linear;
            pointer-events: none;
        `;

        element.style.position = 'relative';
        element.appendChild(ripple);

        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    /**
     * Add scroll effects
     */
    addScrollEffects() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('scroll-animate');
                }
            });
        }, observerOptions);

        const elements = document.querySelectorAll('.feature-card, .form-section, .progress-item');
        elements.forEach(element => {
            observer.observe(element);
        });
    }

    /**
     * Create theme transition
     */
    createThemeTransition() {
        const overlay = document.createElement('div');
        overlay.className = 'theme-transition-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: var(--primary);
            z-index: 10000;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
        `;

        document.body.appendChild(overlay);

        // Trigger transition
        setTimeout(() => {
            overlay.style.opacity = '1';
        }, 10);

        setTimeout(() => {
            overlay.style.opacity = '0';
            setTimeout(() => {
                overlay.remove();
            }, 300);
        }, 300);
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Theme change events
        document.addEventListener('enhancedTabs:tabActivated', () => {
            this.addHoverEffects();
        });

        // Scroll effects
        window.addEventListener('scroll', () => {
            this.handleScroll();
        });

        // Window resize
        window.addEventListener('resize', () => {
            this.handleResize();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 't') {
                e.preventDefault();
                this.cycleTheme();
            }
        });
    }

    /**
     * Handle scroll events
     */
    handleScroll() {
        const scrolled = window.pageYOffset;
        const parallaxElements = document.querySelectorAll('.parallax');
        
        parallaxElements.forEach(element => {
            const speed = element.dataset.speed || 0.5;
            const yPos = -(scrolled * speed);
            element.style.transform = `translateY(${yPos}px)`;
        });
    }

    /**
     * Handle window resize
     */
    handleResize() {
        // Recreate particle canvas if needed
        if (this.particles.length > 0) {
            this.stopParticles();
            this.startParticles();
        }
    }

    /**
     * Cycle through themes
     */
    cycleTheme() {
        const themeIds = Array.from(this.themes.keys());
        const currentIndex = themeIds.indexOf(this.currentTheme);
        const nextIndex = (currentIndex + 1) % themeIds.length;
        const nextTheme = themeIds[nextIndex];
        
        this.applyTheme(nextTheme);
    }

    /**
     * Load theme from storage
     */
    loadThemeFromStorage() {
        const savedTheme = localStorage.getItem('flutter_earth_theme');
        if (savedTheme && this.themes.has(savedTheme)) {
            this.applyTheme(savedTheme);
        }
    }

    /**
     * Save theme to storage
     */
    saveThemeToStorage() {
        localStorage.setItem('flutter_earth_theme', this.currentTheme);
    }

    /**
     * Trigger theme change event
     */
    triggerThemeChange(themeId) {
        const event = new CustomEvent('themeChanged', {
            detail: { themeId, theme: this.themes.get(themeId) },
            bubbles: true
        });
        document.dispatchEvent(event);
    }

    /**
     * Get current theme
     */
    getCurrentTheme() {
        return this.themes.get(this.currentTheme);
    }

    /**
     * Get all available themes
     */
    getAvailableThemes() {
        return Array.from(this.themes.values());
    }

    /**
     * Initialize theme effects
     */
    initialize() {
        if (this.isInitialized) return;

        this.addHoverEffects();
        this.addScrollEffects();
        this.createAnimatedBackground();
        
        this.isInitialized = true;
        console.log('Enhanced Theme Effects initialized');
    }
}

// Initialize theme effects when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.themeEffects = new EnhancedThemeEffects();
    window.themeEffects.initialize();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EnhancedThemeEffects;
} 