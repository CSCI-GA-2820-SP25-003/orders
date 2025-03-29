# NYU DevOps Project Template

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
![Build Status](https://github.com/CSCI-GA-2820-SP25-003/orders/actions/workflows/ci.yml/badge.svg)

<!-- ## Overview

This project template contains starter code for your class project. The `/service` folder contains your `models.py` file for your model and a `routes.py` file for your service. The `/tests` folder has test case starter code for testing the model and the service separately. All you need to do is add your functionality. You can use the [lab-flask-tdd](https://github.com/nyu-devops/lab-flask-tdd) for code examples to copy from. -->

## Automatic Setup

The best way to use this repo is to start your own repo using it as a git template. To do this just press the green **Use this template** button in GitHub and this will become the source for your repository.

## Manual Setup

You can also clone this repository and then copy and paste the starter code into your project repo folder on your local computer. Be careful not to copy over your own `README.md` file so be selective in what you copy.

There are 4 hidden files that you will need to copy manually if you use the Mac Finder or Windows Explorer to copy files from this folder into your repo folder.

These should be copied using a bash shell as follows:

```bash
    cp .gitignore  ../<your_repo_folder>/
    cp .flaskenv ../<your_repo_folder>/
    cp .gitattributes ../<your_repo_folder>/
```

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
pyproject.toml      - Poetry list of Python libraries required by your code

service/                   - service python package
├── __init__.py            - package initializer
├── config.py              - configuration parameters
├── order.py               - module with database model for order
├── item.py                - module with database model for item
├── routes.py              - module with order service routes
└── common                 - common code package
    ├── cli_commands.py    - Flask command to recreate all tables
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/                     - test cases package
├── __init__.py            - package initializer
├── factories.py           - Factory for testing with fake objects
├── test_cli_commands.py   - test suite for the CLI
├── test_models.py         - test suite for business models
└── test_routes.py         - test suite for service routes
```


## Instructions

### Running the API

To start the REST API, use the following command:
```bash
make run
```

## Commands
### Index Page

To access index page, in browser, go to the url:
```url
http://localhost:8080/
```

### Orders
#### Create an Order

```bash
curl -X POST "http://127.0.0.1:8080/orders" \
-H "Content-Type: application/json" \
-d '{"customer_name": "<name>", "status": "<status>"}'
```

#### List Orders
##### List all orders
```bash
curl -X GET "http://127.0.0.1:8080/orders"
```

##### List all orders, filtered by status
```bash
curl -X GET "http://127.0.0.1:8080/orders?status=<status>"
```

##### List order with order_id
```bash
curl -X GET "http://127.0.0.1:8080/orders/<order_id>"
```

#### Update Orders
```bash
curl -X PUT "http://127.0.0.1:8080/orders/<order_id>" \
     -H "Content-Type: application/json" \
     -d '{"customer_name": "<name>", "status": "<status>"}'
```

#### Delete Orders
```bash
curl -X DELETE "http://127.0.0.1:8080/orders/<order_id>"
```

### Items
#### Create and Add an Item
```bash
curl -X POST "http://127.0.0.1:8080/orders/<order_id>/items" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "<item_name>",
           "price": <price>,
           "quantity": <qty>
         }'
```

#### List Items
##### List all items corresponding to order_id
```bash
curl -X GET "http://127.0.0.1:8080/orders/<order_id>/items"
```

##### List item corresponding to order_id and item_id
```bash
curl -X GET "http://127.0.0.1:8080/orders/<order_id>/items/<item_id>"
```

#### Update Items
```bash
curl -X PUT "http://127.0.0.1:8080/orders/<order_id>/items/<item_id>" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "<new_item>",
           "price": <new_price>,
           "quantity": <new_qty>
         }'
```

#### Delete Items
```bash
curl -X DELETE "http://127.0.0.1:8080/orders/<order_id>/items/<item_id>"
```

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
