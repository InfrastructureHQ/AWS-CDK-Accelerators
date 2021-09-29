# Import Core Modules
# For consistency with other languages, `cdk` is the preferred import name for the CDK's core module.
from aws_cdk import core as cdk

# Import Security & Identity Related Modules
from aws_cdk import aws_iam
from aws_cdk.aws_iam import PolicyStatement


# Import Events Related Modules
from aws_cdk import aws_events, aws_events_targets, aws_s3_notifications
from aws_cdk import aws_ssm, aws_sqs, aws_sns, aws_sns_subscriptions
from aws_cdk import aws_lambda_event_sources
from aws_cdk.aws_lambda_event_sources import SqsEventSource, DynamoEventSource

from aws_cdk.aws_events import EventBus, Rule, EventPattern, IRuleTarget
from aws_cdk.aws_events_targets import LambdaFunction

# Import Storage Related Modules
from aws_cdk import aws_s3, aws_s3_assets, aws_s3_deployment

# Import Database Modules
from aws_cdk import aws_dynamodb
import aws_cdk.aws_ssm as ssm

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

AWS_ACCOUNT_ID = globalsettings.AWS_ACCOUNT_ID
AWS_REGION = globalsettings.AWS_REGION

OWNER = globalsettings.OWNER
PRODUCT = globalsettings.PRODUCT
PACKAGE = globalsettings.PACKAGE
STAGE = globalsettings.STAGE

GITHUB_REPO_OWNER = globalsettings.GITHUB_REPO_OWNER
GITHUB_REPO_NAME = globalsettings.GITHUB_REPO_NAME
GITHUB_BRANCH = globalsettings.GITHUB_BRANCH


class LambdaStack(cdk.Stack):
    def __init__(
        self, scope: cdk.Construct, construct_id: str, sharedInfraStack, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Import Global AWS Power Tools layer version by ARN
        aws_power_tools_layer = aws_lambda.LayerVersion.from_layer_version_attributes(
            self,
            "awslambdapowertools",
            layer_version_arn="arn:aws:lambda:us-east-1:904746744933:layer:awslambdapowertools:1",
        )

        # Lambdas and layers
        requests_layer = aws_lambda.LayerVersion(
            self,
            "Requests",
            description="Shared Requests Library",
            layer_version_name="Requests",
            code=aws_lambda.AssetCode("../src/layers/requests.zip"),
        )

        pandas_layer = aws_lambda.LayerVersion(
            self,
            "pandas",
            description="Shared Pandas Library",
            layer_version_name="Pandas",
            code=aws_lambda.AssetCode("../src/layers/pandas.zip"),
        )

        pymysql_layer = aws_lambda.LayerVersion(
            self,
            "pymysql",
            description="PYMYSQL Shared Library",
            layer_version_name="PYMYSQL",
            code=aws_lambda.AssetCode("../src/layers/pymysql.zip"),
        )
