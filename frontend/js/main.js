// Main JavaScript file for "Путешествуй по России" tourist agency

document.addEventListener('DOMContentLoaded', function() {
    // Fetch popular tours for homepage
    if (document.getElementById('popular-tours')) {
        fetchPopularTours();
    }

    // Initialize login form if it exists
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    // Initialize registration form if it exists
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }

    // Initialize tour search form if it exists
    const searchForm = document.getElementById('tour-search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', handleSearch);
    }

    // Initialize booking form if it exists
    const bookingForm = document.getElementById('booking-form');
    if (bookingForm) {
        bookingForm.addEventListener('submit', handleBooking);
    }
});

// Fetch popular tours from API
async function fetchPopularTours() {
    try {
        const response = await fetch('/api/tours?limit=6');
        
        if (!response.ok) {
            throw new Error('Failed to fetch tours');
        }
        
        const tours = await response.json();
        displayTours(tours);
    } catch (error) {
        console.error('Error fetching tours:', error);
        document.getElementById('popular-tours').innerHTML = `
            <div class="error-message">
                <p>Не удалось загрузить туры. Пожалуйста, попробуйте позже.</p>
            </div>
        `;
    }
}

// Display tours in the grid
function displayTours(tours) {
    const toursContainer = document.getElementById('popular-tours');
    
    if (!tours || tours.length === 0) {
        toursContainer.innerHTML = `
            <div class="no-tours-message">
                <p>В данный момент туры не доступны. Пожалуйста, проверьте позже.</p>
            </div>
        `;
        return;
    }
    
    const toursHTML = tours.map(tour => `
        <div class="tour-card">
            <div class="tour-card__image">
                <img src="${tour.image_url || '/static/images/placeholder-tour.jpg'}" alt="${tour.title}">
            </div>
            <div class="tour-card__content">
                <h3 class="tour-card__title">${tour.title}</h3>
                <span class="tour-card__destination">${tour.destination}</span>
                <p>${tour.description ? tour.description.substring(0, 100) + '...' : 'Нет описания'}</p>
                <div class="tour-card__details">
                    <span class="tour-card__price">${tour.price} ₽</span>
                    <a href="/tours/${tour.id}" class="btn btn--primary">Подробнее</a>
                </div>
            </div>
        </div>
    `).join('');
    
    toursContainer.innerHTML = toursHTML;
}

// Handle login form submission
async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    try {
        const response = await fetch('/api/auth/login/access-token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                'username': email,
                'password': password
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Ошибка авторизации');
        }
        
        // Store token in localStorage
        localStorage.setItem('token', data.access_token);
        
        // Redirect to profile or homepage
        window.location.href = '/profile';
        
    } catch (error) {
        const errorElement = document.getElementById('login-error');
        if (errorElement) {
            errorElement.textContent = error.message;
            errorElement.style.display = 'block';
        }
    }
}

// Handle registration form submission
async function handleRegister(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const fullName = document.getElementById('full_name').value;
    
    try {
        const response = await fetch('/api/auth/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email,
                password,
                full_name: fullName
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Ошибка регистрации');
        }
        
        // Show success message and redirect to login
        alert('Регистрация прошла успешно! Теперь вы можете войти в систему.');
        window.location.href = '/login';
        
    } catch (error) {
        const errorElement = document.getElementById('register-error');
        if (errorElement) {
            errorElement.textContent = error.message;
            errorElement.style.display = 'block';
        }
    }
}

// Handle search form submission
function handleSearch(event) {
    event.preventDefault();
    
    const destination = document.getElementById('destination').value;
    const minPrice = document.getElementById('min-price').value;
    const maxPrice = document.getElementById('max-price').value;
    const startDate = document.getElementById('start-date').value;
    
    // Build query string
    const params = new URLSearchParams();
    if (destination) params.append('destination', destination);
    if (minPrice) params.append('min_price', minPrice);
    if (maxPrice) params.append('max_price', maxPrice);
    if (startDate) params.append('start_date', startDate);
    
    // Redirect to search results page
    window.location.href = `/tours/search?${params.toString()}`;
}

// Handle booking form submission
async function handleBooking(event) {
    event.preventDefault();
    
    // Check if user is authenticated
    const token = localStorage.getItem('token');
    if (!token) {
        alert('Пожалуйста, войдите в систему чтобы забронировать тур.');
        window.location.href = '/login';
        return;
    }
    
    const tourId = document.getElementById('tour_id').value;
    const participantsCount = document.getElementById('participants_count').value;
    const totalPrice = document.getElementById('total_price').value;
    
    try {
        const response = await fetch('/api/bookings/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                tour_id: parseInt(tourId),
                participants_count: parseInt(participantsCount),
                total_price: parseFloat(totalPrice)
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Ошибка бронирования');
        }
        
        // Show success message
        alert('Тур успешно забронирован!');
        
        // Redirect to bookings page
        window.location.href = '/profile/bookings';
        
    } catch (error) {
        const errorElement = document.getElementById('booking-error');
        if (errorElement) {
            errorElement.textContent = error.message;
            errorElement.style.display = 'block';
        }
    }
}

// Logout function
function logout() {
    localStorage.removeItem('token');
    window.location.href = '/';
}

// Calculate total price based on tour price and participants
function calculateTotalPrice() {
    const tourPrice = parseFloat(document.getElementById('tour_price').value);
    const participantsCount = parseInt(document.getElementById('participants_count').value);
    const totalPriceElement = document.getElementById('total_price');
    
    if (tourPrice && participantsCount && totalPriceElement) {
        const totalPrice = tourPrice * participantsCount;
        totalPriceElement.value = totalPrice.toFixed(2);
        
        // Update displayed price if element exists
        const displayedPrice = document.getElementById('displayed_total_price');
        if (displayedPrice) {
            displayedPrice.textContent = `${totalPrice.toFixed(2)} ₽`;
        }
    }
} 