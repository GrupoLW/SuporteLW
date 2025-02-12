import sys
from PySide6.QtGui import QScreen
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QGridLayout, QCheckBox, QLineEdit, QPushButton, QLabel, QButtonGroup

from views.components import DirectoryButton, DirectoryLine, DirectoryTitle
from app.analyse_queries_report import AnalyseAll, AnalyseAutuador, AnalyseUF, AnalyseAutuadorWithID

from PySide6.QtCore import Slot, QThread

style_button = '''
    QPushButton{
        background-color: #2B2B2B;
        color: white;
    }
'''

class AnalyseQueries(QWidget):
    def __init__(self, connection, main_window) -> None:
        super().__init__()
        self.con = connection
        self.main_window = main_window
        self.setWindowTitle('Análise de consultas')
        self.setGeometry(300, 300, 800, 600)
        self.center_window()  # Centraliza a janela
        self.gerador_de_consultas = None

        # Configuração padrão
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Containers
        self.header = QWidget()
        self.input_text_area = QTextEdit()
        self._actions = QWidget()
        self.status_bar = QLabel('')

        # Layouts containers
        self.layout_header = QGridLayout()
        self.layout_actions = QGridLayout()

        # Add layouts
        self.layout.addWidget(self.header)
        self.layout.addWidget(self.input_text_area)
        self.layout.addWidget(self._actions)
        self.layout.addWidget(self.status_bar)

        self.header.setLayout(self.layout_header)
        self._actions.setLayout(self.layout_actions)

        # Instância dos containers
        self._make_header()
        self._make_actions()

    def center_window(self):
        screen_geometry = QScreen.availableGeometry(QApplication.primaryScreen())
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())

    def _make_header(self):
        # Botão Voltar para o menu principal
        self.back_button = QPushButton('Voltar para o Menu Principal')
        self.back_button.setMinimumSize(250, 30)
        self.back_button.setMaximumSize(100, 30)
        self.back_button.clicked.connect(self.go_to_main_menu)
        self.layout_header.addWidget(self.back_button, 0, 0, 1, 3)

        # Output
        self.output_directory_title = DirectoryTitle('Output:')
        self.output_directory_line = DirectoryLine()
        self.output_directory_button = DirectoryButton('...', 30, 30, self.output_directory_line, False)
        self.file_name = QLineEdit()
        self.file_name.setPlaceholderText('Nome do arquivo')

        self.output_directory_button.setStyleSheet(style_button)
        self.layout_header.addWidget(self.output_directory_title, 1, 1)
        self.layout_header.addWidget(self.output_directory_line, 1, 2)
        self.layout_header.addWidget(self.output_directory_button, 1, 3)
        self.layout_header.addWidget(self.file_name, 1, 4)

    def _make_actions(self):
        # Check box 1 e label
        self.check_plates = QCheckBox('Placas')
        self.layout_actions.addWidget(self.check_plates, 0, 1)
        # Check box 2 e label
        self.check_ID = QCheckBox('ID_multa')
        self.layout_actions.addWidget(self.check_ID, 0, 2)
        # QGroup
        self.box_group = QButtonGroup()
        self.box_group.addButton(self.check_plates)
        self.box_group.addButton(self.check_ID)
        # Data
        self.line_days = QLineEdit()
        self.line_days.setPlaceholderText('Data: yyyy-mm-dd')
        self.layout_actions.addWidget(self.line_days, 0, 3)
        # Button 1
        self.button_consulta_uf = QPushButton('Emplacamento')
        self.layout_actions.addWidget(self.button_consulta_uf, 0, 4)
        self.button_consulta_uf.setStyleSheet(style_button)
        # Button 2
        self.button_consulta_autuador = QPushButton('Autuador')
        self.layout_actions.addWidget(self.button_consulta_autuador, 0, 5)
        self.button_consulta_autuador.setStyleSheet(style_button)
        # Button 3
        self.button_consulta_autuador_mais_uf = QPushButton('All')
        self.layout_actions.addWidget(self.button_consulta_autuador_mais_uf, 0, 6)
        self.button_consulta_autuador_mais_uf.setStyleSheet(style_button)

        # Ações dos botões
        self.button_consulta_uf.clicked.connect(self._query_uf)
        self.button_consulta_autuador_mais_uf.clicked.connect(self._query_all)
        self.button_consulta_autuador.clicked.connect(self._query_autuador)

    @Slot()
    def _report_finished(self):
        self.status_bar.setText('Relatório Finalizado')

    def _status_report(self, value):
        self.status_bar.setText(value)

    def _query_uf(self):
        lista = self.input_text_area.toPlainText().strip().split()
        if self.check_plates.isChecked():
            AnalyseUF(connection=self.con, output=self.output_directory_line.text(), file_name=self.file_name.text(), plates=lista, date=self.line_days.text())
        elif self.check_ID.isChecked():
            AnalyseAutuadorWithID(connection=self.con, output=self.output_directory_line.text(), file_name=self.file_name.text(), id_multas=lista, date=self.line_days.text())

    def _query_all(self):
        if self.check_ID.isChecked():
            lista = self.input_text_area.toPlainText().strip().split()
            self.analyse = AnalyseAll(connection=self.con, output=self.output_directory_line.text(), file_name=self.file_name.text(), id_multas=lista, date=self.line_days.text())
            self._thread = QThread()

            # Configuração padrão da Thread
            self.analyse.moveToThread(self._thread)
            self._thread.started.connect(self.analyse.make_query)
            self.analyse.terminated.connect(self._thread.quit)
            self._thread.finished.connect(self._thread.deleteLater)
            self.analyse.terminated.connect(self.analyse.deleteLater)

            self.analyse.status_report.connect(self._status_report)
            self.analyse.terminated.connect(self._report_finished)
            self._thread.start()

    def _query_autuador(self):
        if self.check_ID.isChecked():
            lista = self.input_text_area.toPlainText().strip().split()
            AnalyseAutuador(connection=self.con, output=self.output_directory_line.text(), file_name=self.file_name.text(), id_multas=lista, date=self.line_days.text())

    def go_to_main_menu(self):
        self.main_window.show()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = AnalyseQueries(connection=None, main_window=None)

    # Execução da aplicação
    window.show()
    app.exec()
