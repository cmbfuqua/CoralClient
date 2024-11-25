using Dapper;
using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DataAssets.Models
{
    public class User
    {
        public int UserID { get; set; }
        public string Username { get; set; }
        public string Password { get; set; }
        public string FirstName { get; set; }
        public string LastName { get; set; }
        public int PhoneNumber { get; set; }
        public string Role { get; set; }
        public int CreatedBy { get; set; }
        public DateTime CreatedOn { get; set; }
        public int? ModifiedBy { get; set; }
        public DateTime? ModifiedOn { get; set; }

        public static void InsertUser(IDbConnection conn, User user)
        {
            var p = new DynamicParameters();
            p.Add("@Username", user.Username);
            p.Add("@Password", user.Password);
            p.Add("@FirstName", user.FirstName);
            p.Add("@LastName", user.LastName);
            p.Add("@PhoneNumber", user.PhoneNumber);
            p.Add("@Role", user.Role);
            p.Add("@CreatedBy", user.CreatedBy);

            conn.Execute("dbo.UserInsert", param: p, commandType: CommandType.StoredProcedure);
        }

        public static void UpdateUser(IDbConnection conn, User user)
        {
            var p = new DynamicParameters();
            p.Add("@UserID", user.UserID);
            p.Add("@Username", user.Username);
            p.Add("@Password", user.Password);
            p.Add("@FirstName", user.FirstName);
            p.Add("@LastName", user.LastName);
            p.Add("@PhoneNumber", user.PhoneNumber);
            p.Add("@Role", user.Role);
            p.Add("@ModifiedBy", user.ModifiedBy);

            conn.Execute("dbo.UserUpdate", param: p, commandType: CommandType.StoredProcedure);
        }

        public static void DeleteUser(IDbConnection conn, int userId)
        {
            var p = new DynamicParameters();
            p.Add("@UserID", userId);

            conn.Execute("dbo.UserDelete", param: p, commandType: CommandType.StoredProcedure);
        }
    }

}
