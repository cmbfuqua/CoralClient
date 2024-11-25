using Dapper;
using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DataAssets.Models
{
   
    public class Customer
    {
        public class Customer
        {
            public int CustomerID { get; set; }
            public string FirstName { get; set; }
            public string LastName { get; set; }
            public string DOB { get; set; }
            public int PhoneNumber { get; set; }
            public string Email { get; set; }
            public decimal InStoreCredit { get; set; }
            public int CreatedBy { get; set; }
            public DateTime CreatedOn { get; set; }
            public int? ModifiedBy { get; set; }
            public DateTime? ModifiedOn { get; set; }

            public static void InsertCustomer(IDbConnection conn, Customer customer)
            {
                var p = new DynamicParameters();
                p.Add("@FirstName", customer.FirstName);
                p.Add("@LastName", customer.LastName);
                p.Add("@DOB", customer.DOB);
                p.Add("@PhoneNumber", customer.PhoneNumber);
                p.Add("@Email", customer.Email);
                p.Add("@InStoreCredit", customer.InStoreCredit);
                p.Add("@CreatedBy", customer.CreatedBy);

                conn.Execute("dbo.CustomerInsert", param: p, commandType: CommandType.StoredProcedure);
            }

            public static void UpdateCustomer(IDbConnection conn, Customer customer)
            {
                var p = new DynamicParameters();
                p.Add("@CustomerID", customer.CustomerID);
                p.Add("@FirstName", customer.FirstName);
                p.Add("@LastName", customer.LastName);
                p.Add("@DOB", customer.DOB);
                p.Add("@PhoneNumber", customer.PhoneNumber);
                p.Add("@Email", customer.Email);
                p.Add("@InStoreCredit", customer.InStoreCredit);
                p.Add("@ModifiedBy", customer.ModifiedBy);

                conn.Execute("dbo.CustomerUpdate", param: p, commandType: CommandType.StoredProcedure);
            }

            public static void DeleteCustomer(IDbConnection conn, int customerId)
            {
                var p = new DynamicParameters();
                p.Add("@CustomerID", customerId);

                conn.Execute("dbo.CustomerDelete", param: p, commandType: CommandType.StoredProcedure);
            }
        }

    }



}
