# Product Catalog API
 
This repository contains the code for a scalable backend API to manage branded product catalogs and search products with filtering by category and brand.
 
## Installation
 
### Locally
 
All the code and examples were tested on Python 3.11.13 and Node v22.9.0.
 
For Building the Flask application, create a virtual environment and install the requirements with pip.
 
    python3.11 -m venv venv
    source /venv/bin/activate
    pip install -U pip setuptools wheel
    pip install -r requirements.txt
 
For Building the React application, need package.json file to install dependencies with npm.
 
    npm install
    npm run dev
 
OR to create production build
 
    npm run build 

### Using Docker
 
For Building Flask application with docker, use the following commands.
 
    docker build -t product-catalog-api -f docker/Dockerfile.api .
 
OR using docker-compose
 
    docker-compose build api
 
For Building React application with docker, use the following commands.
 
    docker build -t product-catalog-api -f docker/Dockerfile.client .
 
OR using docker-compose
 
    docker-compose build client
 
 
## Running
 
### Locally
 
The application uses following command to perform common tasks such as creating the
database and starting a development server.
 
    flask db init
    flask db migrate
    flask db upgrade
 
After that, you can run the application with the following command:
 
    python app.py
 
 
You can add `--help` to see what other start up options are available.
  
### Using Docker
 
For running the services using docker, you can use the following command to start
each service in separate containers after building client and api images.
 
    docker-compose up
 
you can add `--build` to build required images before starting.
 
By default, docker refers to docker-compose.yml file to orchestrate container runtime environments.
You can add `-f` to pass your YAML file to start the app.
 
 
## Usage
After running the application, it can be accessed via browser on http://localhost:3000.
 