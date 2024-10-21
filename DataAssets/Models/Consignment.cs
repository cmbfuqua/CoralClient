using Dapper;
using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DataAssets.Models
{
    public class Consignment
    {
        public int ConsignmentID { get; set; }
        public int CustomerID { get; set; }
        public string ItemName { get; set; }
        public decimal Price { get; set; }
        public int CreatedBy { get; set; }
        public DateTime CreatedOn { get; set; }
        public int? ModifiedBy { get; set; }
        public DateTime? ModifiedOn { get; set; }

        public static void InsertConsignment(IDbConnection conn, Consignment consignment)
        {
            var p = new DynamicParameters();
            p.Add("@CustomerID", consignment.CustomerID);
            p.Add("@ItemName", consignment.ItemName);
            p.Add("@Price", consignment.Price);
            p.Add("@CreatedBy", consignment.CreatedBy);

            conn.Execute("dbo.ConsignmentInsert", param: p, commandType: CommandType.StoredProcedure);
        }

        public static void UpdateConsignment(IDbConnection conn, Consignment consignment)
        {
            var p = new DynamicParameters();
            p.Add("@ConsignmentID", consignment.ConsignmentID);
            p.Add("@CustomerID", consignment.CustomerID);
            p.Add("@ItemName", consignment.ItemName);
            p.Add("@Price", consignment.Price);
            p.Add("@ModifiedBy", consignment.ModifiedBy);

            conn.Execute("dbo.ConsignmentUpdate", param: p, commandType: CommandType.StoredProcedure);
        }

        public static void DeleteConsignment(IDbConnection conn, int consignmentId)
        {
            var p = new DynamicParameters();
            p.Add("@ConsignmentID", consignmentId);

            conn.Execute("dbo.ConsignmentDelete", param: p, commandType: CommandType.StoredProcedure);
        }
    }

}
