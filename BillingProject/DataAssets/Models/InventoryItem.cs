using Dapper;
using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DataAssets.Models
{
    public class InventoryItem
    {
        public int InventoryItemID { get; set; }
        public string ItemName { get; set; }
        public int CategoryID { get; set; }
        public decimal Price { get; set; }
        public int InventoryAmount { get; set; }
        public string ImageURL { get; set; }
        public int CreatedBy { get; set; }
        public DateTime CreatedOn { get; set; }
        public int? ModifiedBy { get; set; }
        public DateTime? ModifiedOn { get; set; }

        public static void InsertInventoryItem(IDbConnection conn, InventoryItem item)
        {
            var p = new DynamicParameters();
            p.Add("@ItemName", item.ItemName);
            p.Add("@CategoryID", item.CategoryID);
            p.Add("@Price", item.Price);
            p.Add("@InventoryAmount", item.InventoryAmount);
            p.Add("@ImageURL", item.ImageURL);
            p.Add("@CreatedBy", item.CreatedBy);

            conn.Execute("dbo.InventoryItemInsert", param: p, commandType: CommandType.StoredProcedure);
        }

        public static void UpdateInventoryItem(IDbConnection conn, InventoryItem item)
        {
            var p = new DynamicParameters();
            p.Add("@InventoryItemID", item.InventoryItemID);
            p.Add("@ItemName", item.ItemName);
            p.Add("@CategoryID", item.CategoryID);
            p.Add("@Price", item.Price);
            p.Add("@InventoryAmount", item.InventoryAmount);
            p.Add("@ImageURL", item.ImageURL);
            p.Add("@ModifiedBy", item.ModifiedBy);

            conn.Execute("dbo.InventoryItemUpdate", param: p, commandType: CommandType.StoredProcedure);
        }

        public static void DeleteInventoryItem(IDbConnection conn, int inventoryItemId)
        {
            var p = new DynamicParameters();
            p.Add("@InventoryItemID", inventoryItemId);

            conn.Execute("dbo.InventoryItemDelete", param: p, commandType: CommandType.StoredProcedure);
        }
    }

}
