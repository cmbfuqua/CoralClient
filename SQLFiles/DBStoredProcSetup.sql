DROP PROCEDURE IF EXISTS `UserInsert`;
DROP PROCEDURE IF EXISTS `UserUpdate`;
DROP PROCEDURE IF EXISTS `UserDelete`;

DROP PROCEDURE IF EXISTS `CustomerInsert`;
DROP PROCEDURE IF EXISTS `CustomerUpdate`;
DROP PROCEDURE IF EXISTS `CustomerDelete`;

DROP PROCEDURE IF EXISTS `InventoryItemInsert`;
DROP PROCEDURE IF EXISTS `InventoryItemUpdate`;
DROP PROCEDURE IF EXISTS `InventoryItemDelete`;

DROP PROCEDURE IF EXISTS `LoyaltyProgramInsert`;
DROP PROCEDURE IF EXISTS `LoyaltyProgramUpdate`;
DROP PROCEDURE IF EXISTS `LoyaltyProgramDelete`;

DROP PROCEDURE IF EXISTS `ConsignmentInsert`;
DROP PROCEDURE IF EXISTS `ConsignmentUpdate`;
DROP PROCEDURE IF EXISTS `ConsignmentDelete`;

DROP PROCEDURE IF EXISTS `PurchaseHistoryInsert`;
DROP PROCEDURE IF EXISTS `PurchaseHistoryUpdate`;
DROP PROCEDURE IF EXISTS `PurchaseHistoryDelete`;



DELIMITER //
-- ----------------------------------------------------------------
-- User info
-- ----------------------------------------------------------------
CREATE PROCEDURE UserInsert (
    IN p_Username VARCHAR(50),
    IN p_Password VARCHAR(50),
    IN p_FirstName VARCHAR(50),
    IN p_LastName VARCHAR(50),
    IN p_PhoneNumber VARCHAR(15),  -- Assuming phone numbers may contain special characters
    IN p_Role VARCHAR(20),
    IN p_CreatedBy INT
)
BEGIN
    INSERT INTO Users (Username, Password, FirstName, LastName, PhoneNumber, Role, CreatedBy, CreatedOn)
    VALUES (p_Username, p_Password, p_FirstName, p_LastName, p_PhoneNumber, p_Role, p_CreatedBy, NOW());
END //



CREATE PROCEDURE UserUpdate (
    IN p_UserID INT,
    IN p_Username NVARCHAR(50),
    IN p_Password NVARCHAR(50),
    IN p_FirstName NVARCHAR(50),
    IN p_LastName NVARCHAR(50),
    IN p_PhoneNumber INT,
    IN p_Role NVARCHAR(20),
    IN p_ModifiedBy INT
)
BEGIN
    UPDATE Users
    SET Username = p_Username,
        Password = p_Password,
        FirstName = p_FirstName,
        LastName = p_LastName,
        PhoneNumber = p_PhoneNumber,
        Role = p_Role,
        ModifiedBy = p_ModifiedBy,
        ModifiedOn = GETDATE()
    WHERE UserID = p_UserID;
END //

CREATE PROCEDURE UserDelete (
    IN p_UserID INT
)
BEGIN
    DELETE FROM Users WHERE UserID = p_UserID;
END //


-- ----------------------------------------------------------
-- Customer info
-- ----------------------------------------------------------
CREATE PROCEDURE CustomerInsert (
    IN p_FirstName NVARCHAR(50),
    IN p_LastName NVARCHAR(50),
    IN p_DOB NVARCHAR(50),
    IN p_PhoneNumber INT,
    IN p_Email NVARCHAR(50),
    IN p_InStoreCredit DECIMAL(10,2),
    IN p_CreatedBy INT
)
BEGIN
    INSERT INTO Customers (FirstName, LastName, DOB, PhoneNumber, Email, InStoreCredit, CreatedBy, CreatedOn)
    VALUES (p_FirstName, p_LastName, p_DOB, p_PhoneNumber, p_Email, p_InStoreCredit, p_CreatedBy, GETDATE());
END //

CREATE PROCEDURE CustomerUpdate (
    IN p_CustomerID INT,
    IN p_FirstName NVARCHAR(50),
    IN p_LastName NVARCHAR(50),
    IN p_DOB NVARCHAR(50),
    IN p_PhoneNumber INT,
    IN p_Email NVARCHAR(50),
    IN p_InStoreCredit DECIMAL(10,2),
    IN p_ModifiedBy INT
)
BEGIN
    UPDATE Customers
    SET FirstName = p_FirstName,
        LastName = p_LastName,
        DOB = p_DOB,
        PhoneNumber = p_PhoneNumber,
        Email = p_Email,
        InStoreCredit = p_InStoreCredit,
        ModifiedBy = p_ModifiedBy,
        ModifiedOn = GETDATE()
    WHERE CustomerID = p_CustomerID;
END //

CREATE PROCEDURE CustomerDelete (
    IN p_CustomerID INT
)
BEGIN
    DELETE FROM Customers WHERE CustomerID = p_CustomerID;
END //


-- ------------------------------------------------------------
-- Inventory Item info
-- ------------------------------------------------------------
CREATE PROCEDURE InventoryItemInsert (
    IN p_ItemName NVARCHAR(100),
    IN p_CategoryID INT,
    IN p_Price DECIMAL(10,2),
    IN p_InventoryAmount INT,
    IN p_ImageURL NVARCHAR(255),
    IN p_CreatedBy INT
)
BEGIN
    INSERT INTO InventoryItems (ItemName, CategoryID, Price, InventoryAmount, ImageURL, CreatedBy, CreatedOn)
    VALUES (p_ItemName, p_CategoryID, p_Price, p_InventoryAmount, p_ImageURL, p_CreatedBy, GETDATE());
