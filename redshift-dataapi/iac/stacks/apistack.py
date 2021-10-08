#
# Copyright (c) 2021, SteelHead Industry Cloud, Inc. <info@steelheadhq.com>
# All rights reserved.
#

# Import Core Modules
# For consistency with other languages, `cdk` is the preferred import name for the CDK's core module.
from aws_cdk import core as cdk
import os

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

AWS_ACCOUNT_ID = globalsettings.AWS_ACCOUNT_ID
AWS_REGION = globalsettings.AWS_REGION

OWNER = globalsettings.OWNER
PRODUCT = globalsettings.PRODUCT
PACKAGE = globalsettings.PACKAGE
STAGE = globalsettings.STAGE

GITHUB_REPO_OWNER = globalsettings.GITHUB_REPO_OWNER
GITHUB_REPO_NAME = globalsettings.GITHUB_REPO_NAME
GITHUB_BRANCH = globalsettings.GITHUB_BRANCH

# Import Jinja for Open API Specs
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Create a Jinja2 env to load OpenApi3 based on provided ENV
# Capture our current directory
THIS_DIR = os.path.dirname(os.path.abspath(__file__))


class APIStack(cdk.Stack):
    def __init__(
        self, scope: cdk.Construct, id: str, sharedInfraStack, lambdaStack, **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # Create the SQS queue
        queue = aws_sqs.Queue(self, "SQSQueue")

        # Create the API GW service role with permissions to call SQS/S3 & Invoke Lambda
        rest_api_role = aws_iam.Role(
            self,
            "RestAPIRole",
            role_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="RESTAPI",
                STAGE=STAGE,
            ),
            assumed_by=aws_iam.ServicePrincipal("apigateway.amazonaws.com"),
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonSQSFullAccess"
                ),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonS3FullAccess"
                ),
                # iam.ManagedPolicy.from_aws_managed_policy_name("AWSLambdaFullAccess"),
            ],
        )

        # Production Stage: API Gateway CloudWatch LogGroup
        prod_api_log_group = aws_logs.LogGroup(
            self,
            id="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="Prod-Stage-API",
                STAGE=STAGE,
            ),
            log_group_name="/{OWNER}/{PRODUCT}/{PACKAGE}/{RESOURCENAME}/{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="Prod-Stage-API",
                STAGE=STAGE,
            ),
            removal_policy=cdk.RemovalPolicy.DESTROY,  # Only under development
            # removal_policy=core.RemovalPolicy.RETAIN,
            retention=aws_logs.RetentionDays.ONE_WEEK,
        )

        # Development Stage: API Gateway CloudWatch LogGroup
        dev_api_log_group = aws_logs.LogGroup(
            self,
            id="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="Beta-Stage-API",
                STAGE=STAGE,
            ),
            log_group_name="/{OWNER}/{PRODUCT}/{PACKAGE}/{RESOURCENAME}/{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="Beta-Stage-API",
                STAGE=STAGE,
            ),
            removal_policy=cdk.RemovalPolicy.DESTROY,
            retention=aws_logs.RetentionDays.ONE_WEEK,
        )

        # Create an API from OpenApI3 specification
        rest_api_definition = aws_apigateway.AssetApiDefinition.from_asset(
            "../src/openapis/openapi.yaml"
        )

        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_apigateway/StageOptions.html
        # PROD Rest API stage
        rest_api_prod_stage = aws_apigateway.StageOptions(
            stage_name="prod",
            data_trace_enabled=True,
            logging_level=aws_apigateway.MethodLoggingLevel.INFO,
            access_log_format=aws_apigateway.AccessLogFormat.clf(),
            access_log_destination=aws_apigateway.LogGroupLogDestination(
                prod_api_log_group
            ),
            description="Production Stage",
        )

        # PROD Rest API stage
        rest_api_dev_stage = aws_apigateway.StageOptions(
            stage_name="dev",
            data_trace_enabled=True,
            logging_level=aws_apigateway.MethodLoggingLevel.INFO,
            access_log_format=aws_apigateway.AccessLogFormat.clf(),
            access_log_destination=aws_apigateway.LogGroupLogDestination(
                dev_api_log_group
            ),
            description="Development Stage",
        )

        # https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-apigateway.SpecRestApi.html
        rest_api = aws_apigateway.SpecRestApi(
            self,
            id="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="API",
                STAGE=STAGE,
            ),
            rest_api_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="API",
                STAGE=STAGE,
            ),
            deploy=True,
            fail_on_warnings=True,
            cloud_watch_role=True,
            api_definition=rest_api_definition,
            endpoint_types=[aws_apigateway.EndpointType.REGIONAL],
            retain_deployments=False,  # Only under development
            deploy_options=rest_api_prod_stage,
        )

        # ==================================================== #
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_apigateway/ApiKey.html
        rest_api_key = aws_apigateway.ApiKey(
            self,
            "RestApiKey",
            api_key_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="API",
                STAGE=STAGE,
            ),
            description="Rest API Key",
            enabled=True,
            resources=[rest_api],
        )

        partner_api_key = aws_apigateway.ApiKey(
            self,
            "PartnerRestApiKey",
            api_key_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="Partner-API",
                STAGE=STAGE,
            ),
            description="Partner Rest API Key",
            enabled=True,
            resources=[rest_api],
        )

        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_apigateway/UsagePlan.html
        # Rate:
        # 2 requests per second Burst
        # 1 requests Quota
        # 100 requests per day
        rest_api_usage_plan = aws_apigateway.UsagePlan(
            self,
            "UsagePlan",
            api_key=rest_api_key,
            api_stages=[
                aws_apigateway.UsagePlanPerApiStage(
                    api=rest_api,
                    stage=rest_api.deployment_stage,
                )
            ],
            name="Usage-Plan",
            description="Usage Plan",
            quota=aws_apigateway.QuotaSettings(
                limit=100, offset=0, period=aws_apigateway.Period.DAY
            ),
            throttle=aws_apigateway.ThrottleSettings(rate_limit=5, burst_limit=1),
        )

        partner_api_usage_plan = aws_apigateway.UsagePlan(
            self,
            "PartnerUsagePlan",
            api_key=partner_api_key,
            api_stages=[
                aws_apigateway.UsagePlanPerApiStage(
                    api=rest_api,
                    stage=rest_api.deployment_stage,
                )
            ],
            name="Partner Usage-Plan",
            description="Partner Usage Plan",
            quota=aws_apigateway.QuotaSettings(
                limit=100, offset=0, period=aws_apigateway.Period.DAY
            ),
            throttle=aws_apigateway.ThrottleSettings(rate_limit=5, burst_limit=1),
        )

        reqValidator = aws_apigateway.RequestValidator(
            self,
            "RequestValidator",
            rest_api=rest_api,
            validate_request_body=True,
            validate_request_parameters=True,
        )

        # Create a resource named "example" on the base API
        # api_resource = rest_api.root.add_resource("example")

        pets_arn = rest_api.arn_for_execute_api("GET", "/pets")

        example_resource = rest_api.root.add_resource("example")

        pets_resource = rest_api.root.get_resource("/pets")

        # path = pets_resource.path

        # pets_resource_get = rest_api.root.resource_for_path("pets")

        # Create API Integration Response object: https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_apigateway/IntegrationResponse.html
        integration_response = aws_apigateway.IntegrationResponse(
            status_code="200",
            response_templates={"application/json": ""},
        )

        # Create API Integration Options object: https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_apigateway/IntegrationOptions.html
        api_integration_options = aws_apigateway.IntegrationOptions(
            credentials_role=rest_api_role,
            integration_responses=[integration_response],
            request_templates={
                "application/json": "Action=SendMessage&MessageBody=$input.body"
            },
            passthrough_behavior=aws_apigateway.PassthroughBehavior.NEVER,
            request_parameters={
                "integration.request.header.Content-Type": "'application/x-www-form-urlencoded'"
            },
        )

        # Create AWS Integration Object for SQS: https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_apigateway/AwsIntegration.html
        api_resource_sqs_integration = aws_apigateway.AwsIntegration(
            service="sqs",
            integration_http_method="POST",
            path="{}/{}".format(cdk.Aws.ACCOUNT_ID, queue.queue_name),
            options=api_integration_options,
        )

        # Create a Method Response Object: https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_apigateway/MethodResponse.html
        method_response = aws_apigateway.MethodResponse(status_code="200")

        # Add the API GW Integration to the "example" API GW Resource

        example_resource.add_method(
            "POST", api_resource_sqs_integration, method_responses=[method_response]
        )
