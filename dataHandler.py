# -*-coding:utf-8-*-
# @author: JinFeng
# @date: 2019/9/10 15:12

import pandas as pd
import numpy as np

class DataHander(object):
    """
    数据处理
    """
    def __init__(self):
        self.data = None

    def take_part(self,frequence,file_name,ele,cb=None):
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

        for i, test_data in enumerate(data_list):
            if i == ele-1:
                self.data = pd.DataFrame(test_data, columns=df.columns)

        msg = "拆分完成：{}".format(file_name)
        if cb is not None and callable(cb):
            cb("green",msg,"take_part")

    def mean_value(self,path,cb=None):
        df = pd.read_csv(path)
        grouped = df.groupby(by=[df["wind"]])
        columns = None
        values = None
        for wind, item in grouped:
            data = item.mean(axis=0)
            if columns is None:
                print(data)
                columns = data.index
                values = data.values
            else:
                try:
                    values = np.vstack((values, data.values))
                except Exception as e:
                    pass
        self.data = pd.DataFrame(values,columns=columns)
        if cb is not None and callable(cb):
            msg = "处理完成"
            cb("green",msg,"mean_value")


    def export(self,path,cb=None):
        file_name = path.rsplit("/",1)[1]
        self.data.to_csv(file_name)
        msg = "已导出完成".format(file_name)
        if cb is not None and callable(cb):
            cb("green",msg)


data_handler = DataHander()