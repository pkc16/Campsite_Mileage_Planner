import os
import tkinter

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
        self.setHorizontalHeaderLabels(('Site', 'Miles', 'Daily Miles','Campsite? (mark with "x")'))
        self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # set up validation for column
        self.setItemDelegateForColumn(2, FloatDelegate())

        self.df["Miles"] = np.round(self.df["Miles"], decimals=1)
        self.df["Daily Miles"] = np.round(self.df["Daily Miles"], decimals=1)

        # data insertion
        for i in range(self.rowCount()):
            for j in range(self.columnCount()):
                # print(f'init function:  i={i}; j={j}; value = {self.df.iloc[i, j]}')
                self.setItem(i,j, QTableWidgetItem(str(self.df.iloc[i,j])))



        # associate any changes user made to the table data
        self.cellChanged[int, int].connect(self.updateDF)

    def updateDF(self, row, column):
        text = self.item(row, column).text()
        self.df.iloc[row, column] = text


class DFEditor(QWidget):

    # get data; prompt user to select the file which has the data
    # os.chdir("C:\\")
    os.chdir("C:\\Users\\Inspiron3650\\Documents\\PythonScripts\\TrailCampPlanner")
    path = filedialog.askopenfilename(initialdir="C:", title="Select the file which has the trail data")
    df = pd.read_excel(path, engine='openpyxl')

    # add columns
    df.insert(2, 'Daily Miles', '')
    df.insert(3, 'Campsite', '')

    # convert numeric columns to numeric datatype
    df["Miles"] = pd.to_numeric(df["Miles"], downcast="float")
    df["Daily Miles"] = pd.to_numeric(df["Daily Miles"], downcast="float")

    # calculate the running mileage totals between each point
    # first row is just the same value as in the adjacent column
    df.iloc[0,2] = df.iloc[0,1]

    # the rest of the rows are calculated by adding the previous row's value with the current row's value
    for i in range(1,df.shape[0]):
        df.iloc[i,2] = round(df.iloc[i-1,2] + df.iloc[i,1],1)

    # round the "Daily Miles" to 1 decimal place
    df["Daily Miles"] = df["Daily Miles"].astype(float).round(1)

    # make a copy in case needing to reset the dataframe
    df_copy = df.copy()


    def __init__(self):
        super().__init__()
        self.resize(1200,800)

        mainLayout = QVBoxLayout()

        # create table widget
        self.table = TableWidget(DFEditor.df)
        mainLayout.addWidget(self.table)

        # add print button
        button_print = QPushButton('Clear Campsites')
        button_print.setStyleSheet('font-size: 30px')

        # associate button click with method to print
        button_print.clicked.connect(self.reset)

        mainLayout.addWidget(button_print)

        # do similar steps as above for other buttons
        button_recalc = QPushButton('Recalculate Daily Mileage')
        button_recalc.setStyleSheet('font-size: 30px')
        button_recalc.clicked.connect(self.recalculate_miles)
        mainLayout.addWidget(button_recalc)

        button_reverse = QPushButton('Reverse Trail')
        button_reverse.setStyleSheet('font-size: 30px')
        button_reverse.clicked.connect(self.reverse_trail)
        mainLayout.addWidget(button_reverse)

        button_export = QPushButton('Export to CSV file')
        button_export.setStyleSheet('font-size: 30px')
        button_export.clicked.connect(self.export_to_csv)
        mainLayout.addWidget(button_export)

        self.setLayout(mainLayout)

    # def load_data(self):
    #     # get data; prompt user to select the file which has the data
    #     # os.chdir("C:\\")
    #     os.chdir("C:\\Users\\Inspiron3650\\Documents\\PythonScripts\\TrailCampPlanner")
    #     path = filedialog.askopenfilename(initialdir="C:", title="Select the file which has the trail data")
    #     df = pd.read_excel(path, engine='openpyxl')
    #
    #     # add column to use to mark for potential campsites
    #     df.insert(2, 'Daily Miles', '')
    #     df.insert(3, 'Campsite', '')
    #
    #     # convert numeric columns to numeric datatype
    #     df["Miles"] = pd.to_numeric(df["Miles"], downcast="float")
    #     df["Daily Miles"] = pd.to_numeric(df["Daily Miles"], downcast="float")
    #
    #     # calculate the running mileage totals between each point
    #     # first row is just the same value as in the adjacent column
    #     df.iloc[0,2] = df.iloc[0,1]
    #
    #     # the rest of the rows are calculated by adding the previous row's value with the current row's value
    #     for i in range(1, df.shape[0]):
    #         df.iloc[i,2] = df.iloc[i - 1,2] + df.iloc[i,1]
    #
    #     # round the "Daily Miles" to 1 decimal place
    #     df["Daily Miles"] = np.round(df["Daily Miles"], decimals=1)


    def reset(self):
        # set the dataframe back to the original state when it was first loaded from Excel
        self.table.df = self.df_copy

    def export_to_csv(self):
        self.table.df.to_csv('Data export.csv', index=False)
        print('CSV file exported.')

    def reverse_trail(self):
        # change the direction of the trail (reverse the sites in the dataframe)
        self.table.df = self.df_copy.iloc[::-1]

        # take the mileage from the last row (should be 0) and make it the mileage for the first row and shift rest of mileages down 1 row; do the shift first
        self.table.df['Miles'] = self.table.df['Miles'].shift(1)

        # now set the mileage for the first row to be 0
        self.table.df.iloc[0,1] = 0

        # now calculate the mileages for each leg
        # first row is just the same value as in the adjacent column
        self.table.df.iloc[0,2] = self.table.df.iloc[0,1]

        # the rest of the rows are calculated by adding the previous row's value with the current row's value
        for i in range(1, self.table.df.shape[0]):
            self.table.df.iloc[i,2] = self.table.df.iloc[i - 1,2] + self.table.df.iloc[i,1]

        # round the "Daily Miles" to 1 decimal place
        self.table.df["Daily Miles"] = np.round(self.table.df["Daily Miles"], decimals=1)


    def recalculate_miles(self):
        # recalculate daily miles

        # get the indices of the rows which have an "x" for campsite
        idx_array = np.where(self.table.df["Campsite"] == "x")
        listCampsiteRows = self.table.df.iloc[idx_array].index.tolist()

        for index, campsiteRow in enumerate(listCampsiteRows):
            if campsiteRow == listCampsiteRows[0]:
                # calculate mileages from very first row to row of the campsite
                self.calculate_miles_in_segment(0, campsiteRow)

            else:
                # calculate mileages from starting row (which is 1 greater than the previous campsite row) to row of the campsite
                # (increment the endRow so that range function in called function will calculate for the end row)
                self.calculate_miles_in_segment(listCampsiteRows[index - 1] + 1, campsiteRow + 1)

        # now calculate the mileages for the last day
        self.calculate_miles_in_segment(listCampsiteRows[-1] + 1, self.table.df.shape[0])

        self.table.df["Miles"] = self.table.df["Miles"].astype(float).round(1)
        self.table.df["Daily Miles"] = self.table.df["Daily Miles"].astype(float).round(1)

        # update the data in the widget so the changes display on the screen
        for i in range(self.table.rowCount()):
            for j in range(1, self.table.columnCount()-1):
                self.table.setItem(i, j, QTableWidgetItem(str(self.table.df.iloc[i,j])))


    def calculate_miles_in_segment(self, startRow, endRow):
        # calculate mileages from starting row to row of the campsite
        # starting row is just the value from the Miles column
        self.table.df.iloc[startRow,2] = self.table.df.iloc[startRow,1]

        # the rest of the rows are calculated by adding the previous row's value in "Daily Miles" column with the current row's value in "Miles" column
        for i in range(startRow + 1, endRow):
            self.table.df.iloc[i, 2] = self.table.df.iloc[i - 1, 2] + self.table.df.iloc[i, 1]






if __name__ == '__main__':
    root = tkinter.Tk()
    root.withdraw()


    app = QApplication(sys.argv)

    window = DFEditor()
    window.setWindowTitle("Trail Campsite Planner")
    window.show()

    sys.exit(app.exec_())