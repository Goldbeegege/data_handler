# -*-coding:utf-8-*-
# @author: JinFeng
# @date: 2019/9/10 15:12

import pandas as pd
import numpy as np
import datetime

class DataHander(object):
    """
    数据处理
    """
    def __init__(self):
        self.data = None

    def take_part(self,frequence,file_name,**kwargs):
        """
        将每秒数据按照频率拆分开来
        kwargs{
            "textEdit":QTextEdit;
            "pushButton":QPushButton,
            ...
        }
        :param frequence:频率
        :param file_name:文件名
        :return:
        """
        df = pd.read_csv(file_name, low_memory=False)
        df["datetime"] = df["date"] + df["time"]
        grouped = df.groupby(by=["datetime"])

        data_list = [None for i in range(frequence)]
        for second, item in grouped:
            for row in range(frequence):
                try:
                    value = np.vstack((data_list[row], item.iloc[row].values))
                    data_list[row] = value
                except ValueError:
                    data_list[row] = item.iloc[row]
                except IndexError:
                    break
        new_df_list = []
        for i, test_data in enumerate(data_list):
            new_df_list.append(pd.DataFrame(test_data, columns=df.columns))
        self.data = new_df_list

        try:
            kwargs["textEdit"].append("<font style='color:green;'>{} &nbsp;&nbsp;<strong>√</strong> 拆分完成：{}</font><br>".format(
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), file_name) + "\n")
        except KeyError:
            print("keyerror")
        btn = kwargs.get("pushButton","")
        if btn:
            self.common_func(btn,"take_part")


    def common_func(self,btn,obj_name):
        btn.setEnabled(True)
        btn.setObjectName(obj_name)

    def export(self,path,textEdit):
        if isinstance(self.data,list):
            for i,new_df in enumerate(self.data):
                file_name = path  + str(i+1) + ".csv"
                textEdit.append("<font style='color:green;'>{} &nbsp;&nbsp;<strong>√</strong> {}&nbsp;已导出完成</font><br>".format(
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), file_name) + "\n")
                new_df.to_csv(file_name)
            return True


data_handler = DataHander()