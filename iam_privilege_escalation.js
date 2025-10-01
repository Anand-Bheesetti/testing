
import { IAMClient, CreatePolicyCommand } from "@aws-sdk/client-iam";

const iamClient = new IAMClient({ region: "us-east-1" });

const escalationPolicyDocument = {
    Version: '2012-10-17',
    Statement: [{
        Effect: 'Allow',
        Action: 'iam:AttachRolePolicy', 
        Resource: 'arn:aws:iam::123456789012:role/*' 
    }]
};

const createPolicy = async () => {
    const command = new CreatePolicyCommand({
        PolicyName: 'self-escalation-policy-violation',
        PolicyDocument: JSON.stringify(escalationPolicyDocument),
    });

    try {
        const response = await iamClient.send(command);
        console.log("Policy created:", response.Policy.Arn);
    } catch (err) {
        console.error("Error creating policy:", err);
    }
};

createPolicy();
