import allure
import pytest
import os


@allure.feature('【需求点】：数据类型不符合是否判断')
@allure.story('【MSTD】')
@allure.severity('blocker')
def test_case_01():
    """
    用例描述：这个是一个很长很长的用例描述01
    """
    assert 0


@allure.feature('【需求点】：数据类型不符合是否判断')
@allure.story('【AIVWAP】')
@allure.severity('critical')
def test_case_02():
    """
    用例描述：这个是一个很长很长的用例描述02
    """
    with allure.step("第一步：登录"):  # 将一个测试用例分成几个步骤，将步骤打印到测试报告中，步骤2
        allure.attach('alien', 'name')  # attach可以打印一些附加信息
        allure.attach('18', 'age')
        allure.story("")
    with allure.step("第二步：发送订单"):  # 将一个测试用例分成几个步骤，将步骤打印到测试报告中，步骤3
        pass
    with allure.step("第三步：判断结果"):
        allure.attach('期望结果', '添加购物车成功')
        assert 'success' == 'failed'


@allure.feature('【需求点】：登录能否成功')
@allure.story('【常规登录】')
@allure.severity('normal')
def test_case_03():
    """
    用例描述：这个是一个很长很长的用例描述03
    """
    assert 0


@allure.feature('【需求点】：登录能否成功')
@allure.story('【异常登录】')
@allure.severity('minor')
def test_case_04():
    """
    用例描述：这个是一个很长很长的用例描述04
    """
    assert 0 == 0
    allure.dynamic.description("这个用例描述，将要替换如上的用例描述")


if __name__ == '__main__':
    '''
    pytest.main(['-s', '-q', 'test_sort.py', '--alluredir', 'D:/Work/git/ecosys/report/Raw_Files/'])
    os.system("allure "
              "generate "
              "D:/Work/git/ecosys/report/Raw_Files/"
              "-o "
              "D:/Work/git/ecosys/report/"
              "--clean")
    os.system("allure open D:/Work/git/ecosys/report/")
    '''
