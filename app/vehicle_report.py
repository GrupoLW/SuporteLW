from utils.report import Report
from utils.vehicle import Vehicle
from models.vehicle_DAO import find_vehicle_in_db
from views.spreadsheet import concatenate_database_results, search_for_data


from PySide6.QtCore import Signal, QObject

import pandas as pd
import time

class VehicleReport(Report, QObject):
    status_report = Signal(str)
    report_finished = Signal(str)
    error_report = Signal(str)
    terminated = Signal(str)

    def __init__(self, connection, input, output, file_name):
        super().__init__(input, output, file_name)
        self.con = connection


    def make_vehicle_report(self):
        self.read_spreadsheet()
        print('Lendo a planilha...')
        self.status_report.emit('Lendo a planilha...')

        data_sought = search_for_data(self.table_read, 'placa')
        
        if data_sought:
            self.table_read = self.table_read.rename(columns={data_sought: 'Placa Fornecida'})
            self.table_read['Placa Fornecida'] = self.table_read['Placa Fornecida'].apply(Vehicle.clean_data)
        
        data_sought = search_for_data(self.table_read, 'renavam')

        if data_sought:
            self.table_read = self.table_read.rename(columns={data_sought: 'Renavam Fornecido'})
            self.table_read['Renavam Fornecido'] = self.table_read['Renavam Fornecido'].apply(Vehicle.clean_data)
        
        
        data_sought = search_for_data(self.table_read, 'chassi')

        if data_sought:
            self.table_read = self.table_read.rename(columns={data_sought: 'Chassi Fornecido'})
            self.table_read['Chassi Fornecido'] = self.table_read['Chassi Fornecido'].apply(Vehicle.clean_data)
        
        data_sought = search_for_data(self.table_read, 'uf')

        if data_sought:
            self.table_read = self.table_read.rename(columns={data_sought: 'UF Fornecida'})
            self.table_read['UF Fornecida'] = self.table_read['UF Fornecida'].apply(Vehicle.clean_data)


        original_columns = list(self.table_read.columns)
        df_table_read_info = self.table_read
        

        self.status_report.emit('Leitura da planilha finalizada...')

        
        df_result = pd.DataFrame()
        database_info = pd.DataFrame()


        print('DF antes da consulta\n', df_table_read_info)
        if 'Placa Fornecida' in original_columns:
            self.status_report.emit('Consultando pela placa...')
            placas = df_table_read_info.loc[~df_table_read_info['Placa Fornecida'].isna(), 'Placa Fornecida'].to_list()
        
            database_info = find_vehicle_in_db(self.con, 'placa', placas)
            database_info['Análise Veículo'] = 'Encontrado pela Placa'

            

            df_table_read_info = pd.merge(left=df_table_read_info, right=database_info, how='left', left_on='Placa Fornecida', right_on='placa')

            
            
            df_result = concatenate_database_results(df_result, df_table_read_info)

            print(df_result)
            df_table_read_info = df_result.loc[df_result['id_veic'].isna()][original_columns]



            
            if 'id_veic' in df_result.columns:
                df_result = df_result.loc[~df_result['id_veic'].isna()]

            print('Resultado\n', df_result)
            print('Para consulta\n', df_table_read_info)
            if df_table_read_info.empty == False:
                self.status_report.emit('Invertendo as placas e consultando novamente ...')
                df_table_read_info['Placa Fornecida'] = df_table_read_info['Placa Fornecida'].apply(Vehicle.static_reverse_the_plate_pattern)
                placas = df_table_read_info.loc[~df_table_read_info['Placa Fornecida'].isna(), 'Placa Fornecida'].to_list()

                try:
                    database_info = find_vehicle_in_db(self.con, 'placa', placas)
                    database_info['Análise Veículo'] = 'Encontrado pela Placa em outro padrão'
                except Exception:
                    time.sleep(2)

                df_table_read_info = pd.merge(left=df_table_read_info, right=database_info, how='left', left_on='Placa Fornecida', right_on='placa')


                df_result = concatenate_database_results(df_result, df_table_read_info)
                
                df_table_read_info = df_result.loc[df_result['id_veic'].isna()][original_columns]

                if 'id_veic' in df_result.columns:
                    df_result = df_result.loc[~df_result['id_veic'].isna()]

                print('Resultado\n', df_result)
                print('Para consulta\n', df_table_read_info)

        if 'Renavam Fornecido' in original_columns:
            self.status_report.emit('Consultando pelo renavam ...')
            df_table_read_info['Renavam Fornecido'] = df_table_read_info['Renavam Fornecido'].apply(Vehicle.renavam_with_11_digits)
            
            list_renavam = df_table_read_info.loc[~df_table_read_info['Renavam Fornecido'].isna(), 'Renavam Fornecido'].to_list()

            try:
                database_info = find_vehicle_in_db(self.con, 'renavam', list_renavam)
                database_info['Análise Veículo'] = 'Encontrado pelo Renavam'
            except Exception:
                time.sleep(2)


            df_table_read_info = pd.merge(left=df_table_read_info, right=database_info, how='left', left_on='Renavam Fornecido', right_on='renavam')

            df_result = concatenate_database_results(df_result, df_table_read_info)
            df_table_read_info = df_result.loc[df_result['id_veic'].isna()][original_columns]

            if 'id_veic' in df_result.columns:
                df_result = df_result.loc[~df_result['id_veic'].isna()]

            print('Resultado\n', df_result)
            print('Para consulta\n', df_table_read_info)
        

        if 'Chassi Fornecido' in original_columns:
            self.status_report.emit('Consultando pelo Chassi ...')

            list_chassi = df_table_read_info.loc[~df_table_read_info['Chassi Fornecido'].isna(), 'Chassi Fornecido'].to_list()

            try:
                database_info = find_vehicle_in_db(self.con, 'chassi', list_chassi)
                database_info['Análise Veículo'] = 'Encontrado pelo Chassi'
            except Exception:
                time.sleep(2)

            df_table_read_info = pd.merge(left=df_table_read_info, right=database_info, how='left', left_on='Chassi Fornecido', right_on='chassi')

            df_result = concatenate_database_results(df_result, df_table_read_info)

            print('Resultado\n', df_result)
            print('Para consulta\n', df_table_read_info)

        
        print('Resultado\n', df_result)
        print('Para consulta\n', df_table_read_info)


        if 'Análise Veículo' in df_result.columns:
            df_result.loc[df_result['Análise Veículo'].isna(), 'Análise Veículo'] = 'Placa não cadastrada em nosso sistema'
            if 'UF Fornecida' in original_columns:
                df_result.loc[(df_result['UF Fornecida'] != df_result['uf_veic']) & (~df_result['uf_veic'].isna()), 'Análise Emplacamento'] = 'UF Divergente'
                df_result.loc[df_result['Análise Emplacamento'].isna(), 'Análise Emplacamento'] = 'Cadastro Atualizado'
            if 'Placa Fornecida' in original_columns:
                df_result.loc[(df_result['Placa Fornecida'] != df_result['placa']) & (~df_result['placa'].isna()), 'Análise Placa'] = 'Placa Divergente'
                df_result.loc[df_result['Análise Placa'].isna(), 'Análise Placa'] = 'Cadastro Atualizado'
            if 'Renavam Fornecido' in original_columns:
                df_result.loc[(df_result['Renavam Fornecido'] != df_result['renavam']) & (~df_result['renavam'].isna()), 'Análise Renavam'] = 'Renavam Divergente'
                df_result.loc[df_result['Análise Renavam'].isna(), 'Análise Renavam'] = 'Cadastro Atualizado'
            if 'Chassi Fornecido' in original_columns:
                df_result.loc[(df_result['Chassi Fornecido'] != df_result['chassi']) & (~df_result['chassi'].isna()), 'Análise Chassi'] = 'Chassi Divergente'
                df_result.loc[df_result['Análise Chassi'].isna(), 'Análise Chassi'] = 'Cadastro Atualizado'

        print('Resultado\n', df_result)
        print('Para consulta\n', df_table_read_info)

        try:
            self.status_report.emit('Gerando o relatório ...')
            self.produce_report(df_result)
            self.report_finished.emit('O relatório foi gerado com sucesso!!')
        except Exception:
            self.error_report.emit('Um erro ocorreu na hora de escrever o relatório')
        self.terminated.emit('Processo finalizado')




if __name__ == '__main__':
    print('Hello')



