"""stack config"""

from typing import Dict, Optional

import pydantic

from settings.globalsettings import GlobalSettings

globalsettings = GlobalSettings()

AWS_ACCOUNT_ID = globalsettings.AWS_ACCOUNT_ID
AWS_REGION = globalsettings.AWS_REGION


class APIGatewaySettings(
    pydantic.BaseSettings
):  # pylint: disable=too-few-public-methods
    """Application settings"""

    stack_name: str = "APIStack"
    description: Optional[str] = "API Stack"
    aws_default_region = "us-east-1"
    stage: str = "production"
    email: Optional[str] = "<INSERT_EMAIL>"
    cost_center: Optional[str]

    class Config:  # pylint: disable=too-few-public-methods
        """model config"""

        env_file = ".env"
        env_prefix = "STACK_"
