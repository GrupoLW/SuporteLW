from views.spreadsheet import read_the_spreadsheet, write_spreadsheet
from PySide6.QtCore import QObject

class Report (QObject):

    def __init__(self, input, output, file_name):
        super().__init__()
        self._input = input
        self._output = output
        self._file_name = file_name
        self.table_read = None
        
    @property
    def input(self):
        return self._input
    
    @input.setter
    def input(self, input):
        self._input = input

    @property
    def output(self):
        return self._output
    
    @output.setter
    def output(self, output):
        self._output = output

    
    @property
    def file_name(self):
        return self._file_name
    
    @file_name.setter
    def file_name(self, file_name):
        self._file_name = file_name


    def read_spreadsheet(self):
        if self.input != '':
            self.table_read = read_the_spreadsheet(self.input)
        else:
            print('Não foi fornecido o caminho')



    def produce_report(self, df_result):
        write_spreadsheet(df_result, self.output, self.file_name)

    @staticmethod
    def store_the_data_provided(row, column, row_report: list):
        data = None
        if column is not None:
            data = row[column]
            row_report.append(data)
        return data
    



