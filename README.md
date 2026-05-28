# Corals4Cheap Coral Client

This is a Flask-based web application for managing a consignment store for corals, fish, and equipment.

## Features

*   **User Management:** Customers can register, login, and manage their profiles. Admins can manage all users and their roles.
*   **Consignment:** Users can list items for sale.
*   **Product Management:** Admins can manage all products, including featuring them on the homepage.
*   **Order Management:** Admins can create and manage orders for products.
*   **Email Notifications:** The application sends email notifications for various events, such as order creation and password resets.
*   **Billing and Maintenance:** The application includes modules for billing and maintenance (details to be documented).

## Tech Stack

*   **Backend:** Python, Flask
*   **Database:** MySQL (with Flask-SQLAlchemy)
*   **Authentication:** Flask-Login, Flask-Bcrypt
*   **Forms:** Flask-WTF
*   **Email:** Flask-Mail
*   **Cloud Storage:** Google Cloud Storage for image uploads.
*   **Deployment:** Google App Engine

## Project Structure

```
├── app.py                  # Main application file
├── config.py               # Configuration settings
├── models.py               # Database models
├── forms.py                # WTForms definitions
├── requirements.txt        # Python dependencies
├── templates/              # HTML templates
│   ├── base.html           # Base template
│   ├── home.html           # Home page
│   ├── login.html          # Login page
│   └── ...
├── static/                 # Static files (CSS, JS, images)
│   ├── styles.css
│   └── ...
├── billingforms.py         # Forms for the billing module
├── billingmodels.py        # Models for the billing module
├── billingroutes.py        # Routes for the billing module
├── utility_functions.py    # Helper functions
└── ...
```

## Getting Started

### Prerequisites

*   Python 3.x
*   MySQL
*   Google Cloud SDK

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-folder>
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up the database:**
    *   Make sure you have a local MySQL server running.
    *   The application is configured to use the following default credentials for the local database:
        *   **Username:** `root`
        *   **Password:** `password`
        *   **Host:** `localhost`
        *   **Port:** `3306`
    *   If you need to change these credentials, you can do so in the `dev_config.py` file.
    *   Run the `setup_db.py` script to create the database and tables:
        ```bash
        python setup_db.py
        ```

5.  **Run the application:**
    *   Set the `FLASK_ENV` environment variable to `development`:
        ```bash
        set FLASK_ENV=development
        ```
    *   Run the `app.py` script:
        ```bash
        python app.py
        ```
    *   You can also use the `dev.bat` script to start the development server.
