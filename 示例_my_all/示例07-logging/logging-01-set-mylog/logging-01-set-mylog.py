import logging
# import os.path

logging.basicConfig(level=logging.INFO)   #水库总阀门接一个过滤网INFO， //keep

mylogger = logging.getLogger('emc')       #从水库阀门上面接了一个水龙头mylogger
# mylogger.propagate = False                # 防止日志向上传播到根记录器，避免重复输出

txt_file_name = "log01.txt"     # 准备一个水桶log01.txt
# if os.path.isfile(txt_file_name):
#     open(txt_file_name, 'w').close()

file_handler = logging.FileHandler(txt_file_name)  #水桶上面接一根水管file_handler
file_handler.setLevel(logging.INFO)                #水管里面接一个过滤网INFO
mylogger.addHandler(file_handler)                    #水管接到水龙头mylogger上面

logging.info("root log")
mylogger.info("my log")


