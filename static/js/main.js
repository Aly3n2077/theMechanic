document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize date pickers if they exist
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        // Set min date to today
        const today = new Date().toISOString().split('T')[0];
        input.setAttribute('min', today);
    });

    // Service filter functionality
    const serviceFilter = document.getElementById('service-filter');
    if (serviceFilter) {
        serviceFilter.addEventListener('change', function() {
            const selected = this.value;
            const mechanics = document.querySelectorAll('.mechanic-card');
            
            mechanics.forEach(mechanic => {
                if (selected === 'all') {
                    mechanic.style.display = 'block';
                } else {
                    const services = mechanic.getAttribute('data-services').split(',');
                    if (services.includes(selected)) {
                        mechanic.style.display = 'block';
                    } else {
                        mechanic.style.display = 'none';
                    }
                }
            });
        });
    }

    // Mobile menu toggle
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
        });
    }
    
    // Flash message auto-dismiss
    const flashMessages = document.querySelectorAll('.alert-dismissible');
    flashMessages.forEach(message => {
        setTimeout(() => {
            const closeButton = message.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000); // Auto-dismiss after 5 seconds
    });

    // Service selection in booking form
    const serviceSelect = document.getElementById('service_id');
    const pricePlaceholder = document.getElementById('service-price');
    
    if (serviceSelect && pricePlaceholder) {
        serviceSelect.addEventListener('change', function() {
            const selectedOption = this.options[this.selectedIndex];
            const price = selectedOption.textContent.split('$')[1];
            if (price) {
                pricePlaceholder.textContent = `$${price}`;
            }
        });
        // Trigger change event to show initial price
        serviceSelect.dispatchEvent(new Event('change'));
    }

    // Star rating display
    const ratingElements = document.querySelectorAll('.rating');
    ratingElements.forEach(ratingEl => {
        const ratingValue = parseFloat(ratingEl.getAttribute('data-rating'));
        let starsHtml = '';
        
        for (let i = 1; i <= 5; i++) {
            if (i <= ratingValue) {
                starsHtml += '<i class="fas fa-star"></i>';
            } else if (i - 0.5 <= ratingValue) {
                starsHtml += '<i class="fas fa-star-half-alt"></i>';
            } else {
                starsHtml += '<i class="far fa-star"></i>';
            }
        }
        
        ratingEl.innerHTML = starsHtml + ` <span>(${ratingEl.getAttribute('data-count')})</span>`;
    });
});
