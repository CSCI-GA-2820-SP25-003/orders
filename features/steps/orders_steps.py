import os
import requests
from behave import given, when, then


@given("the server is started")
def step_impl(context):
    """Ensure the server is started and accessible."""
    context.base_url = os.getenv("BASE_URL", "http://localhost:8080")
    context.resp = requests.get(context.base_url + "/")
    assert context.resp.status_code == 200


@when('I visit the "home page"')
def step_impl(context):
    """Visit the home page of the Order REST API Service."""
    context.resp = requests.get(context.base_url + "/")
    assert context.resp.status_code == 200


@then('I should see "{message}"')
def step_impl(context, message):
    """I should see a message"""
    print(context.resp.text)
    assert message in str(context.resp.text)


@then('I should not see "{message}"')
def step_impl(context, message):
    """I should see a message"""
    assert message not in str(context.resp.text)
