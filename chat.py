import json
import os
import random
import logging

import match

from responsesEvaluate import Evaluator


def main():

    chatter = GossipBot()
    chatter.randomTalks(num=1000)
    chatter.chatTime()


class GossipBot(object):
    """
    八卦板聊天機器人 ob'_'ov
    """

    def __init__(self, match_type="TF/IDF"):
        self.matcher = match.getMatcher(match_type)
        self.evaluator = Evaluator()
        self.testSegment()
        self.defaultResponse = ["你在說什麼呢？", "我不太明白你的意思"]

    def testSegment(self):
        logging.info("測試斷詞模塊中")
        try:
            self.matcher.wordSegmentation("測試一下斷詞")
            logging.info("測試成功")
        except Exception as e:
            logging.info(repr(e))
            logging.info("模塊載入失敗，請確認data與字典齊全")

    def chatTime(self):
        print("MianBot: 您好，我是你的老朋友眠寶，讓我們來聊聊八卦吧 o_o ")
        while True:
            query = input("User: ")
            print("MianBot: " + self.getResponse(query))

    def getResponse(self, query, threshold=50):

        title, index = self.matcher.match(query)
        sim = self.matcher.getSimilarity()
        if sim < threshold:
            # 如果相似度低於閾值，則回應預設內容
            return random.choice(self.defaultResponse)
        else:
            res = json.load(
                open(
                    os.path.join(
                        "data/processed/reply/", str(int(index / 1000)) + ".json"
                    ),
                    "r",
                    encoding="utf-8",
                )
            )
            targetId = index % 1000
            if not res[targetId]:
                return random.choice(self.defaultResponse)
            candiates = self.evaluator.getBestResponse(res[targetId], topk=3)
            reply = self.randomPick(candiates)
            return reply

    def randomPick(self, answers):
        try:
            answer = random.choice(answers)[0]
        except:
            answer = "內容可能含有不當詞彙，無法回應"
        return answer

    def randomTalks(self, num=100):
        with open("data/Titles.txt", "r", encoding="utf-8") as data:
            titles = [line.strip("\n") for line in data]
        for _ in range(num):
            query = random.choice(titles)
            print("User: " + query)
            print("MianBot: " + self.getResponse(query) + "\n")


if __name__ == "__main__":
    main()
