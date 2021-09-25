本程序使用传统的TuShare接口，并非需要捐赠的pro接口，获取数据无限制;

- 按照股东下降数量
- 按照PBPE
- 按照ROE

安装ta-lib的方法

ta-lib不能直接用pip install ta-lib的方式进行安装，需要下载whl文件，然后pip install xxx.whl的方式进行安装
确认自己的python的版本，比如我本地安装的是python3.8
去python第三方库中下载和我们python匹配的ta-lib，因为我们的python是3.8，操作系统是64，所以我们下载cp38,64位
使用管理员权限运行cmd，执行命令：pip install "C:\Users\Administrator\Downloads\TA_Lib-0.4.20-cp38-cp38-win_amd64.whl"
安装完成
