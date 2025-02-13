import pandas as pd
from PySide6.QtCore import  QObject, Signal



from app.query_info import centralizadores_uf_fonte_consulta
from views.spreadsheet import write_spreadsheet
from utils.vehicle import Vehicle
from app.query_info import centralizadores_uf_fonte_consulta, federal_agencies, centralizadores_estaduais_fonte_consulta, cod_orgao_fonte_consulta_especificidade

class AnalyseAutuadorWithID(QObject):

    def __init__(self, connection, output: str, file_name: str, id_multas: list, date: str):
        self.con = connection
        self.output = output
        self.file_name = file_name
        self.id_multas = id_multas
        self.date = date
        self.make_query()


    def _query(self, id_veiculo, fonte_consulta, data_hora):
        print(id_veiculo, fonte_consulta, data_hora)
        query = """SELECT vuc.data_hora from veiculoUltimaConsulta vuc WHERE vuc.id_veiculo = %s
        and vuc.fonte_consulta = %s and vuc.data_hora >= %s
        GROUP by vuc.id_veiculo LIMIT 1;"""
        try:
            df = pd.read_sql(sql=query, con=self.con, params=(id_veiculo, fonte_consulta, data_hora))
        except Exception as e:
            print(f"Erro na execução da consulta: {e}")
            return None

        if df.empty:
            return None
        else:
            return df['data_hora'].iloc[0]



    def make_query(self):
        placeholder_sequence = ', '.join(['%s'] * len(self.id_multas))

        query = f"""SELECT m.id as id_multa, v.uf_veic, v.placa, m.autoInfracao, m.situacao, o.nome orgaoNome, m.id_veiculo , m.dataHoraUltimaLeitura , m.estado , m.fonteConsulta , m.fonteConsultaBoleto , m.orgao as cod_orgao,
        mo.fonte_consulta as fonteConsultaCodOrgao
        from multaDetalhada m 
        INNER JOIN veiculos v ON (v.id = m.id_veiculo)
        LEFT JOIN orgao o ON (o.cod_orgao = m.orgao)
        left join miner_orgao mo on (m.orgao = mo.cod_orgao)
        where m.id in ({placeholder_sequence});"""

        df = pd.read_sql(sql=query, con=self.con, params=self.id_multas)

        if df.loc[df['fonteConsultaCodOrgao'].isna() == False].empty == False:
            df['Consulta cod_orgao'] = df.loc[df['fonteConsultaCodOrgao'].isna() == False].apply(lambda row: self._query(id_veiculo=row['id_veiculo'], fonte_consulta=row['fonteConsultaCodOrgao'], data_hora=self.date), axis=1)
            df['Consulta cod_orgao'].loc[df['Consulta cod_orgao'].isna() == True] = 'Sem Consulta'
        else:
            df['Consulta cod_orgao'] = 'Não consultamos este órgão autuador'

        
        if df.loc[df['fonteConsulta'].isna() == False].empty == False:
            df['Consulta fonteConsulta'] = df.loc[df['fonteConsulta'].isna() == False].apply(lambda row: self._query(id_veiculo=row['id_veiculo'], fonte_consulta=row['fonteConsulta'], data_hora=self.date), axis=1)
            df['Consulta fonteConsulta'].loc[df['Consulta fonteConsulta'].isna() == True] = 'Sem Consulta'
        else:
            df['Consulta fonteConsulta'] = 'Sem fonte consulta'

        if df.loc[df['fonteConsultaBoleto'].isna() == False].empty == False:
            df['Consulta fonteConsultaBoleto'] = df.loc[df['fonteConsultaBoleto'].isna() == False].apply(lambda row: self._query(id_veiculo=row['id_veiculo'], fonte_consulta=row['fonteConsultaBoleto'], data_hora=self.date), axis=1)
            df['Consulta fonteConsultaBoleto'].loc[df['Consulta fonteConsultaBoleto'].isna() == True] = 'Sem Consulta'
        else:
            df['Consulta fonteConsultaBoleto'] = 'Sem fonte consulta'

        if self.output.strip() != '' and self.file_name.strip() != '':
            try:
                write_spreadsheet(df_result=df, output=self.output, file_name=self.file_name)
            except Exception:
                print('Deu ruim')


