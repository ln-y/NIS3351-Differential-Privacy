# NIS3351 数据库原理与安全 大作业展示

## Introduction

本仓库用于模拟加入差分隐私前后数据库在集合查询下抗差分攻击的能力。

本仓库实现了一个简单的系统，其可以添加/删除好友并查询当前好友的平均年龄和平均学积分。

该系统设计了两种数据库
* `NormalDB`: 普通的数据库
* `PrivacyDB`: 带有差分隐私机制的数据库
  
分别使用这两种数据库作为系统的后端，并在`attacker.py`中模拟进行差分攻击查看上述系统的抗攻击能力。

威胁建模：
假设攻击者知道所有人姓名，能够在系统中添加或删除任何好友

## Quick Start

首先安装环境依赖
```
pip install -r requirements.txt
```

初始时并没有数据文件，先运行`data_gen.py`生成一份数据文件
```
python data_gen.py
```

可以尝试运行系统并在命令中与之交互
```
python simulator.py # 这将启动基于`NormalDB`的系统
python simulator.py --privacy # 这将启动基于`PrivacyDB`的系统
```

运行预先设置好的攻击脚本对不同情况下的系统进行攻击
```
python attack.py
```

## Develop Guide

项目文件作用:
`config.py`: 定义了数据库系统中的部分超参数
`db_uitl.py`: 不同数据库的实现
`data_gen.py`: 用于生成随机的数据文件
`simulator.py`: 待攻击系统的主程序
`attack.py`: 攻击模拟脚本

attack.py的主函数中定义了模拟的过程，可以根据自己的需求自行修改。
config.py中定义了集合查询的最小数目和各项统计数据的隐私预算，可根据需求自行修改。