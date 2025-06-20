/**
 * API module for making requests to the backend API
 */

const API = (function() {
    // Base API URL
    const API_BASE_URL = '/api/v1';
    
    /**
     * Make a fetch request with the specified options
     * @param {string} url - The URL to fetch
     * @param {Object} options - The fetch options
     * @returns {Promise} - The fetch promise
     */
    async function fetchRequest(url, options = {}) {
        // Add default headers
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        // Get token from localStorage if available
        const token = localStorage.getItem('access_token');
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        // Create fetch options
        const fetchOptions = {
            ...options,
            headers
        };
        
        try {
            // Make the request
            const response = await fetch(url, fetchOptions);
            
            // Handle 401 Unauthorized (token expired)
            if (response.status === 401 && token) {
                // Try to refresh the token
                const refreshed = await refreshToken();
                if (refreshed) {
                    // Retry the request with the new token
                    return fetchRequest(url, options);
                } else {
                    // Redirect to login page if token refresh fails
                    window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
                    return null;
                }
            }
            
            // Parse the response
            const data = await response.json();
            
            // Check if the request was successful
            if (!response.ok) {
                throw new Error(data.detail || 'Something went wrong');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }
    
    /**
     * Refresh the access token using the refresh token
     * @returns {Promise<boolean>} - Whether the token was refreshed successfully
     */
    async function refreshToken() {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) return false;
        
        try {
            const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    refresh_token: refreshToken
                })
            });
            
            if (!response.ok) return false;
            
            const data = await response.json();
            localStorage.setItem('access_token', data.access_token);
            
            return true;
        } catch (error) {
            console.error('Token refresh error:', error);
            return false;
        }
    }
    
    /**
     * Make a GET request
     * @param {string} endpoint - The API endpoint
     * @param {Object} params - The query parameters
     * @returns {Promise} - The fetch promise
     */
    function get(endpoint, params = {}) {
        // Build query string
        const queryString = Object.keys(params)
            .filter(key => params[key] !== undefined && params[key] !== null)
            .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
            .join('&');
        
        // Build URL
        const url = `${API_BASE_URL}${endpoint}${queryString ? `?${queryString}` : ''}`;
        
        // Make the request
        return fetchRequest(url);
    }
    
    /**
     * Make a POST request
     * @param {string} endpoint - The API endpoint
     * @param {Object} data - The request body
     * @returns {Promise} - The fetch promise
     */
    function post(endpoint, data = {}) {
        return fetchRequest(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    /**
     * Make a PUT request
     * @param {string} endpoint - The API endpoint
     * @param {Object} data - The request body
     * @returns {Promise} - The fetch promise
     */
    function put(endpoint, data = {}) {
        return fetchRequest(`${API_BASE_URL}${endpoint}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }
    
    /**
     * Make a PATCH request
     * @param {string} endpoint - The API endpoint
     * @param {Object} data - The request body
     * @returns {Promise} - The fetch promise
     */
    function patch(endpoint, data = {}) {
        return fetchRequest(`${API_BASE_URL}${endpoint}`, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
    }
    
    /**
     * Make a DELETE request
     * @param {string} endpoint - The API endpoint
     * @returns {Promise} - The fetch promise
     */
    function del(endpoint) {
        return fetchRequest(`${API_BASE_URL}${endpoint}`, {
            method: 'DELETE'
        });
    }
    
    /**
     * Upload a file
     * @param {string} endpoint - The API endpoint
     * @param {FormData} formData - The form data with files
     * @returns {Promise} - The fetch promise
     */
    function upload(endpoint, formData) {
        // Get token from localStorage if available
        const token = localStorage.getItem('access_token');
        const headers = {};
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        return fetchRequest(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers,
            body: formData
        });
    }
    
    // Tours API
    const tours = {
        /**
         * Get all tours with optional filters
         * @param {Object} filters - The filters to apply
         * @returns {Promise} - The fetch promise
         */
        getAll: (filters = {}) => get('/tours', filters),
        
        /**
         * Get a tour by ID
         * @param {number} id - The tour ID
         * @returns {Promise} - The fetch promise
         */
        getById: (id) => get(`/tours/${id}`),
        
        /**
         * Search for tours
         * @param {Object} searchParams - The search parameters
         * @returns {Promise} - The fetch promise
         */
        search: (searchParams = {}) => get('/tours/search', searchParams)
    };
    
    // Bookings API
    const bookings = {
        /**
         * Get all bookings for the current user
         * @returns {Promise} - The fetch promise
         */
        getAll: () => get('/bookings'),
        
        /**
         * Get a booking by ID
         * @param {number} id - The booking ID
         * @returns {Promise} - The fetch promise
         */
        getById: (id) => get(`/bookings/${id}`),
        
        /**
         * Create a new booking
         * @param {Object} bookingData - The booking data
         * @returns {Promise} - The fetch promise
         */
        create: (bookingData) => post('/bookings', bookingData),
        
        /**
         * Cancel a booking
         * @param {number} id - The booking ID
         * @returns {Promise} - The fetch promise
         */
        cancel: (id) => post(`/bookings/${id}/cancel`)
    };
    
    // Reviews API
    const reviews = {
        /**
         * Get reviews for a tour
         * @param {number} tourId - The tour ID
         * @param {Object} params - The query parameters
         * @returns {Promise} - The fetch promise
         */
        getByTour: (tourId, params = {}) => get(`/tours/${tourId}/reviews`, params),
        
        /**
         * Create a new review
         * @param {number} tourId - The tour ID
         * @param {Object} reviewData - The review data
         * @returns {Promise} - The fetch promise
         */
        create: (tourId, reviewData) => post(`/tours/${tourId}/reviews`, reviewData),
        
        /**
         * Update a review
         * @param {number} reviewId - The review ID
         * @param {Object} reviewData - The review data
         * @returns {Promise} - The fetch promise
         */
        update: (reviewId, reviewData) => put(`/reviews/${reviewId}`, reviewData),
        
        /**
         * Delete a review
         * @param {number} reviewId - The review ID
         * @returns {Promise} - The fetch promise
         */
        delete: (reviewId) => del(`/reviews/${reviewId}`)
    };
    
    // User API
    const user = {
        /**
         * Get the current user profile
         * @returns {Promise} - The fetch promise
         */
        getProfile: () => get('/users/me'),
        
        /**
         * Update the current user profile
         * @param {Object} userData - The user data
         * @returns {Promise} - The fetch promise
         */
        updateProfile: (userData) => put('/users/me', userData),
        
        /**
         * Change the user password
         * @param {Object} passwordData - The password data
         * @returns {Promise} - The fetch promise
         */
        changePassword: (passwordData) => post('/users/me/password', passwordData)
    };
    
    // Auth API
    const auth = {
        /**
         * Login with email and password
         * @param {string} email - The user email
         * @param {string} password - The user password
         * @returns {Promise} - The fetch promise
         */
        login: (email, password) => post('/auth/login', { email, password }),
        
        /**
         * Register a new user
         * @param {Object} userData - The user data
         * @returns {Promise} - The fetch promise
         */
        register: (userData) => post('/auth/register', userData),
        
        /**
         * Logout the current user
         * @returns {Promise} - The fetch promise
         */
        logout: () => {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            return Promise.resolve();
        },
        
        /**
         * Check if the user is authenticated
         * @returns {boolean} - Whether the user is authenticated
         */
        isAuthenticated: () => {
            return !!localStorage.getItem('access_token');
        }
    };
    
    // Public API
    return {
        get,
        post,
        put,
        patch,
        delete: del,
        upload,
        tours,
        bookings,
        reviews,
        user,
        auth
    };
})();

// Export the API module
window.API = API; 