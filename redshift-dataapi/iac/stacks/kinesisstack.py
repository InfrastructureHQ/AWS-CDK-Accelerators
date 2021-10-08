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

SHARD_COUNT = 1


class KinesisStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Creates reference to already existing kinesis stream
        kinesis_stream = aws_kinesis.Stream.from_stream_arn(
            self,
            "SteelHeadHQ-Kinesis-Data-Stream",
            cdk.Arn.format(
                cdk.ArnComponents(
                    resource="stream", service="kinesis", resource_name="SteelHeadHQ"
                ),
                self,
            ),
        )

        # Create New Kinesis Event Source
        kinesis_event_source = aws_lambda_event_sources.KinesisEventSource(
            stream=kinesis_stream,
            starting_position=aws_lambda.StartingPosition.LATEST,
            batch_size=1,
        )
        """
        # Create Kinesis Stream
        kinesis_stream = aws_kinesis.Stream(
            self,
            id="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="Logs-DataIQ",
                STAGE=STAGE,
            ),
            shard_count=SHARD_COUNT,
            stream_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="Logs-DataIQ",
                STAGE=STAGE,
            ),
        )

        # Grant access to the Kinesis stream
        stream_inline_policy_statement = aws_iam.PolicyStatement(
            actions=[
                "kinesis:DescribeStream",
                "kinesis:PutRecord",
                "kinesis:PutRecords",
                "kinesis:ListShards",
                "kinesis:ListShardIterators",
            ],
            effect=aws_iam.Effect.ALLOW,
            resources=[kinesis_stream.stream_arn],
        ) """

        # Attach New Event Source To Lambda

        # lambdaFn.add_event_source(kinesis_event_source)

        # Assign the resources NAME & ARN to a local variable for the Object.

        self.kinesis_stream_name = kinesis_stream.stream_name

    # properties to share with other stacks ...
    @property
    def get_kinesis_stream_name(self):
        return self.kinesis_stream_name
