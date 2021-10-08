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


class EventBridgeStack(cdk.Stack):
    def __init__(
        self, scope: cdk.Construct, construct_id: str, sharedInfraStack, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # EVENTBUS NAMING CONVENTION: event_bus_name="{OWNER}-{PACKAGE}-{EVENTBUSNAME}-{STAGE}-Orchestrator".format(PACKAGE=PACKAGE,EVENTBUSNAME="Usage-Events-Orchestrator",STAGE=STAGE)

        # 1 - Auth, Authorization, IAM and Security Events EventBus
        SecurityEventsOrchestrator = EventBus(
            scope=self,
            id="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="SecurityEvents",
                STAGE=STAGE,
            ),
            event_bus_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="SecurityEvents",
                STAGE=STAGE,
            ),
            # id='DigitalOps-Security-Events-Orchestrator',
            # event_bus_name='DigitalOps-Security-Events-Orchestrator'
        )

        SecurityEventsOrchestratorLG = aws_logs.LogGroup(
            scope=self,
            id="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="SecurityEventsLogs",
                STAGE=STAGE,
            ),
            log_group_name="/{OWNER}/{PRODUCT}/{PACKAGE}/{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="SecurityEvents",
                STAGE=STAGE,
            ),
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # 2 - Core Events EventBus
        CoreEventsOrchestrator = EventBus(
            scope=self,
            id="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="CoreEvents",
                STAGE=STAGE,
            ),
            event_bus_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="CoreEvents",
                STAGE=STAGE,
            ),
        )

        # Assign the resources NAME & ARN to a local variable for the Object.
        self.CoreEventsOrchestrator_name = CoreEventsOrchestrator.event_bus_name
        self.CoreEventsOrchestrator_arn = CoreEventsOrchestrator.event_bus_arn

        CoreEventsOrchestratorLG = aws_logs.LogGroup(
            scope=self,
            id="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="CoreEventsLogs",
                STAGE=STAGE,
            ),
            log_group_name="/{OWNER}/{PRODUCT}/{PACKAGE}/{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="CoreEvents",
                STAGE=STAGE,
            ),
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # 3 - AWS Resource Management Events EventBus
        AWSResourcesEventsOrchestrator = EventBus(
            scope=self,
            id="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="AWSEvents",
                STAGE=STAGE,
            ),
            event_bus_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="AWSEvents",
                STAGE=STAGE,
            ),
            # id='DigitalOps-AWSResources-Events-Orchestrator',
            # event_bus_name='DigitalOps-AWSResources-Events-Orchestrator'
        )

        AWSResourcesEventsOrchestratorLG = aws_logs.LogGroup(
            scope=self,
            id="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="AWSEventsLogs",
                STAGE=STAGE,
            ),
            log_group_name="/{OWNER}/{PRODUCT}/{PACKAGE}/{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="AWSEvents",
                STAGE=STAGE,
            ),
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # 4 - Analytics Events EventBus
        AnalyticsEventsOrchestrator = EventBus(
            scope=self,
            id="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="AnalyticsEvents",
                STAGE=STAGE,
            ),
            event_bus_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="AnalyticsEvents",
                STAGE=STAGE,
            ),
            # id='DigitalOps-Analytics-Events-Orchestrator',
            # event_bus_name='DigitalOps-Analytics-Events-Orchestrator'
        )

        AnalyticsEventsOrchestratorLG = aws_logs.LogGroup(
            scope=self,
            id="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="AnalyticsEventsLogs",
                STAGE=STAGE,
            ),
            log_group_name="/{OWNER}/{PRODUCT}/{PACKAGE}/{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="AnalyticsEvents",
                STAGE=STAGE,
            ),
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # 5 - Third Party Events EventBus
        ThirdPartyEventsOrchestrator = EventBus(
            scope=self,
            id="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="ThirdPartyEvents",
                STAGE=STAGE,
            ),
            event_bus_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="ThirdPartyEvents",
                STAGE=STAGE,
            ),
            # id='DigitalOps-ThirdParty-Events-Orchestrator',
            # event_bus_name='DigitalOps-ThirdParty-Events-Orchestrator'
        )

        ThirdPartyEventsOrchestratorLG = aws_logs.LogGroup(
            scope=self,
            id="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="ThirdPartyEventsLogs",
                STAGE=STAGE,
            ),
            log_group_name="/{OWNER}/{PRODUCT}/{PACKAGE}/{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="ThirdPartyEvents",
                STAGE=STAGE,
            ),
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # 6 - Usage, Billing and Logging Events EventBus
        UsageEventsOrchestrator = EventBus(
            scope=self,
            id="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="UsageEvents",
                STAGE=STAGE,
            ),
            event_bus_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="UsageEvents",
                STAGE=STAGE,
            ),
            # id='DigitalOps-Usage-Events-Orchestrator',
            # event_bus_name='DigitalOps-Usage-Events-Orchestrator'
        )

        UsageEventsOrchestratorLG = aws_logs.LogGroup(
            scope=self,
            id="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="UsageEventsLogs",
                STAGE=STAGE,
            ),
            log_group_name="/{OWNER}/{PRODUCT}/{PACKAGE}/{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="UsageEvents",
                STAGE=STAGE,
            ),
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # 7 - Data - Extract, Load and Transform Events EventBus
        DataEventsOrchestrator = EventBus(
            scope=self,
            id="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="DataEvents",
                STAGE=STAGE,
            ),
            event_bus_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="DataEvents",
                STAGE=STAGE,
            ),
            # id='DigitalOps-Data-Events-Orchestrator',
            # event_bus_name='DigitalOps-Data-Events-Orchestrator'
        )

        DataEventsOrchestratorLG = aws_logs.LogGroup(
            scope=self,
            id="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="DataEventsLogs",
                STAGE=STAGE,
            ),
            log_group_name="/{OWNER}/{PRODUCT}/{PACKAGE}/{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="DataEvents",
                STAGE=STAGE,
            ),
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # 8 - CICD Events EventBus
        CICDEventsOrchestrator = EventBus(
            scope=self,
            id="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="CICDEvents",
                STAGE=STAGE,
            ),
            event_bus_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="CICDEvents",
                STAGE=STAGE,
            ),
            # id='DigitalOps-CICD-Events-Orchestrator',
            # event_bus_name='DigitalOps-CICD-Events-Orchestrator'
        )

        CICDEventsOrchestratorLG = aws_logs.LogGroup(
            scope=self,
            id="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="CICDEventsLogs",
                STAGE=STAGE,
            ),
            log_group_name="/{OWNER}/{PRODUCT}/{PACKAGE}/{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="CICDEvents",
                STAGE=STAGE,
            ),
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # 1 - EventBridge Policy & Permissions: Lambda permission to put events on our EventBridge
        LambdaPolicy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW, resources=["*"], actions=["events:PutEvents"]
        )
        # Usage: your_lambda.add_to_role_policy(LambdaPolicy)

        # 2 - EventBridge Policy & Permissions: Shared across all EventBuses
        event_bridge_put_policy = aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW, resources=["*"], actions=["events:PutEvents"]
        )

        # RULES: Various rules for EventBuses

        # transform_rule.add_target(targets.LambdaFunction(handler=transform_lambda))
        # UpdateExecutionIncidentPolicyRule.add_target(targets.SqsQueue(InfraStack.get_NewIncidentsSQSQueue))

        SecurityEventsRule = aws_events.Rule(
            self,
            "SecurityEventsRule",
            description="Catch all IAM, Cognito Events Rule",
            event_bus=SecurityEventsOrchestrator,
            enabled=True,
            event_pattern=aws_events.EventPattern(source=["aws.iam"]),
            rule_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="CatchAll",
                STAGE=STAGE,
            ),
        )

        # Targets:
        SecurityEventsRule.add_target(
            aws_events_targets.CloudWatchLogGroup(SecurityEventsOrchestratorLG)
        )

        # 1 - ScheduledRule: These are global. Cannot attach to an EventBus
        ScheduledRule = aws_events.Rule(
            self,
            "ScheduledRule",
            description="Run every 2 minute",
            enabled=True,
            # schedule=events.Schedule.cron(* * ? * mon-sun *)
            schedule=aws_events.Schedule.expression("rate(2 minutes)"),
            rule_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="Global-Scheduled",
                STAGE=STAGE,
            ),
        )

        # 2 - ScheduledRule: Using Cron. Global Rule.
        ScheduledRuleMF = aws_events.Rule(
            self,
            "ScheduledRuleMF",
            description="Runs every day at 6PM UTC Monday to Friday",
            schedule=aws_events.Schedule.cron(
                minute="0", hour="18", month="*", week_day="MON-FRI", year="*"
            ),
            rule_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="Scheduled6PM-MF",
                STAGE=STAGE,
            ),
        )

        self.ScheduledRuleMF_name = ScheduledRuleMF.rule_name
        self.ScheduledRuleMF_arn = ScheduledRuleMF.rule_arn

        # rule.add_target(targets.LambdaFunction(transform_lambda))

        # ThirdPartyEventsOrchestrator: Rule to route failures
        ThirdPartyAPIFailedRule = aws_events.Rule(
            self,
            "ThirdPartyAPIFailedRule",
            description="Third Party API Failed Transformation Rule",
            event_bus=ThirdPartyEventsOrchestrator,
            event_pattern=aws_events.EventPattern(
                source=["ThirdPartAPICall"],
                detail_type=["RESTAPI"],
                detail={"status": ["fail"]},
            ),
            rule_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="3rdPartyAPI",
                STAGE=STAGE,
            ),
        )

        EventBUsesARNs = aws_ssm.StringListParameter(
            self,
            "EventBusesARNs",
            allowed_pattern=".*",
            description="EventBuses ARNs",
            parameter_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="EventBuses-ARNs",
                STAGE=STAGE,
            ),
            string_list_value=[
                "{}".format(SecurityEventsOrchestrator.event_bus_arn),
                "{}".format(CICDEventsOrchestrator.event_bus_arn),
                "{}".format(CoreEventsOrchestrator.event_bus_arn),
                "{}".format(SecurityEventsOrchestrator.event_bus_arn),
                "{}".format(SecurityEventsOrchestrator.event_bus_arn),
            ],
            tier=aws_ssm.ParameterTier.STANDARD,
        )

        EventRulesARNs = aws_ssm.StringListParameter(
            self,
            "EventRulesARNs",
            allowed_pattern=".*",
            description="EventRules ARNs",
            parameter_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="RUles-ARNs",
                STAGE=STAGE,
            ),
            string_list_value=[
                "{}".format(SecurityEventsOrchestrator.event_bus_arn),
                "{}".format(CICDEventsOrchestrator.event_bus_arn),
                "{}".format(CoreEventsOrchestrator.event_bus_arn),
                "{}".format(SecurityEventsOrchestrator.event_bus_arn),
                "{}".format(SecurityEventsOrchestrator.event_bus_arn),
            ],
            tier=aws_ssm.ParameterTier.STANDARD,
        )

        APIDestinationsARNs = aws_ssm.StringListParameter(
            self,
            "APIDestinationsARNs",
            allowed_pattern=".*",
            description="API Destinations ARNs",
            parameter_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="APIDestinations-ARNs",
                STAGE=STAGE,
            ),
            string_list_value=[
                "{}".format(SecurityEventsOrchestrator.event_bus_arn),
                "{}".format(CICDEventsOrchestrator.event_bus_arn),
                "{}".format(CoreEventsOrchestrator.event_bus_arn),
                "{}".format(SecurityEventsOrchestrator.event_bus_arn),
                "{}".format(SecurityEventsOrchestrator.event_bus_arn),
            ],
            tier=aws_ssm.ParameterTier.STANDARD,
        )

    # properties to share with other stacks ...
    @property
    def get_core_eventbus_name(self):
        return self.CoreEventsOrchestrator_name

    @property
    def get_core_eventbus_arn(self):
        return self.CoreEventsOrchestrator_arn

    @property
    def get_scheduled_rule_arn(self):
        return self.ScheduledRuleMF_arn
