/**
 * Components module for interactive UI elements
 */

const Components = (function() {
    /**
     * Initialize all components
     */
    function init() {
        // Initialize components when DOM is loaded
        document.addEventListener('DOMContentLoaded', function() {
            initCountdown();
            initImageSlider();
            initTabs();
            initAccordion();
            initStickyElements();
            initFilterToggle();
            initQuantitySelector();
            initMasonryGrid();
            initSmoothScroll();
            initBackToTop();
            initTourMap();
        });
    }
    
    /**
     * Initialize countdown timer
     */
    function initCountdown() {
        const countdownElements = document.querySelectorAll('.countdown');
        
        countdownElements.forEach(element => {
            const targetDate = new Date(element.dataset.targetDate).getTime();
            
            if (isNaN(targetDate)) return;
            
            const daysElement = element.querySelector('.countdown__days');
            const hoursElement = element.querySelector('.countdown__hours');
            const minutesElement = element.querySelector('.countdown__minutes');
            const secondsElement = element.querySelector('.countdown__seconds');
            
            // Update the countdown every second
            const interval = setInterval(() => {
                // Get current date and time
                const now = new Date().getTime();
                
                // Calculate the time remaining
                const timeRemaining = targetDate - now;
                
                // If the countdown is over, clear the interval
                if (timeRemaining < 0) {
                    clearInterval(interval);
                    element.classList.add('countdown--expired');
                    return;
                }
                
                // Calculate days, hours, minutes, and seconds
                const days = Math.floor(timeRemaining / (1000 * 60 * 60 * 24));
                const hours = Math.floor((timeRemaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                const minutes = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((timeRemaining % (1000 * 60)) / 1000);
                
                // Update the elements
                if (daysElement) daysElement.textContent = days.toString().padStart(2, '0');
                if (hoursElement) hoursElement.textContent = hours.toString().padStart(2, '0');
                if (minutesElement) minutesElement.textContent = minutes.toString().padStart(2, '0');
                if (secondsElement) secondsElement.textContent = seconds.toString().padStart(2, '0');
            }, 1000);
        });
    }
    
    /**
     * Initialize image slider
     */
    function initImageSlider() {
        const sliders = document.querySelectorAll('.image-slider');
        
        sliders.forEach(slider => {
            const slidesContainer = slider.querySelector('.image-slider__slides');
            const slides = slider.querySelectorAll('.image-slider__slide');
            const prevButton = slider.querySelector('.image-slider__prev');
            const nextButton = slider.querySelector('.image-slider__next');
            const pagination = slider.querySelector('.image-slider__pagination');
            
            if (!slidesContainer || slides.length === 0) return;
            
            let currentSlide = 0;
            const totalSlides = slides.length;
            
            // Create pagination dots
            if (pagination) {
                for (let i = 0; i < totalSlides; i++) {
                    const dot = document.createElement('button');
                    dot.classList.add('image-slider__dot');
                    dot.setAttribute('aria-label', `Slide ${i + 1}`);
                    dot.addEventListener('click', () => goToSlide(i));
                    pagination.appendChild(dot);
                }
            }
            
            // Go to a specific slide
            function goToSlide(index) {
                currentSlide = index;
                updateSlider();
            }
            
            // Go to the next slide
            function nextSlide() {
                currentSlide = (currentSlide + 1) % totalSlides;
                updateSlider();
            }
            
            // Go to the previous slide
            function prevSlide() {
                currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
                updateSlider();
            }
            
            // Update the slider
            function updateSlider() {
                // Update slides position
                slidesContainer.style.transform = `translateX(-${currentSlide * 100}%)`;
                
                // Update pagination dots
                if (pagination) {
                    const dots = pagination.querySelectorAll('.image-slider__dot');
                    dots.forEach((dot, index) => {
                        if (index === currentSlide) {
                            dot.classList.add('active');
                            dot.setAttribute('aria-current', 'true');
                        } else {
                            dot.classList.remove('active');
                            dot.removeAttribute('aria-current');
                        }
                    });
                }
            }
            
            // Add event listeners
            if (prevButton) {
                prevButton.addEventListener('click', prevSlide);
            }
            
            if (nextButton) {
                nextButton.addEventListener('click', nextSlide);
            }
            
            // Touch events for mobile
            let touchStartX = 0;
            let touchEndX = 0;
            
            slidesContainer.addEventListener('touchstart', e => {
                touchStartX = e.changedTouches[0].screenX;
            });
            
            slidesContainer.addEventListener('touchend', e => {
                touchEndX = e.changedTouches[0].screenX;
                handleSwipe();
            });
            
            function handleSwipe() {
                const threshold = 50; // Minimum distance for swipe
                
                if (touchEndX < touchStartX - threshold) {
                    // Swipe left, go to next slide
                    nextSlide();
                } else if (touchEndX > touchStartX + threshold) {
                    // Swipe right, go to previous slide
                    prevSlide();
                }
            }
            
            // Initialize the slider
            updateSlider();
            
            // Auto-advance slides if data-auto-slide is set
            if (slider.hasAttribute('data-auto-slide')) {
                const interval = parseInt(slider.dataset.autoSlide) || 5000;
                setInterval(nextSlide, interval);
            }
        });
    }
    
    /**
     * Initialize tabs
     */
    function initTabs() {
        const tabContainers = document.querySelectorAll('.tabs');
        
        tabContainers.forEach(container => {
            const tabButtons = container.querySelectorAll('.tabs__button');
            const tabPanels = container.querySelectorAll('.tabs__panel');
            
            if (tabButtons.length === 0 || tabPanels.length === 0) return;
            
            // Add click event to tab buttons
            tabButtons.forEach(button => {
                button.addEventListener('click', () => {
                    const tabId = button.getAttribute('aria-controls');
                    
                    // Deactivate all tabs
                    tabButtons.forEach(btn => {
                        btn.classList.remove('active');
                        btn.setAttribute('aria-selected', 'false');
                    });
                    
                    tabPanels.forEach(panel => {
                        panel.classList.remove('active');
                        panel.setAttribute('aria-hidden', 'true');
                    });
                    
                    // Activate the selected tab
                    button.classList.add('active');
                    button.setAttribute('aria-selected', 'true');
                    
                    const panel = container.querySelector(`#${tabId}`);
                    if (panel) {
                        panel.classList.add('active');
                        panel.setAttribute('aria-hidden', 'false');
                    }
                });
            });
            
            // Activate the first tab by default
            if (tabButtons[0]) {
                tabButtons[0].click();
            }
        });
    }
    
    /**
     * Initialize accordion
     */
    function initAccordion() {
        const accordions = document.querySelectorAll('.accordion');
        
        accordions.forEach(accordion => {
            const items = accordion.querySelectorAll('.accordion__item');
            
            items.forEach(item => {
                const header = item.querySelector('.accordion__header');
                const content = item.querySelector('.accordion__content');
                
                if (!header || !content) return;
                
                header.addEventListener('click', () => {
                    // Check if accordion is set to allow multiple open items
                    const allowMultiple = accordion.hasAttribute('data-allow-multiple');
                    
                    // If not allowing multiple, close all other items
                    if (!allowMultiple) {
                        items.forEach(otherItem => {
                            if (otherItem !== item && otherItem.classList.contains('active')) {
                                otherItem.classList.remove('active');
                                const otherContent = otherItem.querySelector('.accordion__content');
                                if (otherContent) {
                                    otherContent.style.maxHeight = '0';
                                }
                            }
                        });
                    }
                    
                    // Toggle the clicked item
                    item.classList.toggle('active');
                    
                    if (item.classList.contains('active')) {
                        content.style.maxHeight = content.scrollHeight + 'px';
                    } else {
                        content.style.maxHeight = '0';
                    }
                });
                
                // Initialize content height
                if (item.classList.contains('active')) {
                    content.style.maxHeight = content.scrollHeight + 'px';
                } else {
                    content.style.maxHeight = '0';
                }
            });
        });
    }
    
    /**
     * Initialize sticky elements
     */
    function initStickyElements() {
        const stickyElements = document.querySelectorAll('.sticky-element');
        
        stickyElements.forEach(element => {
            const offsetTop = parseInt(element.dataset.offsetTop) || 0;
            const container = document.querySelector(element.dataset.container);
            
            if (!container) return;
            
            const originalTop = element.getBoundingClientRect().top + window.pageYOffset;
            
            window.addEventListener('scroll', () => {
                const containerRect = container.getBoundingClientRect();
                const containerBottom = containerRect.bottom + window.pageYOffset;
                const elementHeight = element.offsetHeight;
                
                if (window.pageYOffset > originalTop - offsetTop) {
                    // Check if the element should be fixed or absolute
                    if (window.pageYOffset + elementHeight + offsetTop > containerBottom) {
                        // Position absolute at the bottom of the container
                        element.style.position = 'absolute';
                        element.style.top = 'auto';
                        element.style.bottom = '0';
                    } else {
                        // Position fixed
                        element.style.position = 'fixed';
                        element.style.top = offsetTop + 'px';
                        element.style.bottom = 'auto';
                    }
                } else {
                    // Reset position
                    element.style.position = '';
                    element.style.top = '';
                    element.style.bottom = '';
                }
            });
        });
    }
    
    /**
     * Initialize filter toggle for mobile
     */
    function initFilterToggle() {
        const filterToggles = document.querySelectorAll('.filter-toggle');
        
        filterToggles.forEach(toggle => {
            const targetId = toggle.getAttribute('data-target');
            const target = document.getElementById(targetId);
            
            if (!target) return;
            
            toggle.addEventListener('click', () => {
                target.classList.toggle('active');
                
                // Update aria attributes
                const expanded = target.classList.contains('active');
                toggle.setAttribute('aria-expanded', expanded.toString());
                target.setAttribute('aria-hidden', (!expanded).toString());
                
                // Update toggle text if needed
                const textElement = toggle.querySelector('.filter-toggle__text');
                if (textElement) {
                    const showText = toggle.getAttribute('data-show-text') || 'Show Filters';
                    const hideText = toggle.getAttribute('data-hide-text') || 'Hide Filters';
                    textElement.textContent = expanded ? hideText : showText;
                }
            });
        });
    }
    
    /**
     * Initialize quantity selector
     */
    function initQuantitySelector() {
        const quantitySelectors = document.querySelectorAll('.quantity-selector');
        
        quantitySelectors.forEach(selector => {
            const input = selector.querySelector('.quantity-selector__input');
            const decrementBtn = selector.querySelector('.quantity-selector__decrement');
            const incrementBtn = selector.querySelector('.quantity-selector__increment');
            
            if (!input || !decrementBtn || !incrementBtn) return;
            
            const min = parseInt(input.getAttribute('min')) || 1;
            const max = parseInt(input.getAttribute('max')) || Infinity;
            const step = parseInt(input.getAttribute('step')) || 1;
            
            decrementBtn.addEventListener('click', () => {
                const currentValue = parseInt(input.value) || 0;
                const newValue = Math.max(currentValue - step, min);
                input.value = newValue;
                input.dispatchEvent(new Event('change'));
                
                // Update button state
                decrementBtn.disabled = newValue <= min;
                incrementBtn.disabled = newValue >= max;
            });
            
            incrementBtn.addEventListener('click', () => {
                const currentValue = parseInt(input.value) || 0;
                const newValue = Math.min(currentValue + step, max);
                input.value = newValue;
                input.dispatchEvent(new Event('change'));
                
                // Update button state
                decrementBtn.disabled = newValue <= min;
                incrementBtn.disabled = newValue >= max;
            });
            
            // Initialize button state
            const currentValue = parseInt(input.value) || 0;
            decrementBtn.disabled = currentValue <= min;
            incrementBtn.disabled = currentValue >= max;
        });
    }
    
    /**
     * Initialize masonry grid
     */
    function initMasonryGrid() {
        const masonryGrids = document.querySelectorAll('.masonry-grid');
        
        masonryGrids.forEach(grid => {
            const items = grid.querySelectorAll('.masonry-grid__item');
            
            if (items.length === 0) return;
            
            // Simple masonry layout using CSS grid
            const updateLayout = () => {
                const columns = parseInt(getComputedStyle(grid).getPropertyValue('--masonry-columns')) || 3;
                
                // Reset heights
                grid.style.gridTemplateRows = '';
                
                // Get the computed column width
                const columnWidth = grid.offsetWidth / columns;
                
                // Calculate item positions
                const columnHeights = Array(columns).fill(0);
                
                items.forEach(item => {
                    // Find the column with the minimum height
                    const minHeightColumn = columnHeights.indexOf(Math.min(...columnHeights));
                    
                    // Position the item
                    item.style.gridColumn = minHeightColumn + 1;
                    item.style.gridRow = columnHeights[minHeightColumn] + 1;
                    
                    // Update the column height
                    columnHeights[minHeightColumn] += 1;
                });
                
                // Set the grid height
                grid.style.gridTemplateRows = `repeat(${Math.max(...columnHeights)}, auto)`;
            };
            
            // Initialize layout
            updateLayout();
            
            // Update layout when window is resized
            window.addEventListener('resize', updateLayout);
            
            // Update layout when images are loaded
            const images = grid.querySelectorAll('img');
            if (images.length > 0) {
                images.forEach(img => {
                    if (img.complete) {
                        updateLayout();
                    } else {
                        img.addEventListener('load', updateLayout);
                    }
                });
            }
        });
    }
    
    /**
     * Initialize smooth scroll for anchor links
     */
    function initSmoothScroll() {
        const anchorLinks = document.querySelectorAll('a[href^="#"]:not([href="#"])');
        
        anchorLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                
                const targetId = link.getAttribute('href');
                const targetElement = document.querySelector(targetId);
                
                if (targetElement) {
                    const headerOffset = 80; // Adjust for fixed header if needed
                    const elementPosition = targetElement.getBoundingClientRect().top;
                    const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                    
                    window.scrollTo({
                        top: offsetPosition,
                        behavior: 'smooth'
                    });
                    
                    // Update URL hash without scrolling
                    history.pushState(null, null, targetId);
                }
            });
        });
    }
    
    /**
     * Initialize back to top button
     */
    function initBackToTop() {
        const backToTopButton = document.querySelector('.back-to-top');
        
        if (!backToTopButton) return;
        
        // Show/hide the button based on scroll position
        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 300) {
                backToTopButton.classList.add('active');
            } else {
                backToTopButton.classList.remove('active');
            }
        });
        
        // Scroll to top when clicked
        backToTopButton.addEventListener('click', (e) => {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    /**
     * Initialize tour map
     */
    function initTourMap() {
        const mapContainers = document.querySelectorAll('.tour-map');
        
        mapContainers.forEach(container => {
            // Check if the map library is loaded
            if (typeof L === 'undefined') return;
            
            const latitude = parseFloat(container.dataset.lat);
            const longitude = parseFloat(container.dataset.lng);
            const zoom = parseInt(container.dataset.zoom) || 13;
            
            if (isNaN(latitude) || isNaN(longitude)) return;
            
            // Initialize the map
            const map = L.map(container).setView([latitude, longitude], zoom);
            
            // Add tile layer (OpenStreetMap)
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            }).addTo(map);
            
            // Add marker
            L.marker([latitude, longitude]).addTo(map);
        });
    }
    
    // Public API
    return {
        init,
        initCountdown,
        initImageSlider,
        initTabs,
        initAccordion,
        initStickyElements,
        initFilterToggle,
        initQuantitySelector,
        initMasonryGrid,
        initSmoothScroll,
        initBackToTop,
        initTourMap
    };
})();

// Initialize components
Components.init();

// Export the Components module
window.Components = Components; 