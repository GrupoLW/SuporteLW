from PySide6.QtGui import QScreen, QShortcut, QKeySequence
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel, QProgressBar, QFileDialog, QMessageBox, QApplication, QTableWidget, QTableWidgetItem
)
import pandas as pd
import mysql.connector
import logging


class ReportsWindow(QWidget):
    def __init__(self, connection, main_window):
        super().__init__()
        self.connection = connection
        self.main_window = main_window
        self.setWindowTitle("Gerador de Relatórios de Multas")
        self.setGeometry(300, 300, 800, 600)
        self.center_window()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.back_button = QPushButton("Voltar para o Menu Principal")
        self.back_button.setMinimumSize(250, 30)
        self.back_button.setMaximumSize(100, 30)
        self.back_button.clicked.connect(self.go_to_main_menu)
        layout.addWidget(self.back_button)

        self.info_label = QLabel("Insira os IDs das multas separados por quebra de linha ou espaço:")
        layout.addWidget(self.info_label)

        self.id_input = QTextEdit()
        layout.addWidget(self.id_input)

        self.generate_button = QPushButton("Gerar Relatório!")
        self.generate_button.clicked.connect(self.generate_report)
        layout.addWidget(self.generate_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.results_table = QTableWidget()
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.results_table)

        self.row_count_label = QLabel("Linhas geradas: 0")
        layout.addWidget(self.row_count_label)

        self.save_button = QPushButton("Salvar Relatório")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_report)
        layout.addWidget(self.save_button)

        self.copy_shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        self.copy_shortcut.activated.connect(lambda: self.copy_table_content(include_header=False))

        self.copy_with_header_shortcut = QShortcut(QKeySequence("Ctrl+Shift+C"), self)
        self.copy_with_header_shortcut.activated.connect(lambda: self.copy_table_content(include_header=True))

        self.setLayout(layout)

    def generate_report(self):
        ids = self.id_input.toPlainText()
        id_list = [id.strip() for id in ids.split() if id.strip().isdigit()]

        if not id_list:
            QMessageBox.warning(self, "Atenção", "Insira ao menos um ID válido.")
            return

        self.progress_bar.setValue(0)

        query = f"""
        #TESTEEEEEEEEEEEEEEEEEE
SELECT 
v.id as id_veic,
v.uf_veic,
v.placa,
CONCAT(CONVERT("'" USING utf8mb4), v.renavam) as renavam,
v.chassi,
m.id_cliente,
CASE 
        WHEN v.cnpj IS NOT NULL AND v.cnpj != '' AND v.cnpj_proprietario IS NOT NULL AND v.cnpj_proprietario != '' AND v.cnpj = v.cnpj_proprietario THEN CONCAT(CONVERT("'" USING utf8mb4), v.cnpj)
        WHEN v.cnpj IS NOT NULL AND v.cnpj != '' AND v.cnpj_proprietario IS NOT NULL AND v.cnpj_proprietario != '' AND v.cnpj != v.cnpj_proprietario THEN CONCAT(CONVERT("'" USING utf8mb4), v.cnpj, ' / ', v.cnpj_proprietario)
        WHEN v.cnpj IS NOT NULL AND v.cnpj != '' THEN CONCAT(CONVERT("'" USING utf8mb4), v.cnpj)
        WHEN v.cnpj_proprietario IS NOT NULL AND v.cnpj_proprietario != '' THEN CONCAT(CONVERT("'" USING utf8mb4), v.cnpj_proprietario)
        ELSE ''
            END AS 'cnpj/cnpj proprietario',
            m.autoInfracao,
            m.autoInfracao2,
            m.autoInfracao3,
            m.AIIPMulta,
            m.id as id_multa,
        
		#Início da análise
		CASE 
		    -- MULTA PAGA
			
			WHEN m.status IN (1, 2) THEN CASE
				WHEN m.historico LIKE '%sistema de pagamentos%' THEN 'Multa paga/baixada pela LW'
				ELSE 'Multa paga/baixada'
			END
		    -- APTO PARA PAGAMENTO
		    WHEN m.dataVencimentoBoleto >= CURDATE() THEN CASE 
		    	WHEN (SELECT COUNT(id) FROM multaDetalhadaImagensMinio WHERE id_multa = m.id AND referencia = 'I' and exclusao is null) > 0 THEN 'Apto para pagamento'
		    	ELSE 'Pendente de maior análise'
		    END
		    
		    -- NÃO MINERAMOS
		    WHEN v.uf_veic IN ('SP','PB','TO','SE','RO','BA') AND 
		         m.orgao IN (261370,261630,261650,261770,261890,262090,263090,263490,264030,264270,264490,264690,265070,265090,265690,266810,267710,268530,268970,269130,269150,269530,269670,270370,270650,271130,
		         271430,272010,126100,127200,219370,224570,231050,233130,235150,236690,261090,261310,261810,262690,265110,265810,266410,267370,269790,270350,261490,261550,261570,261750,262390,262810,263230,263570,
		         265790,265870,266690,267150,267170,267230,267950,268310,268570,270050,270830,271810,261810,267230,261090,269790,262390,265690,267950,230670,235970,261010,261090,261310,261550,261790,261810,261890,
		         262050,262090,262390,262570,262690,262810,262890,263090,263230,263490,264030,264270,264930,264950,265090,265470,265690,265810,265830,265870,265950,266370,266230,266450,266810,267110,267170,267690,
		         267710,267950,268530,268570,268670,268770,268670,269110,269130,269290,269330,269530,269670,270290,270370,270650,270830,271030,272390,272430,272450,272450,272650,272730) THEN 'Não mineramos esse órgão'
		    
		    -- PR - DESPACHANTE (EM TESTES)
		    WHEN m.orgaoNome LIKE '%- PR' THEN 'Consulta através do DESPACHANTE'
		    
		    -- MANUTENÇÃO
		    WHEN (m.orgao IN (229650,262490,262950,263110,264150,264750,266710,297330,268610,269210,270790,271150,271510,271830,270570) OR (m.orgaoNome like '%- SC%')) AND 
		         v.uf_veic IN ('SP','PB','TO','SE','RO','BA','SC', 'PE') THEN 'Órgão(minerador) em manutenção'
	         
		    -- 40 DIAS SEM ATUALIZAR
		    WHEN m.dataHoraUltimaLeitura < DATE_SUB(NOW(), INTERVAL 40 DAY) THEN 
		        CASE 
		            WHEN v.status IN (1, 5) AND m.dataHoraUltimaLeitura < DATE_SUB(NOW(), INTERVAL 40 DAY) THEN 'Consultar novamente - (veiculo inativo)'
		            ELSE 'Multa sem leitura há mais de 40 dias'
		        END
		    
		    -- JOAO PESSOA
			WHEN m.orgao = 220510 AND m.fonteConsultaBoleto = 'pref_joaopessoa' THEN
			    CASE 
			        WHEN m.codigoBarras LIKE '0019%' THEN 'Apto para pagamento'
			        ELSE 'Consultar novamente - (pref_joaopessoa)'
			    END
		    
			-- SITUAÇÃO MULTA
		    WHEN m.situacao IN ('DEFESA', 'DEFESA AUTUAÇÃO', 'DEFESA DEFERIDA', 'Advertida', 'EMITIR ADVERTENCIA', 'Convertido em PAE', 'CANCELADO', 'JARI', 'Encerrado', 'Justificada', 'SOLICITACAO DE ADVERTENCIA EM JULGAMENTO', 'PAGO') AND 
		         m.dataHoraUltimaLeitura < DATE_SUB(NOW(), INTERVAL 20 DAY) THEN CONCAT('Multa ', CONVERT(m.situacao USING utf8mb4), ' - não atualiza boleto')
		         #depende do órgão, disponibiliza o boleto (dívida ativa; suspensao)
		         
		    -- MINERAÇÃO MANUAL
		    WHEN m.cadastroManual = 'S' AND (m.dataHoraUltimaLeitura IS NULL or m.fonteConsulta = '') THEN 'Cadastro Manual, nunca lido pelo minerador'
		    
		    -- NOT SEM BOLETO - MUDAR ESSA REGRA
		    WHEN m.situacao = 'NOTIFICADO' AND (m.dataVencimentoBoleto IS NULL OR m.dataVencimentoBoleto = '') AND m.apCondutorDataVencimento >= DATE_SUB(NOW(), INTERVAL 22 DAY) THEN 'Notificação sem boleto'
			#RS - GO - DNIT - DPRF
		    #o prazo minimo é de 30 dias
		    #tem apCondutor usa a regra, senao usa daataInfracao +40 dias. A data condutor for menor que hj, já venceu e pode virar imposição.
		    #dataInfracao for maior que 4 mese, e se estiver notificada, validar se é passivel de pgto.
		    
		    -- BOLETO VENCIDO ULTIMOS 20 DIAS //// DATE_SUB = DATEE_ADD -35
		    WHEN m.dataVencimentoBoleto >= DATE_SUB(NOW(), INTERVAL 20 DAY) AND m.dataHoraUltimaLeitura >= DATE_SUB(NOW(), INTERVAL 20 DAY) THEN 'Consultar novamente - (boleto recente)'
			#dprf
		    #média 40 dias do primeiro boleto
		    
		    -- DER NOTIFICADO
		    WHEN m.orgao = 126200 AND m.situacao = 'NOTIFICADO' AND m.dataHoraUltimaLeitura >= DATE_SUB(NOW(), INTERVAL 15 DAY) THEN 'DER SP - NOTIFICADO'
		    -- DER IMPOSTO
		    WHEN m.orgao = 126200 AND m.situacao = 'IMPOSTO' AND m.dataHoraUltimaLeitura >= DATE_SUB(NOW(), INTERVAL 15 DAY) THEN 'Apto para pagamento'
		    
		    -- IMAGENS FALTANDO
		    WHEN (SELECT COUNT(id) FROM multaDetalhadaImagensMinio WHERE id_multa = m.id AND imagemNomeOriginal = '' AND referencia = 'I') > 0 THEN 'Consultar novamente - (boleto recente)'
		    ELSE 'Pendente de maior análise'
		END AS 'Análise mineração',
        #Fim da análise

m.status,
        CASE WHEN v.status = 0 THEN "Veículo ativo" WHEN v.status = 1 THEN "Veículo inativo" WHEN v.status = 5 THEN "Veículo com erro de cadastro" END AS 'Situação Veículo',
m.cadastroManual,
m.situacao,
m.apCondutorDataVencimento,
m.dataVencimentoBoleto,
        CASE WHEN (SELECT COUNT(id) FROM multaDetalhadaImagensMinio WHERE id_multa = m.id AND (referencia = 'N')) > 0 THEN 'SIM' ELSE 'NÃO' END AS 'IMG_Notificação',
        CASE WHEN (SELECT COUNT(id) FROM multaDetalhadaImagensMinio WHERE id_multa = m.id AND (referencia = 'NS')) > 0 THEN 'SIM' ELSE 'NÃO' END AS 'IMG_Notificação_GENÉRICA',
        CASE WHEN (SELECT COUNT(id) FROM multaDetalhadaImagensMinio WHERE id_multa = m.id AND referencia = 'I') > 0 THEN 'SIM' ELSE 'NÃO' END AS 'IMG_Boleto',
        CASE WHEN (SELECT COUNT(id) FROM multaDetalhadaImagensMinio WHERE id_multa = m.id AND referencia = 'C') > 0 THEN 'SIM' ELSE 'NÃO' END AS 'IMG_Comprovante',
m.dataHoraUltimaLeitura,
mo.cod_orgao AS miner_cod_orgao,
m.estado,
m.orgao,
o.nome AS orgaoNome,
m.codigo,
t.descricao AS descricaoArtigo,
m.endereco,
m.dataInfracao,
m.horaInfracao,
IF(m.valor = '', t.valor, m.valor) AS valor,
m.valorBoleto,
m.descontoBoleto,
m.jurosBoleto,
CONCAT(CONVERT("'" USING utf8mb4), m.codigoBarras) AS codigoBarras,
m.historico,
m.dataVencimento,
m.cadastroDataHora,
m.fonteConsulta,
m.fonteConsultaBoleto,
nic.id_multa_origem,
nic.ait_multa_origem,
m.exclusao,
m.nroProcessamentoMG
FROM multaDetalhada m
INNER JOIN veiculos v ON v.id = m.id_veiculo
LEFT JOIN tabelaInfracaoDenatranNov16 t ON t.cod_infracao = m.codigo
LEFT JOIN orgao o ON o.cod_orgao = m.orgao
LEFT JOIN multaDetalhadaLinkNic nic ON nic.id_multa_nic = m.id
LEFT JOIN tabela_veiculos_unidas vu ON vu.id_veiculo = v.id
LEFT JOIN miner_orgao mo ON mo.cod_orgao = m.orgao
LEFT JOIN contasReceberReciboItens crri ON crri.id_multa = m.id
WHERE m.id IN ({', '.join(id_list)})
GROUP BY m.autoInfracao
order by `Análise mineração` asc;        
"""

        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

            columns = [desc[0] for desc in cursor.description]

            df = pd.DataFrame(rows, columns=columns)
            df = df.where(pd.notnull(df), "")

            for col in ["historico", "endereco", "descricaoArtigo", "cidade"]:
                if col in df.columns:
                    df[col] = df[col].apply(
                        lambda x: x.replace("\n", " ").replace("\r", " ").strip() if isinstance(x, str) else x
                    )

            logging.debug("DataFrame gerado:\n%s", df.head(10).to_string())

            self.fill_results_table(df)

            self.row_count_label.setText(f"Linhas geradas: {len(df)}")

            self.progress_bar.setValue(100)
            self.save_button.setEnabled(True)
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Erro", f"Erro ao executar a consulta: {e}")

    def fill_results_table(self, df):

        self.results_table.clear()
        self.results_table.setRowCount(len(df))
        self.results_table.setColumnCount(len(df.columns))
        self.results_table.setHorizontalHeaderLabels(df.columns)

        for row_idx, row in enumerate(df.values):
            for col_idx, value in enumerate(row):
                value = str(value) if value is not None else ""
                if df.columns[col_idx] in ["historico", "endereco", "descricaoArtigo", "cidade"]:
                    value = value.replace("\n", " ").replace("\r", " ").strip()
                self.results_table.setItem(row_idx, col_idx, QTableWidgetItem(value))

    def copy_table_content(self, include_header=False):

        row_count = self.results_table.rowCount()
        col_count = self.results_table.columnCount()

        if row_count == 0 or col_count == 0:
            QMessageBox.warning(self, "Atenção", "Não há dados para copiar.")
            return

        selected_rows = self.results_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Atenção", "Selecione as linhas para copiar.")
            return

        content = []
        if include_header:
            header = [self.results_table.horizontalHeaderItem(col).text() for col in range(col_count)]
            content.append("\t".join(header))
        
        for row in selected_rows:
            row_data = [
                self.results_table.item(row.row(), col).text().replace("\n", " ").replace("\r", " ").strip()
                for col in range(col_count)
            ]
            content.append("\t".join(row_data)) 

        clipboard = QApplication.clipboard()
        clipboard.setText("\n".join(content))

        logging.debug("Conteúdo copiado:\n%s", "\n".join(content))

        QMessageBox.information(self, "Sucesso", "Conteúdo copiado para a área de transferência.")

    def save_report(self):

        row_count = self.results_table.rowCount()
        col_count = self.results_table.columnCount()

        if row_count == 0 or col_count == 0:
            QMessageBox.warning(self, "Atenção", "Não há dados para salvar.")
            return

        data = []
        for row in range(row_count):
            data.append([self.results_table.item(row, col).text() for col in range(col_count)])
        columns = [self.results_table.horizontalHeaderItem(col).text() for col in range(col_count)]
        df = pd.DataFrame(data, columns=columns)

        default_filename = "Relatorio_Multas.xlsx"
        save_path, _ = QFileDialog.getSaveFileName(self, "Salvar Relatório", default_filename, "Arquivos Excel (*.xlsx)")
        if save_path:
            if not save_path.endswith(".xlsx"):
                save_path += ".xlsx"
            df.to_excel(save_path, index=False, engine="openpyxl")
            QMessageBox.information(self, "Sucesso", f"Relatório salvo em {save_path}")

    def go_to_main_menu(self):
        self.main_window.show()
        self.close()

    def center_window(self):
        screen_geometry = QScreen.availableGeometry(QApplication.primaryScreen())
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())
