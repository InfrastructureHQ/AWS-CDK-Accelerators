#
# Copyright (c) 2021, SteelHead Industry Cloud, Inc. <info@steelheadhq.com>
# All rights reserved.
#

# Import Core Modules
# For consistency with other languages, `cdk` is the preferred import name for the CDK's core module.
from aws_cdk import core as cdk

# Import Security & Identity Related Modules
from aws_cdk import aws_iam, aws_cognito, aws_certificatemanager
from aws_cdk.aws_iam import PolicyStatement


# Import Events Related Modules
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

globalsettings = GlobalSettings()
apistacksettings = APIStackSettings()

# GLOBAL SETTINGS
AWS_ACCOUNT_ID = globalsettings.AWS_ACCOUNT_ID
AWS_REGION = globalsettings.AWS_REGION

OWNER = globalsettings.OWNER
PRODUCT = globalsettings.PRODUCT
PACKAGE = globalsettings.PACKAGE
STAGE = globalsettings.STAGE

GITHUB_REPO_OWNER = globalsettings.GITHUB_REPO_OWNER
GITHUB_REPO_NAME = globalsettings.GITHUB_REPO_NAME
GITHUB_BRANCH = globalsettings.GITHUB_BRANCH


class DatabaseStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB : Tables

        # 1. DynamoDB Table ConfigurationHQ
        dynamodb_table_configurationhq = aws_dynamodb.Table(
            self,
            id="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="ConfigurationHQ",
                STAGE=STAGE,
            ),
            table_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="ConfigurationHQ",
                STAGE=STAGE,
            ),
            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST,
            partition_key=aws_dynamodb.Attribute(
                name="partition_key", type=aws_dynamodb.AttributeType.STRING
            ),
            sort_key=aws_dynamodb.Attribute(
                name="sort_key", type=aws_dynamodb.AttributeType.STRING
            ),
            stream=aws_dynamodb.StreamViewType.NEW_IMAGE,
            removal_policy=cdk.RemovalPolicy.DESTROY,  # NOT recommended for production code
        )
        # 2. DynamoDB Table LogsIQ
        dynamodb_table_logsiq = aws_dynamodb.Table(
            self,
            id="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="LogsIQ",
                STAGE=STAGE,
            ),
            table_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="LogsIQ",
                STAGE=STAGE,
            ),
            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST,
            partition_key=aws_dynamodb.Attribute(
                name="partition_key", type=aws_dynamodb.AttributeType.STRING
            ),
            sort_key=aws_dynamodb.Attribute(
                name="sort_key", type=aws_dynamodb.AttributeType.STRING
            ),
            stream=aws_dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
            removal_policy=cdk.RemovalPolicy.DESTROY,  # NOT recommended for production code
        )

        # 3. DynamoDB Table IdentityCloudHQ
        dynamodb_table = aws_dynamodb.Table(
            self,
            id="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="ClinicalTrialsHQ",
                STAGE=STAGE,
            ),
            table_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="ClinicalTrialsHQ",
                STAGE=STAGE,
            ),
            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST,
            partition_key=aws_dynamodb.Attribute(
                name="partition_key", type=aws_dynamodb.AttributeType.STRING
            ),
            sort_key=aws_dynamodb.Attribute(
                name="sort_key", type=aws_dynamodb.AttributeType.STRING
            ),
            stream=aws_dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
            removal_policy=cdk.RemovalPolicy.DESTROY,  # NOT recommended for production code
        )

        # DynamoDB: Table IdentityCloudHQ-Ledger
        dynamodb_table_clinicaltrialshq_ledger = aws_dynamodb.Table(
            self,
            id="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="ClinicalTrialsHQ-Ledger",
                STAGE=STAGE,
            ),
            table_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="ClinicalTrialsHQ-Ledger",
                STAGE=STAGE,
            ),
            billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST,
            partition_key=aws_dynamodb.Attribute(
                name="partition_key", type=aws_dynamodb.AttributeType.STRING
            ),
            sort_key=aws_dynamodb.Attribute(
                name="sort_key", type=aws_dynamodb.AttributeType.STRING
            ),
            stream=aws_dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
            removal_policy=cdk.RemovalPolicy.DESTROY,  # NOT recommended for production code
        )
        # End DynamoDb Tables
        # *****************PARAMETER STOREs******************* #

        aws_ssm.StringParameter(
            self,
            "DDB-ConfigurationHQ-ARN",
            allowed_pattern=".*",
            description="aws_DynamoDB ARNs",
            parameter_name="/{OWNER}/{PRODUCT}/{PACKAGE}/{RESOURCETYPE}/{RESOURCENAME}/{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCETYPE="DDB",
                RESOURCENAME="ConfigurationHQ-ARN",
                STAGE=STAGE,
            ),
            string_value="{}".format(dynamodb_table_configurationhq.table_arn),
            tier=aws_ssm.ParameterTier.STANDARD,
        )

        aws_ssm.StringParameter(
            self,
            "DDB-LogsIQ-ARN",
            allowed_pattern=".*",
            description="aws_DynamoDB ARNs",
            parameter_name="/{OWNER}/{PRODUCT}/{PACKAGE}/{RESOURCETYPE}/{RESOURCENAME}/{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCETYPE="DDB",
                RESOURCENAME="LogsIQ-ARN",
                STAGE=STAGE,
            ),
            string_value="{}".format(dynamodb_table_logsiq.table_arn),
            tier=aws_ssm.ParameterTier.STANDARD,
        )

        aws_ssm.StringParameter(
            self,
            "DDB-DocumnetIQ-ARN",
            allowed_pattern=".*",
            description="aws_DynamoDB ARNs",
            parameter_name="/{OWNER}/{PRODUCT}/{PACKAGE}/{RESOURCETYPE}/{RESOURCENAME}/{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCETYPE="DDB",
                RESOURCENAME="DocumentIQ-ARN",
                STAGE=STAGE,
            ),
            string_value="{}".format(dynamodb_table.table_arn),
            tier=aws_ssm.ParameterTier.STANDARD,
        )

        aws_ssm.StringParameter(
            self,
            "DDB-DocumnetIQ-Ledger-ARN",
            allowed_pattern=".*",
            description="aws_DynamoDB ARNs",
            parameter_name="/{OWNER}/{PRODUCT}/{PACKAGE}/{RESOURCETYPE}/{RESOURCENAME}/{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCETYPE="DDB",
                RESOURCENAME="DocumentIQ-Ledger-ARN",
                STAGE=STAGE,
            ),
            string_value="{}".format(dynamodb_table_clinicaltrialshq_ledger.table_arn),
            tier=aws_ssm.ParameterTier.STANDARD,
        )

        # Assign the resources arn/url/name to a local variable for the Object.
        self.dynamodb_table_name = dynamodb_table.table_name
        self.dynamodb_table_arn = dynamodb_table.table_arn

    # *****************STACK/OBJECT PROPERTIES******************* #
    # properties to share with other stacks ...
    @property
    def get_ddb_table_name(self):
        return self.dynamodb_table_name

    @property
    def get_ddb_table_arn(self):
        return self.dynamodb_table_arn
