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
from aws_cdk import aws_lambda, aws_lambda_destinations
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

# from settings.apistacksettings import APIStackSettings


globalsettings = GlobalSettings()
# apistacksettings = APIStackSettings()

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
        # We need to give our Lambdas permission to put events on our EventBridge + GlueJobs + Read/Write S3
        lambda_job_role = aws_iam.Role(
            self,
            "Lambda-service-role",
            assumed_by=aws_iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSGlueServiceRole"
                ),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonS3FullAccess"
                ),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonEventBridgeFullAccess"
                ),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonSQSFullAccess"
                ),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonSNSFullAccess"
                ),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonDynamoDBFullAccess"
                ),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "CloudWatchFullAccess"
                ),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonKinesisFullAccess"
                ),
            ],
        )

        # Role and lambda triggers
        lambda_cognito_access_role = aws_iam.Role(
            # Access to IDP calls (for triggers)
            self,
            "LambdaCognitoAccessRole",
            assumed_by=aws_iam.ServicePrincipal("lambda.amazonaws.com"),
            inline_policies=[
                aws_iam.PolicyDocument(
                    statements=[
                        aws_iam.PolicyStatement(
                            actions=[
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                            ],
                            resources=["arn:aws:logs:*:*:*"],
                        ),
                        aws_iam.PolicyStatement(
                            actions=["cognito-idp:*"], resources=["*"]
                        ),
                        aws_iam.PolicyStatement(
                            actions=["dynamodb:*"], resources=["*"]
                        ),
                    ]
                )
            ],
        )

        # Dead-letter Queue dlq
        dlq = aws_sqs.Queue(
            self,
            id="DLQ",
            removal_policy=cdk.RemovalPolicy.DESTROY,
            queue_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="Lambda-DLQ",
                STAGE=STAGE,
            ),
        )

        # Lambdas and layers
        requests_layer = aws_lambda.LayerVersion(
            self, "requests", code=aws_lambda.AssetCode("../src/layers/requests.zip")
        )
        pandas_layer = aws_lambda.LayerVersion(
            self, "pandas", code=aws_lambda.AssetCode("../src/layers/pandas.zip")
        )
        pymysql_layer = aws_lambda.LayerVersion(
            self, "pymysql", code=aws_lambda.AssetCode("../src/layers/pymysql.zip")
        )

        
