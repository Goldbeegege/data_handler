# -*-coding:utf-8-*-
# @author: JinFeng
# @date: 2019/9/10 9:21


import sys
from PyQt5.QtWidgets import QApplication,QFileDialog,QMainWindow,QInputDialog,QMessageBox
from start import Ui_MainWindow
import datetime
from dataHandler import data_handler
import threading

class App(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)
        self.status = {} #标记当前是什么模式
        self.file_name = None #要处理的文件的文件名，存为实例变量方便后面获取
        self.function_button = [] #存放有哪些功能
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        for i in range(self.ui.horizontalLayout.count()):
            wg = self.ui.horizontalLayout.itemAt(i).widget()
            if wg is not None:
                self.function_button.append(wg)
                wg.clicked.connect(self.dispatch)

        self.ui.pushButton.clicked.connect(self.open_file)
        self.ui.pushButton_2.clicked.connect(self.start_handler)
        self.ui.pushButton_4.clicked.connect(self.export)

    def callback(self,color,msg,func_name=None):
        self.log_msg(color,msg)
        if func_name is not None:
            self.ui.pushButton_4.setEnabled(True)
            self.ui.pushButton_4.setObjectName(func_name)


    def export(self):
        path,types = QFileDialog.getSaveFileName(self,"保存文件",self.file_name,"文件类型(*.csv)")
        if path and types:
            data_handler.export(path,self.callback)
        else:
            self.cancel()


    def log_msg(self,color="purple",msg=None):
        if msg is None:
            msg = "<font style='color:{}'>{} &nbsp;&nbsp;处理中，请稍后......</font><br>".format(color,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        else:
            msg = "<font style='color:{}'>{} &nbsp;&nbsp;{}</font><br>".format(color,datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),msg)
        self.ui.textEdit.append(msg)

    def cancel(self):
        self.log_msg("cyan","已取消")

    def dispatch(self):
        sender = self.sender()
        if self.ui.pushButton_4.objectName() != sender.objectName():
            self.ui.pushButton_2.setEnabled(False)
            self.ui.pushButton_4.setEnabled(False)
        else:
            self.ui.pushButton_2.setEnabled(True)
            self.ui.pushButton_4.setEnabled(True)

        for button in self.function_button:
            if button==sender:
                button.setStyleSheet("color:red")
                button.setEnabled(False)
                if hasattr(self,sender.objectName()):
                    self.log_msg("red","模式：{}".format(sender.text()))
                    self.status = sender
                    self.ui.pushButton.setEnabled(True)
                else:
                    print("method `{}` must be implement".format(sender.objectName()))
            else:
                button.setStyleSheet("color:black")
                button.setEnabled(True)

    def start_handler(self):
        self.log_msg("purple","开始处理：{}<br>".format(self.file_name))
        getattr(self,self.status.objectName())()


    def open_file(self):
        file_name,_ = QFileDialog.getOpenFileName(self,"打卡文件",".","文件类型(*.csv)")
        if file_name:
            self.log_msg("blue","已导入：{}".format(file_name))
            self.ui.pushButton_2.setEnabled(True)
            self.file_name = file_name
        else:
            self.cancel()


    def take_part(self):
        frequence,_ = QInputDialog.getInt(self,"请确认频率","频率默认为",6)
        if frequence and _:
            ele,ok = QInputDialog.getItem(self,"请选择具体元素","元素列表为",[str(i+1) for i in range(frequence)])
            if ele and ok:
                t1 = threading.Thread(target=self.log_msg)
                t1.start()
                t2 = threading.Thread(target=data_handler.take_part,args=(int(frequence),self.file_name,int(ele),self.callback))
                t2.setDaemon(True)
                t2.start()
        else:
            self.cancel()


    def mean_value(self):
        t1 = threading.Thread(target=self.log_msg)
        t1.start()
        t2 = threading.Thread(target=data_handler.mean_value,args=(self.file_name,self.callback))
        t2.setDaemon(True)
        t2.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())

