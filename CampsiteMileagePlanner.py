import sys
import os
import pandas as pd
import numpy as np
from tkinter import *
from tkinter import filedialog
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QPushButton, QItemDelegate, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator

# class for validation
class FloatDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super().__init__()

    def createEditor(self, parent, option, index):
        # add validation
        editor = QLineEdit(parent)
        editor.setValidator(QDoubleValidator())
        return editor


class TableWidget(QTableWidget):
    def  __init__(self, df):
        super().__init__()
        self.df = df
        self.setStyleSheet('font-size: 15px;')

        nRows, nColumns = self.df.shape
        self.setColumnCount(nColumns)
        self.setRowCount(nRows)

        # set up the on-screen display of the table
        self.setHorizontalHeaderLabels(('Start', 'End', 'Miles', 'Daily Miles','Campsite?'))
        self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # set up validation for column
        self.setItemDelegateForColumn(2, FloatDelegate())

        # data insertion
        for i in range(self.rowCount()):
            for j in range(self.columnCount()):
                self.setItem(i,j, QTableWidgetItem(str(self.df.iloc[i,j])))

        # associate any changes user made to the table data
        self.cellChanged[int, int].connect(self.updateDF)

    def updateDF(self, row, column):
        text = self.item(row, column).text()
        self.df.iloc[row, column] = text


class DFEditor(QWidget):
    # data = {
    #     'Col X': ['trailhead','JCT 1','JCT 2','snake creek'],
    #     'Col Y': ['JCT 1', 'JCT 2', 'snake creek', 'campsite'],
    #     'Col Z': [10,20,30,40]
    # }
    #
    # df = pd.DataFrame(data)
    #df = pd.DataFrame()

    # get data; prompt user to select the file which has the data
    # os.chdir("C:\\")
    os.chdir("C:\\Users\\Inspiron3650\\Documents\\PythonScripts\\TrailCampPlanner")
    path = filedialog.askopenfilename(initialdir="C:", title="Select the file which has the trail data")
    df = pd.read_excel(path, engine='openpyxl')

    # add column to use to mark for potential campsites
    df.insert(3, 'Daily Miles', '')
    df.insert(4, 'Campsite', '')

    # convert numeric columns to numeric datatype
    df["Miles"] = pd.to_numeric(df["Miles"], downcast="float")
    df["Daily Miles"] = pd.to_numeric(df["Daily Miles"], downcast="float")


    # calculate the running mileage totals between each point
    # first row is just the same value as in the adjacent column
    df.iloc[0,3] = df.iloc[0,2]

    # the rest of the rows are calculated by adding the previous row's value with the current row's value
    #df.iloc[1,3] = df.iloc[0,3] + df.iloc[1,2]
    for i in range(1,df.shape[0]):
        df.iloc[i,3] = df.iloc[i-1,3] + df.iloc[i,2]

    # round the "Daily Miles" to 1 decimal place
    df["Daily Miles"] = np.round(df["Daily Miles"], decimals=1)

    def __init__(self):
        super().__init__()
        self.resize(1200,800)

        mainLayout = QVBoxLayout()

        # create table widget
        self.table = TableWidget(DFEditor.df)
        mainLayout.addWidget(self.table)

        # add print button
        button_print = QPushButton('Display DF')
        button_print.setStyleSheet('font-size: 30px')

        # associate button click with method to print
        button_print.clicked.connect(self.print_DF_Values)

        mainLayout.addWidget(button_print)

        # do similar steps as above for other buttons
        button_export = QPushButton('Export to CSV file')
        button_export.setStyleSheet('font-size: 30px')
        button_export.clicked.connect(self.export_to_csv)
        mainLayout.addWidget(button_export)

        button_recalc = QPushButton('Recalculate Daily Mileage')
        button_recalc.setStyleSheet('font-size: 30px')
        button_recalc.clicked.connect(self.recalculate_miles)
        mainLayout.addWidget(button_recalc)

        self.setLayout(mainLayout)


    def print_DF_Values(self):
        print(self.table.df)

    def export_to_csv(self):
        self.table.df.to_csv('Data export.csv', index=False)
        print('CSV file exported.')

    def recalculate_miles(self):
        # recalculate daily miles

        # get the indices of the rows which have an "X" for campsite
        idx_array = np.where(self.table.df["Campsite"] == "X")
        listCampsiteRows = self.table.df.iloc[idx_array].index.tolist()
        numCampsiteRows = len(listCampsiteRows)
        print(listCampsiteRows)
        print("size of list = " +  str(numCampsiteRows))
        print("len of df = " + str(len(self.table.df.index)))

        currentListIndex = 0
        segmentMiles = 0.0
        for i in listCampsiteRows:
            print(str(i))
            currentRow = i + 1

            # get the row index of the next campsite
            if numCampsiteRows > 1:
                nextCampsiteRow = listCampsiteRows[currentListIndex + 1]
                initialRow = currentRow
                for i in range(currentRow, nextCampsiteRow + 1):
                    if i == initialRow:
                        segmentMiles = self.table.df.iloc[currentRow, 2]
                        self.table.df.iloc[currentRow, 3] = segmentMiles
                        currentRow = currentRow + 1

                    else:
                        segmentMiles = self.table.df.iloc[currentRow - 1, 3] + self.table.df.iloc[currentRow, 2]
                        self.table.df.iloc[currentRow, 3] = self.table.df.iloc[currentRow - 1, 3] + self.table.df.iloc[currentRow, 2]
                        currentRow = currentRow + 1

                numCampsiteRows = numCampsiteRows - 1

            else:
                # only 1 remaining campsite
                # calculate the daily miles for the next day
                segmentMiles = self.table.df.iloc[currentRow, 2]
                self.table.df.iloc[currentRow, 3] = segmentMiles

                currentRow = currentRow + 1
                for i in range(currentRow, self.table.df.shape[0]):
                    self.table.df.iloc[currentRow, 3] = self.table.df.iloc[currentRow - 1, 3] + self.table.df.iloc[currentRow, 2]
                    currentRow = currentRow + 1

                # round to 1 decimal place
                self.table.df["Daily Miles"] = np.round(self.table.df["Daily Miles"], decimals=1)



if __name__ == '__main__':
    print("running main")
    root = Tk()
    root.withdraw()

    app = QApplication(sys.argv)

    demo = DFEditor()
    demo.show()

    sys.exit(app.exec_())