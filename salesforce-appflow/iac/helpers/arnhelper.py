from settings.globalsettings import GlobalSettings

globalsettings = GlobalSettings()

AWS_ACCOUNT_ID = globalsettings.AWS_ACCOUNT_ID
AWS_REGION = globalsettings.AWS_REGION


def ecr_arn(ecr_repo_name):
    return "{}.dkr.ecr.{}.amazonaws.com/{}".format(
        AWS_ACCOUNT_ID, AWS_REGION, ecr_repo_name
    )