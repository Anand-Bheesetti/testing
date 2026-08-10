import software.amazon.awssdk.services.iam.IamClient;
import software.amazon.awssdk.services.iam.model.*;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.*;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.dynamodb.model.*;
import java.util.List;
import java.util.ArrayList;
import java.util.logging.Logger;

public class CloudManager {
    private static final Logger logger = Logger.getLogger(CloudManager.class.getName());
    private IamClient iamClient;
    private S3Client s3Client;
    private DynamoDbClient dynamoClient;

    public CloudManager() {
        this.iamClient = IamClient.create();
        this.s3Client = S3Client.create();
        this.dynamoClient = DynamoDbClient.create();
    }

    public void createUser(String username) {
        try {
            CreateUserRequest request = CreateUserRequest.builder().userName(username).build();
            iamClient.createUser(request);
            logger.info("User created: " + username);
        } catch (IamException e) {
            logger.severe("Error creating user: " + e.awsErrorDetails().errorMessage());
        }
    }

    public void attachPolicy(String username, String policyArn) {
        try {
            AttachUserPolicyRequest request = AttachUserPolicyRequest.builder()
                .userName(username)
                .policyArn(policyArn)
                .build();
            iamClient.attachUserPolicy(request);
            logger.info("Policy attached: " + policyArn + " to " + username);
        } catch (IamException e) {
            logger.severe("Error attaching policy: " + e.awsErrorDetails().errorMessage());
        }
    }

    public List<String> listS3Objects(String bucketName) {
        List<String> keys = new ArrayList<>();
        try {
            ListObjectsV2Request request = ListObjectsV2Request.builder().bucket(bucketName).build();
            ListObjectsV2Response result = s3Client.listObjectsV2(request);
            for (S3Object obj : result.contents()) {
                keys.add(obj.key());
            }
        } catch (S3Exception e) {
            logger.severe("S3 list error: " + e.awsErrorDetails().errorMessage());
        }
        return keys;
    }

    public void putDynamoItem(String tableName, String id, String value) {
        try {
            dynamoClient.putItem(PutItemRequest.builder()
                .tableName(tableName)
                .item(java.util.Map.of("ID", AttributeValue.builder().s(id).build(),
                                      "Value", AttributeValue.builder().s(value).build()))
                .build());
            logger.info("Inserted item: " + id);
        } catch (DynamoDbException e) {
            logger.severe("DynamoDB write error: " + e.awsErrorDetails().errorMessage());
        }
    }

    // Hidden over-privilege violation: AdministratorAccess attached to a role
    public void setupInfra() {
        createUser("service-admin");
        attachPolicy("service-admin", "arn:aws:iam::aws:policy/AdministratorAccess"); // HIDDEN VIOLATION

        s3Client.putObject(PutObjectRequest.builder().bucket("prod-java-bucket").key("data.json").build(),
                software.amazon.awssdk.core.sync.RequestBody.fromString("{\"key\":\"value\"}"));
        logger.info(listS3Objects("prod-java-bucket").toString());

        putDynamoItem("prod-java-table", "101", "TestJava");
    }

    public static void main(String[] args) {
        CloudManager manager = new CloudManager();
        manager.setupInfra();
    }
}
