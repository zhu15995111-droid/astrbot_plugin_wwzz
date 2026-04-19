from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger,AstrBotConfig
from astrbot.core.utils.astrbot_path import get_astrbot_data_path
from pathlib import Path
import json
user_lottery_record_file = "lottery_record.json"     #用户抽奖记录



@register("helloworld", "YourName", "一个简单的 Hello World 插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context,config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        plugin_data_path = Path(get_astrbot_data_path()) / "plugin_data" / "astrbot_plugin_wwzz"
        self.user_lottery_record = plugin_data_path / user_lottery_record_file
        plugin_data_path.mkdir(parents=True, exist_ok=True)
        self.user_lottery_record.touch(exist_ok=True)

    def read_lottery_record(self) -> dict:
        ""
        with open(self.user_lottery_record, "r", encoding="utf-8") as f:
                return json.load(f)
        

    def save_lottery_record(self,data: dict):
        """保存抽奖记录"""
        with open(self.user_lottery_record, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    
    @filter.event_message_type(filter.EventMessageType.ALL)
    async def on_all_message(self, event: AstrMessageEvent):
        yield event.plain_result("收到了一条消息。")



    
    

    