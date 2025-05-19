document.addEventListener('DOMContentLoaded', function() {
    // Function to handle updating appointment status
    const statusUpdateButtons = document.querySelectorAll('.update-status-btn');
    statusUpdateButtons.forEach(button => {
        button.addEventListener('click', function() {
            const appointmentId = this.getAttribute('data-appointment-id');
            const status = this.getAttribute('data-status');
            const confirmMessage = this.getAttribute('data-confirm-message') || `Are you sure you want to mark this appointment as ${status}?`;
            
            if (confirm(confirmMessage)) {
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = `/appointment/${appointmentId}/update-status/${status}`;
                
                // Add CSRF token
                const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
                if (csrfToken) {
                    const csrfInput = document.createElement('input');
                    csrfInput.type = 'hidden';
                    csrfInput.name = 'csrf_token';
                    csrfInput.value = csrfToken;
                    form.appendChild(csrfInput);
                }
                
                document.body.appendChild(form);
                form.submit();
            }
        });
    });
    
    // Function to filter appointments by status
    const statusFilter = document.getElementById('status-filter');
    if (statusFilter) {
        statusFilter.addEventListener('change', function() {
            const status = this.value;
            const appointments = document.querySelectorAll('.appointment-item');
            
            appointments.forEach(appointment => {
                if (status === 'all' || appointment.getAttribute('data-status') === status) {
                    appointment.style.display = 'block';
                } else {
                    appointment.style.display = 'none';
                }
            });
            
            // Update count
            const visibleCount = document.querySelectorAll('.appointment-item[style="display: block;"]').length;
            const countElement = document.getElementById('appointment-count');
            if (countElement) {
                countElement.textContent = visibleCount;
            }
        });
    }
    
    // Date range filtering for appointments
    const dateRangeFilter = document.getElementById('date-range-filter');
    if (dateRangeFilter) {
        dateRangeFilter.addEventListener('change', function() {
            const range = this.value;
            const appointments = document.querySelectorAll('.appointment-item');
            const now = new Date();
            
            appointments.forEach(appointment => {
                const dateStr = appointment.getAttribute('data-date');
                if (!dateStr) return;
                
                const appointmentDate = new Date(dateStr);
                let show = true;
                
                switch (range) {
                    case 'today':
                        show = isSameDay(now, appointmentDate);
                        break;
                    case 'tomorrow':
                        const tomorrow = new Date(now);
                        tomorrow.setDate(now.getDate() + 1);
                        show = isSameDay(tomorrow, appointmentDate);
                        break;
                    case 'this-week':
                        const endOfWeek = new Date(now);
                        endOfWeek.setDate(now.getDate() + (6 - now.getDay()));
                        show = appointmentDate >= now && appointmentDate <= endOfWeek;
                        break;
                    case 'next-week':
                        const startOfNextWeek = new Date(now);
                        startOfNextWeek.setDate(now.getDate() + (7 - now.getDay()));
                        const endOfNextWeek = new Date(startOfNextWeek);
                        endOfNextWeek.setDate(startOfNextWeek.getDate() + 6);
                        show = appointmentDate >= startOfNextWeek && appointmentDate <= endOfNextWeek;
                        break;
                    case 'this-month':
                        show = appointmentDate.getMonth() === now.getMonth() && 
                               appointmentDate.getFullYear() === now.getFullYear();
                        break;
                    case 'past':
                        show = appointmentDate < now;
                        break;
                    default: // all
                        show = true;
                }
                
                // Apply status filter too if it's active
                const statusFilter = document.getElementById('status-filter');
                if (statusFilter && statusFilter.value !== 'all') {
                    show = show && appointment.getAttribute('data-status') === statusFilter.value;
                }
                
                appointment.style.display = show ? 'block' : 'none';
            });
            
            // Update count
            const visibleCount = document.querySelectorAll('.appointment-item[style="display: block;"]').length;
            const countElement = document.getElementById('appointment-count');
            if (countElement) {
                countElement.textContent = visibleCount;
            }
        });
    }
    
    // Helper function to check if two dates are the same day
    function isSameDay(date1, date2) {
        return date1.getDate() === date2.getDate() &&
               date1.getMonth() === date2.getMonth() &&
               date1.getFullYear() === date2.getFullYear();
    }
    
    // Initialize chart for customer dashboard if chart.js is available
    const appointmentChartCanvas = document.getElementById('appointmentChart');
    if (appointmentChartCanvas && typeof Chart !== 'undefined') {
        // Get appointment data from data attribute
        const appointmentData = JSON.parse(appointmentChartCanvas.getAttribute('data-appointments') || '[]');
        
        // Process data for chart
        const statusCounts = {
            'pending': 0,
            'confirmed': 0,
            'completed': 0,
            'cancelled': 0
        };
        
        appointmentData.forEach(appointment => {
            if (statusCounts[appointment.status] !== undefined) {
                statusCounts[appointment.status]++;
            }
        });
        
        // Create chart
        new Chart(appointmentChartCanvas, {
            type: 'doughnut',
            data: {
                labels: ['Pending', 'Confirmed', 'Completed', 'Cancelled'],
                datasets: [{
                    data: [
                        statusCounts.pending,
                        statusCounts.confirmed,
                        statusCounts.completed,
                        statusCounts.cancelled
                    ],
                    backgroundColor: [
                        '#FFC107', // warning - pending
                        '#17A2B8', // info - confirmed
                        '#2ECC71', // success - completed
                        '#DC3545'  // danger - cancelled
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'Appointment Status'
                    }
                }
            }
        });
    }
    
    // Initialize service history table sorting
    const serviceHistoryTable = document.getElementById('service-history-table');
    if (serviceHistoryTable) {
        const sortableHeaders = serviceHistoryTable.querySelectorAll('th[data-sort]');
        
        sortableHeaders.forEach(header => {
            header.addEventListener('click', function() {
                const column = this.getAttribute('data-sort');
                const currentOrder = this.getAttribute('data-order') || 'asc';
                const newOrder = currentOrder === 'asc' ? 'desc' : 'asc';
                
                // Reset all headers
                sortableHeaders.forEach(h => {
                    h.removeAttribute('data-order');
                    h.querySelector('.sort-icon')?.remove();
                });
                
                // Set this header's order and icon
                this.setAttribute('data-order', newOrder);
                const icon = document.createElement('span');
                icon.className = 'sort-icon ms-1';
                icon.innerHTML = newOrder === 'asc' ? '↑' : '↓';
                this.appendChild(icon);
                
                // Sort the table
                const tbody = serviceHistoryTable.querySelector('tbody');
                const rows = Array.from(tbody.querySelectorAll('tr'));
                
                rows.sort((a, b) => {
                    let aValue = a.querySelector(`td[data-${column}]`)?.getAttribute(`data-${column}`) || '';
                    let bValue = b.querySelector(`td[data-${column}]`)?.getAttribute(`data-${column}`) || '';
                    
                    // Handle numeric values
                    if (!isNaN(aValue) && !isNaN(bValue)) {
                        aValue = parseFloat(aValue);
                        bValue = parseFloat(bValue);
                    }
                    
                    if (aValue < bValue) {
                        return newOrder === 'asc' ? -1 : 1;
                    }
                    if (aValue > bValue) {
                        return newOrder === 'asc' ? 1 : -1;
                    }
                    return 0;
                });
                
                // Reorder the table
                rows.forEach(row => tbody.appendChild(row));
            });
        });
    }
});
