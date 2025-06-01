import json
import os
import random
import jieba

from responsesEvaluate import Evaluator
from Matcher.fuzzyMatcher import FuzzyMatcher
from Matcher.wordWeightMatcher import WordWeightMatcher
from Matcher.bm25Matcher import bestMatchingMatcher
from Matcher.KeywordMatcher import KeywordMatcher
from Matcher.matcher import Matcher


def main():
    matcherTesting("TF/IDF", removeStopWords=False)


def getMatcher(matcherType, removeStopWords=False):
    """
    回傳初始完畢的 Matcher

    Args:
        - matcherType:要使用哪種字串匹配方式
            - Fuzzy
            - WordWeight
        - sort:
            - a boolean value for fuzzy sorting match.
    """

    if matcherType == "WordWeight":
        return woreWeightMatch()
    elif matcherType == "Fuzzy":
        return fuzzyMatch(removeStopWords)
    elif matcherType == "bm25":
        return bm25()
    elif matcherType == "Vectorize":
        pass  # TODO
    elif matcherType == "DeepLearning":
        pass  # TODO
    elif matcherType == "TF/IDF":
        return TFIDFMatcher(removeStopWords)
    else:
        print("[Error]: Invailded type.")
        exit()


def TFIDFMatcher(removeStopWords=False):
    jieba.load_userdict("jieba_dictionary/ptt_dic.txt")
    tfidf_matcher = KeywordMatcher(segLib="jieba", removeStopWords=removeStopWords)
    tfidf_matcher.loadTitles(path="data/Titles.txt")
    tfidf_matcher.initialize()
    return tfidf_matcher


def matcherTesting(matcherType, removeStopWords=False):

    matcher = getMatcher(matcherType, removeStopWords)
    while True:
        query = input("隨便說些什麼吧: ")
        title, index = matcher.match(query)
        sim = matcher.getSimilarity()
        print("最為相似的標題是 %s ，相似度為 %d " % (title, sim))

        res = json.load(
            open(
                os.path.join("data/processed/reply/", str(int(index / 1000)) + ".json"),
                "r",
                encoding="utf-8",
            )
        )
        targetId = index % 1000
        # randomId = random.randrange(0,len(res[targetId]))

        evaluator = Evaluator()
        candiates = evaluator.getBestResponse(
            responses=res[targetId], topk=5, debugMode=False
        )
        print("以下是相似度前 5 高的回應")
        for candiate in candiates:
            print("%s %f" % (candiate[0], candiate[1]))


def woreWeightMatch():

    weightMatcher = WordWeightMatcher(segLib="jieba")
    weightMatcher.loadTitles(path="data/Titles.txt")
    weightMatcher.initialize()
    return weightMatcher


def fuzzyMatch(cleansw=False):

    fuzzyMatcher = FuzzyMatcher(segLib="jieba", removeStopWords=cleansw)
    fuzzyMatcher.loadTitles(path="data/Titles.txt")

    if cleansw:
        fuzzyMatcher.TitlesSegmentation(cleansw)
        fuzzyMatcher.joinTitles()

    return fuzzyMatcher

    # load a custom user dictionary.
    # fuzzyMatcher.TaibaCustomSetting(usr_dict="jieba_dictionary/ptt_dic.txt")

    # load stopwords
    # fuzzyMatcher.loadStopWords(path="data/stopwords/chinese_sw.txt")
    # fuzzyMatcher.loadStopWords(path="data/stopwords/ptt_words.txt")
    # fuzzyMatcher.loadStopWords(path="data/stopwords/specialMarks.txt")


def bm25():

    bm25Matcher = bestMatchingMatcher()
    bm25Matcher.loadTitles(path="data/Titles.txt")
    bm25Matcher.initialize()
    return bm25Matcher


if __name__ == "__main__":
    main()
