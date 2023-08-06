# Flask Micro Blog

A work through of Miguel Grinberg's 
[Flask Mega Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world).

## Setup

### Run with Poetry

#### Prerequisites

[poetry](https://python-poetry.org/) and 
[poethepoet](https://pypi.org/project/poethepoet/0.18.1/)
are required. Install on local python environment:

    pip install poetry

    pip install poethepoet

Create the `venv` for the application:

    poetry install

If there is no db, or this is the first time running the application:
    
    flask db upgrade


#### Run the application

Run the application locally:

    poetry run poe flask

#### Run the tests

To run the unit tests:
    poetry run poe tests



## Configuration




