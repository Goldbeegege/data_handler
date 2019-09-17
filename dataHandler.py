# -*-coding:utf-8-*-
# @author: JinFeng
# @date: 2019/9/10 15:12

import pandas as pd
import numpy as np


class BaseHandler(object):
    def __int__(self):
        self.data = None

class DataHander(BaseHandler):
    """
    数据处理
    """
    def __init__(self):
        self.ret = {"msg":"","color":"green","error":False}

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
        try:
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

            msg = "拆分完成 {}".format(file_name)
            self.ret["msg"] = msg

        except Exception as e:
            self.ret["msg"] = str(e)
            self.ret["color"] = "red"
            self.ret["error"] = True

        if cb is not None and callable(cb):
            cb(**self.ret)

    def mean_value(self,path,cb=None):
        df = pd.read_csv(path)
        try:
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
            msg = "处理完成 {}".format(path)
            self.ret[msg] = msg


        except Exception as e:
            self.ret["msg"] = str(e)
            self.ret["color"] = "red"
            self.ret["error"] = True

        if cb is not None and callable(cb):
            cb(**self.ret)

    def rate_value(self,file_name,rate,cb=None):
        df = pd.read_csv(file_name)
        error = False
        try:
            grouped = df.groupby(by=["wind"])
            column = None
            data = None
            m,n = rate.split("/")
            for wind, item in grouped:
                length = item.shape[0]

                if length*int(m) < int(n):
                    continue

                interval, b = divmod(length*int(m), int(n))
                item = item.sort_values(by=["ang_strain"], ascending=False)
                value = item.iloc[0:interval]
                if column is None:
                    column = value.columns
                    data = value.values
                else:
                    data = np.vstack((data, value.values))
            self.data = pd.DataFrame(data, columns=column)
            msg = "处理完成 {}".format(file_name)
            self.ret[msg] = msg

        except Exception as e:
            self.ret["msg"] = str(e)
            self.ret["color"] = "red"
            self.ret["error"] = True

        if cb is not None and callable(cb):
            cb(**self.ret)

    def increasing_value(self, file_name, count, speed, cb):
        df = pd.read_csv(file_name)
        data_list = []
        temp_list = []
        try:
            for i in range(df.shape[0]):
                if not temp_list:
                    temp_list.append(pd.DataFrame(df.iloc[i].to_dict(), index=[0]))
                else:
                    if df.iloc[i]["wind"] > temp_list[-1]["wind"][0]:
                        temp_list.append(pd.DataFrame(df.iloc[i].to_dict(), index=[0]))
                    else:
                        if len(temp_list) >= int(count) and temp_list[-1]["wind"][0] > float(speed):
                            data = temp_list[0].append(temp_list[1:], ignore_index=True)
                            interval = pd.DataFrame(
                                np.array([" " for i in range(data.shape[-1])]).reshape(1, data.shape[-1]),
                                columns=data.columns.to_list())
                            data = data.append(interval, ignore_index=True)
                            data_list.append(data)
                        temp_list.clear()
            msg = "处理完成 {}".format(file_name)
            self.ret["msg"] = msg

            if len(data_list) == 0:
                msg = "未找到符合条件的数据"
                self.ret["color"] = "red"
                self.ret["msg"] = msg

            elif len(data_list) == 1:
                self.data = data_list[0]
            else:
                self.data = data_list[0].append(data_list[1:], ignore_index=True)
        except Exception as e:
            self.ret["msg"] = str(e)
            self.ret["color"] = "red"
            self.ret["error"] = True

        if cb is not None and callable(cb):
            cb(**self.ret)

    def export(self,path,cb=None):
        file_name = path.rsplit("/",1)[1]
        self.data.to_csv(file_name)
        msg = "已导出 {}".format(file_name)
        self.ret["msg"] = msg
        if cb is not None and callable(cb):
            cb(**self.ret)

data_handler = DataHander()