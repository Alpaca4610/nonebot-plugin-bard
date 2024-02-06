import nonebot
import asyncio
import requests
import io

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message, MessageSegment, PrivateMessageEvent, MessageEvent, helpers
from nonebot.plugin import PluginMetadata

from .config import Config, ConfigError
from bardapi import Bard,BardCookies

__plugin_meta__ = PluginMetadata(
    name="谷歌Bard聊天",
    description="Nonebot框架下的谷歌Bard聊天插件，支持联网搜索和图片识别",
    usage=
    '''
    bard 发起对话
    i识图+图片 调用bard的多模态识别能力识图
    ''',
    config= Config,
    extra={},
    type="application",
    homepage="https://github.com/Alpaca4610/nonebot-plugin-bard",
    supported_adapters={"~onebot.v11"}
)

# 配置导入
plugin_config = Config.parse_obj(nonebot.get_driver().config.dict())

if not plugin_config.bard_token:
    raise ConfigError("请设置bard的cookies")

token = plugin_config.bard_token

if not token:
    raise ConfigError("请设置Bard的cookies!")

public = plugin_config.bard_group_public
session = {}

proxies = {
    'http': plugin_config.bard_proxy,
    'https': plugin_config.bard_proxy
} if plugin_config.bard_proxy else None

cookie_dict = {
    "__Secure-1PSID": token,
    "__Secure-1PSIDTS": plugin_config.bard_token1,
    "__Secure-1PSIDCC": plugin_config.bard_token2
} if plugin_config.bard_token1 and plugin_config.bard_token2 else None

if cookie_dict:
    bard = BardCookies(cookie_dict=cookie_dict, proxies=proxies,language='chinese (simplified)')
else:
    bard = Bard(token=token, proxies=proxies,language='chinese (simplified)')

chat_request = on_command("bard", block=False, priority=1)

@chat_request.handle()
async def _(event: MessageEvent, msg: Message = CommandArg()):
    if isinstance(event, PrivateMessageEvent) and not plugin_config.bard_enable_private_chat:
        chat_request.finish("对不起，私聊暂不支持此功能。")
    img_url = helpers.extract_image_urls(event.message)
    content = msg.extract_plain_text()
    if content == "" or content is None:
        await chat_request.finish(MessageSegment.text("内容不能为空！"))
    await chat_request.send(MessageSegment.text("Bard正在思考中......"))
    loop =  asyncio.get_event_loop()
    if not img_url:
        try:
            res = await loop.run_in_executor(None, get_res ,content)
        except Exception as error:
            await chat_request.finish(str(error))
        await chat_request.finish(MessageSegment.text(res), at_sender=True)
    else:
        try:
            res = await loop.run_in_executor(None, img_process ,content, img_url[0])
        except Exception as error:
            await chat_request.finish(str(error))
        await chat_request.finish(MessageSegment.text(res), at_sender=True)

def get_res(content):
    res = bard.get_answer(content)['content']
    return res

def img_process(content,url):
    # bard = Bard(token=token,language='chinese (simplified)')
    print(url)
    response = requests.get(url)
    data_stream = response.content
    bard_answer = bard.ask_about_image(content, data_stream)
    res = bard_answer['content']
    return res