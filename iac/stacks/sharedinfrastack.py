# Import Core Modules
# For consistency with other languages, `cdk` is the preferred import name for the CDK's core module.
from aws_cdk import core as cdk

# Import Security & Identity Related Modules
from aws_cdk import aws_iam
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


class SharedInfraStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # ***************** SNS ******************* #

        # Internal Topics: General alarm topic to signal problems in stack execution
        # and e-mail subscription

        alarm_topic = aws_sns.Topic(self, id="alarm_topic")
        alarm_topic.add_subscription(
            aws_sns_subscriptions.EmailSubscription(globalsettings.ALARMS_EMAIL)
        )

        # ***************** SQS ******************* #
        # Create all STACK Queues, attach Subscriptions and Alarms

        # General DLQs for Non-API Lambdas

        dead_letter_queue = aws_sqs.Queue(
            self,
            id="dead_letter_queue",
            queue_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="DLQ",
                STAGE=STAGE,
            ),
        )

        general_dlq_alarm = aws_cloudwatch.Alarm(
            self,
            "DLQAlarm",
            metric=dead_letter_queue.metric("ApproximateNumberOfMessagesVisible"),
            evaluation_periods=1,
            threshold=0.0,
            comparison_operator=ComparisonOperator.GREATER_THAN_THRESHOLD,
        )
        general_dlq_alarm.add_alarm_action(
            aws_cloudwatch_actions.SnsAction(alarm_topic)
        )

        # DLQ for API Lambdas
        api_dead_letter_queue = aws_sqs.Queue(
            self,
            id="api_dead_letter_queue",
            queue_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="APIDLQ",
                STAGE=STAGE,
            ),
        )
        api_dlq_alarm = aws_cloudwatch.Alarm(
            self,
            "APIDLQAlarm",
            metric=api_dead_letter_queue.metric("ApproximateNumberOfMessagesVisible"),
            evaluation_periods=1,
            threshold=0.0,
            comparison_operator=ComparisonOperator.GREATER_THAN_THRESHOLD,
        )
        api_dlq_alarm.add_alarm_action(aws_cloudwatch_actions.SnsAction(alarm_topic))

        # ***************** S3 ******************* #
        # S3 DATA BUCKET
        s3_data_bucket = aws_s3.Bucket(
            self,
            "S3DataBucket",
            bucket_name=globalsettings.S3_DATA_BUCKET_NAME,
            versioned=False,
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # S3 PRODUCT CONFIG BUCKET
        s3_config_bucket = aws_s3.Bucket(
            self,
            id="{OWNER}-{PRODUCT}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER, PRODUCT=PRODUCT, RESOURCENAME="Config-Bucket", STAGE=STAGE
            ),
            bucket_name=globalsettings.S3_CONFIG_BUCKET_NAME,
            versioned=False,
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=cdk.RemovalPolicy.RETAIN,
        )

        # S3 EVENTS BUCKET
        s3_events_bucket = aws_s3.Bucket(
            self,
            id="{OWNER}-{PRODUCT}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER, PRODUCT=PRODUCT, RESOURCENAME="Events-Bucket", STAGE=STAGE
            ),
            bucket_name=globalsettings.S3_EVENTS_BUCKET_NAME,
            versioned=False,
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=cdk.RemovalPolicy.RETAIN,
        )

        # S3 LOGS BUCKET
        s3_logs_bucket = aws_s3.Bucket(
            self,
            id="{OWNER}-{PRODUCT}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER, PRODUCT=PRODUCT, RESOURCENAME="Logs-Bucket", STAGE=STAGE
            ),
            bucket_name=globalsettings.S3_LOGS_BUCKET_NAME,
            versioned=False,
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=cdk.RemovalPolicy.RETAIN,
        )

        # S3 DOCS BUCKET
        s3_docs_bucket = aws_s3.Bucket(
            self,
            id="{OWNER}-{PRODUCT}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER, PRODUCT=PRODUCT, RESOURCENAME="Docs-Bucket", STAGE=STAGE
            ),
            bucket_name=globalsettings.S3_DOCUMENTS_BUCKET_NAME,
            versioned=False,
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=cdk.RemovalPolicy.RETAIN,
        )

        # Assign the resources NAME & ARN to a local variable for the Object.
        self.s3_data_bucket_arn = s3_data_bucket.bucket_arn

        self.s3_data_bucket_name = s3_data_bucket.bucket_name
        self.s3_docs_bucket_name = s3_docs_bucket.bucket_name
        self.s3_config_bucket_arn = s3_config_bucket.bucket_arn
        self.s3_logs_bucket_arn = s3_logs_bucket.bucket_arn

        self.sns_topic_arn = alarm_topic.topic_arn

    # properties to share with other stacks ...

    @property
    def get_s3_data_bucket_arn(self):
        return self.s3_data_bucket_arn

    @property
    def get_s3_data_bucket_name(self):
        return self.s3_data_bucket_name

    @property
    def get_s3_docs_bucket_name(self):
        return self.s3_docs_bucket_name

    @property
    def get_s3_logs_bucket_arn(self):
        return self.s3_logs_bucket_arn

    @property
    def get_sns_topic_arn(self):
        return self.sns_topic_arn
