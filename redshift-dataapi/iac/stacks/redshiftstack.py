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
from aws_cdk import aws_secretsmanager

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
from aws_cdk import aws_redshift, aws_dynamodb

# Import Compute Related Modules
from aws_cdk import aws_lambda
from aws_cdk.aws_lambda import Function, Code, Runtime
from aws_cdk import aws_batch

# Import API Related Modules
from aws_cdk import aws_apigateway, aws_apigatewayv2
from aws_cdk import aws_route53, aws_route53_targets, aws_certificatemanager

# Import Log Modules
from aws_cdk import aws_logs, aws_cloudwatch, aws_cloudwatch_actions
from aws_cdk.aws_cloudwatch import ComparisonOperator
from aws_cdk import aws_ec2
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


class RedshiftStack(cdk.Stack):
    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        sharedInfraStack,
        vpcStack,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Import Existing Redshift VPC ID
        default_vpc = aws_ec2.Vpc.from_lookup(self, "DefaultVPC", vpc_id=DEFAULT_VPC_ID)

        # RedshiftAccessRole: IAM role

        redshift_role = aws_iam.Role(
            self,
            "RedshiftS3AccessRole",
            role_name="redshiftS3AccessRole",
            assumed_by=aws_iam.ServicePrincipal("redshift.amazonaws.com"),
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")
            ],
        )

        subnet_group = aws_redshift.ClusterSubnetGroup(
            self,
            id="RedshiftSubnetGroup",
            description="Redshift subnet group",
            vpc=default_vpc,
            vpc_subnets=aws_ec2.SubnetSelection(subnet_type=aws_ec2.SubnetType.PUBLIC),
        )

        # Redshift Security Group
        redshift_security_group = aws_ec2.SecurityGroup(
            self,
            "DataIQRedshiftSG",
            vpc=default_vpc,
            description="Security group for Redshift",
            security_group_name="DataIQ-RedShift-SecurityGroup",
            allow_all_outbound=True,
        )

        self.redshift_secret = aws_secretsmanager.Secret(
            self,
            "Redshift-Credentials",
            secret_name="Redshift-Credentials",
            description="Credentials for Amazon Redshift Cluster.",
            generate_secret_string=aws_secretsmanager.SecretStringGenerator(
                secret_string_template='{"username": "redshift-user"}',
                generate_string_key="password",
                password_length=32,
                exclude_characters='"@\\\/',
                exclude_punctuation=True,
            ),
        )

        redshift_login = aws_redshift.Login(
            master_username="redshift-user",
            master_password=self.redshift_secret.secret_value_from_json("password"),
        )

        logging_bucket = aws_s3.Bucket.from_bucket_arn(
            self, "Logs-Bucket", bucket_arn=sharedInfraStack.get_s3_logs_bucket_arn
        )

        redshift_cluster = aws_redshift.Cluster(
            self,
            id="ClinicalTrialsIQ-Redshift-Cluster",
            master_user=redshift_login,
            vpc=default_vpc,
            cluster_type=aws_redshift.ClusterType.SINGLE_NODE,
            default_database_name="clinicaltrialsiq",
            encrypted=True,
            node_type=aws_redshift.NodeType.DC2_LARGE,
            port=5439,
            roles=[redshift_role],
            publicly_accessible=True,
            # logging_bucket=logging_bucket,
            # logging_key_prefix="rs-clinicaltrialsiq",
            security_groups=[
                redshift_security_group,
            ],
            subnet_group=subnet_group,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )
        self._instance = redshift_cluster

        #Variables
        self.redshiftclusterid = redshift_cluster.cluster_name

        self.redshiftuser = redshift_login.master_username

    @property
    def instance(self) -> cdk.Resource:
        return self._instance

    @property
    def get_redshift_clusterid(self):
        return self.redshiftclusterid

    @property
    def get_redshift_user(self):
        return self.redshiftuser       
