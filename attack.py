# This file simulate the attack process
import subprocess
import re
import pandas as pd
import time
import random
import numpy as np

from matplotlib import pyplot as plt

from config import min_set_query_num

default_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

def read_to_end(stream , suffix: str):
    length = len(suffix)
    output_lst = []
    while True:
        chari = stream.read(1)
        output_lst.append(chari)
        if ''.join(output_lst[-length:]) == suffix:
            break
    return ''.join(output_lst)

class SimulatorApi:
    def __init__(self, args : 'str| None' = None) -> None:
        if args :
            self.process = subprocess.Popen(['python','simulator.py', args], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        else:
            self.process = subprocess.Popen(['python','simulator.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)

        output = read_to_end(self.process.stdout, '>>>')
        print(output, end='')

        self.total_command = 0

    def run_command(self, chars):
        self.process.stdin.write(chars + '\n')
        self.process.stdin.flush()
        output = chars + '\n' + read_to_end(self.process.stdout, '>>>')
        print(output, end='')
        self.total_command += 1
        return output
    
    def quit(self):
        self.process.stdin.write('5\n')
        self.process.stdin.flush()
        self.process.stdin.close()
        self.process.wait()
        print("5")

class Attacker:
    def __init__(self, api: SimulatorApi, all_names: list[str]):
        self.api = api
        self.all_names = all_names

    def get_now_friends(self)-> list[str]:
        return self.api.run_command('1').split('\n')[-2].split()
    
    def add_friends(self, name):
        self.api.run_command(f'2 {name}')
    
    def del_friends(self, name: str):
        self.api.run_command(f'3 {name}')
    
    def query(self):
        use_re = re.compile(r'平均年龄: ([\d\.]+)\n平均成绩: ([\d\.]+)')
        res = self.api.run_command('4')
        match = use_re.findall(res)[0]
        return float(match[0]), float(match[1])
    
    def differential_attack(self, num : int, query_old: tuple[float, float], query_new: tuple[float, float]):
        '''
        基于查询结果进行差分攻击， `query_old`为好友数为num时的查询结果， `query_new`为好友数为num+1时的查询结果
        '''
        age_diff = query_new[0]*(num+1) - query_old[0]*num
        score_diff = query_new[1]*(num+1) - query_old[1]*num
        return age_diff, score_diff

    def queue_attack(self, echoes = 1):
        '''
        攻击方法：
        攻击者运行一个滑动窗口, 并维护2个包含所有姓名的队列A,B, 满足初始时攻击者的好友恰为队列中的前10个元素。

        运行下述算法进行攻击：
        1. 将所有的姓名排成一个队列,初始时攻击者的好友恰为队列中的前10个元素。将这个队列复制一份,得到两个队列A,B
        2. 对B队列进行10次出队操作
        3. 若B队列非空,则进行一次出队操作获取队首元素,添加其为好友,进行一次集合查询
        3. 对A队列进行一次出队操作获取队首元素,删除此好友,进行一次集合查询
        4. 重复步骤2-3,直到B队列为空
        '''
        t_bgein = time.time()
        random.seed(42)
        for i in range(echoes):
            # 初始队列生成
            init_friend = self.get_now_friends()
            queue_B = [i for i in self.all_names if i not in init_friend]
            random.shuffle(queue_B)
            queue_A = list(queue_B) + init_friend

            query_res_lst = []
            age_guess_dic: dict[str, list[int]] = {k: [] for k in self.all_names}
            score_guess_dic: dict[str, list[float]] = {k: [] for k in self.all_names}
            
            # 攻击
            query_res_lst.append(self.query())

            while queue_B:
                new_friend = queue_B.pop()
                self.add_friends(new_friend)
                query_res_lst.append(self.query())
                age_diff, score_diff = self.differential_attack(min_set_query_num , query_res_lst[-2], query_res_lst[-1])
                age_guess_dic[new_friend].append(age_diff)
                score_guess_dic[new_friend].append(score_diff)

                old_friend = queue_A.pop()
                self.del_friends(old_friend)
                query_res_lst.append(self.query())
                age_diff, score_diff = self.differential_attack(min_set_query_num , query_res_lst[-1], query_res_lst[-2])
                age_guess_dic[old_friend].append(age_diff)
                score_guess_dic[old_friend].append(score_diff)

        # 生成攻击结果
        res_lst = []
        for name in self.all_names:
            age_lst = age_guess_dic[name]
            score_lst = score_guess_dic[name]
            res_lst.append((name, round(sum(age_lst)/len(age_lst)), sum(score_lst)/len(score_lst)))
        res_df = pd.DataFrame(res_lst, columns=['name', 'age', 'score'])

        t_end = time.time()
        print(f"\nechoes={echoes} Attack finished, cost {t_end - t_bgein:.3f} s,use {self.api.total_command} operations\nAttack result:\n{res_df}")
        return res_df, query_res_lst
    
def evalute(real_df: pd.DataFrame, res_df_dic: dict[str, pd.DataFrame]):
    age_error_dic = {}
    score_error_dic = {}
    for key, res_df in res_df_dic.items():
        age_error_dic[key] = []
        score_error_dic[key] = []
        age_err_num = 0
        for index, row in res_df.iterrows():
            row_real = real_df.iloc[index, :]
            age_error_dic[key].append(abs(row['age'] - row_real['age']))
            age_err_num += 1 if row['age'] != row_real['age'] else 0
            score_error_dic[key].append(abs(row['score'] - row_real['score']))
        print(f"{key}:\n年龄正确率: {100* (1 - age_err_num/len(res_df)):.2f} %, 平均成绩误差: {sum(score_error_dic[key])/len(res_df):.3f}")
    for key in res_df_dic.keys():
        plt.plot(sorted(age_error_dic[key]), label=f'age diff ({key})')
        plt.plot(sorted(score_error_dic[key]), label=f'score diff ({key})')
    plt.legend()
    plt.show()

def query_diff(real_query : list[tuple[float, float]], dp_query: list[tuple[float, float]], title: str):
    real_age = np.array([real[0] for real in real_query])
    real_score = np.array([real[1] for real in real_query])
    dp_age = np.array([dp[0] for dp in dp_query])
    dp_score = np.array([dp[1] for dp in dp_query])

    sort_index = np.argsort(real_age)
    real_age = real_age[sort_index]
    dp_age = dp_age[sort_index]

    sort_index = np.argsort(real_score)
    real_score = real_score[sort_index]
    dp_score = dp_score[sort_index]

    fig, ax1 = plt.subplots()
    ax1.plot(real_age, label='real age', color = default_colors[0])
    ax1.plot(dp_age, label='dp age', color = default_colors[1])
    ax1.set_ylabel('age')
    ax1.set_ylim(15,30)
    ax2 = ax1.twinx()
    ax2.plot(real_score, label='real score', color = default_colors[2])
    ax2.plot(dp_score, label='dp score', color = default_colors[3])
    ax2.set_ylabel('score')
    plt.legend()
    plt.title(title)
    plt.show()

if __name__ == '__main__':
    df = pd.read_csv('data.csv')

    api = SimulatorApi('')
    attacker = Attacker(api, df["name"].tolist())
    input("Press Enter to continue (attack NormalDB with echoes=1)...")
    res_df, real_query_res_lst = attacker.queue_attack()
    input("Press Enter to continue (attack NormalDB with echoes=10)...")
    res_df2, real_query_res_lst2 = attacker.queue_attack(echoes= 10)
    evalute(df, {"echoes=1": res_df, "echoes=10": res_df2})
    api.quit()

    api = SimulatorApi('--privacy')
    attacker = Attacker(api, df["name"].tolist())
    input("Press Enter to continue (attack PrivacyDB with echoes=1)...")
    res_df, dp_query_res_lst = attacker.queue_attack()
    input("Press Enter to continue (attack PrivacyDB with echoes=10)...")
    res_df2, dp_query_res_lst2 = attacker.queue_attack(echoes= 10)
    evalute(df, {"echoes=1": res_df, "echoes=10": res_df2})
    api.quit()

    # show query diff
    query_diff(real_query_res_lst, dp_query_res_lst, "echoes=1")
    query_diff(real_query_res_lst2, dp_query_res_lst2, "echoes=10")
    


