import re
import pandas as pd
from PySide6.QtCore import QObject

from app.query_info import centralizadores_uf_param_consulta, consulta_uf_de_fora_centralizadores, param_ignore, especificidades, federal_agencies
from utils.vehicle import Vehicle

PREFIX_QUERY = 'java -jar LWDataMiner-2.jar placa '
SUFIX_QUERY = [' --d=', ' +todos']

SUFIX_CHROME = ' --chrome --threads=10 '

class QueryFormat(QObject):
    def __init__(self, connection, day: str, recibo: str) -> None:
        if day.strip() == '':
            day = 1
        if recibo.strip() == '':
            recibo = None
        self.con = connection
        self.day = f'--d={day}'
        self.recibo = recibo


class QueryGeneratorAutuador(QueryFormat, QObject):

    def __init__(self, connection, id_multas, day, recibo):
        super().__init__(connection=connection, day=day, recibo=recibo)
        self.id_multas = id_multas
        self.consultas = {}
        self.lista_consultas = []
        self.text = ''
        self.number_of_queries = 0
        self.make_query()

    def remover_caracteres_especiais(self, texto):
        return re.sub(r'[^\w\s,]', '', texto).replace(' ', '')

    def _sort_query(self, elemento):
        ordem = {'mg': 1, 'mgblt': 2, 'dnit': 3, 'dprf': 4, 'dersp': 5, 'detranpe': 6, 'pa': 7, 'df': 8, 'derba': 9, 'pi': 10}
        if elemento in ordem:
            return True
        else:
            return False

    def make_query(self):
        placeholder_sequence = ', '.join(['%s'] * len(self.id_multas))
        query = f"""SELECT m.id as id_multa, (SELECT v.placa from veiculos v where m.id_veiculo = v.id) as placa, m.estado , m.fonteConsulta , m.fonteConsultaBoleto , m.orgao as cod_orgao, 
        (SELECT v.uf_veic  from veiculos v where v.id=m.id_veiculo) as uf_veic , mo.fonte_consulta as fonteConsultaCodOrgao, 
        (select mo.parametro_miner  from miner_orgao mo where mo.cod_orgao = m.orgao LIMIT 1) as parametro_cod_orgao, 
        (select mo.parametro_miner  from miner_orgao mo where mo.fonte_consulta = m.fonteConsulta LIMIT 1) as parametro_fonte_consulta,
        (select mo.parametro_miner  from miner_orgao mo where mo.fonte_consulta = m.fonteConsultaBoleto LIMIT 1) as parametro_fonte_consulta_boleto
        from multaDetalhada m 
        left join miner_orgao mo on (m.orgao = mo.cod_orgao)
        where m.id in ({placeholder_sequence});"""

        cursor = self.con.cursor()
        cursor.execute(query, tuple(self.id_multas))
        result = cursor.fetchall()

        df_result = pd.DataFrame(result, columns=cursor.column_names)
        cursor.close()

        estado_uf = df_result.loc[~df_result['parametro_cod_orgao'].isin(federal_agencies)]['estado'].unique()

        for uf in estado_uf:
            if uf is None:
                continue
            elif uf in consulta_uf_de_fora_centralizadores:
                param_uf = consulta_uf_de_fora_centralizadores[uf]
                if param_uf in self.consultas:
                    plates = set(df_result.loc[df_result['estado'] == uf]['placa'].to_list())
                    self.consultas[param_uf].update(plates)
                else:
                    self.consultas[param_uf] = set(df_result.loc[df_result['estado'] == uf]['placa'].to_list())

        param_cod_orgao = df_result.loc[~df_result['estado'].isin(consulta_uf_de_fora_centralizadores)]['parametro_cod_orgao'].unique()

        for param in param_cod_orgao:
            if param is None or param in param_ignore:
                continue
            elif param in self.consultas:
                plates = set(df_result.loc[df_result['parametro_cod_orgao'] == param]['placa'].to_list())
                self.consultas[param].update(plates)
            else:
                self.consultas[param] = set(df_result.loc[df_result['parametro_cod_orgao'] == param]['placa'].to_list())

        for especificidade in especificidades:
            if especificidade in self.consultas:
                for param in especificidades[especificidade]:
                    if param in self.consultas:
                        self.consultas[param].update(self.consultas[especificidade])
                    else:
                        self.consultas[param] = self.consultas[especificidade]

        for param, plates in self.consultas.items():
            comando_plates = self.remover_caracteres_especiais(str(plates))
            
            extra_param = '--capcloud' if 'prefeitura' in param.lower() else ''

            threads_param = '--threads=1' if param == 'pr' else ''
            pdf_param = ' --pdf' if param == 'pr' else ''

            if self.recibo:
                if param in ['prefeiturasp', 'sc', 'bradesco']:
                    comando_consulta = f'{PREFIX_QUERY}{param} {comando_plates.strip()} {self.day} +todos --recibo={self.recibo}{SUFIX_CHROME} --attblt {extra_param} {threads_param}{pdf_param}'
                else:
                    comando_consulta = f'{PREFIX_QUERY}{param} {comando_plates.strip()} {self.day} +todos --recibo={self.recibo} --attblt {extra_param} {threads_param}{pdf_param}'
            else:
                if param in ['prefeiturasp', 'sc', 'bradesco']:
                    comando_consulta = f'{PREFIX_QUERY}{param} {comando_plates.strip()} {self.day} +todos{SUFIX_CHROME} --attblt {extra_param} {threads_param}{pdf_param}'
                else:
                    comando_consulta = f'{PREFIX_QUERY}{param} {comando_plates.strip()} {self.day} +todos --attblt {extra_param} {threads_param}{pdf_param}'

            if self._sort_query(param):
                self.lista_consultas.insert(0, comando_consulta.strip())
            else:
                self.lista_consultas.append(comando_consulta.strip())

        self.text = '\n'.join(self.lista_consultas)
        self.make_number_of_queries()

    def make_number_of_queries(self):
        for consulta in self.consultas:
            self.number_of_queries += len(self.consultas[consulta])

