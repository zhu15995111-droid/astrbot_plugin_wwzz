from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger,AstrBotConfig
from astrbot.core.utils.astrbot_path import get_astrbot_data_path
from pathlib import Path
import json
from datetime import date


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

        self.lottery_config(user_id="",group_id="")


    def read_lottery_record(self) -> dict:
        """限制一天抽一次,读取用户抽奖时间"""
        with open(self.user_lottery_record, "r", encoding="utf-8") as f:
                return json.load(f)
        

    def save_lottery_record(self,data: dict):
        """保存抽奖时间的记录"""
        with open(self.user_lottery_record, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def lottery_config(self,user_id:str,group_id:str,target_prize: str|None = "5"):
        prize_list=[]
        for key in self.config["prize_config"]:
            if key=="normal_prize":
                for prize_item in self.config["prize_config"][key]:
                    prize, quantity, probability = prize_item.split(":")
                    if target_prize is not None and prize == target_prize:
                        new_quantity = int(quantity) - 1
                        quantity = str(new_quantity)
                        new_prize_str = f"{prize}:{quantity}:{probability}"
                        prize_index = self.config["prize_config"][key].index(prize_item)
                        self.config["prize_config"][key][prize_index] = new_prize_str
                    prize_list.append({"prize": prize,"quantity": quantity,"probability": probability})
            elif key=="special_prize":
                pass
            elif key=="group_prize":
                pass
        print(prize_list)
        
        
    
    @filter.event_message_type(filter.EventMessageType.ALL)
    async def on_all_message(self, event: AstrMessageEvent):
        group_id = event.get_group_id()
        user_id=event.get_sender_id()
        lottery_record = self.read_lottery_record()
        today = date.today().strftime("%Y/%m/%d")

        if user_id in lottery_record and lottery_record[user_id] == today:
            return


        



    
    

    