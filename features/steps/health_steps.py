import os
import requests
from behave import given, when, then


@when('I visit the "health page"')
def step_impl(context):
    """Visit the health page of the Order REST API Service."""
    context.resp = requests.get(context.base_url + "/health")
    assert context.resp.status_code == 200
