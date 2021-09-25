import pytest
import allure
import os
import analysis_u.strategy.tushare_util as util
from loguru import logger


@allure.feature('全部用户列表所有筛选项一起查询1')
def test_get_pro_client():
    # 初始化
    pro = util.get_pro_client()
    # logger.debug(pro)
    # 使用assert判断结果
    assert pro.empty != False


@allure.feature('全部用户列表所有筛选项一起查询2')
@allure.story('子功能名称')
def test_get_all_code_df():
    # 初始化

    pro = util.get_pro_client()
    # df = pro.get_all_code_df()
    # print(df)
    # logger.debug(pro)
    # 使用assert判断结果
    assert pro.empty != False


@allure.feature('全部用户列表所有筛选项一起查询3')
def test_get_all_code():
    # 初始化
    pro = util.get_pro_client()
    # df = pro.get_all_code()
    # 使用assert判断结果
    assert pro.empty != False


if __name__ == '__main__':
    pytest.main(["-s", "--alluredir", "test_tushare_util.py"])
    # os.system('allure generate ./report/ -o ./report/html/ --clean')
    # os.system("allure open ./report/html/")
