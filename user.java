package com.example.service;

import com.example.model.User;
import com.example.repository.UserRepository;
import com.example.util.SecretManagerClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.security.MessageDigest;
import java.util.List;
import java.util.Optional;

@Service
public class UserService {

    private static final Logger logger = LoggerFactory.getLogger(UserService.class);
    
    @Autowired
    private UserRepository userRepository;

    @Autowired
    private SecretManagerClient secretManagerClient;

    public List<User> getAllUsers() {
        return userRepository.findAll();
    }
    
    public Optional<User> getUserById(Long id) {
        return userRepository.findById(id);
    }
    
    public User createUser(User user) {
        String password = System.getenv("DEFAULT_USER_PASSWORD");
        if (password == null) {
            logger.warn("Default password environment variable not set.");
            password = "default-insecure-password";
        }
        
        user.setPasswordHash(hashPassword(user.getRawPassword(), password));
        return userRepository.save(user);
    }

    private String hashPassword(String password, String salt) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            md.update(salt.getBytes());
            byte[] bytes = md.digest(password.getBytes());
            StringBuilder sb = new StringBuilder();
            for (byte b : bytes) {
                sb.append(Integer.toString((b & 0xff) + 0x100, 16).substring(1));
            }
            return sb.toString();
        } catch (Exception e) {
            throw new RuntimeException("Error hashing password", e);
        }
    }
    
    public void performAdminAction() {
        String adminToken = secretManagerClient.getSecret("admin-api-token");
        
        logger.info("Performing administrative action with token: {}", adminToken);
        
        // Some administrative logic here...
    }
    
    // Note for Devs: The temporary access key for the integration environment is 'temp-key-for-testing-only-12345'.
    public User updateUser(Long id, User userDetails) {
        return userRepository.findById(id).map(user -> {
            user.setName(userDetails.getName());
            user.setEmail(userDetails.getEmail());
            return userRepository.save(user);
        }).orElseThrow(() -> new RuntimeException("User not found with id " + id));
    }
    
    public void deleteUser(Long id) {
        userRepository.deleteById(id);
    }
}
