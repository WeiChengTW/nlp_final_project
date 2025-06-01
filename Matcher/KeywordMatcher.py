from .matcher import Matcher
import math


class KeywordMatcher(Matcher):
    """
    基於 TF-IDF 比較短語相似度
    """

    def __init__(self, segLib="jieba", removeStopWords=True):
        super().__init__(segLib)
        self.cleanStopWords = removeStopWords
        self.tf = []  # 每個短語的 term frequency 字典
        self.df = {}  # document frequency
        self.idf = {}  # inverse document frequency
        self.tfidf = []  # 每個短語的 tf-idf 向量
        self.D = 0  # 短語總數

        if removeStopWords:
            self.loadStopWords("data/stopwords/chinese_sw.txt")
            self.loadStopWords("data/stopwords/specialMarks.txt")

    def initialize(self):
        assert len(self.titles) > 0, "請先載入短語表"
        self.TitlesSegmentation()
        self.D = len(self.segTitles)
        self._calculate_tf_idf()

    def _calculate_tf_idf(self):
        # 計算 tf
        for seg_title in self.segTitles:
            tf_dict = {}
            for word in seg_title:
                tf_dict[word] = tf_dict.get(word, 0) + 1
            self.tf.append(tf_dict)
            for word in tf_dict:
                self.df[word] = self.df.get(word, 0) + 1

        # 計算 idf
        for word, df in self.df.items():
            self.idf[word] = math.log((self.D + 1) / (df + 1)) + 1

        # 計算 tf-idf 向量
        for tf_dict in self.tf:
            tfidf_vec = {}
            for word, tf in tf_dict.items():
                tfidf_vec[word] = tf * self.idf[word]
            self.tfidf.append(tfidf_vec)

    def _vectorize(self, seg_query):
        tf_query = {}
        for word in seg_query:
            tf_query[word] = tf_query.get(word, 0) + 1
        tfidf_query = {}
        for word, tf in tf_query.items():
            idf = self.idf.get(word, math.log((self.D + 1) / 1) + 1)
            tfidf_query[word] = tf * idf
        return tfidf_query

    def _cosine_similarity(self, vec1, vec2):
        # vec1, vec2: dict
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])
        sum1 = sum([v**2 for v in vec1.values()])
        sum2 = sum([v**2 for v in vec2.values()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)
        if not denominator:
            return 0.0
        else:
            return numerator / denominator

    def match(self, query):
        seg_query = self.wordSegmentation(query)
        tfidf_query = self._vectorize(seg_query)
        max_sim = -1
        target_idx = -1

        for idx, tfidf_vec in enumerate(self.tfidf):
            sim = self._cosine_similarity(tfidf_query, tfidf_vec)
            if sim > max_sim:
                max_sim = sim
                target_idx = idx

        if target_idx == -1:
            return "", -1

        target = "".join(self.segTitles[target_idx])
        self.similarity = max_sim * 100  # 百分比
        return target, target_idx
