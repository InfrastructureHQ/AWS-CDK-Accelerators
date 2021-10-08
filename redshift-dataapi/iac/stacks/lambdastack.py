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
        self,
        scope: cdk.Construct,
        construct_id: str,
        sharedInfraStack,
        databasestack,
        redshiftstack,
        # eventbridgestack,
        kinesisstack,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ***************** LAYER:AWS POWER TOOLS ******************* #
        # Import Global AWS Power Tools layer version by ARN
        aws_power_tools_layer = aws_lambda.LayerVersion.from_layer_version_attributes(
            self,
            "awslambdapowertools",
            layer_version_arn="arn:aws:lambda:us-east-1:058863413488:layer:awslambdapowertools:1",
        )

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
                    "AmazonRedshiftFullAccess"
                ),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonRedshiftDataFullAccess"
                ),
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

         # Processor - Kinesis Events
        get_redshift_data = aws_lambda.Function(
            self,
            "Get-Redshift-Data",
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            handler="lambda_function.lambda_handler",
            description="Get Redshift Data",
            role=lambda_job_role,
            timeout=cdk.Duration.seconds(30),
            layers=[pandas_layer, pymysql_layer,aws_power_tools_layer],
            code=aws_lambda.AssetCode("../src/lambdas/get-redshift-data/"),
            function_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="Get-Redshift-Data",
                STAGE=STAGE,
            ),
            dead_letter_queue=dlq,
            memory_size=128,
            on_success=aws_lambda_destinations.EventBridgeDestination(
                # TODO: event_bus=eventbridgestack.get_core_eventbus_name
            ),
            on_failure=aws_lambda_destinations.EventBridgeDestination(),
            environment=
            {
                "CLUSTERID" : redshiftstack.get_redshift_clusterid,
                "REDSHIFTUSER" : redshiftstack.get_redshift_user
            }
        )

        #********************************************* BATCH, GLUE ,APPFLOW ,S3BATCHJOB ,CODEPIPELINE AND CLOUDFORMATION EVENTS LOADERS ****************************************

        
        #  ********************************************* BATCH, GLUE ,APPFLOW ,S3BATCHJOB ,CODEPIPELINE AND CLOUDFORMATION EVENTS LOADERS END ****************************************
 
        # ********************************************* EVENTBRIDGES FOR BATCH, GLUE ,APPFLOW, S3BATCHJOB ,CODEPIPELINE AND CLOUDFORMATION LOADERS **********************************
  
        EventBridgeForCodePipeLineEvents = aws_events.Rule(
            self,
            "CPipeLogger",
            description="Triggers from CodePipeline Events",
            # event_bus=SecurityEventsOrchestrator,
            enabled=True,
            event_pattern=aws_events.EventPattern(source=["aws.codepipeline"]),
            rule_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="CPipeLogger",
                STAGE=STAGE,
            ),
        )

        # Targets:
        EventBridgeForCodePipeLineEvents.add_target(
            aws_events_targets.LambdaFunction(loggercodepipelineEvents)
        )

        EventBridgeForCodeBuildEvents = aws_events.Rule(
            self,
            "CBuildLogger",
            description="Triggers from CloudBuild Events",
            # event_bus=SecurityEventsOrchestrator,
            enabled=True,
            event_pattern=aws_events.EventPattern(source=["aws.codebuild"]),
            rule_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="CBuildLogger",
                STAGE=STAGE,
            ),
        )

        # Targets:
        EventBridgeForCodeBuildEvents.add_target(
            aws_events_targets.LambdaFunction(loggercodebuildEvents)
        )

        EventBridgeForAppflowEvents = aws_events.Rule(
            self,
            "AppflowLogger",
            description="Triggers from Appflow Events",
            # event_bus=SecurityEventsOrchestrator,
            enabled=True,
            event_pattern=aws_events.EventPattern(source=["aws.appflow"]),
            rule_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="AppflowLog",
                STAGE=STAGE,
            ),
        )

        # Targets:
        EventBridgeForAppflowEvents.add_target(
            aws_events_targets.LambdaFunction(loggerappflowEvents)
        )

        EventBridgeForAwsBatchEvents = aws_events.Rule(
            self,
            "AWSBatchLogger",
            description="Triggers from AWSBatch Events",
            # event_bus=SecurityEventsOrchestrator,
            enabled=True,
            event_pattern=aws_events.EventPattern(source=["aws.batch"]),
            rule_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="AwsbatchLog",
                STAGE=STAGE,
            ),
        )

        # Targets:
        EventBridgeForAwsBatchEvents.add_target(
            aws_events_targets.LambdaFunction(loggerawsbatchEvents)
        )

        EventBridgeForGlueJobEvents = aws_events.Rule(
            self,
            "GlueJobLogger",
            description="Triggers from GlueJob Events",
            # event_bus=SecurityEventsOrchestrator,
            enabled=True,
            event_pattern=aws_events.EventPattern(source=["aws.glue"]),
            rule_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="GlueJobLog",
                STAGE=STAGE,
            ),
        )

        # Targets:
        EventBridgeForGlueJobEvents.add_target(
            aws_events_targets.LambdaFunction(loggergluejobEvents)
        )

        # ********************************************* END OF EVENTBRIDGE *******************************************


        # *****************START SSM PARAMETER STOREs******************* #

        ssm.StringParameter(
            self,
            "Get-Redshift-Data-ARN",
            allowed_pattern=".*",
            description="Lambda ARNs",
            parameter_name="/{OWNER}/{PRODUCT}/{PACKAGE}/{RESOURCENAME}/{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="Get-Redshift-Data-ARN",
                STAGE=STAGE,
            ),
            string_value="{}".format(get_redshift_data.function_arn),
            tier=ssm.ParameterTier.STANDARD,
        )

        ssm.StringParameter(
            self,
            "Logger-Codepipeline-Events-ARN",
            allowed_pattern=".*",
            description="Lambda ARNs",
            parameter_name="/{OWNER}/{PRODUCT}/{PACKAGE}/{RESOURCENAME}/{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="Logger-Codepipeline-Events-ARN",
                STAGE=STAGE,
            ),
            string_value="{}".format(loggercodepipelineEvents.function_arn),
            tier=ssm.ParameterTier.STANDARD,
        )

        ssm.StringParameter(
            self,
            "Logger-CodeBuild-Events-ARN",
            allowed_pattern=".*",
            description="Lambda ARNs",
            parameter_name="/{OWNER}/{PRODUCT}/{PACKAGE}/{RESOURCENAME}/{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="Logger-CodeBuild-Events-ARN",
                STAGE=STAGE,
            ),
            string_value="{}".format(loggercodebuildEvents.function_arn),
            tier=ssm.ParameterTier.STANDARD,
        )

        ssm.StringParameter(
            self,
            "Logger-Appflow-Events-ARN",
            allowed_pattern=".*",
            description="Lambda ARNs",
            parameter_name="/{OWNER}/{PRODUCT}/{PACKAGE}/{RESOURCENAME}/{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="Logger-Appflow-Events-ARN",
                STAGE=STAGE,
            ),
            string_value="{}".format(loggerappflowEvents.function_arn),
            tier=ssm.ParameterTier.STANDARD,
        )

        ssm.StringParameter(
            self,
            "Logger-AWSBatch-Events-ARN",
            allowed_pattern=".*",
            description="Lambda ARNs",
            parameter_name="/{OWNER}/{PRODUCT}/{PACKAGE}/{RESOURCENAME}/{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="Logger-AWSBatch-Events-ARN",
                STAGE=STAGE,
            ),
            string_value="{}".format(loggerawsbatchEvents.function_arn),
            tier=ssm.ParameterTier.STANDARD,
        )

        ssm.StringParameter(
            self,
            "Logger-GlueJob-Events-ARN",
            allowed_pattern=".*",
            description="Lambda ARNs",
            parameter_name="/{OWNER}/{PRODUCT}/{PACKAGE}/{RESOURCENAME}/{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="Logger-GlueJob-Events-ARN",
                STAGE=STAGE,
            ),
            string_value="{}".format(loggergluejobEvents.function_arn),
            tier=ssm.ParameterTier.STANDARD,
        )

        
        
        # *****************End SSM PARAMETER STOREs******************* #