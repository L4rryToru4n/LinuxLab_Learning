### LinuxLab
## Description
Linuxlab is a web app for learning Linux CLI using capture the flag method.

![image](https://github.com/user-attachments/assets/3a24e1be-8f62-438b-acc4-ea510036bd70)

![image](https://github.com/user-attachments/assets/01376e97-9382-475f-b2f2-15873e13dd14)

![image](https://github.com/user-attachments/assets/480403e6-1d0a-4437-ba9f-966578aa8e4f)

![image](https://github.com/user-attachments/assets/8c274d3b-5e0c-4977-9849-0d6986783742)

![image](https://github.com/user-attachments/assets/7ff4d546-5520-480b-9809-530abf1e0de0)


## Tech Stack
This project uses Flask framework, Jinja2 for rendering the page, MySQL for database and Gunicorn module for multithreading. However it requires a minimum of Python version 3.10

## Usage Instructions
In order to run the project, first activate the Python virtual environment.
### Linux
```
source .venv/bin/activate
```
### Windows
```
source .venv/Scripts/Activate
```
After that, run the application using Gunicorn module
```
gunicorn -w 2 -b 0.0.0.0:8080 'linuxlab:.__init__:create_app()'
```

For accessing the virtual lab using SSH
```
ssh user_level_name@ip_address -p 9000
```
