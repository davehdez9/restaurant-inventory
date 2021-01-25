# Capstone One: Project Proposal - Restaurant Inventory App   

## What goal will my website be designed to achieve?
The goal of the application is to have a friendly inventory system for people who do not have any knowledge in this type of activity. This would help to maintain control of any item and have an appropriate control of these, allowing them to enter and update any product.

## What kind of users will visit your site? What is the demographic of your users?
The type of users who would use the application would be people who work in the restaurant industry. Especially for people without any knowledge in restaurant management to whom this type of activities are part of their daily work.

## What data do you plan to use? 
User information: Basic information of the person who is using the application.
Products Information/details: Product information such as name, price, brand, product category, etc.
Suppliers/Vendors: Information on the companies that distribute the products.

## Outline
### What does your database schema look like?
The database schema consists of 4 tables: Users, Products, Vendors, and Inventory, as outlined below:

<img src="https://raw.githubusercontent.com/davehdez9/restaurant-inventory/main/inventory_schema_capstone.png" />

### What kind of issues might you run into with your API?
It's a free API, but the only small problem would be that it only allows 10 requests per minute.

### Is there any sensitive information I need to secure?
Yes, users will have login information that will need to be secured.

### What functionality will your app include?
Users can register, login and logout.
Users can track the products they use, manage their inventory for the products in stock, and create/view vendor information for each product.

### What will the user flow look like?
-  User can create an account and login to a dashboard
- From the dashboard, user has access to:
  - Products  
    - User can view, create, update, delete products.
    - Each product is stored with a product name, product description, and amount of product that is sold (ie 2 pounds per package), and the vendor that sells the product.
  - Inventory
    - User can view, create, update, and delete products in their inventory
    - Each inventory item is stored with the product information, and the amount of product in stock.
  - Vendors
    - User can view, create, update, and delete vendors their vendor list
    - Each vendor is stored with vendor name, vendor description, vendor contact, contact email, vendor website
  - User Account/Settings
    - User can view their personal information, and update their information, or delete their account.

### What features make your site more than CRUD? Do you have any stretch goals?
-  **Possible stretch goal:** User can set a minimum amount that we would like to have in stock for a product, and create an alert when the amount in stock for that product falls below that minimum amount.
-  **Possible stretch goal:** User can export inventory as a PDF or CSV report.
-  **Possible stretch goal:** Incorporate product orders.
    -  User can view, create, update, and delete product orders.
    -  In each order, they can select products, amounts, and date of order.
    -  Once an order is received, they can mark the order as received on the dashboard.  Marking the order as received will update the inventory amount.




