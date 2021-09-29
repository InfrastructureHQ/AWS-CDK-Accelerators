# Import Core Modules
# For consistency with other languages, `cdk` is the preferred import name for the CDK's core module.
from aws_cdk import core as cdk

# Import Security & Identity Related Modules
from aws_cdk import aws_iam
from aws_cdk.aws_iam import PolicyStatement


# Import CICD Related Modules
from aws_cdk import pipelines, aws_codepipeline, aws_codepipeline_actions


# Import Storage Related Modules
from aws_cdk import aws_s3, aws_s3_assets, aws_s3_deployment

from stacks.infrastage import InfraStage

# Import Stack Helpers

# Import IAM Policy Helpers

# Import Global & Stack Specific Settings
from settings.globalsettings import GlobalSettings

globalsettings = GlobalSettings()

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


class CICDStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here

        # Stack Environment: Region and Account
        ENV = {
            "region": AWS_ACCOUNT_ID,
            "account": AWS_REGION,
        }

        S3_CICD_BUCKET_NAME = globalsettings.S3_CICD_BUCKET_NAME

        # Source Artifacts: S3 bucket for artifacts +
        source_artifact = aws_codepipeline.Artifact(
            artifact_name="source-art",
        )

        # Build Artifacts: S3 bucket for artifacts +
        cloud_assembly_artifact = aws_codepipeline.Artifact(
            artifact_name="cloud-art",
        )

        # Install Commands
        install_commands = [
            "echo INSTALL COMMANDS",
            "npm install -g aws-cdk",
            # "/root/.pyenv/versions/3.8.8/bin/python3.8 -m pip install --upgrade pip",
            "pip install -r requirements.txt",
            "echo $CODEBUILD_SRC_DIR",
        ]

        # Build Commands
        build_commands = [
            "echo BUILD COMMANDS",
            "echo AWS Region: $AWS_DEFAULT_REGION",
            "echo $CODEBUILD_SRC_DIR",
        ]

        # Test Commands
        test_commands = [
            "echo TEST COMMANDS",
            "echo AWS Region: $AWS_DEFAULT_REGION",
            "echo $CODEBUILD_SRC_DIR",
        ]

        # CODE PIPELINE: pipelines.CdkPipeline can create a new pipeline but if we want more control, create your own pipeline firsts
        # S3 BUCKET: CICD Bucket: TODO: Should be Conditional use existing or create new

        # s3_cicd_bucket = get_or_create_bucket(self, S3_CICD_BUCKET_NAME, S3_CICD_BUCKET_NAME)

        s3_cicd_bucket = aws_s3.Bucket(
            self,
            id="{OWNER}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER, PACKAGE=PACKAGE, RESOURCENAME="CICD", STAGE=STAGE
            ),
            bucket_name=S3_CICD_BUCKET_NAME,
            versioned=False,
            block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=cdk.RemovalPolicy.RETAIN,
        )

        # Existing CICD Bucket:
        """
    existing_cicd_bucket = s3.Bucket.from_bucket_name(self, "ExistingCICDBucket",
                                    bucket_name= self.node.try_get_context("S3_CICD_BUCKET_NAME")) """

        cicd_pipeline_service_role = aws_iam.Role(
            self,
            "CICDServiceRole",
            role_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="CICD-PipeLine",
                STAGE=STAGE,
            ),
            assumed_by=aws_iam.CompositePrincipal(
                aws_iam.ServicePrincipal("codepipeline.amazonaws.com"),
                aws_iam.ServicePrincipal("codebuild.amazonaws.com"),
            ),
        )

        # TODO: Add required policies
        # role.attach_inline_policy(generate_pipeline_policy(scope))

        cicd_pipeline = aws_codepipeline.Pipeline(
            self,
            id="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="CICD-Pipeline",
                STAGE=STAGE,
            ),
            artifact_bucket=s3_cicd_bucket,
            cross_account_keys=False,
            restart_execution_on_update=True,
            pipeline_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                OWNER=OWNER,
                PRODUCT=PRODUCT,
                PACKAGE=PACKAGE,
                RESOURCENAME="CICD-Pipeline",
                STAGE=STAGE,
            ),
            # role=cicd_pipeline_service_role,
        )

        # CDK Pipeline: Self mutating CDK pipeline. We only need to run the "cdk deploy" one time to get the pipeline started.
        pipeline = pipelines.CdkPipeline(
            self,
            "CDKPipeline",
            cloud_assembly_artifact=cloud_assembly_artifact,
            code_pipeline=cicd_pipeline,
            # pipeline_name = "{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(OWNER=OWNER,PRODUCT=PRODUCT,PACKAGE=PACKAGE,RESOURCENAME="CICD-PipeLine",STAGE=STAGE),
            # cross_account_keys=False,
            source_action=aws_codepipeline_actions.GitHubSourceAction(
                action_name="GitHubSourceAction",
                output=source_artifact,
                oauth_token=cdk.SecretValue.secrets_manager("Github-Token"),
                owner=GITHUB_REPO_OWNER,
                repo=GITHUB_REPO_NAME,
                branch=GITHUB_BRANCH,
                trigger=aws_codepipeline_actions.GitHubTrigger.WEBHOOK,
            ),
            synth_action=pipelines.SimpleSynthAction(
                project_name="{OWNER}-{PRODUCT}-{PACKAGE}-{RESOURCENAME}-{STAGE}".format(
                    OWNER=OWNER,
                    PRODUCT=PRODUCT,
                    PACKAGE=PACKAGE,
                    RESOURCENAME="CICDPipeline-Synth",
                    STAGE=STAGE,
                ),
                source_artifact=source_artifact,
                cloud_assembly_artifact=cloud_assembly_artifact,
                subdirectory="",
                install_commands=install_commands,
                build_commands=build_commands,
                test_commands=test_commands,
                synth_command="echo $CODEBUILD_SRC_DIR && cdk synth",
            ),
        )

        deployment = InfraStage(self, "Prod", env=ENV)
        prod_stage = pipeline.add_application_stage(deployment)
