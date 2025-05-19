document.addEventListener('DOMContentLoaded', function() {
    // Initialize flatpickr for date selection
    const dateInput = document.getElementById('date');
    if (dateInput && typeof flatpickr !== 'undefined') {
        const fp = flatpickr(dateInput, {
            enableTime: false,
            dateFormat: "Y-m-d",
            minDate: "today",
            disable: [
                function(date) {
                    // Disable weekends if needed based on mechanic availability
                    // This will be customized based on the mechanic's availability
                    return false; // For now, enable all days
                }
            ],
            onChange: function(selectedDates, dateStr) {
                // When date changes, fetch available time slots
                updateAvailableTimes();
            }
        });
    }

    // Service selection change event
    const serviceSelect = document.getElementById('service_id');
    if (serviceSelect) {
        serviceSelect.addEventListener('change', function() {
            updateAvailableTimes();
        });
    }

    // Function to update available time slots
    function updateAvailableTimes() {
        const dateInput = document.getElementById('date');
        const serviceSelect = document.getElementById('service_id');
        const mechanicIdInput = document.getElementById('mechanic_id');
        const timeContainer = document.getElementById('time-slots-container');
        const timeInput = document.getElementById('time');
        
        if (!dateInput || !serviceSelect || !mechanicIdInput || !timeContainer || !timeInput) {
            return;
        }
        
        const date = dateInput.value;
        const serviceId = serviceSelect.value;
        const mechanicId = mechanicIdInput.value;
        
        if (!date || !serviceId || !mechanicId) {
            timeContainer.innerHTML = '<p class="text-muted">Please select a date and service first.</p>';
            return;
        }
        
        // Show loading indicator
        timeContainer.innerHTML = '<p class="text-center"><i class="fas fa-spinner fa-spin"></i> Loading available times...</p>';
        
        // Fetch available time slots from the server
        fetch(`/get-available-times?mechanic_id=${mechanicId}&date=${date}&service_id=${serviceId}`)
            .then(response => response.json())
            .then(data => {
                const availableTimes = data.available_times || [];
                
                if (availableTimes.length === 0) {
                    timeContainer.innerHTML = '<p class="alert alert-warning">No available time slots for this date. Please select another date.</p>';
                    timeInput.value = '';
                    return;
                }
                
                // Create time slot buttons
                let timeSlotHtml = '<p>Select a time slot:</p><div class="time-slots">';
                
                availableTimes.forEach(time => {
                    timeSlotHtml += `<div class="time-slot" data-time="${time}">${time}</div>`;
                });
                
                timeSlotHtml += '</div>';
                timeContainer.innerHTML = timeSlotHtml;
                
                // Add click event to time slots
                document.querySelectorAll('.time-slot').forEach(slot => {
                    slot.addEventListener('click', function() {
                        const time = this.getAttribute('data-time');
                        document.querySelectorAll('.time-slot').forEach(s => s.classList.remove('selected'));
                        this.classList.add('selected');
                        timeInput.value = time;
                    });
                });
                
                // If there's a previously selected time, highlight it
                if (timeInput.value) {
                    const selectedSlot = document.querySelector(`.time-slot[data-time="${timeInput.value}"]`);
                    if (selectedSlot) {
                        selectedSlot.classList.add('selected');
                    }
                }
            })
            .catch(error => {
                console.error('Error fetching time slots:', error);
                timeContainer.innerHTML = '<p class="alert alert-danger">Error loading time slots. Please try again.</p>';
            });
    }

    // Vehicle information validation
    const vehicleForm = document.getElementById('booking-form');
    if (vehicleForm) {
        vehicleForm.addEventListener('submit', function(event) {
            const make = document.getElementById('make').value;
            const model = document.getElementById('model').value;
            const year = document.getElementById('year').value;
            const description = document.getElementById('description').value;
            const time = document.getElementById('time').value;
            
            if (!make || !model || !year || !description || !time) {
                event.preventDefault();
                showFormError('Please fill out all required fields');
                return;
            }
            
            // Validate year
            const yearInt = parseInt(year);
            const currentYear = new Date().getFullYear();
            if (isNaN(yearInt) || yearInt < 1900 || yearInt > currentYear + 1) {
                event.preventDefault();
                showFormError(`Please enter a valid year between 1900 and ${currentYear + 1}`);
                return;
            }
        });
    }

    // Show form error message
    function showFormError(message) {
        const errorContainer = document.getElementById('form-error');
        if (errorContainer) {
            errorContainer.textContent = message;
            errorContainer.style.display = 'block';
            
            // Scroll to error message
            errorContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
            alert(message);
        }
    }

    // Initialize the available times if date and service are already selected
    updateAvailableTimes();
});
