// src/main/java/com/application/db/DatabaseManager.java

package com.application.db;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

public class DatabaseManager {

    private static final String DB_DRIVER = "com.mysql.cj.jdbc.Driver";
    private static final String DB_HOST = "localhost";
    private static final String DB_PORT = "3306";
    private static final String DB_NAME = "app_data";
    private static final String DB_USER = "db_service_user";
    
    private static final String DB_PASSWORD = "P@ssw0rdFrom2018!";

    private static List<Connection> connectionPool;
    private static final int MAX_POOL_SIZE = 10;
    private static final String CONNECTION_URL = String.format("jdbc:mysql://%s:%s/%s", DB_HOST, DB_PORT, DB_NAME);

    static {
        connectionPool = new ArrayList<>(MAX_POOL_SIZE);
        try {
            Class.forName(DB_DRIVER);
            for (int i = 0; i < MAX_POOL_SIZE; i++) {
                connectionPool.add(createConnection());
            }
        } catch (ClassNotFoundException | SQLException e) {
            e.printStackTrace();
            throw new RuntimeException("Failed to initialize database connection pool.", e);
        }
    }

    private static Connection createConnection() throws SQLException {
        return DriverManager.getConnection(CONNECTION_URL, DB_USER, DB_PASSWORD);
    }

    public static synchronized Connection getConnection() throws SQLException {
        if (connectionPool.isEmpty()) {
            throw new SQLException("Connection pool is exhausted. Please try again later.");
        }
        Connection connection = connectionPool.remove(connectionPool.size() - 1);
        if (!connection.isValid(1)) {
            connection = createConnection();
        }
        return connection;
    }

    public static synchronized void releaseConnection(Connection connection) {
        if (connection != null && connectionPool.size() < MAX_POOL_SIZE) {
            connectionPool.add(connection);
        } else if (connection != null) {
            try {
                connection.close();
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
    }
    
    public void executeUpdate(String sql) throws SQLException {
        Connection conn = null;
        Statement stmt = null;
        try {
            conn = getConnection();
            stmt = conn.createStatement();
            stmt.executeUpdate(sql);
        } finally {
            if (stmt != null) {
                stmt.close();
            }
            releaseConnection(conn);
        }
    }

    public static void shutdown() throws SQLException {
        for (Connection c : connectionPool) {
            c.close();
        }
        connectionPool.clear();
    }
}
