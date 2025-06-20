/**
 * Main JavaScript file for the "Путешествуй по России" travel website
 */

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    initTooltips();
    
    // Initialize Bootstrap popovers
    initPopovers();
    
    // Initialize header scroll effect
    initHeaderScroll();
    
    // Initialize form validation
    initFormValidation();
    
    // Initialize interactive components
    initComponents();
    
    // Initialize image lazy loading
    initLazyLoading();
});

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
}

/**
 * Initialize Bootstrap popovers
 */
function initPopovers() {
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
}

/**
 * Initialize header scroll effect
 */
function initHeaderScroll() {
    const header = document.querySelector('.header');
    if (!header) return;
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            header.classList.add('header--scrolled');
        } else {
            header.classList.remove('header--scrolled');
        }
    });
}

/**
 * Initialize form validation
 */
function initFormValidation() {
    // Get all forms that need validation
    const forms = document.querySelectorAll('.needs-validation');
    
    // Loop over them and prevent submission
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * Initialize all interactive components
 */
function initComponents() {
    // Initialize date pickers
    initDatePickers();
    
    // Initialize number inputs
    initNumberInputs();
    
    // Initialize range sliders
    initRangeSliders();
    
    // Initialize custom select elements
    initCustomSelects();
    
    // Initialize star ratings
    initStarRatings();
    
    // Initialize image galleries
    initImageGalleries();
    
    // Initialize scroll animations
    initScrollAnimations();
}

/**
 * Initialize date pickers
 */
function initDatePickers() {
    const datePickers = document.querySelectorAll('.date-picker');
    if (datePickers.length === 0) return;
    
    // Add date picker initialization if needed
    // This is a placeholder for potential date picker library integration
}

/**
 * Initialize number inputs with increment/decrement buttons
 */
function initNumberInputs() {
    const numberInputs = document.querySelectorAll('.number-input');
    
    numberInputs.forEach(container => {
        const input = container.querySelector('input');
        const decrementBtn = container.querySelector('.number-input__decrement');
        const incrementBtn = container.querySelector('.number-input__increment');
        
        if (!input || !decrementBtn || !incrementBtn) return;
        
        const min = parseInt(input.getAttribute('min')) || 0;
        const max = parseInt(input.getAttribute('max')) || Infinity;
        const step = parseInt(input.getAttribute('step')) || 1;
        
        decrementBtn.addEventListener('click', () => {
            const currentValue = parseInt(input.value) || 0;
            const newValue = Math.max(currentValue - step, min);
            input.value = newValue;
            input.dispatchEvent(new Event('change'));
        });
        
        incrementBtn.addEventListener('click', () => {
            const currentValue = parseInt(input.value) || 0;
            const newValue = Math.min(currentValue + step, max);
            input.value = newValue;
            input.dispatchEvent(new Event('change'));
        });
    });
}

/**
 * Initialize range sliders
 */
function initRangeSliders() {
    const rangeSliders = document.querySelectorAll('.range-slider');
    
    rangeSliders.forEach(slider => {
        const input = slider.querySelector('input[type="range"]');
        const valueDisplay = slider.querySelector('.range-slider__value');
        
        if (!input || !valueDisplay) return;
        
        // Update value display on input change
        input.addEventListener('input', () => {
            valueDisplay.textContent = input.value;
        });
        
        // Initialize value display
        valueDisplay.textContent = input.value;
    });
}

/**
 * Initialize custom select elements
 */
function initCustomSelects() {
    const customSelects = document.querySelectorAll('.custom-select');
    
    customSelects.forEach(select => {
        // Placeholder for custom select initialization
    });
}

/**
 * Initialize interactive star ratings
 */
function initStarRatings() {
    const interactiveRatings = document.querySelectorAll('.star-rating--interactive');
    
    interactiveRatings.forEach(container => {
        const inputGroup = container.querySelector('.star-rating__input-group');
        const inputs = container.querySelectorAll('.star-rating__input');
        
        if (!inputGroup || inputs.length === 0) return;
        
        // Set initial data-rating attribute based on checked input
        inputs.forEach(input => {
            if (input.checked) {
                inputGroup.setAttribute('data-rating', input.value);
            }
            
            // Update data-rating attribute on input change
            input.addEventListener('change', () => {
                inputGroup.setAttribute('data-rating', input.value);
            });
        });
    });
}

/**
 * Initialize image galleries
 */
function initImageGalleries() {
    const galleries = document.querySelectorAll('.image-gallery');
    
    galleries.forEach(gallery => {
        const thumbnails = gallery.querySelectorAll('.image-gallery__thumbnail');
        const mainImage = gallery.querySelector('.image-gallery__main-image');
        
        if (!mainImage || thumbnails.length === 0) return;
        
        thumbnails.forEach(thumbnail => {
            thumbnail.addEventListener('click', () => {
                // Remove active class from all thumbnails
                thumbnails.forEach(t => t.classList.remove('active'));
                
                // Add active class to clicked thumbnail
                thumbnail.classList.add('active');
                
                // Update main image
                const imageUrl = thumbnail.getAttribute('data-image');
                if (imageUrl) {
                    mainImage.src = imageUrl;
                }
            });
        });
    });
}

/**
 * Initialize scroll animations
 */
function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    
    if (animatedElements.length === 0) return;
    
    // Check if element is in viewport
    function isElementInViewport(el) {
        const rect = el.getBoundingClientRect();
        return (
            rect.top <= (window.innerHeight || document.documentElement.clientHeight) * 0.8 &&
            rect.bottom >= 0
        );
    }
    
    // Add animation class when element is in viewport
    function handleScrollAnimation() {
        animatedElements.forEach(element => {
            if (isElementInViewport(element) && !element.classList.contains('animated')) {
                element.classList.add('animated');
            }
        });
    }
    
    // Initial check
    handleScrollAnimation();
    
    // Check on scroll
    window.addEventListener('scroll', handleScrollAnimation);
}

/**
 * Initialize lazy loading for images
 */
function initLazyLoading() {
    // Check if browser supports native lazy loading
    if ('loading' in HTMLImageElement.prototype) {
        // Use native lazy loading
        const lazyImages = document.querySelectorAll('img[loading="lazy"]');
        lazyImages.forEach(img => {
            if (img.dataset.src) {
                img.src = img.dataset.src;
            }
        });
    } else {
        // Fallback for browsers that don't support native lazy loading
        const lazyImages = document.querySelectorAll('.lazy-image');
        
        if (lazyImages.length === 0) return;
        
        // Create IntersectionObserver if supported
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.classList.remove('lazy-image');
                            imageObserver.unobserve(img);
                        }
                    }
                });
            });
            
            lazyImages.forEach(img => {
                imageObserver.observe(img);
            });
        } else {
            // Fallback for browsers that don't support IntersectionObserver
            // Load all images immediately
            lazyImages.forEach(img => {
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.classList.remove('lazy-image');
                }
            });
        }
    }
} 