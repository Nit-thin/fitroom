// Main JavaScript file for Fitroom website

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initAnimations();
    initFormValidation();
    initSearchFunctionality();
    initWorkoutTimer();
    initProgressTracking();
    initMobileMenu();
    initWorkoutLogging();
    initExercisePlayButtons();
    initLikeButtons();
    initShareButtons();
});

// Animation initialization
function initAnimations() {
    // Intersection Observer for fade-in animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
            }
        });
    }, observerOptions);

    // Observe elements for animation
    document.querySelectorAll('.card, .feature-card, .stats-card').forEach(el => {
        observer.observe(el);
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Form validation
function initFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    showFieldError(field, 'This field is required');
                    isValid = false;
                } else {
                    clearFieldError(field);
                }

                // Email validation
                if (field.type === 'email' && field.value) {
                    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    if (!emailRegex.test(field.value)) {
                        showFieldError(field, 'Please enter a valid email address');
                        isValid = false;
                    }
                }

                // Password validation
                if (field.type === 'password' && field.value) {
                    if (field.value.length < 6) {
                        showFieldError(field, 'Password must be at least 6 characters long');
                        isValid = false;
                    }
                }
            });

            if (!isValid) {
                e.preventDefault();
            }
        });
    });
}

function showFieldError(field, message) {
    clearFieldError(field);
    field.classList.add('is-invalid');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

// Search functionality
function initSearchFunctionality() {
    const searchInput = document.querySelector('#searchInput');
    if (!searchInput) return;

    let searchTimeout;
    
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        
        searchTimeout = setTimeout(() => {
            if (query.length >= 2) {
                performSearch(query);
            } else {
                clearSearchResults();
            }
        }, 300);
    });
}

function performSearch(query) {
    // Show loading state
    const searchResults = document.querySelector('#searchResults');
    if (searchResults) {
        searchResults.innerHTML = '<div class="text-center"><div class="spinner mx-auto"></div></div>';
        searchResults.style.display = 'block';
    }

    // Simulate API call (replace with actual API call)
    setTimeout(() => {
        // Mock search results
        const results = [
            { type: 'workout', name: 'Full Body HIIT', category: 'Cardio' },
            { type: 'exercise', name: 'Push-ups', muscle_group: 'Chest' },
            { type: 'workout', name: 'Strength Training', category: 'Strength' }
        ].filter(item => 
            item.name.toLowerCase().includes(query.toLowerCase()) ||
            (item.category && item.category.toLowerCase().includes(query.toLowerCase())) ||
            (item.muscle_group && item.muscle_group.toLowerCase().includes(query.toLowerCase()))
        );

        displaySearchResults(results);
    }, 500);
}

function displaySearchResults(results) {
    const searchResults = document.querySelector('#searchResults');
    if (!searchResults) return;

    if (results.length === 0) {
        searchResults.innerHTML = '<div class="p-3 text-muted">No results found</div>';
        return;
    }

    const resultsHTML = results.map(result => `
        <div class="search-result-item p-3 border-bottom">
            <div class="d-flex align-items-center">
                <i class="fas fa-${result.type === 'workout' ? 'dumbbell' : 'running'} me-3 text-primary"></i>
                <div>
                    <h6 class="mb-1">${result.name}</h6>
                    <small class="text-muted">${result.category || result.muscle_group}</small>
                </div>
            </div>
        </div>
    `).join('');

    searchResults.innerHTML = resultsHTML;
}

function clearSearchResults() {
    const searchResults = document.querySelector('#searchResults');
    if (searchResults) {
        searchResults.style.display = 'none';
    }
}

