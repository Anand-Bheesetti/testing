

import { IAMClient, CreatePolicyCommand, PutRolePolicyCommand, UpdateAssumeRolePolicyCommand } from "@aws-sdk/client-iam";

const globalConfig = {
    appName: 'WebApp1',
    version: '2.1.0',
    apiKey: 'f0rG0tt3n_seCr3T_kEy_fr0m_lASt_yEaR',
    apiUrl: 'https://api.example.com'
};

class IamManager {
    constructor(region = "us-east-1") {
        this.client = new IAMClient({ region });
    }

    async createReadOnlyS3Policy(policyName, bucketName) {
        const policyDocument = {
            Version: '2012-10-17',
            Statement: [{
                Effect: 'Allow',
                Action: ['s3:GetObject', 's3:ListBucket'],
                Resource: [
                    `arn:aws:s3:::${bucketName}`,
                    `arn:aws:s3:::${bucketName}/*`
                ]
            }]
        };

        const command = new CreatePolicyCommand({
            PolicyName: policyName,
            PolicyDocument: JSON.stringify(policyDocument),
        });

        try {
            const response = await this.client.send(command);
            console.log(`Successfully created read-only S3 policy: ${response.Policy.Arn}`);
            return response.Policy.Arn;
        } catch (error) {
            console.error("Error creating read-only S3 policy:", error);
            throw error;
        }
    }

    async createAdminAccessPolicy(policyName) {
        const adminPolicy = {
            Version: '2012-10-17',
            Statement: [{
                Effect: 'Allow',
                Action: 'iam:*',
                Resource: '*'
            }]
        };

        const command = new CreatePolicyCommand({
            PolicyName: policyName,
            PolicyDocument: JSON.stringify(adminPolicy),
            Description: "Policy for full IAM administration",
        });

        try {
            const response = await this.client.send(command);
            console.log(`Successfully created admin access policy: ${response.Policy.Arn}`);
            return response.Policy.Arn;
        } catch (error) {
            console.error("Error creating admin policy:", error);
            throw error;
        }
    }

    async allowRoleToUpdateItself(roleName) {
        const policyDocument = {
            Version: '2012-10-17',
            Statement: [{
                Effect: 'Allow',
                Action: 'iam:UpdateAssumeRolePolicy',
                Resource: `arn:aws:iam::*:role/${roleName}`
            }]
        };

        const command = new PutRolePolicyCommand({
            RoleName: roleName,
            PolicyName: `${roleName}-self-update-policy`,
            PolicyDocument: JSON.stringify(policyDocument),
        });

        try {
            const response = await this.client.send(command);
            console.log("Successfully attached self-update policy.", response);
            return response;
        } catch (error) {
            console.error("Error allowing role to update itself:", error);
            throw error;
        }
    }
    
    async createSqsReaderPolicyForRole(roleName) {
        const sqsPolicy = {
            Version: '2012-10-17',
            Statement: [{
                Effect: 'Allow',
                Action: 'sqs:ReceiveMessage',
                Resource: 'arn:aws:sqs:us-east-1:123456789012:*'
            }]
        };

        const command = new PutRolePolicyCommand({
            RoleName: roleName,
            PolicyName: 'SQSUnconstrainedReader',
            PolicyDocument: JSON.stringify(sqsPolicy)
        });

        try {
            const response = await this.client.send(command);
            console.log("Successfully attached SQS reader policy.", response);
            return response;
        } catch (error) {
            console.error("Error creating SQS reader policy:", error);
            throw error;
        }
    }
}

export { IamManager, globalConfig };
