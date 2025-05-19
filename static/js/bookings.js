document.addEventListener('DOMContentLoaded', function() {
    // Function to update booking status
    function updateBookingStatus(bookingId, newStatus, button) {
        // Disable button to prevent multiple clicks
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Updating...';
        
        fetch('/api/update_booking_status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                booking_id: bookingId,
                status: newStatus
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update the UI to reflect the new status
                const statusBadge = button.closest('.booking-item').querySelector('.booking-status');
                
                // Remove old status classes
                statusBadge.classList.remove('badge-pending', 'badge-confirmed', 'badge-completed', 'badge-cancelled');
                
                // Add new status class
                statusBadge.classList.add(`badge-${newStatus.toLowerCase()}`);
                
                // Update status text
                statusBadge.textContent = newStatus;
                
                // If cancelled or completed, remove action buttons
                if (newStatus === 'Completed' || newStatus === 'Cancelled') {
                    const actionButtons = button.closest('.booking-actions');
                    if (actionButtons) {
                        actionButtons.innerHTML = `<span class="text-muted">Status: ${newStatus}</span>`;
                    }
                } else {
                    // Re-enable the button for other statuses
                    button.disabled = false;
                    button.innerHTML = button.getAttribute('data-original-text');
                }
                
                // Show success message
                const alertContainer = document.getElementById('alert-container');
                if (alertContainer) {
                    const alert = document.createElement('div');
                    alert.className = 'alert alert-success alert-dismissible fade show';
                    alert.innerHTML = `
                        <strong>Success!</strong> ${data.message}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    `;
                    alertContainer.appendChild(alert);
                    
                    // Auto dismiss after 5 seconds
                    setTimeout(() => {
                        alert.classList.remove('show');
                        setTimeout(() => alert.remove(), 150);
                    }, 5000);
                }
            } else {
                // Show error and reset button
                button.disabled = false;
                button.innerHTML = button.getAttribute('data-original-text');
                
                const alertContainer = document.getElementById('alert-container');
                if (alertContainer) {
                    const alert = document.createElement('div');
                    alert.className = 'alert alert-danger alert-dismissible fade show';
                    alert.innerHTML = `
                        <strong>Error!</strong> ${data.message}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    `;
                    alertContainer.appendChild(alert);
                    
                    // Auto dismiss after 5 seconds
                    setTimeout(() => {
                        alert.classList.remove('show');
                        setTimeout(() => alert.remove(), 150);
                    }, 5000);
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            button.disabled = false;
            button.innerHTML = button.getAttribute('data-original-text');
            
            const alertContainer = document.getElementById('alert-container');
            if (alertContainer) {
                const alert = document.createElement('div');
                alert.className = 'alert alert-danger alert-dismissible fade show';
                alert.innerHTML = `
                    <strong>Error!</strong> Failed to update booking status. Please try again.
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                `;
                alertContainer.appendChild(alert);
                
                // Auto dismiss after 5 seconds
                setTimeout(() => {
                    alert.classList.remove('show');
                    setTimeout(() => alert.remove(), 150);
                }, 5000);
            }
        });
    }
    
    // Attach event listeners to all status update buttons
    const statusButtons = document.querySelectorAll('[data-booking-id][data-status]');
    statusButtons.forEach(button => {
        // Store original button text for restoration after API call
        button.setAttribute('data-original-text', button.innerHTML);
        
        button.addEventListener('click', function() {
            const bookingId = this.getAttribute('data-booking-id');
            const newStatus = this.getAttribute('data-status');
            
            if (newStatus === 'Cancel') {
                // Confirm before cancelling
                if (confirm('Are you sure you want to cancel this booking? This action cannot be undone.')) {
                    updateBookingStatus(bookingId, 'Cancelled', this);
                }
            } else {
                updateBookingStatus(bookingId, newStatus, this);
            }
        });
    });
    
    // Filter functionality for dashboard bookings
    const bookingFilterSelect = document.getElementById('booking-filter');
    if (bookingFilterSelect) {
        bookingFilterSelect.addEventListener('change', function() {
            const filterValue = this.value.toLowerCase();
            const bookingItems = document.querySelectorAll('.booking-item');
            
            bookingItems.forEach(item => {
                const status = item.querySelector('.booking-status').textContent.toLowerCase();
                
                if (filterValue === 'all' || status === filterValue) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }
});
