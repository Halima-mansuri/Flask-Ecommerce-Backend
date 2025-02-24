Flask E-Commerce Backend

This project is a backend system for an e-commerce application built using Flask, providing functionalities for admins, service providers, and customers. It supports user authentication, product management, order processing, and notifications.

🚀 Project Setup Instructions

1️⃣ Clone the Repository

    git clone <repository_url>
    cd <project_folder>

2️⃣ Create and Activate Virtual Environment

    # Create virtual environment
    python -m venv venv

    # Activate virtual environment
    # For Windows:
    venv\Scripts\activate

    # For macOS/Linux:
    source venv/bin/activate

3️⃣ Install Dependencies

    pip install -r requirements.txt

4️⃣ Configure MySQL Database

    Ensure that MySQL is running and create the database:
    
    CREATE DATABASE IF NOT EXISTS ecommerce_db;

5️⃣ Run Database Migrations

    # Run only if migrations folder does not exist
    flask db init  

    # Generate migration files
    flask db migrate -m "Initial migration"

    # Apply migrations to the database
    flask db upgrade

6️⃣ Start the Flask Server

    # Run the Flask server
    flask run

7️⃣ Set Up Environment Variables

    Create a .env file in the root directory and add the following:

    SECRET_KEY=supersecretkey
    SQLALCHEMY_DATABASE_URI=mysql+pymysql://root@localhost:3307/ecommerce_db

    # Set the Flask app 
    FLASK_APP=app.py

    # Optional: Enable development mode for debugging
    FLASK_ENV=development


🌐 Base URL

    http://127.0.0.1:5000/api/v1/
    
⚡ Notes

    Ensure that the MySQL service is running before starting the Flask server.
    For JWT-protected routes, include the access token in the Authorization header:

    Authorization: Bearer <your_jwt_token>





