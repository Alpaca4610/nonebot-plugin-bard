import nonebot
import requests

from nonebot import on_command,require
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageSegment, PrivateMessageEvent, MessageEvent, helpers , GROUP_OWNER , GROUP_ADMIN
from nonebot.permission import SUPERUSER

from nonebot.plugin import PluginMetadata

from .config import Config, ConfigError
from gemini_webapi import GeminiClient

# require("nonebot_plugin_htmlrender")
# from nonebot_plugin_htmlrender import md_to_pic

__plugin_meta__ = PluginMetadata(
    name="谷歌Gemini Pro聊天",
    description="Nonebot框架下的谷歌Gemini Pro聊天插件，支持联网搜索和图片识别",
    usage=
    '''
    Gemini 文字/图片 发起无记忆对话
    连续对话 文字/图片 发起有记忆对话
    连续对话结束 结束本次有记忆对话
    ''',
    config= Config,
    extra={},
    type="application",
    homepage="https://github.com/Alpaca4610/nonebot-plugin-bard",
    supported_adapters={"~onebot.v11"}
)

# 配置导入
plugin_config = Config.parse_obj(nonebot.get_driver().config.dict())

token1 = plugin_config.gemini_token1
token2 = plugin_config.gemini_token2

if not (token1 and token2):
    raise ConfigError("请设置Gemini的cookies")

proxies = {
    'http': plugin_config.gemini_proxy,
    'https': plugin_config.gemini_proxy
} if plugin_config.gemini_proxy else None

client = GeminiClient(token1, token2, proxy=proxies)

public = plugin_config.gemini_group_public
session = {}

chat_request = on_command("Gemini", block=False, priority=1)
@chat_request.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    if isinstance(event, PrivateMessageEvent) and not plugin_config.gemini_enable_private_chat:
        chat_request.finish("对不起，私聊暂不支持此功能。")
    img_url = helpers.extract_image_urls(event.message)
    content = msg.extract_plain_text()
    if content == "" or content is None:
        await chat_request.finish(MessageSegment.text("内容不能为空！"))
    await chat_request.send(MessageSegment.text("Gemini正在思考中......"))
    if not img_url:
        try:
            res = await client.generate_content(content)
        except Exception as error:
            await chat_request.finish(str(error))
        # pic = await md_to_pic(res.text, width=800)
        # await chat_request.send(MessageSegment.image(pic), at_sender=True)
        await chat_request.finish(MessageSegment.text(res.text), at_sender=True)
    else:
        try:
            response = requests.get(img_url[0])
            res = await client.generate_content(content, image=response.content)
        except Exception as error:
            await chat_request.finish(str(error))
        await chat_request.finish(MessageSegment.text(res.text), at_sender=True)

chat_record = on_command("连续对话", block=False, priority=1)
@chat_record.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    if isinstance(event, PrivateMessageEvent) and not plugin_config.gemini_enable_private_chat:
        chat_record.finish("对不起，私聊暂不支持此功能。")
    img_url = helpers.extract_image_urls(event.message)
    content = msg.extract_plain_text()
    if content == "" or content is None:
        await chat_record.finish(MessageSegment.text("内容不能为空！"))
    await chat_record.send(MessageSegment.text("Gemini正在思考中......"))

    session_id = create_session_id(event)
    if session_id not in session:
        session[session_id] = client.start_chat()

    if not img_url:
        try:
            res = await session[session_id].send_message(content)
        except Exception as error:
            await chat_record.finish(str(error))
        await chat_record.finish(MessageSegment.text(res.text), at_sender=True)
    else:
        try:
            response = requests.get(img_url[0])
            res = await session[session_id].send_message(content, image=response.content)
        except Exception as error:
            await chat_record.finish(str(error))
        await chat_record.finish(MessageSegment.text(res.text), at_sender=True)

chat_stop = on_command("结束连续对话", block=False, priority=1)
@chat_stop.handle()
async def _(event: MessageEvent):
    del session[create_session_id(event)]
    await chat_stop.finish(MessageSegment.text("成功清除历史记录！"), at_sender=True)

def create_session_id(event):
    if isinstance(event, PrivateMessageEvent):
        session_id = f"Private_{event.user_id}"
    elif public:
        session_id = event.get_session_id().replace(f"{event.user_id}", "Public")
    else:
        session_id = event.get_session_id()
    return session_id

clear_data = on_command("清除记忆", block=False, priority=1,permission=SUPERUSER | GROUP_OWNER | GROUP_ADMIN)
@clear_data.handle()
async def _():
    global session
    session = {}
    await clear_data.finish(MessageSegment.text("成功清除所有记忆！"), at_sender=True)