class AnalyseAutuador(QObject):

    def __init__(self, connection, output: str, file_name: str, id_multas: list, date: str):
        self.con = connection
        self.output = output
        self.file_name = file_name
        self.id_multas = id_multas
        self.date = date
        self.make_query()


    def _query(self, id_veiculo, fonte_consulta, data_hora):
        print(id_veiculo, fonte_consulta, data_hora)
        query = """SELECT vuc.data_hora from veiculoUltimaConsulta vuc WHERE vuc.id_veiculo = %s
        and vuc.fonte_consulta = %s and vuc.data_hora >= %s
        GROUP by vuc.id_veiculo LIMIT 1;"""
        try:
            df = pd.read_sql(sql=query, con=self.con, params=(id_veiculo, fonte_consulta, data_hora))
        except Exception as e:
            print(f"Erro na execução da consulta: {e}")
            return None

        if df.empty:
            return None
        else:
            return df['data_hora'].iloc[0]



    def make_query(self):
        placeholder_sequence = ', '.join(['%s'] * len(self.id_multas))

        query = f"""SELECT m.id as id_multa, v.uf_veic, v.placa, m.autoInfracao, m.situacao, o.nome orgaoNome, m.id_veiculo , m.dataHoraUltimaLeitura , m.estado , m.fonteConsulta , m.fonteConsultaBoleto , m.orgao as cod_orgao,
        mo.fonte_consulta as fonteConsultaCodOrgao
        from multaDetalhada m 
        INNER JOIN veiculos v ON (v.id = m.id_veiculo)
        LEFT JOIN orgao o ON (o.cod_orgao = m.orgao)
        left join miner_orgao mo on (m.orgao = mo.cod_orgao)
        where m.id in ({placeholder_sequence});"""

        df = pd.read_sql(sql=query, con=self.con, params=self.id_multas)


        if df.loc[df['fonteConsultaCodOrgao'].isna() == False].empty == False:
            df['Consulta cod_orgao'] = df.loc[df['fonteConsultaCodOrgao'].isna() == False].apply(lambda row: self._query(id_veiculo=row['id_veiculo'], fonte_consulta=row['fonteConsultaCodOrgao'], data_hora=self.date), axis=1)
            df['Consulta cod_orgao'].loc[df['Consulta cod_orgao'].isna() == True] = 'Sem Consulta'
        else:
            df['Consulta cod_orgao'] = 'Não consultamos este órgão autuador'
        
        if df.loc[df['fonteConsulta'].isna() == False].empty == False:
            df['Consulta fonteConsulta'] = df.loc[df['fonteConsulta'].isna() == False].apply(lambda row: self._query(id_veiculo=row['id_veiculo'], fonte_consulta=row['fonteConsulta'], data_hora=self.date), axis=1)
            df['Consulta fonteConsulta'].loc[df['Consulta fonteConsulta'].isna() == True] = 'Sem Consulta'
        else:
            df['Consulta fonteConsulta'] = 'Sem fonte consulta'

        if df.loc[df['fonteConsultaBoleto'].isna() == False].empty == False:
            df['Consulta fonteConsultaBoleto'] = df.loc[df['fonteConsultaBoleto'].isna() == False].apply(lambda row: self._query(id_veiculo=row['id_veiculo'], fonte_consulta=row['fonteConsultaBoleto'], data_hora=self.date), axis=1)
            df['Consulta fonteConsultaBoleto'].loc[df['Consulta fonteConsultaBoleto'].isna() == True] = 'Sem Consulta'
        else:
            df['Consulta fonteConsultaBoleto'] = 'Sem fonte consulta'

        if self.output.strip() != '' and self.file_name.strip() != '':
            try:
                write_spreadsheet(df_result=df, output=self.output, file_name=self.file_name)
            except Exception:
                print('Deu ruim')







