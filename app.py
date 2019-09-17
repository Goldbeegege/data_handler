# -*-coding:utf-8-*-
# @author: JinFeng
# @date: 2019/9/10 9:21


import sys
from PyQt5.QtWidgets import QApplication,QFileDialog,QMainWindow,QInputDialog,QMessageBox,QPushButton
from start import Ui_MainWindow
import datetime
from dataHandler import data_handler
import threading

class App(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)
        self.status = {} #标记当前是什么模式
        self.last_mode = None #上一次处理文件的模式
        self.file_name = None #要处理的文件的文件名，存为实例变量方便后面获取
        self.mode_button = [] #存放有哪些模式
        self.function_button = [] #存放功能按钮
        self.activate_button = None #表示功能按钮具体哪一个被激活

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.origin_button = [self.ui.pushButton, self.ui.pushButton_2, self.ui.pushButton_4]
        #存放上个最基本的按钮，方便以后进行扩展
        #激活的按钮只能是这三个，并且根据该按钮在self.function_button中的索引进行层级判断；
        #若索引值为2，那么索引小于等于2的按钮全部被激活，大于2的全部未被激活，为了方便管理功能按钮是否能都点击

        for i in range(self.ui.horizontalLayout.count()):
            wg = self.ui.horizontalLayout.itemAt(i).widget()
            if isinstance(wg,QPushButton):
                self.mode_button.append(wg)
                wg.clicked.connect(self.dispatch)
                #获取所有的模式按钮并且分发槽函数

        for j in range(self.ui.verticalLayout_2.count()):
            func_tool = self.ui.verticalLayout_2.itemAt(j).widget()
            if isinstance(func_tool,QPushButton):
                func_tool.clicked.connect(getattr(self,func_tool.objectName()))
                self.function_button.append(func_tool)
                #获取所有的功能按钮并分发槽函数

    def dispatch(self):
        """
        统一接收有模式按钮的信号，并根据反射指定处理函数
        :return:
        """
        sender = self.sender()
        if self.last_mode != sender.objectName():
            #判断这次点击的模式是不是上一次处理的，若已经处理过，则可以直接导出，提高用户体验
            self.activate_button = self.origin_button[0]
            self.activateButton()

        else:
            self.activate_button = self.origin_button[-1]
            self.activateButton()

        for button in self.mode_button:
            if button==sender:
                button.setStyleSheet("color:red") #模式按钮选中的样式
                button.setEnabled(False) #选中或不可在点击
                if hasattr(self,sender.objectName()):
                    self.log_msg("red","模式：{}".format(sender.text())) #将模式信息写入文本框中
                    self.status = sender
                else:
                    print("method `{}` must be implement".format(sender.objectName()))
            else:
                button.setStyleSheet("color:black")
                button.setEnabled(True)

    def activateButton(self):
        """
        根据索引判断激活按钮的层级关系
        :return:
        """
        index = self.function_button.index(self.activate_button)
        for i,button in enumerate(self.function_button):
            if i <= index:
                button.setEnabled(True)
            else:
                button.setEnabled(False)

    def open_file(self):
        """
        功能按钮导入的槽函数
        :return:
        """
        file_name,_ = QFileDialog.getOpenFileName(self,"打开文件",".","文件类型(*.csv)")
        if file_name:
            self.log_msg("blue","已导入：{}".format(file_name))
            self.activate_button = self.origin_button[1]
            self.activateButton()
            self.file_name = file_name
        else:
            self.cancel()

    def start_handler(self):
        """
        开始的槽函数
        :return:
        """
        self.log_msg("purple","开始处理：{}<br>".format(self.file_name))
        getattr(self,self.status.objectName())()
        data_handler.__init__()

    def callback(self,**kwargs):
        """
        回调函数，当某一个功能完成之后毁掉该函数，主要是在文本框中书写内容
        :param kwargs:
        :return:
        """
        self.log_msg(kwargs.get("color","purple"),kwargs.get("msg"))

        if not kwargs.get("error"):
            self.activate_button = self.origin_button[-1]
            self.last_mode = self.status.objectName()
        else:
            self.activate_button = self.origin_button[0]
        self.activateButton()

    def export(self):
        """
        导出按钮的槽函数
        :return:
        """
        path,types = QFileDialog.getSaveFileName(self,"保存文件",self.file_name,"文件类型(*.csv)")
        if path and types:
            data_handler.export(path,self.callback)
        else:
            self.cancel()

    def log_msg(self,color="purple",msg=None):
        """
        向文本框中写出当前处理的状态
        :param color: 颜色
        :param msg: 处理信息
        :return:
        """
        if msg is None:
            msg = "<font style='color:{}'>{} &nbsp;&nbsp;处理中，请稍后......</font><br>".format(color,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        else:
            msg = "<font style='color:{}'>{} &nbsp;&nbsp;{}</font><br>".format(color,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),msg)
        self.ui.textEdit.append(msg)

    def cancel(self):
        #点击对话框关闭按钮的动作
        self.log_msg("cyan","已取消")

    def muti_task(self,func,*args):
        """
        开启多线程
        :param func:指定多线程的函数
        :param args: 函数的参数
        :return:
        """
        t1 = threading.Thread(target=self.log_msg)
        t1.start()
        t2 = threading.Thread(target=func, args=args)
        t2.setDaemon(True)
        t2.start()

    #下面是具体的功能函数
    def take_part(self):
        frequence,_ = QInputDialog.getInt(self,"请确认频率","频率默认为",6)
        if frequence and _:
            ele,ok = QInputDialog.getItem(self,"请选择具体元素","元素列表为",[str(i+1) for i in range(frequence)])
            if ele and ok:
                self.muti_task(data_handler.take_part,*(int(frequence),self.file_name,int(ele),self.callback))
        else:
            self.cancel()

    def mean_value(self):
        self.muti_task(data_handler.mean_valu,*(self.file_name,self.callback))

    def rate_value(self):
        rate,ok = QInputDialog.getText(self,"请选择比例","默认比例为",text="1/2")
        if rate and ok:
            self.muti_task(data_handler.rate_value,*(self.file_name,rate,self.callback))
        else:
            self.cancel()

    def increasing_value(self):
        count, ok = QInputDialog.getInt(self, "请选择风速连续不减的个数", "风速连续不减的个数为", value=5)
        if count and ok:
            speed, _ = QInputDialog.getText(self, "限制风速", "最大风速不小于", text="5.0")

            if speed and _:
                self.muti_task(data_handler.increasing_value,*(self.file_name, count,speed,self.callback))
            else:
                self.cancel()
        else:
            self.cancel()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())

