import sys, socket
from PyQt5.QtWidgets import QApplication,QMainWindow,QLabel,QVBoxLayout,QPushButton,QWidget,QTableWidget,QTableWidgetItem,QHeaderView,QLineEdit,QHBoxLayout,QDialog,QFormLayout
from PyQt5.QtCore import QTimer,Qt
from PyQt5.QtGui import QFont
from config import LOG_FILE, ADMIN_CREDENTIALS, ADMIN_HOST, ADMIN_PORT

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__(); self.setWindowTitle("Admin Login"); self.setFixedSize(300,150)
        layout=QFormLayout(); self.user=QLineEdit(); self.pwd=QLineEdit(); self.pwd.setEchoMode(QLineEdit.Password)
        layout.addRow("Admin ID:",self.user); layout.addRow("Password:",self.pwd)
        btn=QPushButton("Login"); btn.clicked.connect(self.check); layout.addWidget(btn); self.setLayout(layout)
    def check(self):
        if ADMIN_CREDENTIALS.get(self.user.text())==self.pwd.text(): self.accept()
        else: self.user.clear(); self.pwd.clear(); self.user.setPlaceholderText("Invalid credentials")

class FirewallDashboard(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("Firewall Admin Dashboard"); self.setGeometry(100,100,1000,600); self.logs=[]
        main=QVBoxLayout(); title=QLabel("Real-Time Firewall Monitoring & Control"); title.setFont(QFont("Arial",16,QFont.Bold)); title.setAlignment(Qt.AlignCenter); main.addWidget(title)
        self.table=QTableWidget(); self.table.setColumnCount(4); self.table.setHorizontalHeaderLabels(["Time","Event","IP","Reason"]); self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); main.addWidget(self.table)
        ctrl=QHBoxLayout(); self.ip_input=QLineEdit(); self.ip_input.setPlaceholderText("Enter IP address")
        block=QPushButton("Block IP"); unblock=QPushButton("Unblock IP"); block.clicked.connect(self.block_ip); unblock.clicked.connect(self.unblock_ip)
        ctrl.addWidget(self.ip_input); ctrl.addWidget(block); ctrl.addWidget(unblock); main.addLayout(ctrl)
        container=QWidget(); container.setLayout(main); self.setCentralWidget(container)
        self.timer=QTimer(); self.timer.timeout.connect(self.load_logs); self.timer.start(2000)
    def send_admin_command(self,cmd):
        try:
            s=socket.socket(socket.AF_INET,socket.SOCK_STREAM); s.connect((ADMIN_HOST,ADMIN_PORT)); s.sendall(cmd.encode()); s.close()
        except Exception as e: print("Admin command error:",e)
    def block_ip(self):
        ip=self.ip_input.text().strip()
        if ip: self.send_admin_command(f"BLOCK {ip}"); self.ip_input.clear()
    def unblock_ip(self):
        ip=self.ip_input.text().strip()
        if ip: self.send_admin_command(f"UNBLOCK {ip}"); self.ip_input.clear()
    def load_logs(self):
        if not LOG_FILE.exists(): return
        parsed=[]
        for line in LOG_FILE.read_text(encoding="utf-8").splitlines():
            try:
                t=line.split("]")[0].strip("["); rest=line.split("]",1)[1]; event=rest.split(":",1)[0].strip(); ip=rest.split("IP=")[1].split(",")[0]; reason=rest.split("Reason=")[1].strip(); parsed.append((t,event,ip,reason))
            except Exception: continue
        if parsed!=self.logs: self.logs=parsed; self.update_table()
    def update_table(self):
        self.table.setRowCount(len(self.logs))
        for r,row in enumerate(self.logs):
            for c,val in enumerate(row): self.table.setItem(r,c,QTableWidgetItem(val))

def run():
    app=QApplication(sys.argv); login=LoginDialog()
    if login.exec_()==QDialog.Accepted:
        gui=FirewallDashboard(); gui.show(); sys.exit(app.exec_())
if __name__=="__main__": run()
