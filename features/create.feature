Feature: Create an order
  As a developer
  I need to add BDD to our create route
  So that the route is clearly defined and understood by all stakeholders

  Background:
    Given the server is started

  Scenario: Create an order with only name
    When I create an order with name:
      | customer_name |
      | Alice         |
    Then an order should be created successfully

  Scenario: Successfully create orders with name and status
    When I create orders with name and status:
      | customer_name | status  |
      | John Doe      | PENDING |
      | Jane Smith    | SHIPPED |
    Then all orders should be created successfully

  
