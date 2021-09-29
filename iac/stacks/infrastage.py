# Import Core Modules
# For consistency with other languages, `cdk` is the preferred import name for the CDK's core module.
from aws_cdk import core as cdk
from aws_cdk.core import App, Construct, Stack, Stage, Environment, Tags
import os

# Import Stacks

from stacks.sharedinfrastack import SharedInfraStack


from stacks.lambdastack import LambdaStack
from stacks.apistack import APIStack


# from stacks.codebuildstack import CodeBuildStack


# Import Global & Stack Specific Settings
from settings.globalsettings import GlobalSettings
from settings.apigateway import APIGatewaySettings


globalsettings = GlobalSettings()
apistacksettings = APIGatewaySettings()

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

        # API Stack
        api_stack = APIStack(
            self,
            "{OWNER}-{PRODUCT}-{PACKAGE}-{STACKNAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                STACKNAME="APIStack",
                STAGE=STAGE,
            ),
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
            env=ENV,
        )
