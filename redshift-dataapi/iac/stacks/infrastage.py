#
# Copyright (c) 2021, SteelHead Industry Cloud, Inc. <info@steelheadhq.com>
# All rights reserved.
#

# Import Core Modules
# For consistency with other languages, `cdk` is the preferred import name for the CDK's core module.
from aws_cdk import core as cdk
from aws_cdk.core import App, Construct, Stack, Stage, Environment, Tags
import os

# Import Stacks
from stacks.sharedinfrastack import SharedInfraStack
from stacks.eventbridgestack import EventBridgeStack
from stacks.kinesisstack import KinesisStack
from stacks.vpcstack import VPCStack
from stacks.redshiftstack import RedshiftStack

from stacks.lambdastack import LambdaStack
from stacks.cognitostack import CognitoStack
from stacks.apistack import APIStack
from stacks.databasestack import DatabaseStack
from stacks.stepfunctionsstack import StepFunctionsStack
from stacks.gluestack import GlueStack

# from stacks.codebuildstack import CodeBuildStack


# Import Global & Stack Specific Settings
from settings.globalsettings import GlobalSettings
from settings.apistacksettings import APIStackSettings

globalsettings = GlobalSettings()
apistacksettings = APIStackSettings()

# Stack Environment: Region and Account
AWS_ACCOUNT_ID = globalsettings.AWS_ACCOUNT_ID
AWS_REGION = globalsettings.AWS_REGION

# Resource Naming
OWNER = globalsettings.OWNER
PRODUCT = globalsettings.PRODUCT
PACKAGE = globalsettings.PACKAGE
STAGE = globalsettings.STAGE

# CICD & CodeBuild
GITHUB_REPO_OWNER = globalsettings.GITHUB_REPO_OWNER
GITHUB_REPO_NAME = globalsettings.GITHUB_REPO_NAME
GITHUB_BRANCH = globalsettings.GITHUB_BRANCH


class InfraStage(cdk.Stage):
    def __init__(self, scope: cdk.Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        ENV = {
            "region": AWS_REGION,
            "account": AWS_ACCOUNT_ID,
        }

        # Shared Infra Stack
        sharedinfra_stack = SharedInfraStack(
            self,
            "{OWNER}-{PRODUCT}-{PACKAGE}-{STACKNAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                STACKNAME="SharedInfraStack",
                STAGE=STAGE,
            ),
            env=ENV,
        )

        # EventBridge Stack
        # eventbridge_stack = EventBridgeStack(
        #     self,
        #     "{OWNER}-{PRODUCT}-{PACKAGE}-{STACKNAME}-{STAGE}".format(
        #         OWNER=OWNER,
        #         PRODUCT=PRODUCT,
        #         PACKAGE=PACKAGE,
        #         STACKNAME="EventBridgeStack",
        #         STAGE=STAGE,
        #     ),
        #     sharedinfra_stack,
        #     env=ENV,
        # )

        # Database Stack
        database_stack = DatabaseStack(
            self,
            "{OWNER}-{PRODUCT}-{PACKAGE}-{STACKNAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                STACKNAME="DatabaseStack",
                STAGE=STAGE,
            ),
            env=ENV,
        )

        # Kinesis Stack
        kinesis_stack = KinesisStack(
            self,
            "{OWNER}-{PRODUCT}-{PACKAGE}-{STACKNAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                STACKNAME="KinesisStack",
                STAGE=STAGE,
            ),
            env=ENV,
        )
         
        # VPC Stack
        vpc_stack = VPCStack(
            self,
            "{OWNER}-{PRODUCT}-{PACKAGE}-{STACKNAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                STACKNAME="VPCStack",
                STAGE=STAGE,
            ),
            env=ENV,
        )

        redshift_stack = RedshiftStack(
            self,
            "{OWNER}-{PRODUCT}-{PACKAGE}-{STACKNAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                STACKNAME="RedshiftStack",
                STAGE=STAGE,
            ),
            sharedinfra_stack,
            vpc_stack,
            env=ENV,
        )

        # Lambda Stack
        lambda_stack = LambdaStack(
            self,
            "{OWNER}-{PRODUCT}-{PACKAGE}-{STACKNAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                STACKNAME="LambdaStack",
                STAGE=STAGE,
            ),
            sharedinfra_stack,
            database_stack,
            redshift_stack,
            # eventbridge_stack,
            kinesis_stack,
            env=ENV,
        )


        # API Stack
        # api_stack = APIStack(
        #     self,
        #     "{OWNER}-{PRODUCT}-{PACKAGE}-{STACKNAME}-{STAGE}".format(
        #         OWNER=OWNER,
        #         PRODUCT=PRODUCT,
        #         PACKAGE=PACKAGE,
        #         STACKNAME="APIStack",
        #         STAGE=STAGE,
        #     ),
        #     sharedinfra_stack,
        #     lambda_stack,
        #     env=ENV,
        # )

        # Step Function Stack
        stepfunction_stack = StepFunctionsStack(
            self,
            "{OWNER}-{PRODUCT}-{PACKAGE}-{STACKNAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                STACKNAME="StepFunctionsStack",
                STAGE=STAGE,
            ),
            sharedinfra_stack,
            lambda_stack,
            env=ENV,
        )

        # # Glue Stack
        # glue_stack = GlueStack(
        #     self,
        #     "{OWNER}-{PRODUCT}-{PACKAGE}-{STACKNAME}-{STAGE}".format(
        #         OWNER=OWNER,
        #         PRODUCT=PRODUCT,
        #         PACKAGE=PACKAGE,
        #         STACKNAME="GlueStack",
        #         STAGE=STAGE,
        #     ),
        #     sharedinfra_stack,
        #     env=ENV,
        # )

        # Cognito Stack
        # cognito_stack = CognitoStack(
        #     self,
        #     "{OWNER}-{PRODUCT}-{PACKAGE}-{STACKNAME}-{STAGE}".format(
        #         OWNER=OWNER,
        #         PRODUCT=PRODUCT,
        #         PACKAGE=PACKAGE,
        #         STACKNAME="CognitoStack",
        #         STAGE=STAGE,
        #     ),
        #     lambda_stack,
        #     env=ENV,
        # )

        

        
