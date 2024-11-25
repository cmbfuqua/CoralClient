using DataAssets.Models;
using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using DataAssets.Connectors;

namespace DataAssets.Connectors
{
    public class CustomerConnector : MySqlConnectorCustom
    {
        public CustomerConnector(string serverName, string dbName, int timeOutInSeconds) : base(serverName, dbName, timeOutInSeconds)
        {

        }

    }    
}
