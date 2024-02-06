from pydantic import Extra, BaseModel
from typing import Optional


class Config(BaseModel, extra=Extra.ignore):
    bard_token: Optional[str] = ""
    bard_token1: Optional[str] = ""
    bard_token2: Optional[str] = ""
    bard_enable_private_chat: bool = True # 私聊开关，默认开启，改为False关闭
    bard_group_public: bool = False  # 群聊是否开启公共会话
    bard_proxy: Optional[str] = ""    # 无法访问Bard的地区请配置此项

class ConfigError(Exception):
    pass