class QueryGeneratorUF(QueryFormat, QObject):

    def __init__(self, connection, plates, day, recibo):
        super().__init__(connection=connection, day=day, recibo=recibo)
        self.plates = plates
        self.consultas = {}
        self.lista_consultas = []
        self.nao_consultamos = {}
        self.text = ''
        self.number_of_queries = 0
        self.make_query()

    def remover_caracteres_especiais(self, texto):
        return re.sub(r'[^\w\s,]', '', texto).replace(' ', '')


    def _sort_query(self, elemento):
        ordem = {'mg': 1, 'detranpe': 2, 'pa': 3, 'df': 4, 'pi': 5}
        if elemento in ordem:
            return True
        else:
            return False

    def search_vehicle_in_db(self, df, param):
        placeholder_sequence = ', '.join(['%s'] * len(param))
        query = f"""SELECT v.placa as placa_lw_x , v.uf_veic as uf_veic_x from veiculos v where v.placa in ({placeholder_sequence});"""
        df_result = pd.read_sql(sql=query, con=self.con, params=param)
        df = pd.merge(df, df_result,how='left', left_on=['Placa'], right_on='placa_lw_x')
        df['placa_lw'].fillna(df['placa_lw_x'], inplace=True)
        df['uf_veic'].fillna(df['uf_veic_x'], inplace=True)
        df.drop(['placa_lw_x', 'uf_veic_x'], axis=1, inplace=True)
        return df

    def make_query(self):
        df = pd.DataFrame({'Placa': self.plates, 'placa_lw': None, 'uf_veic': None})
        df['Placa'].astype(str)

        df = self.search_vehicle_in_db(df=df, param=self.plates)

        if df.loc[df['placa_lw'].isna()].empty == False:
            df.loc[df['placa_lw'].isna(), 'Placa'] = df.loc[df['placa_lw'].isna(), 'Placa'].apply(lambda plate: Vehicle.static_reverse_the_plate_pattern(plate))
            plates = df.loc[df['placa_lw'].isna(), 'Placa'].to_list()
            df = self.search_vehicle_in_db(df=df, param=plates)

        uf_consultas = df['uf_veic'].unique()

        for uf in uf_consultas:
            if uf in centralizadores_uf_param_consulta:
                param_uf = centralizadores_uf_param_consulta[uf]
                if param_uf in self.consultas:
                    plates = set(df.loc[df['uf_veic'] == uf]['placa_lw'].to_list())
                    self.consultas[param_uf].update(plates)
                else:
                    self.consultas[param_uf] = set(df.loc[df['uf_veic'] == uf]['placa_lw'].to_list())
            else:
                plates = set(df.loc[df['uf_veic'] == uf]['placa_lw'].to_list())
                if uf in self.nao_consultamos:
                    self.nao_consultamos[uf].update(plates)
                else:
                    self.nao_consultamos[uf] = plates

        # Adicionando consultas para as federal_agencies (dnit e dprf)
        valid_plates = set(df['placa_lw'].dropna().to_list())
        if not valid_plates:
            valid_plates = set(self.plates)
        for agency in federal_agencies:
            if agency in self.consultas:
                self.consultas[agency].update(valid_plates);
            else:
                self.consultas[agency] = valid_plates.copy()

        for param, plates in self.consultas.items():
            comando_plates = self.remover_caracteres_especiais(str(plates))
            extra_param = '--capcloud' if 'prefeitura' in param.lower() else ''
            threads_param = '--threads=1' if param == 'pr' else ''
            pdf_param = ' --pdf' if param == 'pr' else ''
            if self.recibo:
                if param in ['prefeiturasp', 'sc', 'bradesco']:
                    comando_consulta = f'{PREFIX_QUERY}{param} {comando_plates.strip()} {self.day} +todos --recibo={self.recibo}{SUFIX_CHROME} --attblt {extra_param} {threads_param}{pdf_param}'
                else:
                    comando_consulta = f'{PREFIX_QUERY}{param} {comando_plates.strip()} {self.day} +todos --recibo={self.recibo} --attblt {extra_param} {threads_param}{pdf_param}'
            else:
                if param in ['prefeiturasp', 'sc', 'bradesco']:
                    comando_consulta = f'{PREFIX_QUERY}{param} {comando_plates.strip()} {self.day} +todos{SUFIX_CHROME} --attblt {extra_param} {threads_param}{pdf_param}'
                else:
                    comando_consulta = f'{PREFIX_QUERY}{param} {comando_plates.strip()} {self.day} +todos --attblt {extra_param} {threads_param}{pdf_param}'

            if self._sort_query(param):
                self.lista_consultas.insert(0, comando_consulta.strip())
            else:
                self.lista_consultas.append(comando_consulta.strip())

        self.lista_consultas.append(f'\nUF que não consultamos:{str(self.nao_consultamos)}')

        if df.loc[df['placa_lw'].isna()].empty == False:
            veiculo_nao_cadastrado = set(df.loc[df['placa_lw'].isna()]['Placa'].to_list())
            self.lista_consultas.append(f'\n\nVeiculos não cadastrados:\n{veiculo_nao_cadastrado}')


        self.text = '\n'.join(self.lista_consultas)
        self.make_number_of_queries()

    def make_number_of_queries(self):
        for consulta in self.consultas:
            self.number_of_queries += len(self.consultas[consulta])



