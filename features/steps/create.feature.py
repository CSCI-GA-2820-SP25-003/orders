from behave import given, when, then
import os
import requests


@when("I create orders with name and status")
def step_impl(context):
    context.responses = []
    for row in context.table:
        payload = {
            "customer_name": row["customer_name"],
            "status": row["status"].upper(),
        }
        response = requests.post(f"{context.base_url}/orders", json=payload)
        context.responses.append(response)


@then("all orders should be created successfully")
def step_impl(context):
    for response in context.responses:
        assert (
            response.status_code == 201
        ), f"Expected 201 Created, got {response.status_code}"


@when("I create an order with name")
def step_impl(context):
    row = context.table[0]
    payload = {"customer_name": row["customer_name"]}
    response = requests.post(f"{context.base_url}/orders", json=payload)
    context.response = response
    context.order = response.json() if response.status_code == 201 else {}


@then("an order should be created successfully")
def step_impl(context):
    assert (
        context.response.status_code == 201
    ), f"Expected 201 but got {context.response.status_code}"
    assert "id" in context.order, "No order ID returned"
    assert context.order["customer_name"] == "Alice"
    assert (
        context.order["status"] == "PENDING"
    ), f"Expected default status 'PENDING', got {context.order['status']}"


@when("I try to create an order with missing name")
def step_impl(context):
    # No customer_name provided
    payload = {"status": "PENDING"}

    response = requests.post(f"{context.base_url}/orders", json=payload)
    context.response = response


@then("the order creation should fail")
def step_impl(context):
    # Expecting 400 Bad Request
    assert (
        context.response.status_code == 400
    ), f"Expected failure 400, got {context.response.status_code}"


@when("I create an order with name and non-existent status:")
def step_impl(context):
    row = context.table[0]
    payload = {
        "customer_name": row["customer_name"],
        "status": row["status"],
    }

    response = requests.post(f"{context.base_url}/orders", json=payload)
    context.response = response
