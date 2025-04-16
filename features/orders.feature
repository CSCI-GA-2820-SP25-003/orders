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

Scenario: Query Orders by Various Criteria
    When I visit the "Home Page"
    And I press the "Clear" button
    # Test filtering by customer name
    When I set the "Customer Name" to "Customer One"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Customer One" in the results
    And I should not see "Customer Two" in the results
    And I should not see "Customer Three" in the results
    
    # Test filtering by status
    When I press the "Clear" button
    And I select "SHIPPED" in the "Status" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Customer Two" in the results
    And I should not see "Customer One" in the results
    And I should not see "Customer Three" in the results
    
    # Test filtering by product name
    When I press the "Clear" button
    And I set the "Product Name" to "Macbook"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Customer Three" in the results
    And I should not see "Customer One" in the results
    And I should not see "Customer Two" in the results
    
    # Test combined filters
    When I press the "Clear" button
    And I set the "Customer Name" to "Customer Three"
    And I select "CANCELLED" in the "Status" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Customer Three" in the results
    And I should see "CANCELLED" in the results
    And I should not see "Customer One" in the results
    And I should not see "Customer Two" in the results

Scenario: Cancel an Order
    When I visit the "Home Page"
    And I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    When I copy the "Order ID" field
    And I press the "Clear" button
    And I paste the "Order ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Customer One" in the "Customer Name" field
    And I should see "CREATED" in the "Status" field
    When I press the "Cancel" button
    Then I should see the message "Success"
    And I should see "CANCELLED" in the "Status" field
    When I press the "Clear" button
    And I paste the "Order ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "CANCELLED" in the "Status" field