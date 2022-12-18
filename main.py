from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtWidgets import QMessageBox
import sys
import pandas as pd
from datetime import datetime
import warnings
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
warnings.filterwarnings('ignore')

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('arayuz.ui', self)
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.data = pd.read_csv('fuel.csv')
        self.button = self.findChild(QtWidgets.QPushButton, 'pushButton')
        self.button.clicked.connect(self.pen_fre_grafik)
        self.frekansButton = self.findChild(QtWidgets.QPushButton, 'frekansButton')
        self.frekansButton.clicked.connect(self.frekans_grafik)
        self.penetrasyonButton = self.findChild(QtWidgets.QPushButton, 'penetrasyonButton')
        self.penetrasyonButton.clicked.connect(self.penetrasyon_grafik)
        self.vehicle_type = None
        self.engine_type = None
        self.model_type = None
        self.plate = None
        self.show()
    
    def clearchecked(self):
        self.dieselButton.setAutoExclusive(False)
        self.benzineButton.setAutoExclusive(False)
        self.binekButton.setAutoExclusive(False)
        self.ticariButton.setAutoExclusive(False)

        self.dieselButton.setChecked(False)
        self.benzineButton.setChecked(False)
        self.binekButton.setChecked(False)
        self.ticariButton.setChecked(False)

        self.dieselButton.setAutoExclusive(True)
        self.benzineButton.setAutoExclusive(True)
        self.binekButton.setAutoExclusive(True)
        self.ticariButton.setAutoExclusive(True)
    
    def getdetails(self):
        self.plate = self.plateNo.toPlainText()
        self.diesel = self.dieselButton.isChecked()
        self.benzin = self.benzineButton.isChecked()
        self.binek = self.binekButton.isChecked()
        self.ticari = self.ticariButton.isChecked()
        self.model = self.comboBox.currentText()
        self.date = self.tarihBox.currentText()
        if self.checkItems() != True:
            return 0
        self.filtered_data = self.filterdata(self.data,model=self.model_type,engine_type=self.engine_type,
                                                fuel_city=self.plate,vehicle_type=self.vehicle_type)

        self.pen_fre = self.pen_frekans(self.filtered_data)
        self.clearchecked()   
        if type(self.pen_fre) == int:
            return 0

    def penetrasyon_grafik(self):
        self.penetrasyon_data()
        plt.ion()
        labels = self.hist_data["date"]
        benzin_alan = self.hist_data["alım yapan"]
        benzin_almayan = self.hist_data["alım yapmayan"]

        x = np.arange(len(labels))
        width = 0.35

        fig, ax = plt.subplots()
        rects1 = ax.bar(x - width/2, benzin_alan, width, label='Alım yapan')
        rects2 = ax.bar(x + width/2, benzin_almayan, width, label='Alım yapmayan')

        
        ax.set_ylabel('Unique Kişi Yüzdesi')
        ax.set_title('Aylık Unique Kişi Oranı')
        ax.set_xticks(x, labels)
        ax.legend(loc=1)

        ax.bar_label(rects1, padding=3)
        ax.bar_label(rects2, padding=3)

        fig.tight_layout()

        plt.show()

    def penetrasyon_data(self):
        if self.getdetails() == 0:
            return 0
        data = self.data.groupby(["asset_id","data_month"]).sum().reset_index()
        self.hist_data = pd.DataFrame(columns=["date","alım yapan","alım yapmayan"])
        d = datetime.now()
        d = int(d.strftime("%m"))
        for i in range(1,d-1):
            tarih = "2022-" + str(i)
            alım_yapan_kisi = len(data[(data["benzin alım"] > 0 )& (data["data_month"] == tarih)])
            alım_yapmayan_kisi = len(data[(data["benzin almama"] > 0 )& (data["data_month"] == tarih)])
            dict_f = {
                "date":tarih,
                "alım yapan":round((alım_yapan_kisi / (alım_yapan_kisi + alım_yapmayan_kisi) )* 100,2),
                "alım yapmayan":round((alım_yapmayan_kisi / (alım_yapan_kisi + alım_yapmayan_kisi) )* 100,2)
            }                  
            self.hist_data = self.hist_data.append(dict_f,ignore_index=True)
        

    def pen_fre_grafik(self):
        if self.getdetails() == 0:
            return 0
        plt.ion()
        plt.figure()
        data = self.pen_fre[self.pen_fre["tarih"] == self.date]
        sns.scatterplot(data=data,x="penetrasyon",y="frekans",hue="istasyon")
        plt.title(f"{self.date} Penetrasyon-Frekans Grafiği")
        plt.show()

    def frekans_grafik(self):
        if self.getdetails() == 0:
            return 0
        plt.ion()
        plt.figure()
        for x in ["opet","shell","petrol ofisi","bp","other"]:
            data = self.pen_fre[self.pen_fre["istasyon"]==x]
            plt.plot(data["tarih"],data["frekans"],label=x)
        plt.legend(loc=1)
        plt.show()

    def pen_frekans(self,data):
        result = pd.DataFrame(columns=["frekans","penetrasyon","istasyon","tarih"])
        group_data = data.groupby(["asset_id","data_month"]).sum().reset_index()
        x = 1
        d = datetime.now()
        d = int(d.strftime("%m"))
        for i in range(d-2):
            tarih = '2022-' + str(x)
            for station in ["opet","shell","petrol ofisi","bp","other"]:
                try:
                    frekans = sum(group_data[(group_data["data_month"] == tarih) & (group_data[station +" alım"] > 0)][station + " alım"]) / len(group_data[(group_data["data_month"] == tarih) & (group_data[station+" alım"] > 0)])
                    penetrasyon = len(group_data[(group_data["data_month"] == tarih) & (group_data[station + " alım"]>0)])
                    toplam_alım = len(group_data[(group_data["data_month"] == tarih) & (group_data["benzin alım"]>0)])
                    dict_f = {  "frekans":frekans,
                                "penetrasyon":(penetrasyon/toplam_alım)*100,
                                "istasyon":station,
                                "tarih":tarih }
                    result = result.append(dict_f,ignore_index=True)
                except Exception as err:
                    msg = QMessageBox()
                    msg.setWindowTitle("Hata")
                    msg.setText(f'Yaptığınız filtrelerde hata bulunmakta tekrar kontrol ediniz! \n{err}')
                    msg.exec_()
                    return 0
            x += 1
        return result


    def filterdata(self,data,model=None,engine_type=None,fuel_city=None,vehicle_type=None):
        if model != None:
            data = data[data["model"] == model]
        if engine_type != None:
            data = data[data["engine_type"] == engine_type]
        if fuel_city != None:
            data = data[data["fuel_city"] == fuel_city]
        if vehicle_type != None:
            data = data[data["vehicle_type"] == vehicle_type]
        return data


    def show_error_msg_plate(self):
        msg = QMessageBox()
        msg.setWindowTitle("Hata")
        msg.setText("Plaka değerini kontrol ediniz. Geçerli değerler : 1-81")
        msg.setIcon(QMessageBox.Critical)
        msg.exec_()
    
    def checkItems(self):
        if self.plate != "":
            try:
                self.plate = int(self.plate)
                if self.plate < 1 or self.plate > 81:
                    self.show_error_msg_plate()
                    return False
            except:
                self.show_error_msg_plate()
                return False
        else:
            self.plate = None   
        if self.diesel:
            self.engine_type = "DIZEL"
        if self.benzin:
            self.engine_type = "BENZIN"
        if self.binek:
            self.vehicle_type = "BİNEK"
        if self.ticari:
            self.vehicle_type = "TİCARİ"
        if self.model == "":
            self.model_type = None
        if self.model != "":
            self.model_type = self.model
        return True

    
app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_() 