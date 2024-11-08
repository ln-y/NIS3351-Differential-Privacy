# This file used to generate data for target system
import pandas as pd
import random
from faker import Faker

res_lst = []
gen_data_num = 100

fake = Faker()
use_name = set()

for i in range(gen_data_num):
    name = fake.first_name()
    while name in use_name:
        name = fake.first_name()
    res_lst.append([name, int(18+ 5*random.random()), 60 + 40*random.random()])
    use_name.add(name)

df = pd.DataFrame(res_lst, columns=['name', 'age', 'score'])
df.to_csv('data.csv', index=False)