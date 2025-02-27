# Hmart
E-Commerce Website with Django
This is a Django-based e-commerce website project. It allows users to browse products, manage their cart, and perform various e-commerce operations. This README will guide you through setting up and running the project on your local machine.

Prerequisites
Before setting up the project, ensure that you have the following:

Python 3.x
MySQL database installed on your machine
Setup Instructions
1. Create a Python Virtual Environment
To avoid conflicts with other projects, create a new virtual environment.

# Navigate to your project directory
cd path/to/your/project

# Create a virtual environment
python3 -m venv venv
2. Clone the Project
Clone this repository to your local machine.

git clone https://github.com/Hami-611/E-commerce_Website_using_Django.git
cd your-repository
3. Install Dependencies
Install the necessary Python packages from the requirements.txt file.

# Activate the virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the required packages
pip install -r requirements.txt
4. Install MySQL Client
Since the project uses MySQL as the database, you need to install the MySQL client.

# Install MySQL client
pip install mysqlclient
Ensure that you have MySQL installed and configured on your machine.

5. Activate the Virtual Environment
Activate the virtual environment before running the project.

# On Windows
venv\Scripts\activate
6. Database Migrations
Run the database migrations to set up your database tables.

# Run migrations
python manage.py migrate
7. Create a Superuser
If you want to access the admin panel, create a superuser.

# Create a superuser
python manage.py createsuperuser
Follow the prompts to create your admin account.

8. Run the Development Server
Start the Django development server to test the project.

# Run the server
python manage.py runserver
Visit http://127.0.0.1:8000/ in your browser to view the website.

9. Additional Configurations
Make sure to update your settings.py for MySQL database connection and other project-specific configurations like adding applications.

Feel free to adjust any project-specific details or add more steps based on your setup!