class QueryGeneratorUFWithID(QueryFormat, QObject):

    def __init__(self, connection, id_multas, day, recibo):
        super().__init__(connection=connection, day=day, recibo=recibo)
        self.id_multas = id_multas
        self.consultas = {}
        self.lista_consultas = []
        self.text = ''
        self.number_of_queries = 0
        self.make_query()

    def remover_caracteres_especiais(self, texto):
        return re.sub(r'[^\w\s,]', '', texto).replace(' ', '')


    def _sort_query(self, elemento):
        ordem = {'mg': 1, 'mgblt': 2,'dnit': 3, 'dprf': 4, 'dersp': 5, 'detranpe': 6, 'pa': 7, 'df': 8, 'derba': 9, 'pi': 10}
        if elemento in ordem:
            return True
        else:
            return False

    def make_query(self):
        placeholder_sequence = ', '.join(['%s'] * len(self.id_multas))
        query = f"""SELECT m.id as id_multa, (SELECT v.placa from veiculos v where m.id_veiculo = v.id) as placa, m.estado , m.fonteConsulta , m.fonteConsultaBoleto , m.orgao as cod_orgao, 
        (SELECT v.uf_veic  from veiculos v where v.id=m.id_veiculo) as uf_veic , mo.fonte_consulta as fonteConsultaCodOrgao, 
        (select mo.parametro_miner  from miner_orgao mo where mo.cod_orgao = m.orgao LIMIT 1) as parametro_cod_orgao, 
        (select mo.parametro_miner  from miner_orgao mo where mo.fonte_consulta = m.fonteConsulta LIMIT 1) as parametro_fonte_consulta,
        (select mo.parametro_miner  from miner_orgao mo where mo.fonte_consulta = m.fonteConsultaBoleto LIMIT 1) as parametro_fonte_consulta_boleto
        from multaDetalhada m 
        left join miner_orgao mo on (m.orgao = mo.cod_orgao)
        where m.id in ({placeholder_sequence});"""

        cursor = self.con.cursor()
        cursor.execute(query, tuple(self.id_multas))
        result = cursor.fetchall()

        df_result = pd.DataFrame(result, columns=cursor.column_names)
        cursor.close()

        uf_veic_list = df_result['uf_veic'].unique()

        for uf in uf_veic_list:
            if uf == None:
                continue
            elif uf in centralizadores_uf_param_consulta:
                param_uf = centralizadores_uf_param_consulta[uf]
                if param_uf in self.consultas:
                    plates = set(df_result.loc[df_result['uf_veic'] == uf]['placa'].to_list())
                    self.consultas[param_uf].update(plates)
                else:
                    self.consultas[param_uf] = set(df_result.loc[df_result['uf_veic'] == uf]['placa'].to_list())

        for param, plates in self.consultas.items():
            comando_plates = self.remover_caracteres_especiais(str(plates))
            extra_param = '--capcloud' if 'prefeitura' in param.lower() else ''
            threads_param = '--threads=1' if param == 'pr' else ''
            pdf_param = ' --pdf' if param == 'pr' else ''
            if self.recibo:
                if param in ['prefeiturasp', 'sc', 'bradesco']:
                    comando_consulta = f'{PREFIX_QUERY}{param} {comando_plates.strip()} {self.day} +todos --recibo={self.recibo}{SUFIX_CHROME} --attblt {extra_param} {threads_param}{pdf_param}'
                else:
                    comando_consulta = f'{PREFIX_QUERY}{param} {comando_plates.strip()} {self.day} +todos --recibo={self.recibo} --attblt {extra_param} {threads_param}{pdf_param}'
            else:
                if param in ['prefeiturasp', 'sc', 'bradesco']:
                    comando_consulta = f'{PREFIX_QUERY}{param} {comando_plates.strip()} {self.day} +todos{SUFIX_CHROME} --attblt {extra_param} {threads_param}{pdf_param}'
                else:
                    comando_consulta = f'{PREFIX_QUERY}{param} {comando_plates.strip()} {self.day} +todos --attblt {extra_param} {threads_param}{pdf_param}'

            if self._sort_query(param):
                self.lista_consultas.insert(0, comando_consulta.strip())
            else:
                self.lista_consultas.append(comando_consulta.strip())

        self.text = '\n'.join(self.lista_consultas)
        self.make_number_of_queries()

    def make_number_of_queries(self):
        for consulta in self.consultas:
            self.number_of_queries += len(self.consultas[consulta])





