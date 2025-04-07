Feature: The order service back-end
  As a manager
  I need a RESTful catalog service
  So that I can keep track of all orders

Background:
  Given the server is started

Scenario: The server is running
  When I visit the "home page"
  Then I should see "Order Demo RESTful Service"
  And I should not see "404 Not Found"


