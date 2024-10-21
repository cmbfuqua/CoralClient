using Dapper;
using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DataAssets.Models
{
    public class PurchaseHistory
    {
        public int PurchaseID { get; set; }          // Primary Key
        public int CustomerID { get; set; }          // Foreign Key from Customers
        public int InventoryItemID { get; set; }     // Foreign Key from InventoryItems
        public DateTime PurchaseDate { get; set; }   // Date of Purchase
        public decimal PurchasePrice { get; set; }   // Price at the time of purchase
        public int Quantity { get; set; }            // Quantity purchased
        public decimal TotalPrice { get; set; }      // Total price for the purchase
        public int CreatedBy { get; set; }           // User who created the record
        public DateTime CreatedOn { get; set; }      // Timestamp of record creation


        public class PurchaseHistoryRepository
        {
            public static void InsertPurchaseHistory(IDbConnection conn, PurchaseHistory purchase)
            {
                var p = new DynamicParameters();
                p.Add("@CustomerID", purchase.CustomerID);
                p.Add("@InventoryItemID", purchase.InventoryItemID);
                p.Add("@PurchaseDate", purchase.PurchaseDate);
                p.Add("@PurchasePrice", purchase.PurchasePrice);
                p.Add("@Quantity", purchase.Quantity);
                p.Add("@TotalPrice", purchase.TotalPrice);
                p.Add("@CreatedBy", purchase.CreatedBy);

                conn.Execute("dbo.PurchaseHistoryInsert", param: p, commandType: CommandType.StoredProcedure);
            }

            public static void UpdatePurchaseHistory(IDbConnection conn, PurchaseHistory purchase)
            {
                var p = new DynamicParameters();
                p.Add("@PurchaseID", purchase.PurchaseID);
                p.Add("@CustomerID", purchase.CustomerID);
                p.Add("@InventoryItemID", purchase.InventoryItemID);
                p.Add("@PurchaseDate", purchase.PurchaseDate);
                p.Add("@PurchasePrice", purchase.PurchasePrice);
                p.Add("@Quantity", purchase.Quantity);
                p.Add("@TotalPrice", purchase.TotalPrice);

                conn.Execute("dbo.PurchaseHistoryUpdate", param: p, commandType: CommandType.StoredProcedure);
            }

            public static void DeletePurchaseHistory(IDbConnection conn, int purchaseId)
            {
                var p = new DynamicParameters();
                p.Add("@PurchaseID", purchaseId);

                conn.Execute("dbo.PurchaseHistoryDelete", param: p, commandType: CommandType.StoredProcedure);
            }
        }



    }

}
