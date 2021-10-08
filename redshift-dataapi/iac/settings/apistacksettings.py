"""stack config"""

from typing import Dict, Optional

import pydantic

from settings.globalsettings import GlobalSettings

globalsettings = GlobalSettings()

AWS_ACCOUNT_ID = globalsettings.AWS_ACCOUNT_ID
AWS_REGION = globalsettings.AWS_REGION


class APIStackSettings(pydantic.BaseSettings):  # pylint: disable=too-few-public-methods
    """Application settings"""

    stack_name: str = "APIStack"
    description: Optional[str] = "API Stack"
    aws_default_region = "us-east-1"
    stage: str = "production"
    email: Optional[str] = "ashish.tomar@versatilecapitalist.com"
    cost_center: Optional[str]
    api_name: Optional[str] = "LifeSciencesDataIQ"
    api_version: Optional[str] = "LifeSciencesDataIQ"

    stack_bucket_name: str = "Bucket"
    stack_bucket_enable_cors: Optional[bool] = False
    stack_bucket_public_read: Optional[bool] = False
    stack_bucket_prune: bool = False

    enable_api: Optional[bool] = False

    additional_env: Dict[str, str] = {}

    class Config:  # pylint: disable=too-few-public-methods
        """model config"""

        env_file = ".env"
        env_prefix = "STACK_"
