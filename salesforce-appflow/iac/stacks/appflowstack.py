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

S3_DATA_BUCKET_NAME = globalsettings.S3_DATA_BUCKET_NAME


class AppFlowStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        s3_config_bucket = aws_s3.Bucket(
            self,
            "BucketConfig",
            bucket_name="<INSERT_VALUE>",
            versioned=False,
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        s3_new_config_bucket = aws_s3.Bucket(
            self,
            "BucketNewConfig",
            bucket_name="<INSERT_VALUE>",
            versioned=False,
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        appflow_service_role = aws_iam.Role(
            self,
            "AppFlowServiceRole",
            assumed_by=aws_iam.ServicePrincipal("appflow.amazonaws.com"),
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")
            ],
        )

        s3_new_config_bucket.add_to_resource_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                actions=[
                    "s3:PutObject",
                    "s3:AbortMultipartUpload",
                    "s3:ListMultipartUploadParts",
                    "s3:ListBucketMultipartUploads",
                    "s3:GetBucketAcl",
                    "s3:PutBucketAcl",
                ],
                resources=[
                    s3_new_config_bucket.bucket_arn,
                    s3_new_config_bucket.bucket_arn + "/*",
                ],
                principals=[aws_iam.ServicePrincipal("appflow.amazonaws.com")],
            )
        )

        s3_config_bucket.add_to_resource_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                actions=[
                    "s3:PutObject",
                    "s3:AbortMultipartUpload",
                    "s3:ListMultipartUploadParts",
                    "s3:ListBucketMultipartUploads",
                    "s3:GetBucketAcl",
                    "s3:PutBucketAcl",
                ],
                resources=[
                    s3_config_bucket.bucket_arn,
                    s3_config_bucket.bucket_arn + "/*",
                ],
                principals=[aws_iam.ServicePrincipal("appflow.amazonaws.com")],
            )
        )
        """
        # AppFlow: Extract Deleted Accounts
        
        cfn_appflow_deleted_Accounts = cloudformation_include.CfnInclude(self, 
        id = "{OWNER}-{PRODUCT}-{RESOURCENAME}-{STAGE}".format(OWNER=OWNER,PRODUCT=PRODUCT,RESOURCENAME="Deleted-Accounts",STAGE=STAGE),
        template_file="stacks/cfn/deleted-accounts.yaml"
        ) 
        """

        # AppFlow: Extract - Standard Objects

        # AppFlow: Extract Accounts
        cfn_appflow_Accounts = cloudformation_include.CfnInclude(
            self,
            id="{OWNER}-{PRODUCT}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                RESOURCENAME="Accounts",
                STAGE=STAGE,
            ),
            template_file="stacks/cfn/accounts.yaml",
            parameters={"S3Bucket": S3_DATA_BUCKET_NAME},
        )

        # AppFlow: Extract Contacts
        cfn_appflow_Contacts = cloudformation_include.CfnInclude(
            self,
            id="{OWNER}-{PRODUCT}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                RESOURCENAME="Contacts",
                STAGE=STAGE,
            ),
            template_file="stacks/cfn/contacts.yaml",
            parameters={"S3Bucket": S3_DATA_BUCKET_NAME},
        )

        # AppFlow: Extract Leads
        cfn_appflow_Leads = cloudformation_include.CfnInclude(
            self,
            id="{OWNER}-{PRODUCT}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER, 
                PRODUCT=PRODUCT, 
                RESOURCENAME="Leads", 
                STAGE=STAGE
            ),
            template_file="stacks/cfn/leads.yaml",
            parameters={"S3Bucket": S3_DATA_BUCKET_NAME},
        )

        # AppFlow: Extract Opportunities
        cfn_appflow_Opportunities = cloudformation_include.CfnInclude(
            self,
            id="{OWNER}-{PRODUCT}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                RESOURCENAME="Opportunities",
                STAGE=STAGE,
            ),
            template_file="stacks/cfn/opportunities.yaml",
            parameters={"S3Bucket": S3_DATA_BUCKET_NAME},
        )

        # AppFlow: Extract OpportunityLineItems
        cfn_appflow_OLI = cloudformation_include.CfnInclude(
            self,
            id="{OWNER}-{PRODUCT}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                RESOURCENAME="OpportunityLineItems",
                STAGE=STAGE,
            ),
            template_file="stacks/cfn/opportunitylineItems.yaml",
            parameters={"S3Bucket": S3_DATA_BUCKET_NAME},
        )
 
        # AppFlow: Extract OrderLineItems
        cfn_appflow_OrderLineItems = cloudformation_include.CfnInclude(
            self,
            id="{OWNER}-{PRODUCT}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                RESOURCENAME="OrderLineItems",
                STAGE=STAGE,
            ),
            template_file="stacks/cfn/orderlineitems.yaml",
            parameters={"S3Bucket": S3_DATA_BUCKET_NAME},
        )

        # AppFlow: Extract Orders
        cfn_appflow_Orders = cloudformation_include.CfnInclude(
            self,
            id="{OWNER}-{PRODUCT}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER, 
                PRODUCT=PRODUCT, 
                RESOURCENAME="Orders", 
                STAGE=STAGE
            ),
            template_file="stacks/cfn/orders.yaml",
            parameters={"S3Bucket": S3_DATA_BUCKET_NAME},
        )

        # AppFlow: Extract PricebookEntries
        cfn_appflow_PricebookEntries = cloudformation_include.CfnInclude(
            self,
            id="{OWNER}-{PRODUCT}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                RESOURCENAME="PricebookEntries",
                STAGE=STAGE,
            ),
            template_file="stacks/cfn/pricebookentries.yaml",
            parameters={"S3Bucket": S3_DATA_BUCKET_NAME},
        )

        # AppFlow: Extract Pricebook
        cfn_appflow_Pricebooks = cloudformation_include.CfnInclude(
            self,
            id="{OWNER}-{PRODUCT}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                RESOURCENAME="Pricebook",
                STAGE=STAGE,
            ),
            template_file="stacks/cfn/pricebooks.yaml",
            parameters={"S3Bucket": S3_DATA_BUCKET_NAME},
        )

        # AppFlow: Extract Products
        cfn_appflow_Products = cloudformation_include.CfnInclude(
            self,
            id="{OWNER}-{PRODUCT}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                RESOURCENAME="Products",
                STAGE=STAGE,
            ),
            template_file="stacks/cfn/products.yaml",
            parameters={"S3Bucket": S3_DATA_BUCKET_NAME},
        )

        

        

        