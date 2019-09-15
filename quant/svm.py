from sklearn import svm
from quant import DC

# 机器学习暂时找不到应用场景
def svm_cal(stock, start_date, end_date):
    stock = stock
    dc = DC.data_collect(stock, start_date, end_date)
    train = dc.data_train
    target = dc.data_target
    test_case = [dc.test_case]

    model = svm.SVC()  # 建模
    model.fit(train, target)  # 训练
    ans2 = model.predict(test_case)  # 预测
    # 输出对2018-03-02的涨跌预测，1表示涨，0表示不涨。
    print(ans2[0])

def main():
    # 模拟数据
    stock = "600548.SH"
    start_date = '20100912'
    end_date = '20190912'
    svm_cal(stock, start_date, end_date)


if __name__ == '__main__':
    main()
