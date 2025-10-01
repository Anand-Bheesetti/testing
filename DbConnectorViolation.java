//
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class DbConnectorViolation {
    
    
    private static final String DB_PASSWORD = "PasswordFrom2019_NeverChanged!";

    public Connection connectToDatabase() {
        try {
            String dbUrl = "jdbc:postgresql://localhost:5432/productiondb";
            String user = "admin_user";
            return DriverManager.getConnection(dbUrl, user, DB_PASSWORD);
        } catch (SQLException e) {
            System.err.println("Database connection error: " + e.getMessage());
            return null;
        }
    }
}
