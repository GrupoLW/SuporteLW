import logging
import os
import sys
import traceback
from views.db_acess import DBAccessWindow
from PySide6.QtWidgets import QApplication, QMessageBox

# Configuração do arquivo de log
log_file = "app_error.log"
logging.basicConfig(
    filename=log_file,
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = DBAccessWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        # Captura o erro no arquivo de log
        logging.error("Erro crítico no programa", exc_info=True)

        # Exibe uma mensagem ao usuário (se possível)
        error_message = (
            f"O programa encontrou um erro crítico e será encerrado.\n"
            f"Verifique o arquivo de log '{os.path.abspath(log_file)}' para mais detalhes."
        )
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Erro")
        msg_box.setText("Erro no programa!")
        msg_box.setDetailedText(str(e))
        msg_box.exec()

        # Encerra o programa
        sys.exit(1)
