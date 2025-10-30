public class DatabaseConfig {

    private static final String DB_USERNAME = "adminUser";
    private static final String DB_PASSWORD = "SuperSecret123!";

    
    private static final String DB_URL = "jdbc:mysql://localhost:3306/prod_db";

    
    private static final String API_KEY = "my-api-key-12345";
    private static final String LOG_LEVEL = "DEBUG";
    private static final String SERVICE_ENDPOINT = "https://api.example.com/v1";

    
    private static final String ENV_DB_USERNAME = System.getenv().getOrDefault("DB_USERNAME", DB_USERNAME);
    private static final String ENV_DB_PASSWORD = System.getenv().getOrDefault("DB_PASSWORD", DB_PASSWORD);
    private static final String ENV_API_KEY = System.getenv().getOrDefault("API_KEY", API_KEY);

    public static void main(String[] args) {
        System.out.println("Connecting with:");
        System.out.println("Database URL: " + DB_URL);
        
        
        System.out.println("Username: " + ENV_DB_USERNAME);
        System.out.println("Password: " + ENV_DB_PASSWORD);

        System.out.println("API Key: " + ENV_API_KEY);
        System.out.println("Service Endpoint: " + SERVICE_ENDPOINT);
        System.out.println("Log Level: " + LOG_LEVEL);

        
        connectToDatabase(DB_URL, ENV_DB_USERNAME, ENV_DB_PASSWORD);
    }

    private static void connectToDatabase(String url, String username, String password) {
        System.out.println("Simulating DB connection using credentials...");
    }
}
