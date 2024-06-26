# SOFTWARE-ARCHITECTURE

## Graduate Level Course | USC 

## PAndemic TRacking OnLine App (PATROL App)

PATROL is an innovative Android application designed to address the challenges posed during a pandemic, especially with crowd monitoring and health management in various locations. With a focus on user empowerment and data-driven decision-making, PATROL enables users to monitor crowd density, track health statuses, ensure effective communication channels, and facilitate resource management. Leveraging advanced technologies like Bluetooth Low Energy (BLE), location services, and firebase messaging service, the app provides real-time information to the general public,  government officials, e-commerce vendors, developers, and researchers ensuring timely response to health threats, effective communication during emergencies and extending the data to implement further solutions. 

## PATROL Frontend

View - [View Android Code](https://github.com/nil-mohanty/PATROLApp)

## PATROL Server

This is the backend server of PATROL created using Python, Flask, Firebase

```bash
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

## Python Environment
```bash
-- python -m venv venv
-- venv\Scripts\activate
-- pip install -r requirements.txt
-- python main.py
```


## Poetry 
- Dependency management tool
```bash
-- MAC: curl -sSL https://install.python-poetry.org | python3 - --git https://github.com/python-poetry/poetry.git@main
-- WINDOWS: (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
-- poetry --version
-- poetry add <package-name>
```


## Run

```bash
-- poetry update
-- poetry shell
-- python main.py
```


## Docker Instructions

- Make a configuration file``.env``
- Run the command ``docker build --tag patrol-docker .``
- Then run ``docker run -d -p 5001:5000 patrol-docker``
- In the above command, ``5001`` is the port of local machine and ``5000`` is the port of the docker network
- The server will be in either ``http://localhost:5001`` or ``http://0.0.0.0:5001``


## Structure

```bash

PATROL:.
│   .env
│   .gitignore
│   .pre-commit-config.yaml
│   Dockerfile
│   main.py
│   patrol.log
│   poetry.lock
│   pyproject.toml
│   README.md
│   requirements.txt
│
└───src
    │   app.py
    │   firebase.py
    │   settings.py
    │   __init__.py
    │
    ├───database
    │   crud.py
    │   db.py
    │   model.py
    │   schema.txt
    │   __init__.py
    │
    ├───router
    │   user.py
    │   notification.py
    │   __init__.py
    │
    ├───static
    │    log_config.ini
    │    __init__.py
    │
    ├───utils
    │   logger.py
    │   __init__.py
    │
    └───__pycache__

```
