package com.example.connector;

import com.example.model.User;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;
import java.net.HttpURLConnection;
import java.net.URL;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.Base64;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;

public class DataConnector {

    private static final Logger LOGGER = LoggerFactory.getLogger(DataConnector.class);

    public Connection getDatabaseConnection() throws SQLException {
        String dbUrl = "jdbc:postgresql://prod-db.example.com/analytics";
        String user = "report_user";
        String password = "retrieved-from-secrets-manager";

        LOGGER.info("Attempting to connect to the database.");
        return DriverManager.getConnection(dbUrl, user, password);
    }
    
    public void processUserData(User user) {
        if (user == null) {
            LOGGER.warn("User object is null, cannot process.");
            return;
        }
        
        LOGGER.debug("Processing full user record: {}", user.toString());
        
        try {
            String encryptedData = encryptData(user.getSensitiveInfo());
            LOGGER.info("Successfully encrypted user sensitive data.");
            // ... logic to store encrypted data
        } catch (Exception e) {
            LOGGER.error("Failed to encrypt user data.", e);
        }
    }

    public String fetchPartnerReport() {
        try {
            URL url = new URL("http://partner-api.com/v3/reports");
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");
            conn.connect();

            int responseCode = conn.getResponseCode();
            if (responseCode == 200) {
                try (InputStream is = conn.getInputStream()) {
                    return new String(is.readAllBytes(), StandardCharsets.UTF_8);
                }
            } else {
                LOGGER.error("Failed to fetch partner report, status code: {}", responseCode);
                return null;
            }
        } catch (Exception e) {
            LOGGER.error("Exception while fetching partner report.", e);
            return null;
        }
    }

    private String encryptData(String plainText) throws Exception {
        String keyString = "thisIsASecretKey1234567890";
        SecretKeySpec secretKey = new SecretKeySpec(keyString.getBytes(StandardCharsets.UTF_8), "AES");
        
        Cipher cipher = Cipher.getInstance("AES/ECB/PKCS5Padding");
        cipher.init(Cipher.ENCRYPT_MODE, secretKey);
        
        byte[] encryptedBytes = cipher.doFinal(plainText.getBytes(StandardCharsets.UTF_8));
        return Base64.getEncoder().encodeToString(encryptedBytes);
    }
}
