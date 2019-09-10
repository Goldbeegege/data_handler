# -*-coding:utf-8-*-
# @author: JinFeng
# @date: 2019/9/10 9:21


import sys
from PyQt5.QtWidgets import QApplication,QFileDialog,QLabel,QMainWindow,QInputDialog,QMessageBox
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
        self.frequence = 0
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

    def export(self):
        text = self.status.text()

        ret,ok = QInputDialog.getText(self,"请确定文件名","默认保存文件名为",text=text)
        if ret and ok:
            path = QFileDialog.getExistingDirectory(self,"选择文件夹")
            if self.status.objectName() == "take_part":
                files = "\n".join(path.replace("/","//") + "//"+text+str(i+1) + ".csv" for i in range(self.frequence))

                msg = "拆分出来的数据共分成{}个文件，文件路径分别为:".format(str(self.frequence)) + "\n" + files
                ret = QMessageBox.information(self,"提示信息",msg,QMessageBox.Yes|QMessageBox.No,QMessageBox.Yes)
                if QMessageBox.Yes == ret:
                    data_handler.export(path.replace("/","//") + "//"+text,self.ui.textEdit)

    def log_msg(self,msg=None):
        if msg is None:
            msg = "<font style='color:purple'>{} &nbsp;&nbsp;处理中，请稍后......</font><br>".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.ui.textEdit.append(msg)

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
                    self.log_msg("<font style='color:red'>模式：{}</font><br>".format(sender.text())+ "\n")
                    self.status = sender
                    self.ui.pushButton.setEnabled(True)
                else:
                    print("method `{}` must be implement".format(sender.objectName()))
            else:
                button.setStyleSheet("color:black")
                button.setEnabled(True)

    def start_handler(self):
        self.log_msg("<font style='color:purple'>{} &nbsp;&nbsp;开始处理：{}</font><br>".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),self.file_name)+ "\n")

        getattr(self,self.status.objectName())()


    def open_file(self):
        file_name,_ = QFileDialog.getOpenFileName(self,"打卡文件",".","文件类型(*.csv)")
        if file_name:
            self.log_msg("<font style='color:blue;'>{} &nbsp;&nbsp;已导入：{}</font><br>".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),file_name)+ "\n")
            self.ui.pushButton_2.setEnabled(True)
            self.file_name = file_name
        return False

    def take_part(self):
        self.frequence,_ = QInputDialog.getInt(self,"请确认频率","频率默认为",6)
        if self.frequence and _:
            t1 = threading.Thread(target=self.log_msg)
            t1.start()
            t2 = threading.Thread(target=data_handler.take_part,args=(int(self.frequence),self.file_name),kwargs={"textEdit":self.ui.textEdit,"pushButton":self.ui.pushButton_4})
            t2.setDaemon(True)
            t2.start()


    def mean_value(self):
        sender = self.sender()
        print(sender)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())

