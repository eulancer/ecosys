from sklearn import svm
import pymysql.cursors
import datetime
import DC

import config
from collector.tushare_util import get_pro_client


# 【模型评估】通过回测+推进式建模的方式对模型进行评估，主要计算查准率Precision，查全率Recall，F1分值，并存入结果表。
# para_window 回测窗口长度
# para_dc_window 数据预处理所需的时间窗长度

def model_eva(stock, state_dt, para_window, para_dc_window):
    # 建立数据库连接，设置tushare token
    db = pymysql.connect(host=config.host, user=config.user, passwd='', db=config.db, charset=config.unicode)
    cursor = db.cursor()
    pro = get_pro_client()

    # 建评估时间序列, para_window参数代表回测窗口长度
    model_test_date_start = (
            datetime.datetime.strptime(state_dt, '%Y%m%d') - datetime.timedelta(days=para_window)).strftime(
        '%Y%m%d')
    model_test_date_end = state_dt
    df = pro.trade_cal(exchange_id='', is_open=1, start_date=model_test_date_start, end_date=model_test_date_end)
    date_temp = list(df.iloc[:, 1])
    model_test_date_seq = [(datetime.datetime.strptime(x, "%Y%m%d")).strftime('%Y%m%d') for x in date_temp]

    # 清空评估用的中间表model_ev_mid
    sql_truncate_model_test = 'truncate table model_ev_mid'
    cursor.execute(sql_truncate_model_test)
    db.commit()
    return_flag = 0
    print("清空评估用的中间表")

    # 开始回测，其中para_dc_window参数代表建模时数据预处理所需的时间窗长度
    for d in range(len(model_test_date_seq)):
        model_test_new_start = (datetime.datetime.strptime(model_test_date_seq[d], '%Y%m%d') - datetime.timedelta(
            days=para_dc_window)).strftime('%Y%m%d')
        print("model_test_new_start" + str(model_test_new_start))
        model_test_new_end = model_test_date_seq[d]
        print("model_test_new_end" + str(model_test_new_end))
        try:
            dc = DC.data_collect(stock, model_test_new_start, model_test_new_end)
            print("set(dc.data_target)"+str(set(dc.data_target)))
            if len(set(dc.data_target)) <= 1:
                continue
        except Exception as exp:
            print("DC 没有数据，就没法更新ev_mid表")
            return_flag = 1
            break
        train = dc.data_train
        target = dc.data_target
        test_case = [dc.test_case]
        #print("train"+str(train))

        model = svm.SVC()  # 建模
        model.fit(train, target)  # 训练
        ans2 = model.predict(test_case)  # 预测

        # 将预测结果插入到中间表
        sql_insert = "insert into model_ev_mid(trade_date,ts_code,resu_predict)values('%s','%s','%.2f')" % (
            model_test_new_end, stock, float(ans2[0]))
        cursor.execute(sql_insert)
        db.commit()
    if return_flag == 1:
        acc = recall = acc_neg = f1 = 0
        return -1
    else:
        # 在中间表中刷真实值
        for i in range(len(model_test_date_seq)):
            sql_select = "select * from stock_his_data a where a.ts_code = '%s' and a.trade_date >= '%s' order by a.trade_date asc limit 2" % (
                stock, model_test_date_seq[i])
            cursor.execute(sql_select)
            done_set2 = cursor.fetchall()
            if len(done_set2) <= 1:
                break
            resu = 0
            if float(done_set2[1][6]) / float(done_set2[0][6]) > 1.00:
                resu = 1
            sql_update = "update model_ev_mid w set w.resu_real = '%.2f' where w.trade_date = '%s' and w.ts_code = '%s'" % (
                resu, model_test_date_seq[i], stock)
            cursor.execute(sql_update)
            db.commit()
        # 计算查全率
        sql_resu_recall_son = "select count(*) from model_ev_mid a where a.resu_real is not null and a.resu_predict = 1 and a.resu_real = 1"
        cursor.execute(sql_resu_recall_son)
        recall_son = cursor.fetchall()[0][0]
        sql_resu_recall_mon = "select count(*) from model_ev_mid a where a.resu_real is not null and a.resu_real = 1"
        cursor.execute(sql_resu_recall_mon)
        recall_mon = cursor.fetchall()[0][0]
        if recall_mon == 0:
            acc = recall = acc_neg = f1 = 0
        else:
            recall = recall_son / recall_mon
        # 计算查准率
        sql_resu_acc_son = "select count(*) from model_ev_mid a where a.resu_real is not null and a.resu_predict = 1 and a.resu_real = 1"
        cursor.execute(sql_resu_acc_son)
        acc_son = cursor.fetchall()[0][0]
        sql_resu_acc_mon = "select count(*) from model_ev_mid a where a.resu_real is not null and a.resu_predict = 1"
        cursor.execute(sql_resu_acc_mon)
        acc_mon = cursor.fetchall()[0][0]
        if acc_mon == 0:
            acc = recall = acc_neg = f1 = 0
        else:
            acc = acc_son / acc_mon
        # 计算查准率(负样本)
        sql_resu_acc_neg_son = "select count(*) from model_ev_mid a where a.resu_real is not null and a.resu_predict = -1 and a.resu_real = -1"
        cursor.execute(sql_resu_acc_neg_son)
        acc_neg_son = cursor.fetchall()[0][0]
        sql_resu_acc_neg_mon = "select count(*) from model_ev_mid a where a.resu_real is not null and a.resu_predict = -1"
        cursor.execute(sql_resu_acc_neg_mon)
        acc_neg_mon = cursor.fetchall()[0][0]
        if acc_neg_mon == 0:
            acc_neg_mon = -1
            acc_neg = -1
        else:
            acc_neg = acc_neg_son / acc_neg_mon
        # 计算 F1 分值
        if acc + recall == 0:
            acc = recall = acc_neg = f1 = 0
        else:
            f1 = (2 * acc * recall) / (acc + recall)
    sql_predict = "select resu_predict from model_ev_mid a where a.trade_date = '%s'" % (model_test_date_seq[-1])
    cursor.execute(sql_predict)
    done_predict = cursor.fetchall()
    predict = 0
    if len(done_predict) != 0:
        predict = int(done_predict[0][0])
    # 将评估结果存入结果表model_ev_resu中
    sql_final_insert = "insert into model_ev_resu(trade_date,ts_code,acc,recall,f1,acc_neg,bz,predict)values('%s','%s','%.4f','%.4f','%.4f','%.4f','%s','%s')" % (
        state_dt, stock, acc, recall, f1, acc_neg, 'svm', str(predict))
    cursor.execute(sql_final_insert)
    db.commit()
    db.close()
    print("写结果")
    print(str(state_dt) + '   Precision : ' + str(acc) + '   Recall : ' + str(recall) + '   F1 : ' + str(
        f1) + '   Acc_Neg : ' + str(acc_neg))
    return 1
