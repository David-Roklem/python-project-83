### Hexlet tests and linter status:
[![Actions Status](https://github.com/David-Roklem/python-project-83/workflows/hexlet-check/badge.svg)](https://github.com/David-Roklem/python-project-83/actions)
[![lint_check](https://github.com/David-Roklem/python-project-83/actions/workflows/lint-check.yaml/badge.svg?branch=main)](https://github.com/David-Roklem/python-project-83/actions/workflows/lint-check.yaml)
[![Maintainability](https://api.codeclimate.com/v1/badges/fe790627cc6e86b7db59/maintainability)](https://codeclimate.com/github/David-Roklem/python-project-83/maintainability)


# python-project-83
This project deployed on Railway.app. Check it out [here](https://python-project-83-production-98c7.up.railway.app/)


## Getting Started

### Dependencies
```
python = ">=3.8.1,<4.0.0"
Flask = "^2.2.3"
gunicorn = "^20.1.0"
python-dotenv = "^1.0.0"
psycopg2-binary = "^2.9.6"
validators = "^0.20.0"
beautifulsoup4 = "^4.12.2"
requests = "^2.30.0"
flake8 = "^6.0.0"
```

### Installing
This project uses poetry as a package manager as well as virtual environment. So clone this project, then install poetry with the command in terminal:
```
git clone https://github.com/GregTMJ/python-project-83.git
```
```
pip install poetry
```
After that, using short commands from Makefile, run:
```
make install
```
The last command will install all the needed dependencies

### Executing program
As this project uses [https://pypi.org/project/python-dotenv/](python-dotenv) library, first of all you need to configure your .env with the following variables:
```
SECRET_KEY
DATABASE_URL
```
For `SECRET_KEY` I recommend using repl type the next commands:
```
>>> import secrets
>>> secrets.token_hex(16)
```
This will generate a hexadecimal secret key, safe enough for production use

DATABASE_URL variable is set up by following this scheme:
`{provider}://{user}:{password}@{host}:{port}/{db}`

For example:
```
DATABASE_URL=postgresql://janedoe:mypassword@localhost:5432/mydb
```

That's it, you can now use and test the project.
