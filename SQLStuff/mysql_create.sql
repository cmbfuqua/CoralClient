-- Create Database
CREATE DATABASE CoralClientSeller;
USE CoralClientSeller;

-- Create tables
CREATE TABLE roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    name NVARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE permissions (
    permission_id INT AUTO_INCREMENT PRIMARY KEY,
    name NVARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(100)
);

CREATE TABLE role_permissions (
    role_id INT NOT NULL,
    permission_id INT NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(permission_id) ON DELETE CASCADE
);

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username NVARCHAR(50) NOT NULL UNIQUE,
    password_hash NVARCHAR(128) NOT NULL,
    email NVARCHAR(100) NOT NULL UNIQUE,
    role_id INT,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    DOB DATE,
    phone_number VARCHAR(20),
    is_maintenance BOOLEAN,
    in_store_credit FLOAT,
    PasswordReset BOOLEAN,
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);

CREATE TABLE item_types (
    item_type_id INT AUTO_INCREMENT PRIMARY KEY,
    name NVARCHAR(50) NOT NULL
);

CREATE TABLE item_subtypes (
    item_subtype_id INT AUTO_INCREMENT PRIMARY KEY,
    item_type_id INT,
    name NVARCHAR(50) NOT NULL,
    FOREIGN KEY (item_type_id) REFERENCES item_types(item_type_id)
);

CREATE TABLE consignment_products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    image_url NVARCHAR(255),
    item_type_id INT,
    item_subtype_id INT,
    seller_id INT,
    featured BOOLEAN,
    order_status VARCHAR(5),
    FOREIGN KEY (item_type_id) REFERENCES item_types(item_type_id),
    FOREIGN KEY (item_subtype_id) REFERENCES item_subtypes(item_subtype_id),
    FOREIGN KEY (seller_id) REFERENCES users(user_id)
);

CREATE TABLE maintenance_visits (
    visit_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    before_picture VARCHAR(255),
    ammonia FLOAT,
    nitrite FLOAT,
    nitrate FLOAT,
    ph FLOAT,
    phosphates FLOAT,
    calcium FLOAT,
    magnesium FLOAT,
    alkalinity FLOAT,
    notes TEXT,
    recommendations TEXT,
    after_picture VARCHAR(255),
    date_of_visit DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES users(user_id)
);

CREATE TABLE Bill (
    BillID INT AUTO_INCREMENT PRIMARY KEY,
    VisitID INT NOT NULL,
    TotalAmount DECIMAL(10, 2) NOT NULL,
    IsPaid BOOLEAN DEFAULT 0,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    PaidAt DATETIME,
    Notes TEXT,
    FOREIGN KEY (VisitID) REFERENCES maintenance_visits(visit_id) ON DELETE CASCADE
);

CREATE TABLE BillLineItem (
    LineItemID INT AUTO_INCREMENT PRIMARY KEY,
    BillID INT NOT NULL,
    Description NVARCHAR(255) NOT NULL,
    Quantity INT DEFAULT 1,
    UnitPrice DECIMAL(10, 2) NOT NULL,
    TotalPrice DECIMAL(10, 2) GENERATED ALWAYS AS (Quantity * UnitPrice) STORED,
    FOREIGN KEY (BillID) REFERENCES Bill(BillID) ON DELETE CASCADE
);

CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    buyer_id INT,
    seller_id INT,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    product_dropoff DATE,
    product_pickup DATE,
    payment_status VARCHAR(50),
    order_status VARCHAR(5),
    FOREIGN KEY (product_id) REFERENCES consignment_products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (buyer_id) REFERENCES users(user_id),
    FOREIGN KEY (seller_id) REFERENCES users(user_id)
);

-- Create view
CREATE VIEW vw_permissions AS
SELECT r.role_id, r.name AS role_name, p.*
FROM roles r
JOIN role_permissions rp ON r.role_id = rp.role_id
JOIN permissions p ON rp.permission_id = p.permission_id;

-- Add User
CREATE USER 'CoralClientSellerApp'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON CoralClientSeller.* TO 'CoralClientSellerApp'@'localhost';

-- Apply roles
-- Note: MySQL doesn't have db_owner/db_datareader/db_datawriter, use GRANT as needed.
