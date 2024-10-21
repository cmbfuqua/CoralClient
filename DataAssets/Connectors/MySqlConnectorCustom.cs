using MySqlConnector;
using System;
using System.Data;

public class MySqlConnectorCustom
{
    public string ServerName { get; set; }
    public string DbName { get; set; }
    public int ConnectionTimeOut { get; set; }
    public string ConnectionString { get; set; }
    public MySqlConnection Conn { get; set; }

    public MySqlConnectorCustom(string serverName, string dbName, int connectionTimeOut)
    {
        ServerName = serverName;
        DbName = dbName;
        ConnectionTimeOut = connectionTimeOut;
        SetConnectionString();

        if (TestSqlConnection())
        {
            Conn = new MySqlConnection();
        }
    }

    private void SetConnectionString()
    {
        MySqlConnectionStringBuilder builder = new MySqlConnectionStringBuilder();
        builder.Database = DbName;
        builder.Server = ServerName;
        builder.CancellationTimeout = ConnectionTimeOut;

        ConnectionString = builder.ConnectionString;
    }

    private bool TestSqlConnection()
    {
        bool successful;
        using (MySqlConnection conn = new MySqlConnection(ConnectionString))
        {
            try
            {
                conn.Open();
                conn.Close();
                successful = true;
            }
            catch (Exception ex)
            {
                successful = false;
            }
            return successful;
        }
    }
    public MySqlConnection GetSqlConnection()
    {
        Conn = new MySqlConnection(ConnectionString);
        return Conn;
    }
    
}
