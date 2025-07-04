
1./data/hjw/github/getDialog/bin/start.sh 作为执行入口,先将src/py设置为 python home,再调用main.py
2.将项目/data/hjw/github/getDialog/src/py/steps目录下各步骤的可执行py文件入口收敛在main.py中,main.py任务执行入口,整合当前各步骤的执行参数,其他步骤只是作为单独模块,被main.py引用,不可被直接执行
3.main.py中有usage使用说明
