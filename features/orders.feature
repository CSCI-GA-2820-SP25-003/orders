Feature: The order service back-end
  As a manager
  I need a RESTful catalog service
  So that I can keep track of all orders

Background:
    Given the following orders
        | customer_name  | status    | product_name  | quantity | price   |
        | Customer One   | CREATED   | T-Shirt       | 2        | 99.99   |
        | Customer Two   | SHIPPED   | Phone         | 1        | 429.99  |
        | Customer Three | CANCELLED | Macbook       | 1        | 999.99  |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Order Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: The server is running
    When I visit the "Health Page"
    Then I should see "Healthy" in the health page
    And I should not see "404 Not Found"