class AnalyseUF(QObject):
    def __init__(self, connection, output: str, file_name: str, plates: list, date: str):
        self.con = connection
        self.output = output
        self.file_name = file_name
        self.plates = plates
        self.date = date
        self.make_query()

    def search_vehicle_in_db(self, df, param):
        placeholder_sequence = ', '.join(['%s'] * len(param))
        query = f"""SELECT v.placa as placa_lw_x , v.uf_veic as uf_veic_x from veiculos v where v.placa in ({placeholder_sequence});"""
        df_result = pd.read_sql(sql=query, con=self.con, params=param)
        df = pd.merge(df, df_result,how='left', left_on=['Placa'], right_on='placa_lw_x')
        df['placa_lw'].fillna(df['placa_lw_x'], inplace=True)
        df['uf_veic'].fillna(df['uf_veic_x'], inplace=True)
        df.drop(['placa_lw_x', 'uf_veic_x'], axis=1, inplace=True)
        return df

    def _query(self, plate, fonte_consulta, data_hora):
        print(plate, fonte_consulta, data_hora)
        query = """SELECT vuc.data_hora from veiculoUltimaConsulta vuc 
        WHERE vuc.id_veiculo = (SELECT v.id FROM veiculos v where v.placa = %s)
        and vuc.fonte_consulta = %s and vuc.data_hora >= %s
        GROUP by vuc.id_veiculo LIMIT 1;"""
        df = pd.read_sql(sql=query, con=self.con, params=(plate,fonte_consulta, data_hora))
        print (df)
        if df.empty:
            return None
        else:
            result = df['data_hora']
            return result


    def make_query(self):
        df = pd.DataFrame({'Placa': self.plates, 'placa_lw': None, 'uf_veic': None})
        df['Placa'].astype(str)

        df = self.search_vehicle_in_db(df=df, param=self.plates)

        #Invertendo a placa
        if df.loc[df['placa_lw'].isna()].empty == False:
            df.loc[df['placa_lw'].isna(), 'Placa'] = df.loc[df['placa_lw'].isna(), 'Placa'].apply(lambda plate: Vehicle.static_reverse_the_plate_pattern(plate))
            plates = df.loc[df['placa_lw'].isna(), 'Placa'].to_list()
            df = self.search_vehicle_in_db(df=df, param=plates)

        if df.loc[df['uf_veic'].isin(centralizadores_uf_fonte_consulta.keys())].empty == False:
            df['Consulta_uf'] = df.loc[df['uf_veic'].isin(centralizadores_uf_fonte_consulta.keys())].apply(lambda row: self._query(plate=row['placa_lw'], fonte_consulta=centralizadores_uf_fonte_consulta[row['uf_veic']], data_hora=self.date), axis=1)
            df['Consulta_uf'].loc[df['Consulta_uf'].isna() == True] = 'Não consultamos esta UF'
        else:
            df['Consulta_uf'] = 'Não consultamos esta UF'

        if self.output.strip() != '' and self.file_name.strip() != '':
            try:
                write_spreadsheet(df_result=df, output=self.output, file_name=self.file_name)
            except Exception:
                print('Deu ruim')
        


