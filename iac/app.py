# Import Core Modules
# For consistency with other languages, `cdk` is the preferred import name for the CDK's core module.
from aws_cdk import core as cdk
from aws_cdk.core import App, Stack, Tags
import os

# Import CICD Stack
from stacks.cicdstack import CICDStack

# Import Stacks
# from stacks.appflowstack import AppFlowStack
from stacks.apistack import APIStack
from stacks.sharedinfrastack import SharedInfraStack
from stacks.lambdastack import LambdaStack

# Import Global & Stack Specific Settings
from settings.globalsettings import GlobalSettings
from settings.apistacksettings import APIStackSettings


globalsettings = GlobalSettings()
apistacksettings = APIStackSettings()

# Stack Environment: Region and Account
AWS_ACCOUNT_ID = globalsettings.AWS_ACCOUNT_ID
AWS_REGION = globalsettings.AWS_REGION


OWNER = globalsettings.OWNER
PRODUCT = globalsettings.PRODUCT
PACKAGE = globalsettings.PACKAGE
STAGE = globalsettings.STAGE

app = cdk.App()

# Stack Environment: Region and Account
ENV = {
    "region": AWS_REGION,
    "account": AWS_ACCOUNT_ID,
}

# ***************** CICD Stack ******************* #

# CICD Stack
cicd_stack = CICDStack(
    app,
    "{OWNER}-{PRODUCT}-{PACKAGE}-{STACKNAME}-{STAGE}".format(
        OWNER=OWNER,
        PRODUCT=PRODUCT,
        PACKAGE=PACKAGE,
        STACKNAME="CICDStack",
        STAGE=STAGE,
    ),
    env=ENV,
)
# Add a tag to all constructs in the Stack
Tags.of(cicd_stack).add("Package", PACKAGE)

'''
# ***************** All Other Stack ******************* #
# Shared Infra Stack
sharedinfra_stack = SharedInfraStack(
    app,
    "{OWNER}-{PRODUCT}-{PACKAGE}-{STACKNAME}-{STAGE}".format(
        OWNER=OWNER,
        PRODUCT=PRODUCT,
        PACKAGE=PACKAGE,
        STACKNAME="SharedInfraStack",
        STAGE=STAGE,
    ),
    env=ENV,
)
# Add a tag to all constructs in the Stack
Tags.of(sharedinfra_stack).add("Package", PACKAGE)
# Databse Stack
database_stack = DatabaseStack(
    app,
    "{OWNER}-{PRODUCT}-{PACKAGE}-{STACKNAME}-{STAGE}".format(
        OWNER=OWNER,
        PRODUCT=PRODUCT,
        PACKAGE=PACKAGE,
        STACKNAME="DatabaseStack",
        STAGE=STAGE,
    ),
    env=ENV,
)
# Add a tag to all constructs in the Stack
Tags.of(database_stack).add("Package", PACKAGE)
# Lambda Stack
lambda_stack = LambdaStack(
    app,
    "{OWNER}-{PRODUCT}-{PACKAGE}-{STACKNAME}-{STAGE}".format(
        OWNER=OWNER,
        PRODUCT=PRODUCT,
        PACKAGE=PACKAGE,
        STACKNAME="LambdaStack",
        STAGE=STAGE,
    ),
    sharedinfra_stack,
    database_stack,
    env=ENV,
)
# Add a tag to all constructs in the Stack
Tags.of(lambda_stack).add("Package", PACKAGE)
# API Stack
api_stack = APIStack(
    app,
    "{OWNER}-{PRODUCT}-{PACKAGE}-{STACKNAME}-{STAGE}".format(
        OWNER=OWNER, PRODUCT=PRODUCT, PACKAGE=PACKAGE, STACKNAME="APIStack", STAGE=STAGE
    ),
    sharedinfra_stack,
    lambda_stack,
    env=ENV,
)
# Add a tag to all constructs in the Stack
Tags.of(api_stack).add("Package", PACKAGE)
# EventBridge Stack
eventbridge_stack = EventBridgeStack(
    app,
    "{OWNER}-{PRODUCT}-{PACKAGE}-{STACKNAME}-{STAGE}".format(
        OWNER=OWNER,
        PRODUCT=PRODUCT,
        PACKAGE=PACKAGE,
        STACKNAME="EventBridgeStack",
        STAGE=STAGE,
    ),
    sharedinfra_stack,
    lambda_stack,
    env=ENV,
)
# Add a tag to all constructs in the Stack
Tags.of(eventbridge_stack).add("Package", PACKAGE)
"""
# AppFlow Stack
appflow_stack = AppFlowStack(
    app,
    "{OWNER}-{PRODUCT}-{PACKAGE}-{STACKNAME}-{STAGE}".format(
        OWNER=OWNER,
        PRODUCT=PRODUCT,
        PACKAGE=PACKAGE,
        STACKNAME="AppFlowStack",
        STAGE=STAGE,
    ),
    env=ENV,
)
# Add a tag to all constructs in the Stack
Tags.of(appflow_stack).add("Package", PACKAGE)
"""
'''
app.synth()
