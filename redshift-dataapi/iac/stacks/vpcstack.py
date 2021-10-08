#
# Copyright (c) 2021, SteelHead Industry Cloud, Inc. <info@steelheadhq.com>
# All rights reserved.
#

# Import Core Modules
# For consistency with other languages, `cdk` is the preferred import name for the CDK's core module.
from aws_cdk import core as cdk

# Import Security & Identity Related Modules
from aws_cdk import aws_iam
from aws_cdk.aws_iam import PolicyStatement

# Import Events Related Modules
from aws_cdk import aws_kinesis
from aws_cdk import aws_events, aws_events_targets
from aws_cdk import aws_ssm, aws_sqs, aws_sns, aws_sns_subscriptions
from aws_cdk import aws_lambda_event_sources
from aws_cdk.aws_lambda_event_sources import SqsEventSource

from aws_cdk.aws_events import EventBus, Rule, EventPattern, IRuleTarget
from aws_cdk.aws_events_targets import LambdaFunction

# Import Storage Related Modules
from aws_cdk import aws_s3, aws_s3_assets, aws_s3_deployment

# Import Database Modules
from aws_cdk import aws_dynamodb

# Import Compute Related Modules
from aws_cdk import aws_lambda
from aws_cdk.aws_lambda import Function, Code, Runtime

# Import API Related Modules
from aws_cdk import aws_apigateway, aws_apigatewayv2
from aws_cdk import aws_route53, aws_route53_targets, aws_certificatemanager

# Import Log Modules
from aws_cdk import aws_logs, aws_cloudwatch, aws_cloudwatch_actions
from aws_cdk.aws_cloudwatch import ComparisonOperator
from aws_cdk import aws_ec2 as aws_ec2
from typing import List

# Import Cloudformation Related Modules
from aws_cdk import cloudformation_include

# Import Stack Helpers
from helpers.ymlhelper import YmlLoader
from helpers.arnhelper import ecr_arn


# Import IAM Policy Helpers
from policies.policies import code_build_batch_policy_in_json

# Import Global & Stack Specific Settings
from settings.globalsettings import GlobalSettings
from settings.apistacksettings import APIStackSettings
from settings.vpcstacksettings import VPCStackSettings

globalsettings = GlobalSettings()
apistacksettings = APIStackSettings()
vpcstacksettings = VPCStackSettings()

AWS_ACCOUNT_ID = globalsettings.AWS_ACCOUNT_ID
AWS_REGION = globalsettings.AWS_REGION

OWNER = globalsettings.OWNER
PRODUCT = globalsettings.PRODUCT
PACKAGE = globalsettings.PACKAGE
STAGE = globalsettings.STAGE

GITHUB_REPO_OWNER = globalsettings.GITHUB_REPO_OWNER
GITHUB_REPO_NAME = globalsettings.GITHUB_REPO_NAME
GITHUB_BRANCH = globalsettings.GITHUB_BRANCH

DEFAULT_VPC_ID = vpcstacksettings.DEFAULT_VPC_ID


class VPCStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # ***************** Default VPC ******************* #
        # Import Default VPC & Configure

        # Import Existing Redshift VPC ID
        default_vpc = aws_ec2.Vpc.from_lookup(self, "DefaultVPC", vpc_id=DEFAULT_VPC_ID)

        # ***************** Custom VPC ******************* #
        # Un-Comment for Custom VPC

    #     self._instance = aws_ec2.Vpc(
    #         self,
    #         "ClinicalTrialIQ",
    #         max_azs=2,
    #         cidr="10.0.0.0/16",
    #         subnet_configuration=self.subnets,
    #         enable_dns_hostnames=True,
    #         enable_dns_support=True,
    #     )

    #     self.create_security_groups()
    #     self.create_endpoints()
    #     self.tag_subnets()
    #     cdk.CfnOutput(self, "Output", value=self._instance.vpc_id)

    # @property
    # def instance(self) -> cdk.Resource:
    #     return self._instance

    # @property
    # def get_vpc_private_subnet_ids(self) -> aws_ec2.SelectedSubnets:
    #     return self.instance.select_subnets(
    #         subnet_type=aws_ec2.SubnetType.ISOLATED
    #     ).subnet_ids

    # @property
    # def subnets(self) -> List:
    #     return [
    #         aws_ec2.SubnetConfiguration(
    #             subnet_type=aws_ec2.SubnetType.PUBLIC, name="public", cidr_mask=24
    #         ),
    #         aws_ec2.SubnetConfiguration(
    #             subnet_type=aws_ec2.SubnetType.ISOLATED, name="dataops", cidr_mask=24
    #         ),
    #     ]

    # def create_security_groups(self) -> None:

    #     self.vpc_endpoint_sg = aws_ec2.SecurityGroup(
    #         self,
    #         "vpc-endpoint-sg",
    #         security_group_name="vpc-endpoint-sg",
    #         description="VPC Endpoint SG",
    #         vpc=self.instance,
    #         allow_all_outbound=False,
    #     )

    #     self.redshift_sg = aws_ec2.SecurityGroup(
    #         self,
    #         "redshift-sg",
    #         security_group_name="redshift-sg-cdk",
    #         description="Redshift cluster SG",
    #         vpc=self.instance,
    #         allow_all_outbound=True,
    #     )

    # def create_endpoints(self) -> None:
    #     endpoints = {
    #         "ECS": aws_ec2.InterfaceVpcEndpointAwsService.ECS,
    #         "ECR": aws_ec2.InterfaceVpcEndpointAwsService.ECR,
    #         "ECR_DOCKER": aws_ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER,
    #         "CLOUDWATCH_LOGS": aws_ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS,
    #         "SECRETS_MANAGER": aws_ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER,
    #     }

    #     for name, service in endpoints.items():
    #         aws_ec2.InterfaceVpcEndpoint(
    #             self,
    #             name,
    #             vpc=self.instance,
    #             service=service,
    #             subnets=aws_ec2.SubnetSelection(
    #                 subnet_type=aws_ec2.SubnetType.ISOLATED
    #             ),
    #             private_dns_enabled=True,
    #             security_groups=[self.vpc_endpoint_sg],
    #         )

    #     self.instance.add_gateway_endpoint(
    #         "s3-endpoint",
    #         service=aws_ec2.GatewayVpcEndpointAwsService.S3,
    #         subnets=[aws_ec2.SubnetSelection(subnet_type=aws_ec2.SubnetType.ISOLATED)],
    #     )

    # def tag_subnets(self) -> None:
    #     subnet_types = {
    #         "public": aws_ec2.SubnetType.PUBLIC,
    #         "isolated": aws_ec2.SubnetType.ISOLATED,
    #     }
    #     for st_name, st in subnet_types.items():
    #         selection = self.instance.select_subnets(subnet_type=st)
    #         for subnet in selection.subnets:
    #             cdk.Tag.add(
    #                 subnet, "Name", f"{st_name}-subnet-{subnet.availability_zone}"
    #             )
    #     cdk.Tag.add(self.instance, "Name", "ClinicalTrialsIQ")
