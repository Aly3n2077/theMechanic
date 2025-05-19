# Harare Mobile Mechanics

A comprehensive mobile mechanic booking platform that connects customers with automotive service providers in Harare.

## 🔧 Project Overview

Harare Mobile Mechanics is a web-based platform designed to revolutionize how vehicle owners in Harare connect with skilled mechanics. The platform facilitates convenient booking of mobile mechanics who can perform services at the customer's location, eliminating the need to visit traditional repair shops.

### Key Features

- **Mechanic Booking System**: Book skilled mechanics for various automotive services
- **Service Recommendations**: Intelligent service suggestions based on issue descriptions
- **Mechanic Ratings & Reviews**: Build trust through customer feedback
- **User Dashboard**: Track bookings, manage vehicles, and receive notifications
- **Vehicle Marketplace**: Buy and sell vehicles directly on the platform
- **Location-Based Matching**: Find mechanics near your location

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Flask web framework
- PostgreSQL database (for production)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/harare-mobile-mechanics.git
   cd harare-mobile-mechanics
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python main.py
   ```

4. Access the application at:
   ```
   http://localhost:5000
   ```

## 📱 Application Structure

The application follows a modular structure:

```
harare-mobile-mechanics/
├── static/                # Static assets (CSS, JS, images)
│   ├── css/               # Stylesheets
│   └── js/                # JavaScript files
├── templates/             # HTML templates
├── data.py                # Data handling and business logic
├── forms.py               # Form definitions
├── main.py                # Application entry point
├── models.py              # Data models
├── routes.py              # Route definitions
└── utils.py               # Utility functions
```

## 🔍 Core Functionality

### Mechanic Booking Process

1. User describes their automotive issue
2. System recommends appropriate services
3. User selects a mechanic based on expertise, ratings, and availability
4. User books a time slot for the service
5. Mechanic receives notification and confirms the booking
6. Service is performed at the scheduled time
7. User can leave a review after service completion

### Vehicle Marketplace

1. Users can list vehicles for sale with detailed information
2. Prospective buyers can search and filter available vehicles
3. Direct contact between buyers and sellers is facilitated
4. Integration with mechanic services for pre-purchase inspections

## 🛠️ Services Offered

- **Regular Maintenance**: Oil changes, fluid checks, filter replacements
- **Repair Work**: Engine, transmission, brake, electrical system repairs
- **Diagnostics**: Comprehensive vehicle inspections and problem identification
- **Specialty Services**: Classic car restoration, performance tuning
- **Emergency Services**: Breakdown assistance, jump starts, tire changes
- **Vehicle Marketplace**: Car selling/buying, restoration, modifications, key cutting

## 👥 User Types

1. **Customers**: Vehicle owners seeking automotive services
2. **Mechanics**: Skilled professionals providing mobile repair services
3. **Administrators**: Platform managers (future implementation)

## 📈 Future Development Roadmap

- Map integration for enhanced location-based services
- Mobile application development
- Payment gateway integration
- Subscription-based service plans
- Parts inventory and ordering system
- Fleet management services for businesses

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contact

For questions or feedback, please contact:
- Phone: +263 77 152 2122 / +263 78 683 8849
- Email: info@hararemechanics.com