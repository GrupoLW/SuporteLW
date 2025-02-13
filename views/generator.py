import sys
from PySide6.QtGui import QScreen
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextEdit, QGridLayout, QCheckBox, QLineEdit, QPushButton, QLabel, QButtonGroup
)

from app.query_generator import QueryGeneratorUFAutuador, QueryGeneratorUF, QueryGeneratorAutuador, QueryGeneratorUFWithID
from app.query_info import fetch_orgaos_homologados_query


class QueryGenerator(QWidget):
    def __init__(self, connection, main_window) -> None:
        super().__init__()
        self.con = connection
        self.main_window = main_window
        self.gerador_de_consultas = None

        self.setWindowTitle('Gerador de consultas')
        self.setGeometry(300, 300, 800, 600)
        self.center_window()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.header = QWidget()
        self.input_text_area = QTextEdit()
        self._actions = QWidget()
        self.output_text_area = QTextEdit()
        self.status_bar = QLabel('')

        self.layout_header = QGridLayout()
        self.layout_actions = QGridLayout()

        self.layout.addWidget(self.header)
        self.layout.addWidget(self.input_text_area)
        self.layout.addWidget(self._actions)
        self.layout.addWidget(self.output_text_area)
        self.layout.addWidget(self.status_bar)

        self.header.setLayout(self.layout_header)
        self._actions.setLayout(self.layout_actions)

        self._make_header()
        self._make_actions()

    def center_window(self):
        screen_geometry = QScreen.availableGeometry(QApplication.primaryScreen())
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())

    def _make_header(self):
        self.back_button = QPushButton('Voltar para o Menu Principal')
        self.back_button.clicked.connect(self.go_to_main_menu)
        self.layout_header.addWidget(self.back_button, 0, 0, 1, 2)

        self.recibo_line = QLineEdit()
        self.layout_header.addWidget(self.recibo_line, 1, 1)
        self.recibo_line.setPlaceholderText('Recibo')

        self.line_days = QLineEdit()
        self.layout_header.addWidget(self.line_days, 1, 2)
        self.line_days.setPlaceholderText('Dias')

    def _make_actions(self):
        self.check_plates = QCheckBox('Placas')
        self.check_ID = QCheckBox('ID_multa')
        self.check_client_id = QCheckBox('ID_cliente')

        self.client_id_label = QLabel('Digite o ID:')
        self.client_id_input = QLineEdit()
        self.client_id_label.setFixedSize(250, 30)
        self.client_id_input.setFixedSize(250, 30)
        self.client_id_input.setEnabled(False)

        self.layout_actions.addWidget(self.check_plates, 0, 0)
        self.layout_actions.addWidget(self.check_ID, 1, 0)
        self.layout_actions.addWidget(self.check_client_id, 2, 0)

        self.layout_actions.addWidget(self.client_id_label, 2, 1)
        self.layout_actions.addWidget(self.client_id_input, 2, 2)

        self.button_consulta_uf = QPushButton('Consulta UF')
        self.button_consulta_autuador = QPushButton('Órgão Autuador')
        self.button_consulta_autuador_mais_uf = QPushButton('UF + autuador')
        self.button_orgaos_homologados = QPushButton('Órgãos Homologados')

        self.layout_actions.addWidget(self.button_consulta_uf, 0, 1)
        self.layout_actions.addWidget(self.button_consulta_autuador, 1, 1)
        self.layout_actions.addWidget(self.button_consulta_autuador_mais_uf, 0, 2)
        self.layout_actions.addWidget(self.button_orgaos_homologados, 1, 2)

        self.check_plates.stateChanged.connect(self._handle_checkbox_selection)
        self.check_ID.stateChanged.connect(self._handle_checkbox_selection)
        self.check_client_id.stateChanged.connect(self._handle_checkbox_selection)

        self.button_consulta_uf.clicked.connect(self._query_uf)
        self.button_consulta_autuador.clicked.connect(self._query_autuador)
        self.button_consulta_autuador_mais_uf.clicked.connect(self._query_uf_e_autuador)
        self.button_orgaos_homologados.clicked.connect(self._query_orgaos_homologados)

    def _handle_checkbox_selection(self):

        self.output_text_area.clear()
        self.client_id_input.setEnabled(False)
        self.button_consulta_uf.setEnabled(False)
        self.button_consulta_autuador.setEnabled(False)
        self.button_consulta_autuador_mais_uf.setEnabled(False)
        self.button_orgaos_homologados.setEnabled(False)

        if self.check_plates.isChecked():
            self.check_ID.blockSignals(True)
            self.check_client_id.blockSignals(True)
            self.check_ID.setChecked(False)
            self.check_client_id.setChecked(False)
            self.check_ID.blockSignals(False)
            self.check_client_id.blockSignals(False)
            self.button_consulta_uf.setEnabled(True)

        elif self.check_ID.isChecked():
            self.check_plates.blockSignals(True)
            self.check_client_id.blockSignals(True)
            self.check_plates.setChecked(False)
            self.check_client_id.setChecked(False)
            self.check_plates.blockSignals(False)
            self.check_client_id.blockSignals(False)
            self.button_consulta_uf.setEnabled(True)
            self.button_consulta_autuador.setEnabled(True)
            self.button_consulta_autuador_mais_uf.setEnabled(True)

        elif self.check_client_id.isChecked():
            self.check_plates.blockSignals(True)
            self.check_ID.blockSignals(True)
            self.check_plates.setChecked(False)
            self.check_ID.setChecked(False)
            self.check_plates.blockSignals(False)
            self.check_ID.blockSignals(False)
            self.client_id_input.setEnabled(True)
            self.button_orgaos_homologados.setEnabled(True)

            self.check_plates.toggled.connect(self._handle_checkbox_selection)
            self.check_ID.toggled.connect(self._handle_checkbox_selection)
            self.check_client_id.toggled.connect(self._handle_checkbox_selection)

            self.check_plates.toggled.connect(self._handle_checkbox_selection)
            self.check_ID.toggled.connect(self._handle_checkbox_selection)
            self.check_client_id.toggled.connect(self._handle_checkbox_selection)


    def _query_uf(self):
        if self.check_plates.isChecked():
            lista = self.input_text_area.toPlainText().strip().split()
            gerador_de_consultas = QueryGeneratorUF(connection=self.con, plates=lista, recibo=self.recibo_line.text(), day=self.line_days.text())
            self.output_text_area.setPlainText(gerador_de_consultas.text)
            self.status_bar.setText(f'Número de consultas: {gerador_de_consultas.number_of_queries}')
        elif self.check_ID.isChecked():
            lista = self.input_text_area.toPlainText().strip().split()
            gerador_de_consultas = QueryGeneratorUFWithID(connection=self.con, id_multas=lista, recibo=self.recibo_line.text(), day=self.line_days.text())
            self.output_text_area.setPlainText(gerador_de_consultas.text)
            self.status_bar.setText(f'Número de consultas: {gerador_de_consultas.number_of_queries}')

    def _query_uf_e_autuador(self):
        if self.check_ID.isChecked():
            lista = self.input_text_area.toPlainText().strip().split()
            gerador_de_consultas = QueryGeneratorUFAutuador(connection=self.con, id_multas=lista, recibo=self.recibo_line.text(), day=self.line_days.text())
            self.output_text_area.setPlainText(gerador_de_consultas.text)
            self.status_bar.setText(f'Número de consultas: {gerador_de_consultas.number_of_queries}')

    def _query_autuador(self):
        if self.check_ID.isChecked():
            lista = self.input_text_area.toPlainText().strip().split()
            gerador_de_consultas = QueryGeneratorAutuador(connection=self.con, id_multas=lista, recibo=self.recibo_line.text(), day=self.line_days.text())
            self.output_text_area.setPlainText(gerador_de_consultas.text)
            self.status_bar.setText(f'Número de consultas: {gerador_de_consultas.number_of_queries}')

    def _query_orgaos_homologados(self):
        """Consulta órgãos homologados com base no ID do cliente."""
        client_id = self.client_id_input.text().strip()
        if not client_id.isdigit():
            self.status_bar.setText('ID Cliente inválido. Insira um número válido.')
            return

        query = fetch_orgaos_homologados_query(client_id)
        try:
            cursor = self.con.cursor()
            cursor.execute(query)
            results = cursor.fetchall()

            commands = [row[6] for row in results]
            self.output_text_area.setPlainText('\n'.join(commands))
            self.status_bar.setText(f'{len(commands)} comandos gerados com sucesso.')
        except Exception as e:
            self.status_bar.setText(f'Erro ao executar a consulta: {e}')

    def go_to_main_menu(self):
        self.main_window.show()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QueryGenerator(connection=None, main_window=None)
    window.show()
    app.exec()
