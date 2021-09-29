# Stack Global Settings
# Deployment Environment Settings + Settings for Resource Naming + Default/Standard Resources

from typing import Dict, Optional

import pydantic


class GlobalSettings(pydantic.BaseSettings):  # pylint: disable=too-few-public-methods
    """Global Settings"""

    DESCRIPTION: Optional[str] = "Example Stack"

    # Used when AWS CDK defines AWS resources.
    AWS_ACCOUNT_ID: str = "<INSERT_AWS_ACCOUNT_ID>"
    AWS_REGION: str = "us-east-1"

    # Used for AWS resource naming
    OWNER: str = "Owner"
    PRODUCT: str = "Product"
    PACKAGE: str = "Package"
    STAGE: str = "DEV"

    # Used for CICD and AWS CodeBuild
    GITHUB_REPO_OWNER: str = "RepoOwner"
    GITHUB_REPO_NAME: str = "RepoName"
    GITHUB_BRANCH: str = "main"

    # Various Standard S3 Buckets for this CDK App.

    # Standard S3 Buckets

    S3_DATA_BUCKET_NAME: str = (
        "{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{ZONE}-{STAGE}".format(
            OWNER="shq",
            PRODUCT=PRODUCT.lower(),
            PACKAGE=PACKAGE.lower(),
            RESOURCENAME="data",
            ZONE="001",
            STAGE=STAGE.lower(),
        )
    )

    S3_DOCUMENTS_BUCKET_NAME: str = (
        "{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{ZONE}-{STAGE}".format(
            OWNER="shq",
            PRODUCT=PRODUCT.lower(),
            PACKAGE=PACKAGE.lower(),
            RESOURCENAME="docs",
            ZONE="001",
            STAGE=STAGE.lower(),
        )
    )

    S3_CONFIG_BUCKET_NAME: str = (
        "{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{ZONE}-{STAGE}".format(
            OWNER="shq",
            PRODUCT=PRODUCT.lower(),
            PACKAGE=PACKAGE.lower(),
            RESOURCENAME="config",
            ZONE="001",
            STAGE=STAGE.lower(),
        )
    )

    S3_CICD_BUCKET_NAME: str = (
        "{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{ZONE}-{STAGE}".format(
            OWNER="shq",
            PRODUCT=PRODUCT.lower(),
            PACKAGE=PACKAGE.lower(),
            RESOURCENAME="cicd",
            ZONE="001",
            STAGE=STAGE.lower(),
        )
    )
    S3_EVENTS_BUCKET_NAME: str = (
        "{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{ZONE}-{STAGE}".format(
            OWNER="shq",
            PRODUCT=PRODUCT.lower(),
            PACKAGE=PACKAGE.lower(),
            RESOURCENAME="events",
            ZONE="001",
            STAGE=STAGE.lower(),
        )
    )
    S3_LOGS_BUCKET_NAME: str = (
        "{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{ZONE}-{STAGE}".format(
            OWNER="shq",
            PRODUCT=PRODUCT.lower(),
            PACKAGE=PACKAGE.lower(),
            RESOURCENAME="logs",
            ZONE="001",
            STAGE=STAGE.lower(),
        )
    )

    S3_CUSTOMER_DATA_BUCKET_NAME: str = (
        "{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{ZONE}-{STAGE}".format(
            OWNER="shq",
            PRODUCT=PRODUCT.lower(),
            PACKAGE=PACKAGE.lower(),
            RESOURCENAME="customerdata",
            ZONE="001",
            STAGE=STAGE.lower(),
        )
    )

    S3_DATA_LAKE_BUCKET_NAME: str = (
        "{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{ZONE}-{STAGE}".format(
            OWNER="shq",
            PRODUCT=PRODUCT.lower(),
            PACKAGE=PACKAGE.lower(),
            RESOURCENAME="datalake",
            ZONE="001",
            STAGE=STAGE.lower(),
        )
    )

    S3_DOCUMENTS_BUCKET_NAME: str = (
        "{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{ZONE}-{STAGE}".format(
            OWNER="shq",
            PRODUCT=PRODUCT.lower(),
            PACKAGE=PACKAGE.lower(),
            RESOURCENAME="docs",
            ZONE="001",
            STAGE=STAGE.lower(),
        )
    )

    S3_EXISTING_DOCUMENTS_BUCKET_NAME: str = (
        "{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{ZONE}-{STAGE}".format(
            OWNER="shq",
            PRODUCT=PRODUCT.lower(),
            PACKAGE=PACKAGE.lower(),
            RESOURCENAME="xdocs",
            ZONE="001",
            STAGE=STAGE.lower(),
        )
    )

    REST_API_NAME: str = ""
    REST_API_ROLE: str = ""
    SQS_QUEUE_NAME: str = ""
    SNS_TOPIC_NAME: str = ""

    # Various Standard EventBridge Buses & Rules for this CDK App.

    # Various Standard EventBridge Buses for this CDK App.
    ROLE_PREFIX: Optional[str]

    # Cloud Watch Alarm Settings
    ALARMS_EMAIL: Optional[str] = "<INSERT_EMAIL>"

    # Resource Tags
    COST_CENTER: Optional[str]

    class Config:  # pylint: disable=too-few-public-methods
        """model config"""

        env_file = ".env"
        env_prefix = "STACK_"