END //

CREATE PROCEDURE InventoryItemUpdate (
    IN p_InventoryItemID INT,
    IN p_ItemName NVARCHAR(100),
    IN p_CategoryID INT,
    IN p_Price DECIMAL(10,2),
    IN p_InventoryAmount INT,
    IN p_ImageURL NVARCHAR(255),
    IN p_ModifiedBy INT
)
BEGIN
    UPDATE InventoryItems
    SET ItemName = p_ItemName,
        CategoryID = p_CategoryID,
        Price = p_Price,
        InventoryAmount = p_InventoryAmount,
        ImageURL = p_ImageURL,
        ModifiedBy = p_ModifiedBy,
        ModifiedOn = GETDATE()
    WHERE InventoryItemID = p_InventoryItemID;
END //

CREATE PROCEDURE InventoryItemDelete (
    IN p_InventoryItemID INT
)
BEGIN
    DELETE FROM InventoryItems WHERE InventoryItemID = p_InventoryItemID;
END //


-- -------------------------------------------------------------
-- Consignment info
-- -------------------------------------------------------------
CREATE PROCEDURE ConsignmentInsert (
    IN p_CustomerID INT,
    IN p_ItemName NVARCHAR(100),
    IN p_Price DECIMAL(10,2),
    IN p_CreatedBy INT
)
BEGIN
    INSERT INTO Consignments (CustomerID, ItemName, Price, CreatedBy, CreatedOn)
    VALUES (p_CustomerID, p_ItemName, p_Price, p_CreatedBy, GETDATE());
END //

CREATE PROCEDURE ConsignmentUpdate (
    IN p_ConsignmentID INT,
    IN p_CustomerID INT,
    IN p_ItemName NVARCHAR(100),
    IN p_Price DECIMAL(10,2),
    IN p_ModifiedBy INT
)
BEGIN
    UPDATE Consignments
    SET CustomerID = p_CustomerID,
        ItemName = p_ItemName,
        Price = p_Price,
        ModifiedBy = p_ModifiedBy,
        ModifiedOn = GETDATE()
    WHERE ConsignmentID = p_ConsignmentID;
END //

CREATE PROCEDURE ConsignmentDelete (
    IN p_ConsignmentID INT
)
BEGIN
    DELETE FROM Consignments WHERE ConsignmentID = p_ConsignmentID;
END //


-- ----------------------------------------------------------------
-- Loyalty Program info
-- ----------------------------------------------------------------
CREATE PROCEDURE LoyaltyProgramInsert (
    IN p_CustomerID INT,
    IN p_CreditAdded DECIMAL(10,2),
    IN p_Reason NVARCHAR(255),
    IN p_CreatedBy INT
)
BEGIN
    INSERT INTO LoyaltyPrograms (CustomerID, CreditAdded, Reason, CreatedBy, CreatedOn)
    VALUES (p_CustomerID, p_CreditAdded, p_Reason, p_CreatedBy, GETDATE());
END //

CREATE PROCEDURE LoyaltyProgramUpdate (
    IN p_LoyaltyID INT,
    IN p_CustomerID INT,
    IN p_CreditAdded DECIMAL(10,2),
    IN p_Reason NVARCHAR(255)
)
BEGIN
    UPDATE LoyaltyPrograms
    SET CustomerID = p_CustomerID,
        CreditAdded = p_CreditAdded,
        Reason = p_Reason
    WHERE LoyaltyID = p_LoyaltyID;
END //

CREATE PROCEDURE LoyaltyProgramDelete (
    IN p_LoyaltyID INT
)
BEGIN
    DELETE FROM LoyaltyPrograms WHERE LoyaltyID = p_LoyaltyID;
END //

-- ----------------------------------------------------------
-- Purchase history info
-- ----------------------------------------------------------
CREATE PROCEDURE PurchaseHistoryInsert (
    IN p_CustomerID INT,
    IN p_InventoryItemID INT,
    IN p_PurchaseDate DATETIME,
    IN p_PurchasePrice DECIMAL(10,2),
    IN p_Quantity INT,
    IN p_TotalPrice DECIMAL(10,2),
    IN p_CreatedBy INT
)
BEGIN
    INSERT INTO PurchaseHistory (CustomerID, InventoryItemID, PurchaseDate, PurchasePrice, Quantity, TotalPrice, CreatedBy, CreatedOn)
    VALUES (p_CustomerID, p_InventoryItemID, p_PurchaseDate, p_PurchasePrice, p_Quantity, p_TotalPrice, p_CreatedBy, GETDATE());
END //

CREATE PROCEDURE PurchaseHistoryUpdate (
    IN p_PurchaseID INT,
    IN p_CustomerID INT,
    IN p_InventoryItemID INT,
    IN p_PurchaseDate DATETIME,
    IN p_PurchasePrice DECIMAL(10,2),
    IN p_Quantity INT,
    IN p_TotalPrice DECIMAL(10,2)
)
BEGIN
    UPDATE PurchaseHistory
    SET CustomerID = p_CustomerID,
        InventoryItemID = p_InventoryItemID,
        PurchaseDate = p_PurchaseDate,
        PurchasePrice = p_PurchasePrice,
        Quantity = p_Quantity,
        TotalPrice = p_TotalPrice
    WHERE PurchaseID = p_PurchaseID;
END //

CREATE PROCEDURE PurchaseHistoryDelete (
    IN p_PurchaseID INT
)
BEGIN
    DELETE FROM PurchaseHistory WHERE PurchaseID = p_PurchaseID;
END //


