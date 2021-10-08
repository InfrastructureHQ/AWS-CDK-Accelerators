#
# Copyright (c) 2021, SteelHead Industry Cloud, Inc. <info@steelheadhq.com>
# All rights reserved.
#

# Import Core Modules
# For consistency with other languages, `cdk` is the preferred import name for the CDK's core module.
from aws_cdk import core as cdk

# Import Security & Identity Related Modules
from aws_cdk import aws_iam, aws_cognito, aws_certificatemanager

# from aws_cdk.aws_cognito import (
#     UserPool,
#     UserPoolClient,
#     UserPoolDomain,
#     OAuthSettings,
#     CognitoDomainOptions,
#     CfnIdentityPool,
#     CfnIdentityPoolRoleAttachment,
#     UserVerificationConfig,
#     SignInAliases,
#     StandardAttributes,
#     StandardAttribute,
#     PasswordPolicy,
#     AccountRecovery,
#     AutoVerifiedAttrs,
# )
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


class CognitoStack(cdk.Stack):
    def __init__(
        self, scope: cdk.Construct, construct_id: str, lambdastack, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ***************** User Pool ******************* #

        # Create the API GW service role with permissions to call SQS/S3 & Invoke Lambda
        cognito_userpool_role = aws_iam.Role(
            self,
            "Cognito-User-Pool-Role",
            role_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="CognitoUserPool",
                STAGE=STAGE,
            ),
            assumed_by=aws_iam.ServicePrincipal("cognito-idp.amazonaws.com"),
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonSQSFullAccess"
                ),
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonS3FullAccess"
                ),
            ],
        )

        # Creates Cognito User Pool
        user_pool = aws_cognito.UserPool(
            self,
            id="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="UserPool",
                STAGE=STAGE,
            ),
            user_pool_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="UserPool",
                STAGE=STAGE,
            ),
            account_recovery=aws_cognito.AccountRecovery.EMAIL_AND_PHONE_WITHOUT_MFA,
            auto_verify=aws_cognito.AutoVerifiedAttrs(email=True),
            standard_attributes={
                "email": {"required": False, "mutable": False},
                "fullname": {"required": False, "mutable": True},
            },
            custom_attributes={
                "tenantid": aws_cognito.StringAttribute(
                    min_len=1, max_len=256, mutable=True
                ),
                "external_orgid": aws_cognito.StringAttribute(
                    min_len=1, max_len=256, mutable=True
                ),
                "external_userid": aws_cognito.StringAttribute(
                    min_len=1, max_len=256, mutable=True
                ),
                "company_name": aws_cognito.StringAttribute(
                    min_len=1, max_len=256, mutable=True
                ),
                "department": aws_cognito.StringAttribute(
                    min_len=1, max_len=256, mutable=True
                ),
                "division": aws_cognito.StringAttribute(
                    min_len=1, max_len=256, mutable=True
                ),
                "role": aws_cognito.StringAttribute(
                    min_len=1, max_len=256, mutable=True
                ),
                "title": aws_cognito.StringAttribute(
                    min_len=1, max_len=256, mutable=True
                ),
                "accountid": aws_cognito.StringAttribute(
                    min_len=1, max_len=256, mutable=True
                ),
                "contactid": aws_cognito.StringAttribute(
                    min_len=1, max_len=256, mutable=True
                ),
            },
            mfa=aws_cognito.Mfa.OFF,
            self_sign_up_enabled=True,
            # single email mulitple user create
            sign_in_aliases=aws_cognito.SignInAliases(username=False, email=False),
            user_verification={"email_style": aws_cognito.VerificationEmailStyle.LINK},
            # TODO: Add additional lambda triggers
            lambda_triggers=aws_cognito.UserPoolTriggers(
                pre_sign_up=aws_lambda.Function.from_function_arn(
                    self,
                    "Producer-Pre-SignUp",
                    lambdastack.get_trigger_pre_signup_arn,
                ),
                pre_authentication=aws_lambda.Function.from_function_arn(
                    self,
                    "Producer-Pre-Authentication",
                    lambdastack.get_trigger_pre_authentication_arn,
                ),
                pre_token_generation=aws_lambda.Function.from_function_arn(
                    self,
                    "Producer-Pre-Token-Generation",
                    lambdastack.get_trigger_pre_tokengeneration_arn,
                ),
                post_authentication=aws_lambda.Function.from_function_arn(
                    self,
                    "Producer-Post-Authentication",
                    lambdastack.get_trigger_post_authentication_arn,
                ),
                post_confirmation=aws_lambda.Function.from_function_arn(
                    self,
                    "Producer-Post-Confirmation",
                    lambdastack.get_trigger_post_confirmation_arn,
                ),
            ),
        )

        user_pool.policies = aws_cognito.CfnUserPool.PoliciesProperty(
            password_policy=aws_cognito.CfnUserPool.PasswordPolicyProperty(
                minimum_length=8,
                require_lowercase=True,
                require_numbers=True,
                require_symbols=True,
                require_uppercase=True,
            )
        )

        # ***************** User Pool Client ******************* #
        # Creates the cognito user pool client
        user_pool_client_salesforce_sites = aws_cognito.UserPoolClient(
            self,
            id="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="EndUserPool-Client",
                STAGE=STAGE,
            ),
            user_pool=user_pool,
            generate_secret=False,
            id_token_validity=cdk.Duration.hours(24),
            auth_flows=aws_cognito.AuthFlow(
                admin_user_password=True,
                custom=True,
                user_password=True,
                user_srp=True,
            ),
            prevent_user_existence_errors=True,
            o_auth=aws_cognito.OAuthSettings(
                # Authorization code grant is the preferred method for authorizing end users.
                # Use Client credentials grant to to authorize machine-to-machine requests.
                # https://aws.amazon.com/blogs/mobile/understanding-amazon-cognito-user-pool-oauth-2-0-grants/
                flows=aws_cognito.OAuthFlows(
                    authorization_code_grant=True,
                    implicit_code_grant=False,
                    client_credentials=False,
                ),
                scopes=[
                    aws_cognito.OAuthScope.EMAIL,
                    aws_cognito.OAuthScope.OPENID,
                    aws_cognito.OAuthScope.PROFILE,
                    aws_cognito.OAuthScope.COGNITO_ADMIN,
                ],
                callback_urls=["https://login.steelheadhq.com"],
            ),
            user_pool_client_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="EndUserPool-Client",
                STAGE=STAGE,
            ),
        )

        """
        user_pool_client_api_to_api = aws_cognito.UserPoolClient(
            self,
            id="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="APIUserPool-Client",
                STAGE=STAGE,
            ),
            user_pool=user_pool,
            generate_secret=True,
            id_token_validity=cdk.Duration.hours(24),
            auth_flows=aws_cognito.AuthFlow(
                admin_user_password=False,
                custom=True,
                user_password=False,
                user_srp=True,
            ),
            prevent_user_existence_errors=True,
            o_auth=aws_cognito.OAuthSettings(
                # Authorization code grant is the preferred method for authorizing end users.
                # Use Client credentials grant to to authorize machine-to-machine requests.
                # https://aws.amazon.com/blogs/mobile/understanding-amazon-cognito-user-pool-oauth-2-0-grants/
                flows=aws_cognito.OAuthFlows(
                    authorization_code_grant=False,
                    implicit_code_grant=False,
                    client_credentials=True,
                ),
                scopes=[
                    # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_cognito/OAuthScope.html#aws_cdk.aws_cognito.OAuthScope
                    # aws_cognito.OAuthScope.EMAIL,
                    # aws_cognito.OAuthScope.OPENID,
                    # aws_cognito.OAuthScope.PROFILE,
                    aws_cognito.OAuthScope.COGNITO_ADMIN,
                ],
                callback_urls=["https://login.steelheadhq.com"],
            ),
            user_pool_client_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="APIUserPool-Client",
                STAGE=STAGE,
            ),
        ) """

        standard_userpoll_group = aws_cognito.CfnUserPoolGroup(
            self,
            "Standard-UserPool-Group",
            group_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="Standard-Users",
                STAGE=STAGE,
            ),
            description="Standard-Users",
            user_pool_id=user_pool.user_pool_id,
        )
        admin_userpool_group = aws_cognito.CfnUserPoolGroup(
            self,
            "Admin-UserPool-Group",
            group_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="Admin-Users",
                STAGE=STAGE,
            ),
            description="Administrators",
            user_pool_id=user_pool.user_pool_id,
        )

        # Create Identity Pool 

        identity_pool = aws_cognito.CfnIdentityPool(
            self,
            id="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="Identity-Pool",
                STAGE=STAGE,
            ),
            identity_pool_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="Identity-Pool",
                STAGE=STAGE,
            ),
            allow_unauthenticated_identities=True,
            # The Amazon Cognito user pools and their client IDs.
            cognito_identity_providers=[
                aws_cognito.CfnIdentityPool.CognitoIdentityProviderProperty(
                    client_id=user_pool_client_salesforce_sites.user_pool_client_id,
                    provider_name=user_pool.user_pool_provider_name,
                ),
                # aws_cognito.CfnIdentityPool.CognitoIdentityProviderProperty(
                #     client_id=user_pool_client_api_to_api.user_pool_client_id,
                #     provider_name=user_pool.user_pool_provider_name,
                # ),
            ],
        )

        # ***************** IAM: ROLES ******************* #
        # Cognito Authenticated Role
        cognito_authenticated_role = aws_iam.Role(
            self,
            "Cognito-Authenticated-Role",
            role_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="Authenticated",
                STAGE=STAGE,
            ),
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonESCognitoAccess"
                )
            ],
            assumed_by=aws_iam.FederatedPrincipal(
                "cognito-identity.amazonaws.com",
                assume_role_action="sts:AssumeRoleWithWebIdentity",
                conditions={
                    "StringEquals": {
                        "cognito-identity.amazonaws.com:aud": identity_pool.ref
                    },
                    "ForAnyValue:StringLike": {
                        "cognito-identity.amazonaws.com:amr": "authenticated"
                    },
                },
            ),
        )

        cognito_authenticated_role.attach_inline_policy(
            aws_iam.Policy(
                self,
                "Cognito-Authenticated-Role-Policy",
                policy_name="cognito-Authenticated-Role-Policy",
                statements=[
                    aws_iam.PolicyStatement(
                        actions=[
                            "mobileanalytics:PutEvents",
                            "cognito-sync:*",
                            "execute-api:*",
                        ],
                        resources=["*"],
                    ),
                    # Provide full access to IoT for the authenticated user
                    # The AWS IoT policy scopes down the access
                    aws_iam.PolicyStatement(actions=["iot:*"], resources=["*"]),
                ],
            )
        )

        # Cognito Unauthenticated Role
        cognito_unauthenticated_role = aws_iam.Role(
            self,
            "Cognito-Unauthenticated-Role",
            role_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="Unauthenticated",
                STAGE=STAGE,
            ),
            assumed_by=aws_iam.FederatedPrincipal(
                "cognito-identity.amazonaws.com",
                conditions={
                    "StringEquals": {
                        "cognito-identity.amazonaws.com:aud": identity_pool.ref
                    },
                    "ForAnyValue:StringLike": {
                        "cognito-identity.amazonaws.com:amr": "unauthenticated"
                    },
                },
                assume_role_action="sts:AssumeRoleWithWebIdentity",
            ),
        )

        cognito_unauthenticated_role.attach_inline_policy(
            aws_iam.Policy(
                self,
                "cognito-Unauthenticated-Role-Policy",
                policy_name="cognito-Unauthenticated-Role-Policy",
                statements=[
                    aws_iam.PolicyStatement(
                        actions=[
                            "mobileanalytics:PutEvents",
                            "cognito-sync:*",
                            "execute-api:*",
                            "kinesis:PutRecord",
                            "kinesis:PutRecords",
                        ],
                        resources=[
                            "*",
                            "arn:aws:kinesis:*:*:stream/*",
                        ],
                    ),
                    aws_iam.PolicyStatement(
                        actions=[
                            "sts:AssumeRole",
                        ],
                        resources=[
                            "<Resource-ARN>",
                        ],
                    ),
                ],
            )
        )

        # Finally, attach authenticated and Unauthenticated roles to Identity pool
        aws_cognito.CfnIdentityPoolRoleAttachment(
            self,
            "CDDIdentityPoolRoleAttach",
            identity_pool_id=identity_pool.ref,
            roles={
                "authenticated": cognito_authenticated_role.role_arn,
                "unauthenticated": cognito_unauthenticated_role.role_arn,
            },
        )

        # Add Domain
        domain = user_pool.add_domain(
            "CognitoDomain", cognito_domain={"domain_prefix": "identitycloudhq"}
        )
