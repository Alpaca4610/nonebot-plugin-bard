from pydantic import Extra, BaseModel
from typing import Optional


class Config(BaseModel, extra=Extra.ignore):
    bard_token: Optional[str] = ""

    bard_enable_private_chat: bool = True # 私聊开关，默认开启，改为False关闭
    bard_group_public: bool = False  # 群聊是否开启公共会话
    

class ConfigError(Exception):
    pass
