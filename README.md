# Areus
Simplified web application for managing databases, inspired by phpMyAdmin. 
## Idea
PhpMyAdmin, while powerful, has certain drawbacks including outdated design, excessive functionality, and occasional performance issues. This project aims to address these issues by providing a modern, clean, and simplified alternative for database management using the Django framework. 
# Technological stack
- Django
- Django Rest Framework
- Sessions
- MySQL
- Swagger
- Docker
- HTML/CSS
- JavaScript
- TypeScript
# Swagger
https://sviatoslavbaranetskyi.github.io/Areus/
# Starting a project
To run the project, you first need to create an .env file in the root directory and specify the following environment variables to connect to the database:
```
DB_NAME=test
DB_USER=user
DB_PASS=pass
DB_ROOT_PASSWORD=pass
```
After this, you can run the project using the `docker-compose up` command. Choose whether you need to run the project in development or production mode using the respective command:
- For development mode:
```
docker compose -f docker-compose.dev.yml up
```
- For production mode:
```
docker compose -f docker-compose.prod.yml up
```
# Future plans:
- Enhance security features
- Implement support for additional database management systems
- Enhance the user interface
## Developers
- Sviatoslav Baranetskyi<br>
  Email: svyatoslav.baranetskiy738@gmail.com
- Danylo Havryliv<br>
  Email: evg829@gmail.com
- Huk Maksym<br>
  Email: mkaimg1@gmail.com
