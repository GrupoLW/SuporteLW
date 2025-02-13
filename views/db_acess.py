import sys
import mysql.connector
import os
import json
from views.reports_window import ReportsWindow
from views.generator import QueryGenerator
from views.analyse_queries import AnalyseQueries
from models.db_model import connect
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox
from PySide6.QtCore import QTimer

style_button = '''
    QPushButton{
        background-color: #2B2B2B;
        color: white;
    }
'''

WIDHT_WINDOW = 500
HEIGHT_WINDOW = 240

USERNAME_FILE = ".username.json"


class ServicesWindow(QWidget):
    def __init__(self, connection) -> None:
        super().__init__()
        self.con = connection

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setWindowTitle('Serviços - Suporte LW')
        self.setGeometry(300, 300, 600, 400)
        self.center_window()

        self.button_reports_window = QPushButton('Gerador de relatórios')
        self.button_query_generator = QPushButton('Gerador de consultas')
        self.button_analyse_queries = QPushButton('Analisar Consultas')

        self.layout.addWidget(self.button_reports_window)
        self.layout.addWidget(self.button_query_generator)
        self.layout.addWidget(self.button_analyse_queries)

        self.button_reports_window.setMinimumSize(400, 100)
        self.button_query_generator.setMinimumSize(400, 100)
        self.button_analyse_queries.setMinimumSize(400, 100)
        self.button_reports_window.setStyleSheet(style_button)
        self.button_query_generator.setStyleSheet(style_button)
        self.button_analyse_queries.setStyleSheet(style_button)

        self.button_query_generator.clicked.connect(self.to_enter_in_generator)
        self.button_reports_window.clicked.connect(self.to_enter_in_reports_window)
        self.button_analyse_queries.clicked.connect(self.to_enter_in_analyse_queries)

    def center_window(self):
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())

    def to_enter_in_generator(self):
        self.generator = QueryGenerator(connection=self.con, main_window=self)
        self.generator.show()
        self.hide()

    def to_enter_in_reports_window(self):
        self.reports_window = ReportsWindow(connection=self.con, main_window=self)
        self.reports_window.show()
        self.hide()

    def to_enter_in_analyse_queries(self):
        self.reports_window = AnalyseQueries(connection=self.con, main_window=self)
        self.reports_window.show()
        self.hide()


class DBAccessWindow(QMainWindow):
    def __init__(self, parent: QWidget | None = None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        self.db_config = {
            'user': '',
            'password': '',
            'host': '192.168.100.8',
            'database': 'sistemaMultas'
        }

        self.con = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.keep_connection_alive)

        self.cw = QWidget()
        self.cw_layout = QVBoxLayout()
        self.cw.setLayout(self.cw_layout)
        self.setCentralWidget(self.cw)

        self.user_label = QLabel('User: ')
        self.user_line = QLineEdit()
        self.user_line.setPlaceholderText('Digite seu User Name...')

        self.password = QLabel('Password: ')
        self.pass_line = QLineEdit()
        self.pass_line.setPlaceholderText('Digite sua senha...')
        self.pass_line.setEchoMode(QLineEdit.Password)

        self.remember_me_checkbox = QCheckBox('Lembrar acesso (usuário)')

        self.error_label = QLabel('')

        self.login_button = QPushButton('Login')
        self.login_button.setStyleSheet(style_button)
        self.login_button.clicked.connect(self.login)

        self.cw_layout.addWidget(self.user_label)
        self.cw_layout.addWidget(self.user_line)
        self.cw_layout.addWidget(self.password)
        self.cw_layout.addWidget(self.pass_line)
        self.cw_layout.addWidget(self.remember_me_checkbox)
        self.cw_layout.addWidget(self.error_label)
        self.cw_layout.addWidget(self.login_button)

        self.setWindowTitle('Acesso ao Banco de dados')
        self.adjustFixedSize()
        self.center_window()

        self.load_username()

    def center_window(self):
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())

    def adjustFixedSize(self):
        self.setMinimumWidth(WIDHT_WINDOW)
        self.setMinimumHeight(HEIGHT_WINDOW)
        self.setMaximumWidth(WIDHT_WINDOW)
        self.setMaximumHeight(HEIGHT_WINDOW)

    def login(self):
        try:
            self.db_config['user'] = self.user_line.text()
            self.db_config['password'] = self.pass_line.text()
            self.con = connect(self.db_config)

            if self.con:
                self.services_window = ServicesWindow(connection=self.con)
                self.hide()
                self.services_window.show()
                self.timer.start(60000)

                if self.remember_me_checkbox.isChecked():
                    self.save_username()
        except mysql.connector.Error as err:
            if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
                self.error_label.setText("Usuário ou senha incorretos.")
            else:
                self.error_label.setText(f"Erro ao conectar: {err}")

    def save_username(self):

        username = self.user_line.text()
        with open(USERNAME_FILE, "w") as f:
            json.dump({"username": username}, f)

    def load_username(self):

        if os.path.exists(USERNAME_FILE):
            with open(USERNAME_FILE, "r") as f:
                data = json.load(f)
                self.user_line.setText(data.get("username", ""))
                self.remember_me_checkbox.setChecked(True)
        else:
            self.remember_me_checkbox.setChecked(False)

    def keep_connection_alive(self):
        try:
            if self.con and not self.con.is_connected():
                self.con = connect(self.db_config)
        except Exception as e:
            print(f"Erro ao manter a conexão ativa: {e}")

    def closeEvent(self, event):
        if self.con and self.con.is_connected():
            self.con.close()
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    db_window = DBAccessWindow()
    db_window.show()
    app.exec()
