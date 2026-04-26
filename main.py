from turtle import pen

from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger,AstrBotConfig
from astrbot.core.utils.astrbot_path import get_astrbot_data_path
from pathlib import Path
import json
import os
import random
from datetime import date

from .help_txt import LOTTERY_HELP_TMPL


user_lottery_record_file = "lottery_record.json"     #用户抽奖记录(今天是否抽了)



@register("helloworld", "YourName", "一个简单的 Hello World 插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context,config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        plugin_data_path = Path(get_astrbot_data_path()) / "plugin_data" / "astrbot_plugin_wwzz"
        self.user_lottery_record = plugin_data_path / user_lottery_record_file
        plugin_data_path.mkdir(parents=True, exist_ok=True)
        self.user_lottery_record.touch(exist_ok=True)

        self.user_id = None#初始化为空
        self.group_id = None#初始化为空

    def read_lottery_record(self) -> dict:
        """限制一天抽一次,读取用户抽奖时间"""
        if os.path.getsize(self.user_lottery_record) == 0:
            return {}
        with open(self.user_lottery_record, "r", encoding="utf-8") as f:
            return json.load(f)
        

    def save_lottery_record(self,data: dict):
        """保存抽奖时间的记录"""
        with open(self.user_lottery_record, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def lottery_config(self,target_prize: str|None = ""):
        self.prize_list = [] #奖品: {数量+概率}
        for key in self.config["prize_config"]:
            if key=="normal_prize":
                for prize_item in list(self.config["prize_config"][key]):
                    prize, quantity, probability = prize_item.split(":")
                    prob = int(probability)
                    
                    if target_prize is not None and prize == target_prize:
                        new_quantity = int(quantity) - 1
                        quantity = str(new_quantity)
                        prize_index = self.config["prize_config"][key].index(prize_item)
                        if int(quantity) <= 0:
                            self.config["prize_config"][key].pop(prize_index)
                        else:
                            new_prize_str = f"{prize}:{quantity}:{probability}"
                            self.config["prize_config"][key][prize_index] = new_prize_str
                        self.config.save_config()
                    
                    if int(quantity) > 0:
                        self.prize_list.append({prize: {"quantity": quantity, "probability": probability}})

            elif key=="special_prize":
                pass
                
            elif key=="group_prize":
                for prize_item in list(self.config["prize_config"][key]):
                    groupid,prize, quantity, probability = prize_item.split(":")
                    prob = int(probability)
                    if groupid == self.group_id:
                        if target_prize is not None and prize == target_prize:
                            new_quantity = int(quantity) - 1
                            quantity = str(new_quantity)
                            prize_index = self.config["prize_config"][key].index(prize_item)
                            if int(quantity) <= 0:
                                self.config["prize_config"][key].pop(prize_index)
                            else:
                                new_prize_str = f"{groupid}:{prize}:{quantity}:{probability}"
                                self.config["prize_config"][key][prize_index] = new_prize_str
                            self.config.save_config()
                        
                        if int(quantity) > 0:
                            self.prize_list.append({prize: {"quantity": quantity, "probability": probability}})

        
        self.prizes = []
        self.weights = []
        if not self.prize_list:
            return
        for item in self.prize_list:
            name = next(iter(item.keys()))
            prob = int(item[name]["probability"])
            self.prizes.append(name)
            self.weights.append(prob)
        weights_sum = sum(self.weights)
        if 0 < weights_sum < 100:
            self.prizes.append("谢谢参与")
            self.weights.append(100 - weights_sum)

    def draw_prize(self):
        if not self.prizes:
            return "谢谢参与"
        return random.choices(self.prizes, weights=self.weights, k=1)[0]
    
    

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def on_all_message(self, event: AstrMessageEvent):
        group_id = event.get_group_id()
        user_id=event.get_sender_id()
        lottery_record = self.read_lottery_record()
        today = date.today().strftime("%Y/%m/%d")

        if user_id in lottery_record and lottery_record[user_id] == today:
            return
        if self.group_id!=group_id:
            self.group_id=group_id
            self.lottery_config()
        print(self.weights)
        user_prize=self.draw_prize()
        lottery_record[user_id] = today
        self.save_lottery_record(lottery_record)

        if user_prize == "谢谢参与":
            return
        self.lottery_config(target_prize=user_prize)
        yield event.plain_result(f"{today}\n恭喜{user_id}抽中了{user_prize}!")

        
    @filter.command("抽奖帮助")
    async def lottery_help(self, event: AstrMessageEvent):
        # 渲染模板并生成图片
        url = await self.html_render(LOTTERY_HELP_TMPL, {})
        yield event.image_result(url)

    
    

    