class QueryGeneratorUFAutuador(QueryFormat, QObject):

    def __init__(self, connection, id_multas, day, recibo):
        super().__init__(connection=connection, day=day, recibo=recibo)
        self.id_multas = id_multas
        self.consultas = {}
        self.lista_consultas = []
        self.text = ''
        self.number_of_queries = 0
        self.make_query()

    def remover_caracteres_especiais(self, texto):
        return re.sub(r'[^\w\s,]', '', texto).replace(' ', '')


    def _sort_query(self, elemento):
        ordem = {'mg': 1, 'mgblt': 2,'dnit': 3, 'dprf': 4, 'dersp': 5, 'detranpe': 6, 'pa': 7, 'df': 8, 'derba': 9, 'pi': 10}
        if elemento in ordem:
            return True
        else:
            return False


    def make_query(self):
        placeholder_sequence = ', '.join(['%s'] * len(self.id_multas))
        query = f"""SELECT m.id as id_multa, (SELECT v.placa from veiculos v where m.id_veiculo = v.id) as placa, m.estado , m.fonteConsulta , m.fonteConsultaBoleto , m.orgao as cod_orgao, 
        (SELECT v.uf_veic  from veiculos v where v.id=m.id_veiculo) as uf_veic , mo.fonte_consulta as fonteConsultaCodOrgao, 
        (select mo.parametro_miner  from miner_orgao mo where mo.cod_orgao = m.orgao LIMIT 1) as parametro_cod_orgao, 
        (select mo.parametro_miner  from miner_orgao mo where mo.fonte_consulta = m.fonteConsulta LIMIT 1) as parametro_fonte_consulta,
        (select mo.parametro_miner  from miner_orgao mo where mo.fonte_consulta = m.fonteConsultaBoleto LIMIT 1) as parametro_fonte_consulta_boleto
        from multaDetalhada m 
        left join miner_orgao mo on (m.orgao = mo.cod_orgao)
        where m.id in ({placeholder_sequence});"""

        cursor = self.con.cursor()
        cursor.execute(query, tuple(self.id_multas))
        result = cursor.fetchall()

        df_result = pd.DataFrame(result, columns=cursor.column_names)
        cursor.close()

        uf_veic_list = df_result['uf_veic'].unique()

        for uf in uf_veic_list:
            if uf == None:
                continue
            elif uf in centralizadores_uf_param_consulta:
                param_uf = centralizadores_uf_param_consulta[uf]
                if param_uf in self.consultas:
                    plates = set(df_result.loc[df_result['uf_veic'] == uf]['placa'].to_list())
                    self.consultas[param_uf].update(plates)
                else:
                    self.consultas[param_uf] = set(df_result.loc[df_result['uf_veic'] == uf]['placa'].to_list())

        estado_uf = df_result.loc[~df_result['parametro_cod_orgao'].isin(federal_agencies)]['estado'].unique()


        for uf in estado_uf:
            if uf == None:
                continue
            elif uf in consulta_uf_de_fora_centralizadores:
                param_uf = consulta_uf_de_fora_centralizadores[uf]
                if param_uf in self.consultas:
                    plates = set(df_result.loc[df_result['estado'] == uf]['placa'].to_list())
                    self.consultas[param_uf].update(plates)
                else:
                    self.consultas[param_uf] = set(df_result.loc[df_result['estado'] == uf]['placa'].to_list())

        param_cod_orgao = df_result.loc[~df_result['estado'].isin(consulta_uf_de_fora_centralizadores)]['parametro_cod_orgao'].unique()

        for param in param_cod_orgao:
            if param == None or param in param_ignore:
                continue
            elif param in self.consultas:
                plates = set(df_result.loc[df_result['parametro_cod_orgao'] == param]['placa'].to_list())
                self.consultas[param].update(plates)
            else:
                self.consultas[param] = set(df_result.loc[df_result['parametro_cod_orgao'] == param]['placa'].to_list())


        param_fonte_consulta = df_result['parametro_fonte_consulta'].unique()

        for param in param_fonte_consulta:
            if param == None or param in param_ignore:
                continue
            elif param in self.consultas:
                plates = set(df_result.loc[df_result['parametro_fonte_consulta'] == param]['placa'].to_list())
                self.consultas[param].update(plates)
            else:
                self.consultas[param] = set(df_result.loc[df_result['parametro_fonte_consulta'] == param]['placa'].to_list())

        param_fonte_consulta_boleto = df_result['parametro_fonte_consulta_boleto'].unique()

        for param in param_fonte_consulta_boleto:
            if param == None or param in param_ignore:
                continue
            elif param in self.consultas:
                plates = set(df_result.loc[df_result['parametro_fonte_consulta_boleto'] == param]['placa'].to_list())
                self.consultas[param].update(plates)
            else:
                self.consultas[param] = set(df_result.loc[df_result['parametro_fonte_consulta_boleto'] == param]['placa'].to_list())


        for especificidade in especificidades:
            if especificidade in self.consultas:
                for param in especificidades[especificidade]:
                    if param in self.consultas:
                        self.consultas[param].update(self.consultas[especificidade])
                    else:
                        self.consultas[param] = self.consultas[especificidade]
                    

        for param, plates in self.consultas.items():
            comando_plates = self.remover_caracteres_especiais(str(plates))
            extra_param = '--capcloud' if 'prefeitura' in param.lower() else ''
            threads_param = '--threads=1' if param == 'pr' else ''
            pdf_param = ' --pdf' if param == 'pr' else ''
            if self.recibo:
                if param in ['prefeiturasp', 'sc', 'bradesco']:
                    comando_consulta = f'{PREFIX_QUERY}{param} {comando_plates.strip()} {self.day} +todos --recibo={self.recibo}{SUFIX_CHROME} --attblt {extra_param} {threads_param}{pdf_param}'
                else:
                    comando_consulta = f'{PREFIX_QUERY}{param} {comando_plates.strip()} {self.day} +todos --recibo={self.recibo} --attblt {extra_param} {threads_param}{pdf_param}'
            else:
                if param in ['prefeiturasp', 'sc', 'bradesco']:
                    comando_consulta = f'{PREFIX_QUERY}{param} {comando_plates.strip()} {self.day} +todos{SUFIX_CHROME} --attblt {extra_param} {threads_param}{pdf_param}'
                else:
                    comando_consulta = f'{PREFIX_QUERY}{param} {comando_plates.strip()} {self.day} +todos --attblt {extra_param} {threads_param}{pdf_param}'

            if self._sort_query(param):
                self.lista_consultas.insert(0, comando_consulta.strip())
            else:
                self.lista_consultas.append(comando_consulta.strip())


        self.text = '\n'.join(self.lista_consultas)
        self.make_number_of_queries()

    def make_number_of_queries(self):
        for consulta in self.consultas:
            self.number_of_queries += len(self.consultas[consulta])
            
