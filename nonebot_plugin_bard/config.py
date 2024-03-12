from pydantic import Extra, BaseModel
from typing import Optional


class Config(BaseModel, extra=Extra.ignore):
    gemini_token1: Optional[str] = ""     #   Secure_1PSID
    gemini_token2: Optional[str] = ""     #   Secure_1PSIDTS

    gemini_enable_private_chat: bool = True # 私聊开关，默认开启，改为False关闭
    gemini_group_public: bool = False  # 群聊是否开启公共会话
    gemini_proxy: Optional[str] = ""    # 无法访问Gemini的地区请配置此项

class ConfigError(Exception):
    pass
