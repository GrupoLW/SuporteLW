from PySide6.QtWidgets import QLineEdit, QPushButton, QLabel, QWidget, QFileDialog
from PySide6.QtCore import Qt


# Colors
PRIMARY_COLOR = '#1e81b0'
DARKER_PRIMARY_COLOR = '#16658a'
DARKEST_PRIMARY_COLOR = '#115270'


# Sizing
BIG_FONT_SIZE = 15
MEDIUM_FONT_SIZE = 12
SMALL_FONT_SIZE = 10
TEXT_MARGIN = 10
MINIMUM_WIDTH = 500

class DirectoryLine(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configStyle()

    def configStyle(self):
        self.setStyleSheet(f'font-size: {MEDIUM_FONT_SIZE}px; padding:4px;')
        self.setMinimumWidth(MINIMUM_WIDTH)
        self.setReadOnly(True)
        self.setPlaceholderText('Selecione um arquivo...')


class DirectoryButton(QPushButton):

    def __init__(self, text, _widht, _height, directory_line: DirectoryLine, _is_input : bool):
        super().__init__(text=text)
        self._widht = _widht
        self._height = _height
        self._input = _is_input
        self.setMaximumSize(_widht, _height)
        self.directory_line = directory_line

        if self._input:
            self.clicked.connect(self.search_file)
        else:
            self.clicked.connect(self.search_directory)

    def search_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        caminho_arquivo, _ = QFileDialog.getOpenFileName(self, "Selecione um arquivo", "", "Arquivos Excel (*.xlsx *.xls *.ods)", options=options)

        if caminho_arquivo:  # Verificar se o arquivo foi selecionado
            self.directory_line.setText(caminho_arquivo)

    def search_directory(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self, "Selecione um diretório", options=options)

        if directory:  # Verificar se o diretório foi selecionado
            self.directory_line.setText(directory)

    def _connectButtonClicked(self, button, slot):
        button.clicked.connect(slot)  # type: ignore


class DirectoryTitle(QLabel):
    def __init__(self, text: str, parent: QWidget | None = None) -> None:
            super().__init__(text, parent)
            self.configStyle()

    def configStyle(self):
        self.setStyleSheet(f'font-size: {MEDIUM_FONT_SIZE}px; paddind: 5px;')
        self.setAlignment(Qt.AlignmentFlag.AlignRight)


