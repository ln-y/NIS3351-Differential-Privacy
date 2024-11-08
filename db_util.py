# The file simulates two database offer set query
#  `NormalDB` : database without Differential Privacy
#  `PrivacyDB` : database with Differential Privacy

import pandas as pd
import numpy as np

from config import min_set_query_num, age_epsilon, score_epsilon

class NormalDB:
    def __init__(self, db_file : str):
        self.db = pd.read_csv(db_file)

    def query(self, query : list[str]):
        if len(query) < min_set_query_num:
            print(f"at least use {min_set_query_num} people in set query, but now is {len(query)}")
            return -1., -1.
        df_out = self.db[self.db['name'].isin(query)]
        return (df_out["age"].mean(), df_out["score"].mean())

    def get_all_people(self):
        return self.db['name'].tolist()


class PrivacyDB:
    def __init__(self, db_file : str):
        self.db = pd.read_csv(db_file)
        self.age_epsilon = age_epsilon
        self.score_epsilon = score_epsilon

    def query(self, query : list[str]):
        if len(query) < min_set_query_num:
            print(f"at least use {min_set_query_num} people in set query, but now is {len(query)}")
            return -1., -1.
        sensitivity = 1 / len(query)
        df_out = self.db[self.db['name'].isin(query)]
        # 计算拉普拉斯分布的尺度参数
        age_scale = sensitivity / self.age_epsilon
        score_scale = sensitivity / self.score_epsilon

        return (df_out["age"].mean() + np.random.laplace(loc=0, scale=age_scale), df_out["score"].mean() + np.random.laplace(loc=0, scale=score_scale))

    def get_all_people(self):
        return self.db['name'].tolist()