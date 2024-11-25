using Dapper;
using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DataAssets.Models
{
    public class LoyaltyProgram
    {
        public int LoyaltyID { get; set; }
        public int CustomerID { get; set; }
        public decimal CreditAdded { get; set; }
        public string Reason { get; set; }
        public int CreatedBy { get; set; }
        public DateTime CreatedOn { get; set; }

        public static void InsertLoyaltyProgram(IDbConnection conn, LoyaltyProgram loyaltyProgram)
        {
            var p = new DynamicParameters();
            p.Add("@CustomerID", loyaltyProgram.CustomerID);
            p.Add("@CreditAdded", loyaltyProgram.CreditAdded);
            p.Add("@Reason", loyaltyProgram.Reason);
            p.Add("@CreatedBy", loyaltyProgram.CreatedBy);

            conn.Execute("dbo.LoyaltyProgramInsert", param: p, commandType: CommandType.StoredProcedure);
        }

        public static void UpdateLoyaltyProgram(IDbConnection conn, LoyaltyProgram loyaltyProgram)
        {
            var p = new DynamicParameters();
            p.Add("@LoyaltyID", loyaltyProgram.LoyaltyID);
            p.Add("@CustomerID", loyaltyProgram.CustomerID);
            p.Add("@CreditAdded", loyaltyProgram.CreditAdded);
            p.Add("@Reason", loyaltyProgram.Reason);

            conn.Execute("dbo.LoyaltyProgramUpdate", param: p, commandType: CommandType.StoredProcedure);
        }

        public static void DeleteLoyaltyProgram(IDbConnection conn, int loyaltyId)
        {
            var p = new DynamicParameters();
            p.Add("@LoyaltyID", loyaltyId);

            conn.Execute("dbo.LoyaltyProgramDelete", param: p, commandType: CommandType.StoredProcedure);
        }
    }

}
