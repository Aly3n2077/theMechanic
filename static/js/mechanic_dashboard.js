document.addEventListener('DOMContentLoaded', function() {
    // Dashboard statistics display
    const updateDashboardStats = () => {
        const upcomingBookingsCount = document.querySelectorAll('.upcoming-bookings .booking-item').length;
        const completedBookingsCount = document.querySelectorAll('.completed-bookings .booking-item').length;
        
        // Update the dashboard stats
        const upcomingStats = document.getElementById('upcoming-count');
        const completedStats = document.getElementById('completed-count');
        const totalStats = document.getElementById('total-bookings');
        
        if (upcomingStats) upcomingStats.textContent = upcomingBookingsCount;
        if (completedStats) completedStats.textContent = completedBookingsCount;
        if (totalStats) totalStats.textContent = upcomingBookingsCount + completedBookingsCount;
    };
    
    // Call the function on page load
    updateDashboardStats();
    
    // Tab functionality for dashboard
    const dashboardTabs = document.querySelectorAll('.dashboard-tab');
    const tabContents = document.querySelectorAll('.tab-content');
    
    dashboardTabs.forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all tabs
            dashboardTabs.forEach(t => t.classList.remove('active'));
            
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Hide all tab contents
            tabContents.forEach(content => content.style.display = 'none');
            
            // Show the corresponding tab content
            const targetId = this.getAttribute('data-target');
            document.getElementById(targetId).style.display = 'block';
        });
    });
    
    // Initialize first tab as active
    if (dashboardTabs.length > 0) {
        dashboardTabs[0].click();
    }
    
    // Filter functionality for bookings by date
    const dateFilter = document.getElementById('date-filter');
    if (dateFilter) {
        dateFilter.addEventListener('change', function() {
            const selectedDate = this.value;
            const bookingItems = document.querySelectorAll('.booking-item');
            
            bookingItems.forEach(item => {
                const bookingDate = item.getAttribute('data-date');
                
                if (!selectedDate || bookingDate === selectedDate) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
            
            // Update stats after filtering
            updateDashboardStats();
        });
    }
    
    // Toggle availability status
    const availabilityToggles = document.querySelectorAll('.availability-toggle');
    availabilityToggles.forEach(toggle => {
        toggle.addEventListener('change', function() {
            const timeSlot = this.getAttribute('data-timeslot');
            const day = this.getAttribute('data-day');
            const available = this.checked;
            
            // Here we would normally make an API call to update availability
            console.log(`Update availability: ${day} ${timeSlot} - ${available ? 'Available' : 'Unavailable'}`);
            
            // Visually update the availability slot
            const slot = this.closest('.availability-slot');
            if (slot) {
                if (available) {
                    slot.classList.remove('unavailable');
                    slot.classList.add('available');
                } else {
                    slot.classList.remove('available');
                    slot.classList.add('unavailable');
                }
            }
        });
    });
});