class QueryGeneratorUFPrefeituras(QueryFormat, QObject):
    def __init__(self, connection, plates, prefeituras, day, recibo):
        super().__init__(connection=connection, day=day, recibo=recibo)
        self.plates = plates
        self.prefeituras = prefeituras
        self.consultas = {}
        self.lista_consultas = []
        self.nao_consultamos = {}
        self.text = ''
        self.number_of_queries = 0
        self.make_query()

    def remover_caracteres_especiais(self, texto):
        return re.sub(r'[^\w\s,]', '', texto).replace(' ', '')

    def _sort_query(self, elemento):
        ordem = {'mg': 1, 'detranpe': 2, 'pa': 3, 'df': 4, 'pi': 5}
        if elemento in ordem:
            return True
        else:
            return False

    def search_vehicle_in_db(self, df, param):
        placeholder_sequence = ', '.join(['%s'] * len(param))
        query = f"""SELECT v.placa as placa_lw_x , v.uf_veic as uf_veic_x from veiculos v where v.placa in ({placeholder_sequence});"""
        df_result = pd.read_sql(sql=query, con=self.con, params=param)
        df = pd.merge(df, df_result,how='left', left_on=['Placa'], right_on='placa_lw_x')
        df['placa_lw'].fillna(df['placa_lw_x'], inplace=True)
        df['uf_veic'].fillna(df['uf_veic_x'], inplace=True)
        df.drop(['placa_lw_x', 'uf_veic_x'], axis=1, inplace=True)
        return df

    def make_query(self):
        df = pd.DataFrame({'Placa': self.plates, 'placa_lw': None, 'uf_veic': None})
        df['Placa'].astype(str)

        df = self.search_vehicle_in_db(df=df, param=self.plates)

        if df.loc[df['placa_lw'].isna()].empty == False:
            df.loc[df['placa_lw'].isna(), 'Placa'] = df.loc[df['placa_lw'].isna(), 'Placa'].apply(lambda plate: Vehicle.static_reverse_the_plate_pattern(plate))
            plates = df.loc[df['placa_lw'].isna(), 'Placa'].to_list()
            df = self.search_vehicle_in_db(df=df, param=plates)

        uf_consultas = df['uf_veic'].unique()

        for uf in uf_consultas:
            if uf in centralizadores_uf_param_consulta:
                param_uf = centralizadores_uf_param_consulta[uf]
                if param_uf in self.consultas:
                    plates = set(df.loc[df['uf_veic'] == uf]['placa_lw'].to_list())
                    self.consultas[param_uf].update(plates)
                else:
                    self.consultas[param_uf] = set(df.loc[df['uf_veic'] == uf]['placa_lw'].to_list())
            else:
                plates = set(df.loc[df['uf_veic'] == uf]['placa_lw'].to_list())
                if uf in self.nao_consultamos:
                    self.nao_consultamos[uf].update(plates)
                else:
                    self.nao_consultamos[uf] = plates

        # Adicionando consultas apenas para as prefeituras selecionadas
        valid_plates = set(df['placa_lw'].dropna().to_list())
        if not valid_plates:
            valid_plates = set(self.plates)
        for prefeitura in self.prefeituras:
            if prefeitura in self.consultas:
                self.consultas[prefeitura].update(valid_plates)
            else:
                self.consultas[prefeitura] = valid_plates.copy()

        for param, plates in self.consultas.items():
            if param not in self.prefeituras:
                continue
            comando_plates = self.remover_caracteres_especiais(str(plates))
            extra_param = '--capcloud' if 'prefeitura' in param.lower() else ''
            threads_param = '--threads=1' if param == 'pr' else ''
            pdf_param = ' --pdf' if param == 'pr' else ''
            if self.recibo:
                if param in ['prefeiturasp', 'sc', 'bradesco']:
                    comando_consulta = f'{PREFIX_QUERY}{param} {comando_plates.strip()} {self.day} +todos --recibo={self.recibo}{SUFIX_CHROME} --attblt {extra_param} {threads_param}{pdf_param}'
                else:
                    comando_consulta = f'{PREFIX_QUERY}{param} {comando_plates.strip()} {self.day} +todos --recibo={self.recibo} --attblt {extra_param} {threads_param}{pdf_param}'
            else:
                if param in ['prefeiturasp', 'sc', 'bradesco']:
                    comando_consulta = f'{PREFIX_QUERY}{param} {comando_plates.strip()} {self.day} +todos{SUFIX_CHROME} --attblt {extra_param} {threads_param}{pdf_param}'
                else:
                    comando_consulta = f'{PREFIX_QUERY}{param} {comando_plates.strip()} {self.day} +todos --attblt {extra_param} {threads_param}{pdf_param}'

            if self._sort_query(param):
                self.lista_consultas.insert(0, comando_consulta.strip())
            else:
                self.lista_consultas.append(comando_consulta.strip())

        self.lista_consultas.append(f'\nUF que não consultamos:{str(self.nao_consultamos)}')

        if df.loc[df['placa_lw'].isna()].empty == False:
            veiculo_nao_cadastrado = set(df.loc[df['placa_lw'].isna()]['Placa'].to_list())
            self.lista_consultas.append(f'\n\nVeiculos não cadastrados:\n{veiculo_nao_cadastrado}')

        self.text = '\n'.join(self.lista_consultas)
        self.make_number_of_queries()

    def make_number_of_queries(self):
        for consulta in self.consultas:
            self.number_of_queries += len(self.consultas[consulta])
            
if __name__ == '__main__':
    print('Hello')
