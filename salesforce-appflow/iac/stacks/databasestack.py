from aws_cdk import core as cdk
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_sqs as sqs
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_events as events
from aws_cdk import aws_events_targets as targets
import aws_cdk.aws_ssm as ssm

from settings.globalsettings import GlobalSettings

globalsettings = GlobalSettings()

# GLOBAL SETTINGS
OWNER = globalsettings.OWNER
PRODUCT = globalsettings.PRODUCT
PACKAGE = globalsettings.PACKAGE
STAGE = globalsettings.STAGE


class DatabaseStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB: Table
        dynamodb_table = dynamodb.Table(
            self,
            id="{OWNER}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PACKAGE=PACKAGE,
                RESOURCENAME="DynamoDB",
                STAGE=STAGE,
            ),
            table_name="{OWNER}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PACKAGE=PACKAGE,
                RESOURCENAME="DynamoDB",
                STAGE=STAGE,
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            partition_key=dynamodb.Attribute(
                name="partition_key", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="sort_key", type=dynamodb.AttributeType.STRING
            ),
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
            removal_policy=cdk.RemovalPolicy.DESTROY,  # NOT recommended for production code
        )

        dynamodb_table.table_stream_arn

        # *****************PARAMETER STOREs******************* #

        ssm.StringParameter(
            self,
            "DDB-ARN",
            allowed_pattern=".*",
            description="DynamoDB ARNs",
            parameter_name="/{OWNER}/{PRODUCT}/{PACKAGE}/{RESOURCENAME}/{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="DDB-ARN",
                STAGE=STAGE,
            ),
            string_value="{}".format(dynamodb_table.table_arn),
            tier=ssm.ParameterTier.STANDARD,
        )

        # *****************PARAMETER STOREs******************* #

        # Assign the resources arn/url/name to a local variable for the Object.
        self.dynamodb_table_name = dynamodb_table

    # *****************STACK/OBJECT PROPERTIES******************* #
    # properties to share with other stacks ...
    @property
    def get_ddb_table_name(self):
        return self.dynamodb_table_name
