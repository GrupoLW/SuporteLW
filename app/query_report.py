from PySide6.QtCore import Signal, QObject
import pandas as pd
from datetime import datetime as dt

from utils.report import Report


class QueryReport(Report, QObject):
    status_report = Signal(str)
    report_finished = Signal(str)
    error_report = Signal(str)
    terminated = Signal(str)

    def __init__(self, connection, input, output, file_name):
        super().__init__(input, output, file_name)
        self.con = connection
        self.make_consultas_report()
        self.con.close()


    def consulta_banco(con, query, params):
        df = pd.read_sql(sql=query, con=con, params=params)
        if df.empty:
            return None
        else:
            return df.iloc[0]

    def make_consultas_report(self):

       
        self.read_spreadsheet()
        df = self.table_read
        
        print('Lendo a planilha...')
        self.status_report.emit('Lendo a planilha...')

        id_multas = df['id_multa'].tolist()

        placeholder_sequence = ', '.join(['%s'] * len(id_multas))

        query = f"""SELECT m.id as id_multa, m.id_veiculo , m.dataHoraUltimaLeitura , m.estado , m.fonteConsulta , m.fonteConsultaBoleto , m.orgao as cod_orgao, (SELECT v.uf_veic  from veiculos v where v.id=m.id_veiculo) as uf_veic ,
        mo.fonte_consulta as fonteConsultaCodOrgao
        from multaDetalhada m 
        left join miner_orgao mo on (m.orgao = mo.cod_orgao)
        where m.id in ({placeholder_sequence});"""


        cursor = self.con.cursor()
        cursor.execute(query, tuple(id_multas))
        result = cursor.fetchall()
        df = pd.DataFrame(result, columns=cursor.column_names)
        cursor.close()

        uf_dos_centralizadores = {'PA': 'detran_pa', 'PE': 'detran_pe', 'RS': 'detran_rs', 'MG': 'detran_mg', 'GO': 'detran_go', 'AL': 'detran_al', 'SC': 'detran_sc', 
                          'RN': 'detran_rn', 'DF': 'detran_df', 'ES': 'detran_es', 'PI': 'detran_pi', 'PR': 'git_parana', 'CE': 'detran_ce_multa', 'RR': 'detran_rr',
                          'AM': 'detran_am', 'BA': 'detranba_pdf', 'RJ': 'detran_rj', 'MT': 'detran_mt', 'MA': 'detran_ma', 'MS': 'detran_ms'}

        data = str(dt.now().date())

        query = """SELECT COUNT(vh2.id_veiculo) as Consulta from veiculoHistoricoConsultaDois vh2 
        WHERE vh2.id_veiculo = %s and vh2.fonteConsulta = %s and vh2.erro = 0 and vh2.dataConsulta >= %s;"""

        df['Consulta_uf'] = df.loc[df['uf_veic'].isin(uf_dos_centralizadores.keys())].apply(lambda row: self.consulta_banco(con=self.con, query=query, params=[row['id_veiculo'], uf_dos_centralizadores[row['uf_veic']], data]), axis=1)
        
        df['Consulta_uf'].loc[df['Consulta_uf'].isna() == True] = 'Não consultamos esta UF'

        df['Consulta cod_orgao'] = df.loc[df['fonteConsultaCodOrgao'].isna() == False].apply(lambda row: self.consulta_banco(con=self.con, query=query, params=[row['id_veiculo'], row['fonteConsultaCodOrgao'], data]), axis=1)

        df['Consulta fonteConsulta'] = df.loc[df['fonteConsulta'].isna() == False].apply(lambda row: self.consulta_banco(con=self.con, query=query, params=[row['id_veiculo'], row['fonteConsulta'], data]), axis=1)

        try:
            self.status_report.emit('Gerando o relatório ...')
            self.produce_report(df)
            self.report_finished.emit('O relatório foi gerado com sucesso!!')
        except Exception:
            self.error_report.emit('Um erro ocorreu na hora de escrever o relatório')
        self.terminated.emit('Processo finalizado')




if __name__ == '__main__':
    print('Hello')



