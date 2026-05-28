# Corals4Cheap Coral Client - Developer Guide

This document provides essential information for developing, building, and running the Coral Client application.

## Project Overview

Corals4Cheap Coral Client is a Flask-based web application designed for managing a coral consignment store and professional aquarium maintenance services.

### Key Features
- **User & Role Management**: Supports users, sellers, and administrators with role-based access control.
- **Consignment System**: Allows users to list corals, fish, and equipment for sale with image uploads to Google Cloud Storage.
- **Order Workflow**: Admin-managed order creation, tracking drop-offs, pickups, and payment status.
- **Billing & Maintenance Module**: A dedicated system for logging maintenance visits, recording water chemistry parameters, and generating automated monthly invoices as PDFs.
- **Email Notifications**: Automated emails for order status changes, password resets, and invoice delivery.

### Tech Stack
- **Backend**: Python 3.x, Flask
- **Database**: 
  - **Development**: SQLite (`instance/dev_database.db`)
  - **Production**: MySQL (via `ProdConfig`)
  - **ORM**: Flask-SQLAlchemy
- **Authentication**: Flask-Login, Flask-Bcrypt
- **Storage**: Google Cloud Storage (GCS) for images and generated PDFs.
- **Email**: Flask-Mail (integrated with Gmail SMTP).
- **Frontend**: Jinja2 Templates, Vanilla CSS, JavaScript.
- **Deployment**: Google App Engine with Waitress as the WSGI server.

---

## Getting Started

### Prerequisites
- Python 3.8+
- Google Cloud SDK (for GCS access and deployment)
- Service account key (default: `corals4cheap-65a82a68dbed.json`)

### Installation
1. **Clone the repository.**
2. **Create a virtual environment**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

### Database Setup
To initialize the local SQLite database and create tables:
```powershell
python setup_db.py
```

### Running the Application
#### Development Mode
Use the provided batch file or set the environment variable:
```powershell
.\dev.bat
# OR
$env:FLASK_ENV="development"
python app.py
```
The app will be available at `http://localhost:8080`.

#### Production Mode
Set `FLASK_ENV` to `production` and ensure all required environment variables (e.g., `SECRET_KEY`, `MAIL_PASSWORD`) are configured.

---

## Project Structure & Conventions

### Core Modules
- `app.py`: Main entry point, route definitions for user management and consignment.
- `models.py`: Core database schema (User, Role, ConsignmentProduct, Order).
- `forms.py`: WTForms for registration, login, and consignment.
- `DB.py`: Centralized Flask app and SQLAlchemy instance initialization.
- `config.py` / `base_config.py` / `dev_config.py`: Hierarchical configuration management.

### Billing & Maintenance Module
- `billingroutes.py`: Blueprint (`billing_bp`) handling maintenance logs and invoice generation.
- `billingmodels.py`: Schema for `Bill`, `MaintenanceVisit`, `BillLineItem`, and `ChemicalRanges`.
- `billingforms.py`: Forms for maintenance visits and billing line items.

### Utility & Helpers
- `gcs_utils.py`: Logic for interacting with Google Cloud Storage.
- `utility_functions.py`: Email notification helpers and administrative decorators.

### Styling & Assets
- `static/styles.css`: Main stylesheet.
- `static/js/`: Client-side logic (e.g., `filter.js`).
- `templates/`: HTML templates organized by module (e.g., `templates/billing/` for maintenance-related pages).

### Development Conventions
- **Routing**: Core routes are in `app.py`; modular features should use Flask Blueprints (e.g., `billing_bp`).
- **Data Access**: Use SQLAlchemy query syntax. Prefer `joinedload` for efficient related data fetching in the billing module.
- **Storage**: Never store uploads locally in production; always use the `upload_image_to_gcs` helper.
- **Invoicing**: PDFs are generated using `reportlab` and emailed via `flask-mail`.

---

## Key Commands
| Task | Command |
| :--- | :--- |
| Run Dev Server | `.\dev.bat` |
| Init Database | `python setup_db.py` |
| Install Deps | `pip install -r requirements.txt` |
| Deployment | `gcloud app deploy` |

## TODO / Future Improvements
- [ ] Implement unit and integration tests (none found in the current root).
- [ ] Refactor `app.py` to move more routes into Blueprints for better scalability.
- [ ] Enhance validation for water chemistry parameters in `billingforms.py`.
