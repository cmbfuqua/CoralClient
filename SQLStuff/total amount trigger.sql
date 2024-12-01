CREATE TRIGGER UpdateBillTotalAmount
ON BillLineItem
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    -- Update TotalAmount for affected bills
    UPDATE Bill
    SET TotalAmount = (
        SELECT COALESCE(SUM(Quantity * UnitPrice), 0)
        FROM BillLineItem
        WHERE BillLineItem.BillID = Bill.BillID
    )
    WHERE BillID IN (
        -- Include affected BillIDs from INSERTED, DELETED tables
        SELECT DISTINCT BillID FROM INSERTED
        UNION
        SELECT DISTINCT BillID FROM DELETED
    );
END;
GO