// Workout timer functionality
function initWorkoutTimer() {
    const timerDisplay = document.querySelector('#workoutTimer');
    if (!timerDisplay) return;

    let timerInterval;
    let seconds = 0;
    let isRunning = false;

    const startButton = document.querySelector('#startTimer');
    const pauseButton = document.querySelector('#pauseTimer');
    const resetButton = document.querySelector('#resetTimer');

    if (startButton) {
        startButton.addEventListener('click', startTimer);
    }
    if (pauseButton) {
        pauseButton.addEventListener('click', pauseTimer);
    }
    if (resetButton) {
        resetButton.addEventListener('click', resetTimer);
    }

    function startTimer() {
        if (!isRunning) {
            isRunning = true;
            timerInterval = setInterval(updateTimer, 1000);
            if (startButton) startButton.style.display = 'none';
            if (pauseButton) pauseButton.style.display = 'inline-block';
        }
    }

    function pauseTimer() {
        isRunning = false;
        clearInterval(timerInterval);
        if (startButton) startButton.style.display = 'inline-block';
        if (pauseButton) pauseButton.style.display = 'none';
    }

    function resetTimer() {
        pauseTimer();
        seconds = 0;
        updateTimerDisplay();
        if (startButton) startButton.style.display = 'inline-block';
        if (pauseButton) pauseButton.style.display = 'none';
    }

    function updateTimer() {
        seconds++;
        updateTimerDisplay();
    }

    function updateTimerDisplay() {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        timerDisplay.textContent = 
            `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
}

// Progress tracking
function initProgressTracking() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    progressBars.forEach(bar => {
        const target = bar.getAttribute('data-target');
        if (target) {
            animateProgressBar(bar, parseInt(target));
        }
    });
}

function animateProgressBar(bar, target) {
    let current = 0;
    const increment = target / 100;
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        bar.style.width = current + '%';
        bar.textContent = Math.round(current) + '%';
    }, 20);
}

// Mobile menu functionality
function initMobileMenu() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        // Close mobile menu when clicking on a link
        const navLinks = navbarCollapse.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth < 992) {
                    navbarCollapse.classList.remove('show');
                }
            });
        });

        // Close mobile menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!navbarToggler.contains(e.target) && !navbarCollapse.contains(e.target)) {
                navbarCollapse.classList.remove('show');
            }
        });
    }
}

// Utility functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

function formatDuration(minutes) {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    
    if (hours > 0) {
        return `${hours}h ${mins}m`;
    }
    return `${mins}m`;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// API helper functions
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(endpoint, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        showNotification('An error occurred. Please try again.', 'danger');
        throw error;
    }
}

// Workout logging functionality
function initWorkoutLogging() {
    const logWorkoutBtns = document.querySelectorAll('.log-workout-btn');
    
    logWorkoutBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const workoutId = this.getAttribute('data-workout-id');
            const workoutName = this.getAttribute('data-workout-name') || 'Workout';
            
            // Show confirmation dialog
            if (confirm(`Log "${workoutName}" as completed?`)) {
                logWorkout(workoutId, workoutName);
            }
        });
    });
}

function logWorkout(workoutId, workoutName) {
    // Simulate API call to log workout
    showNotification(`Great job! "${workoutName}" has been logged.`, 'success');
    
    // Update progress bars
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        const currentWidth = parseInt(bar.style.width) || 0;
        const newWidth = Math.min(currentWidth + 20, 100);
        bar.style.width = newWidth + '%';
        bar.textContent = Math.round(newWidth) + '%';
    });
    
    // Update workout count
    const workoutCountElements = document.querySelectorAll('.workout-count');
    workoutCountElements.forEach(element => {
        const currentCount = parseInt(element.textContent) || 0;
        element.textContent = currentCount + 1;
    });
}

// Exercise play button functionality
function initExercisePlayButtons() {
    const playButtons = document.querySelectorAll('.fa-play-circle, .exercise-play-btn');
    
    playButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const exerciseName = this.closest('.list-group-item').querySelector('h6').textContent;
            showNotification(`Playing ${exerciseName} demonstration...`, 'info');
            
            // Add visual feedback
            this.style.color = '#28a745';
            setTimeout(() => {
                this.style.color = '';
            }, 1000);
        });
    });
}

// Like button functionality
function initLikeButtons() {
    const likeButtons = document.querySelectorAll('.like-btn');
    
    likeButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const isLiked = this.classList.contains('liked');
            
            if (isLiked) {
                this.classList.remove('liked', 'btn-danger');
                this.classList.add('btn-outline-danger');
                this.innerHTML = '<i class="fas fa-heart me-2"></i>Like';
                showNotification('Removed from favorites', 'info');
            } else {
                this.classList.add('liked', 'btn-danger');
                this.classList.remove('btn-outline-danger');
                this.innerHTML = '<i class="fas fa-heart me-2"></i>Liked';
                showNotification('Added to favorites!', 'success');
            }
        });
    });
}

// Share button functionality
function initShareButtons() {
    const shareButtons = document.querySelectorAll('.share-btn');
    
    shareButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const workoutName = this.getAttribute('data-workout-name') || 'this workout';
            const url = window.location.href;
            
            if (navigator.share) {
                navigator.share({
                    title: `Check out ${workoutName} on Fitroom!`,
                    url: url
                });
            } else {
                // Fallback: copy to clipboard
                navigator.clipboard.writeText(url).then(() => {
                    showNotification('Link copied to clipboard!', 'success');
                }).catch(() => {
                    showNotification('Share feature not available', 'warning');
                });
            }
        });
    });
}

// Export functions for use in other scripts
window.FitroomApp = {
    showNotification,
    formatDuration,
    formatDate,
    apiCall,
    logWorkout
}; 