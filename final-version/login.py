from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, 
                            QRadioButton, QLineEdit, QPushButton, QMessageBox, QButtonGroup)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import subprocess
import sys

# Predefined correct id and password
CORRECT_ID = "admin"
CORRECT_PASS = "1234"

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Node Selection and Login")
        self.setFixedSize(300, 300)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Node selection
        node_label = QLabel("Select Node Type:")
        node_label.setFont(QFont("Arial", 12))
        self.layout.addWidget(node_label, alignment=Qt.AlignCenter)
        
        self.node_type_group = QButtonGroup(self)
        
        self.master_radio = QRadioButton("Master")
        self.master_radio.setFont(QFont("Arial", 11))
        self.node_type_group.addButton(self.master_radio)
        self.layout.addWidget(self.master_radio, alignment=Qt.AlignCenter)
        
        self.slave_radio = QRadioButton("Slave")
        self.slave_radio.setFont(QFont("Arial", 11))
        self.node_type_group.addButton(self.slave_radio)
        self.layout.addWidget(self.slave_radio, alignment=Qt.AlignCenter)
        
        # ID and Password fields
        id_label = QLabel("User ID:")
        id_label.setFont(QFont("Arial", 12))
        self.layout.addWidget(id_label)
        
        self.entry_id = QLineEdit()
        self.entry_id.setFont(QFont("Arial", 12))
        self.layout.addWidget(self.entry_id)
        
        pass_label = QLabel("Password:")
        pass_label.setFont(QFont("Arial", 12))
        self.layout.addWidget(pass_label)
        
        self.entry_pass = QLineEdit()
        self.entry_pass.setFont(QFont("Arial", 12))
        self.entry_pass.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.entry_pass)
        
        # Login button
        self.login_btn = QPushButton("Proceed")
        self.login_btn.setFont(QFont("Arial", 12))
        self.login_btn.setStyleSheet("background-color: green; color: white;")
        self.login_btn.clicked.connect(self.check_login)
        self.layout.addWidget(self.login_btn)
        
    def check_login(self):
        selected_node = None
        if self.master_radio.isChecked():
            selected_node = "Master"
        elif self.slave_radio.isChecked():
            selected_node = "Slave"
            
        if not selected_node:
            QMessageBox.warning(self, "Node Type Missing", "Please select a node type (Master or Slave).")
            return
            
        if selected_node == "Master":
            user_id = self.entry_id.text()
            password = self.entry_pass.text()

            if user_id == CORRECT_ID and password == CORRECT_PASS:
                QMessageBox.information(self, "Login Successful", "Welcome!")

                # Start s1.py servers in background
                subprocess.Popen([sys.executable, "s1.py", "8081"])
                subprocess.Popen([sys.executable, "s1.py", "8082"])
                subprocess.Popen([sys.executable, "s1.py", "8083"])

                self.close()  # Close the login window

                # Now open adv3_ui.py
                subprocess.run([sys.executable, "adv4_ui.py"])
            else:
                QMessageBox.critical(self, "Login Failed", "Incorrect ID or Password.")

        elif selected_node == "Slave":
            # Slave node - directly open slave_ui.py to see available files
            self.close()
            subprocess.run([sys.executable, "slave_ui.py"])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())