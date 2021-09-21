import pytest
import allure
import os

if __name__ == '__main__':
    """此时生成的报告文件为json格式"""
    pytest.main(["-s", "--alluredir", "./report/raw",  "tests/strategy/test_sort.py"])

    # pytest.main(['-s', '-q', 'tests/strategy/test_sort.py', '--alluredir', 'D:/Work/git/ecosys/report/raw/'])

    os.system("allure "
              "generate "
              "D:/Work/git/ecosys/report/raw/ "
              "-o "
              "D:/Work/git/ecosys/report//html/ "
              "--clean")
    os.system("allure open D:/Work/git/ecosys/report/html/ ")

'''
os.system('allure generate ./report/raw -o ./report/html/ --clean')
os.system("allure open ./report/html/")
'''
