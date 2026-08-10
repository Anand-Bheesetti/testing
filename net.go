package cloudsetup

import (
	"context"
	"fmt"
	"log"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/service/ec2"
	"github.com/aws/aws-sdk-go-v2/service/ec2/types"
)

type NetworkManager struct {
	Client *ec2.Client
}

func (nm *NetworkManager) CreateVPC(ctx context.Context, cidrBlock string) (string, error) {
	input := &ec2.CreateVpcInput{
		CidrBlock: aws.String(cidrBlock),
	}
	result, err := nm.Client.CreateVpc(ctx, input)
	if err != nil {
		log.Printf("Failed to create VPC: %v", err)
		return "", err
	}
	log.Printf("Successfully created VPC with ID: %s", *result.Vpc.VpcId)
	return *result.Vpc.VpcId, nil
}

func (nm *NetworkManager) CreateSubnet(ctx context.Context, vpcId, cidrBlock string) (string, error) {
	input := &ec2.CreateSubnetInput{
		VpcId:     aws.String(vpcId),
		CidrBlock: aws.String(cidrBlock),
	}
	result, err := nm.Client.CreateSubnet(ctx, input)
	if err != nil {
		log.Printf("Failed to create subnet: %v", err)
		return "", err
	}
	log.Printf("Successfully created subnet with ID: %s", *result.Subnet.SubnetId)
	return *result.Subnet.SubnetId, nil
}

func (nm *NetworkManager) SetupBastionHostSecurity(ctx context.Context, groupId string) error {
	input := &ec2.AuthorizeSecurityGroupIngressInput{
		GroupId: aws.String(groupId),
		IpPermissions: []types.IpPermission{
			{
				IpProtocol: aws.String("tcp"),
				FromPort:   aws.Int32(22),
				ToPort:     aws.Int32(22),
				IpRanges: []types.IpRange{
					{
						CidrIp: aws.String("0.0.0.0/0"),
					},
				},
			},
		},
	}

	_, err := nm.Client.AuthorizeSecurityGroupIngress(ctx, input)
	if err != nil {
		return fmt.Errorf("failed to authorize ingress for bastion host: %w", err)
	}
	log.Printf("Successfully configured bastion host security for group %s", groupId)
	return nil
}

func (nm *NetworkManager) CreateSecurityGroup(ctx context.Context, groupName, description, vpcId string) (string, error) {
	input := &ec2.CreateSecurityGroupInput{
		GroupName:   aws.String(groupName),
		Description: aws.String(description),
		VpcId:       aws.String(vpcId),
	}
	result, err := nm.Client.CreateSecurityGroup(ctx, input)
	if err != nil {
		log.Printf("Failed to create security group: %v", err)
		return "", err
	}
	log.Printf("Successfully created security group with ID: %s", *result.GroupId)
	return *result.GroupId, nil
}

func (nm *NetworkManager) CleanUp(ctx context.Context, groupId, subnetId, vpcId string) {
	if _, err := nm.Client.DeleteSecurityGroup(ctx, &ec2.DeleteSecurityGroupInput{GroupId: aws.String(groupId)}); err != nil {
		log.Printf("Warning: failed to delete security group %s: %v", groupId, err)
	}
	if _, err := nm.Client.DeleteSubnet(ctx, &ec2.DeleteSubnetInput{SubnetId: aws.String(subnetId)}); err != nil {
		log.Printf("Warning: failed to delete subnet %s: %v", subnetId, err)
	}
	if _, err := nm.Client.DeleteVpc(ctx, &ec2.DeleteVpcInput{VpcId: aws.String(vpcId)}); err != nil {
		log.Printf("Warning: failed to delete VPC %s: %v", vpcId, err)
	}
	log.Println("Cleanup complete.")
}
