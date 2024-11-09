# entry of taregt system
import random
import argparse

from db_util import NormalDB, PrivacyDB
from config import min_set_query_num

class Simulator:
    def __init__(self, db: NormalDB):
        self.db = db
        self.all_people = self.db.get_all_people()
        random.seed(42)
        self.friends = random.sample(self.all_people, min_set_query_num)

    def run(self):
        print('='*20,"Weclome to 学在交大 system",'='*20)
        print('1. 查询好友列表 Usage: 1')
        print('2. 添加好友 Usage: 2 <name>')
        print('3. 删除好友 Usage: 3 <name>')
        print('4. 查看好友信息 Usage: 4')
        print('5. 退出')
        while 1:
            command = self.bash_info()
            return_code = self.run_bash(command)
            if return_code:
                break
        
    def bash_info(self):
        return input('>>>')
    
    def show_friends(self):
        info = '  '.join(self.friends)
        print(f"好友列表:\n{info}")

    def add_friend(self, friend_name: str):
        if friend_name not in self.all_people:
            print(f'{friend_name} 不存在')
            return
        self.friends.append(friend_name)
    
    def del_friend(self, friend_name: str):
        if friend_name not in self.friends:
            print(f'{friend_name} 不在好友列表中')
            return
        self.friends.remove(friend_name)
    
    def run_bash(self, command_str : str):
        args_lst = command_str.split(' ')
        if not len(args_lst):
            print('command error')
        if args_lst[0] == '1':
            self.show_friends()
        elif args_lst[0] == '2':
            if len(args_lst)!= 2:
                print('command error, Usage: 2 <name>')
                return 0
            self.add_friend(args_lst[1])
        elif args_lst[0] == '3':
            if len(args_lst)!= 2:
                print('command error, Usage: 3 <name>')
                return 0
            self.del_friend(args_lst[1])
        elif args_lst[0] == '4':
            query_data = self.db.query(self.friends)
            print(f"查询结果:\n平均年龄: {query_data[0]:.2f}\n平均成绩: {query_data[1]:.2f}")
        elif args_lst[0] == '5':
            return 1
        else:
            print(f'command {args_lst[0]} not found')
        return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--privacy', action='store_true', default= False)
    args = parser.parse_args()

    if args.privacy:
        sim = Simulator(PrivacyDB("data.csv"))
    else:
        sim = Simulator(NormalDB("data.csv"))
    sim.run()