class AnalyseAll(QObject):
    status_report = Signal(str)
    report_finished = Signal(str)
    error_report = Signal(str)
    terminated = Signal(str)

    def __init__(self, connection, output: str, file_name: str, id_multas: list, date: str):
        super().__init__()
        self.con = connection
        self.output = output
        self.file_name = file_name
        self.id_multas = id_multas
        self.date = date

    def _query(self, id_veiculo, fonte_consulta, data_hora):
        print(id_veiculo, fonte_consulta, data_hora)
        query = """SELECT vuc.data_hora from veiculoUltimaConsulta vuc WHERE vuc.id_veiculo = %s
        and vuc.fonte_consulta = %s and vuc.data_hora >= %s
        GROUP by vuc.id_veiculo LIMIT 1;"""
        try:
            df = pd.read_sql(sql=query, con=self.con, params=(id_veiculo, fonte_consulta, data_hora))
        except Exception as e:
            print(f"Erro na execução da consulta: {e}")
            return None

        if df.empty:
            return None
        else:
            return df['data_hora'].iloc[0]



    def make_query(self):
        placeholder_sequence = ', '.join(['%s'] * len(self.id_multas))
        self.status_report.emit('Procurando as multas no Banco')

        query = f"""SELECT m.id as id_multa, v.uf_veic, v.placa, m.autoInfracao, m.situacao, o.nome orgaoNome, m.id_veiculo , m.dataHoraUltimaLeitura , m.estado , m.fonteConsulta , m.fonteConsultaBoleto , m.orgao as cod_orgao,
        mo.fonte_consulta as fonteConsultaCodOrgao
        from multaDetalhada m 
        INNER JOIN veiculos v ON (v.id = m.id_veiculo)
        LEFT JOIN orgao o ON (o.cod_orgao = m.orgao)
        left join miner_orgao mo on (m.orgao = mo.cod_orgao)
        where m.id in ({placeholder_sequence});"""

        df = pd.read_sql(sql=query, con=self.con, params=self.id_multas)

        if df.loc[df['uf_veic'].isin(centralizadores_uf_fonte_consulta.keys())].empty == False:
            self.status_report.emit('Verificando as consultas no Emplacametnto')
            df['Consulta_uf'] = df.loc[df['uf_veic'].isin(centralizadores_uf_fonte_consulta.keys())].apply(lambda row: self._query(id_veiculo=row['id_veiculo'], fonte_consulta=centralizadores_uf_fonte_consulta[row['uf_veic']], data_hora=self.date), axis=1)
            df['Consulta_uf'].loc[df['Consulta_uf'].isna() == True] = 'Sem consulta'
        else:
            df['Consulta_uf'] = 'Não consultamos esta UF'

        if df.loc[df['fonteConsultaCodOrgao'].isin(federal_agencies)].empty == False:
            df.loc[df['fonteConsultaCodOrgao'].isin(federal_agencies), 'Consulta Centralizador Estado'] = 'Agência Federal (DPRF/DNIT)'
        
        
        if df.loc[~df['fonteConsultaCodOrgao'].isin(federal_agencies)].empty == False:
            self.status_report.emit('Verificando as consultas no Centralizador Estadual')
            df.loc[(~df['fonteConsultaCodOrgao'].isin(federal_agencies)) & (df['estado'].isin(centralizadores_estaduais_fonte_consulta.keys())), 'Consulta Centralizador Estado'] = df.loc[(~df['fonteConsultaCodOrgao'].isin(federal_agencies)) & (df['estado'].isin(centralizadores_estaduais_fonte_consulta.keys()))].apply(lambda row: self._query(id_veiculo=row['id_veiculo'], fonte_consulta=centralizadores_estaduais_fonte_consulta[row['estado']], data_hora=self.date), axis=1)
            df['Consulta Centralizador Estado'].loc[df['Consulta Centralizador Estado'].isna() == True] = 'Sem consulta'


        if df.loc[df['cod_orgao'].isin(cod_orgao_fonte_consulta_especificidade.keys())].empty == False:
            df.loc[df['cod_orgao'].isin(cod_orgao_fonte_consulta_especificidade.keys()), 'Consulta cod_orgao'] = df.loc[df['cod_orgao'].isin(cod_orgao_fonte_consulta_especificidade.keys())].apply(lambda row: self._query(id_veiculo=row['id_veiculo'], fonte_consulta=cod_orgao_fonte_consulta_especificidade[row['cod_orgao']], data_hora=self.date), axis=1)


        if df.loc[(~df['cod_orgao'].isin(cod_orgao_fonte_consulta_especificidade.keys())) & (df['fonteConsultaCodOrgao'].isna() == False)].empty == False:
            self.status_report.emit('Verificando as consultas no Código do órgão autuador')
            df.loc[(df['fonteConsultaCodOrgao'].isna() == False) & (~df['cod_orgao'].isin(cod_orgao_fonte_consulta_especificidade.keys())), 'Consulta cod_orgao'] = df.loc[(df['fonteConsultaCodOrgao'].isna() == False) & (~df['cod_orgao'].isin(cod_orgao_fonte_consulta_especificidade.keys()))].apply(lambda row: self._query(id_veiculo=row['id_veiculo'], fonte_consulta=row['fonteConsultaCodOrgao'], data_hora=self.date), axis=1)
            df['Consulta cod_orgao'].loc[df['Consulta cod_orgao'].isna() == True] = 'Sem Consulta'
        else:
            df['Consulta cod_orgao'] = 'Não consultamos este órgão autuador'
        

        if df.loc[df['fonteConsulta'].isna() == False].empty == False:
            self.status_report.emit('Verificando as consultas na fonte consulta')
            df['Consulta fonteConsulta'] = df.loc[df['fonteConsulta'].isna() == False].apply(lambda row: self._query(id_veiculo=row['id_veiculo'], fonte_consulta=row['fonteConsulta'], data_hora=self.date), axis=1)
            df['Consulta fonteConsulta'].loc[df['Consulta fonteConsulta'].isna() == True] = 'Sem Consulta'
        else:
            df['Consulta fonteConsulta'] = 'Sem fonte consulta'

        if df.loc[df['fonteConsultaBoleto'].isna() == False].empty == False:
            self.status_report.emit('Verificando as consultas na fonte consulta Boleto')
            df['Consulta fonteConsultaBoleto'] = df.loc[df['fonteConsultaBoleto'].isna() == False].apply(lambda row: self._query(id_veiculo=row['id_veiculo'], fonte_consulta=row['fonteConsultaBoleto'], data_hora=self.date), axis=1)
            df['Consulta fonteConsultaBoleto'].loc[df['Consulta fonteConsultaBoleto'].isna() == True] = 'Sem Consulta'
        else:
            df['Consulta fonteConsultaBoleto'] = 'Sem fonte consulta'
        
        if self.output.strip() != '' and self.file_name.strip() != '':
            try:
                self.status_report.emit('Criando o relatório')
                write_spreadsheet(df_result=df, output=self.output, file_name=self.file_name)
                self.terminated.emit('Relatório criado')
            except Exception:
                self.terminated.emit('Deu ruim na hora de tentar criar o relatório')
                print('Deu ruim')





if __name__ == '__main__':
    print('Hello')



