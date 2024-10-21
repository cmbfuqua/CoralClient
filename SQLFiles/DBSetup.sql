-- Create User Table
drop table if exists LoyaltyProgram;
drop table if exists PurchaseHistory;
drop table if exists InventoryItem;
drop table if exists Categories;
drop table if exists Consignment;
drop table if exists Customer;
drop table if exists UserTable;

CREATE TABLE `UserTable` (
    `UserID` INT NOT NULL AUTO_INCREMENT,
    `Username` VARCHAR(255) NOT NULL,
    `Password` VARCHAR(255) NOT NULL,
    `FirstName` VARCHAR(255) NOT NULL,
    `LastName` VARCHAR(255) NOT NULL,
    `PhoneNumber` int,
    `Role` VARCHAR(50) NOT NULL, -- For different permissions (admin, staff, etc.)
    `CreatedBy` INT,
    `CreatedOn` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `ModifiedBy` INT,
    `ModifiedOn` DATETIME,
    PRIMARY KEY (`UserID`)
);

-- Create Customer Table
CREATE TABLE `Customer` (
    `CustomerID` INT NOT NULL AUTO_INCREMENT,
    `FirstName` VARCHAR(255),
    `LastName` VARCHAR(255),
    `DOB` VARCHAR(255),
    `PhoneNumber` int,
    `Email` VARCHAR(255),
    `InStoreCredit` DECIMAL(10, 2) DEFAULT 0.00,
    `CreatedBy` INT,
    `CreatedOn` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `ModifiedBy` INT,
    `ModifiedOn` DATETIME,
    PRIMARY KEY (`CustomerID`),
    FOREIGN KEY	(`CreatedBy`) REFERENCES `UserTable`(`UserID`)
);



CREATE TABLE `Categories` (
    `CategoryID` INT NOT NULL AUTO_INCREMENT,
	`CategoryName` VARCHAR(255),
    `CreatedBy` INT,
    `CreatedOn` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `ModifiedBy` INT,
    `ModifiedOn` DATETIME,
    Primary Key (`CategoryID`),
    FOREIGN KEY	(`CreatedBy`) REFERENCES `UserTable`(`UserID`)
    );
    
-- Create Inventory Table
CREATE TABLE `InventoryItem` (
    `InventoryItemID` INT NOT NULL AUTO_INCREMENT,
    `ItemName` VARCHAR(255),
    `CategoryID` INT,
    `Price` DECIMAL(10, 2),
    `InventoryAmount` int,
    `ImageURL` VARCHAR(255), -- For storing the path to the image
    `CreatedBy` INT,
    `CreatedOn` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `ModifiedBy` INT,
    `ModifiedOn` DATETIME,
    PRIMARY KEY (`InventoryItemID`), 
    FOREIGN KEY (`CategoryID`) REFERENCES `Categories`(`CategoryID`),
    FOREIGN KEY	(`CreatedBy`) REFERENCES `UserTable`(`UserID`)
);

-- Create Consignment Table
CREATE TABLE `Consignment` (
    `ConsignmentID` INT NOT NULL AUTO_INCREMENT,
    `CustomerID` INT,
    `ItemName` VARCHAR(255),
    `Price` DECIMAL(10, 2),
    `CreatedBy` INT,
    `CreatedOn` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `ModifiedBy` INT,
    `ModifiedOn` DATETIME,
    PRIMARY KEY (`ConsignmentID`),
    FOREIGN KEY	(`CreatedBy`) REFERENCES `UserTable`(`UserID`),
    Foreign Key (`CustomerID`) REFERENcEs `Customer`(`CustomerID`)
);

-- Create Loyalty Program Table
CREATE TABLE `LoyaltyProgram` (
    `LoyaltyID` INT NOT NULL AUTO_INCREMENT,
    `CustomerID` INT,
    `CreditAdded` DECIMAL(10, 2),
    `Reason` VARCHAR(255),
    `CreatedBy` INT,
    `CreatedOn` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`LoyaltyID`),
    FOREIGN KEY (`CustomerID`) REFERENCES `Customer`(`CustomerID`),
    FOREIGN KEY	(`CreatedBy`) REFERENCES `UserTable`(`UserID`)
);

-- Insert test user
-- Create Purchase History Table
CREATE TABLE `PurchaseHistory` (
    `PurchaseID` INT NOT NULL AUTO_INCREMENT,
    `CustomerID` INT,
    `InventoryItemID` INT,
    `PurchaseDate` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `PricePaid` DECIMAL(10, 2),
    `CreatedBy` INT,
    `CreatedOn` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `ModifiedBy` INT,
    `ModifiedOn` DATETIME,
    PRIMARY KEY (`PurchaseID`),
    FOREIGN KEY (`CustomerID`) REFERENCES `Customer`(`CustomerID`),
    FOREIGN KEY (`InventoryItemID`) REFERENCES `InventoryItem`(`InventoryItemID`),
    FOREIGN KEY	(`CreatedBy`) REFERENCES `UserTable`(`UserID`)
);