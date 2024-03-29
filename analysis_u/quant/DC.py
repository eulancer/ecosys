# -*- coding:utf8 -*-
import numpy as np
import pymysql

# 机器学习暂时找不到应用场景
import config


class data_collect(object):

    def __init__(self, in_code, start_dt, end_dt):
        ans = self.collect_DATA(in_code, start_dt, end_dt)

    def collect_DATA(self, in_code, start_dt, end_dt):
        # 建立数据库连接，获取日线基础行情(开盘价，收盘价，最高价，最低价，成交量，成交额)
        db = pymysql.connect(host=config.host, user=config.user, passwd='', db=config.db, charset=config.unicode)
        cursor = db.cursor()
        sql_done_set = "SELECT * FROM stock_his_data where ts_code = '%s' and trade_date >= '%s' and trade_date<= '%s' order by trade_date asc" % (
            in_code, start_dt, end_dt)

        cursor.execute(sql_done_set)
        done_set = cursor.fetchall()
        # print("DC 开始采集数据" + str(done_set))
        # print()
        if len(done_set) == 0:
            raise Exception
        # print(len(done_set))
        self.date_seq = []
        self.open_list = []
        self.close_list = []
        self.high_list = []
        self.low_list = []
        self.vol_list = []
        self.amount_list = []
        for i in range(len(done_set)):
            self.date_seq.append(done_set[i][0])
            self.open_list.append(float(done_set[i][3]))
            self.high_list.append(float(done_set[i][4]))
            self.low_list.append(float(done_set[i][5]))
            self.close_list.append(float(done_set[i][6]))
            self.vol_list.append(float(done_set[i][10]))
            self.amount_list.append(float(done_set[i][11]))
        cursor.close()
        db.close()
        # print("self.close_list" + str(self.close_list))
        # 将日线行情整合为训练集(其中self.train是输入集，self.target是输出集，self.test_case是end_dt那天的单条测试输入)
        self.data_train = []
        self.data_target = []
        self.data_target_onehot = []
        self.cnt_pos = 0
        self.test_case = []
        #print("self.data_train" + str(self.data_train))

        for i in range(1, len(self.close_list)):
            train = [self.open_list[i - 1], self.close_list[i - 1], self.high_list[i - 1], self.low_list[i - 1],
                     self.vol_list[i - 1], self.amount_list[i - 1]]
            self.data_train.append(np.array(train))
            if self.close_list[i] / self.close_list[i - 1] > 1.0:
                self.data_target.append(float(1.00))
                self.data_target_onehot.append([1, 0, 0])
            else:
                self.data_target.append(float(0.00))
                self.data_target_onehot.append([0, 1, 0])
        # print("self.data_train" + str(self.data_train))
        con_len=[]
        for x in self.data_target:
            if x == 1.00:
                con_len.append(x)
        self.cnt_pos=len(con_len)
        self.test_case = np.array(
            [self.open_list[-1], self.close_list[-1], self.high_list[-1], self.low_list[-1], self.vol_list[-1],
             self.amount_list[-1]])
        self.data_train = np.array(self.data_train)
        self.data_target = np.array(self.data_target)
        return 1
