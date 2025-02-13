from utils.report import Report, StandardProcess
from utils.fine import Fine
from models.vehicle_DAO import find_vehicle_in_db
from models.fine_DAO import search_fine_in_db



class ReportFine (Report):
    def __init__(self, input, output, file_name):
        super().__init__(input,output, file_name )
        self.process = StandardProcess(self)
        self.make_report_fine()


    def make_report_fine(self):
        self.report_column_names.extend(['Status Veículo', 'Status Infração'])
        help = True
        for row in self.table_read.values:
            row_report = []

            vehicle_read = None
            vehicle_read = self.process.standard_vehicle_storage(row, row_report)

            ait_read = self.process.standard_fine_storage(row, row_report)

            status_vehicle = ''
            status_multa = ''
            vehicle_in_db = None
            id_vehicle = None
            fine_in_db = None


            if vehicle_read is None:
                status_vehicle = 'Dados do veículo incorreto'
            else:
                vehicle_in_db = find_vehicle_in_db(vehicle_read)
                if vehicle_in_db is not None:
                    id_vehicle = vehicle_in_db[0][0]
                    status_vehicle = 'Veículo cadastrado'
                else:
                    status_vehicle = 'Veículo não cadastrado'

            row_report.append(status_vehicle)
            if ait_read is None:
                status_multa = 'AIT não fornecido'
            elif ait_read is not None and id_vehicle is not None:
                column_name ,fine_in_db = search_fine_in_db(id_vehicle, ait_read.ait)
                if fine_in_db:
                    if help:
                        help=False
                        self.report_column_names.extend(column_name)
                    status_multa = 'Infração Localizada'
                else:
                    status_multa = 'Infração não localizada'
            else:
                status_multa = 'Veiculo não cadastrado'

            row_report.append(status_multa)

            if fine_in_db is not None:
                row_report.extend(fine_in_db[0])
            else:
                while len(row_report) < len(self.report_column_names):
                    row_report.append('')

            self.table_values.append(row_report)

        print('Colunas', self.report_column_names)
        for row in self.table_values:
            print(row)
        self.produce_report()











if __name__ == '__main__':
    print('implementar')



    