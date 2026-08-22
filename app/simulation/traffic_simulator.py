# Traffic simulator preserved as a separate module.
import sys, time, random
from collections import defaultdict
from PyQt5.QtWidgets import QApplication,QMainWindow,QLabel,QVBoxLayout,QPushButton,QWidget,QTableWidget,QTableWidgetItem,QHeaderView,QLineEdit,QHBoxLayout,QProgressBar,QDialog,QFormLayout
from PyQt5.QtCore import Qt,QThread,pyqtSignal
from PyQt5.QtGui import QFont
from config import RATE_LIMIT, SECURITY_LEVELS, ADMIN_CREDENTIALS, LOG_FILE
BLACKLIST=set(); TRUSTED_IPS={"192.168.1.1","10.0.0.10"}; request_count=defaultdict(int); blocked_ips=set()
def log_event(event,ip,reason="N/A"):
    LOG_FILE.parent.mkdir(parents=True,exist_ok=True); ts=time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime()); msg=f"[{ts}] {event}: IP={ip}, Reason={reason}\n"; LOG_FILE.open("a",encoding="utf-8").write(msg); print(msg.strip())
def rate_limiter(ip):
    request_count[ip]+=1
    if request_count[ip]>RATE_LIMIT: BLACKLIST.add(ip); blocked_ips.add(ip); log_event("BLOCKED",ip,"Rate limit exceeded"); return False
    return True
def enforce_mls(ip,level):
    if ip in BLACKLIST: log_event("BLOCKED",ip,"Blacklisted IP"); return False
    if level>SECURITY_LEVELS["medium"] and ip not in TRUSTED_IPS: log_event("BLOCKED",ip,"Insufficient security level"); return False
    log_event("ALLOWED",ip,"Access granted"); return True
def generate_random_ip(): return ".".join(str(random.randint(1,255)) for _ in range(4))
class LoginDialog(QDialog):
    def __init__(self):
        super().__init__(); self.setWindowTitle("Admin Login"); layout=QFormLayout(); self.id_input=QLineEdit(); self.password_input=QLineEdit(); self.password_input.setEchoMode(QLineEdit.Password); layout.addRow("Admin ID:",self.id_input); layout.addRow("Password:",self.password_input); b=QPushButton("Login"); b.clicked.connect(self.verify); layout.addWidget(b); self.setLayout(layout)
    def verify(self):
        if ADMIN_CREDENTIALS.get(self.id_input.text())==self.password_input.text(): self.accept()
        else: self.id_input.clear(); self.password_input.clear()
class RequestSimulator(QThread):
    update_progress=pyqtSignal(int); update_traffic=pyqtSignal(list); simulation_complete=pyqtSignal()
    def __init__(self): super().__init__(); self.total_requests=0; self.max_requests=60; self.running=True
    def run(self):
        ips=[generate_random_ip() for _ in range(10)]+list(TRUSTED_IPS)
        while self.running and self.total_requests<self.max_requests:
            updates=[]
            for ip in ips:
                if self.total_requests>=self.max_requests: self.running=False; break
                allowed=rate_limiter(ip); level=random.choice(list(SECURITY_LEVELS.values()))
                if allowed: updates.append((time.strftime("%H:%M:%S"),ip,"ALLOWED" if enforce_mls(ip,level) else "BLOCKED"))
                self.update_progress.emit(int(self.total_requests/self.max_requests*100)); self.total_requests+=1
            self.update_traffic.emit(updates); time.sleep(1)
        self.update_progress.emit(100); self.simulation_complete.emit()
class FirewallSimulator(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("Network Traffic Security Simulator"); self.setGeometry(100,100,1000,700); self.traffic_stats=[]; layout=QVBoxLayout(); h=QLabel("Network Traffic Security Simulator"); h.setFont(QFont("Arial",16,QFont.Bold)); h.setAlignment(Qt.AlignCenter); layout.addWidget(h)
        self.table=QTableWidget(); self.table.setColumnCount(3); self.table.setHorizontalHeaderLabels(["Time","IP","Status"]); self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); layout.addWidget(self.table); self.progress=QProgressBar(); layout.addWidget(self.progress); self.start=QPushButton("Start Simulation"); self.start.clicked.connect(self.start_simulation); layout.addWidget(self.start); c=QWidget(); c.setLayout(layout); self.setCentralWidget(c)
    def start_simulation(self):
        self.sim=RequestSimulator(); self.sim.update_progress.connect(self.progress.setValue); self.sim.update_traffic.connect(self.update); self.sim.start()
    def update(self,updates):
        self.traffic_stats.extend(updates); self.table.setRowCount(len(self.traffic_stats))
        for r,row in enumerate(self.traffic_stats):
            for c,v in enumerate(row): self.table.setItem(r,c,QTableWidgetItem(v))
def run():
    app=QApplication(sys.argv); login=LoginDialog()
    if login.exec_()==QDialog.Accepted: w=FirewallSimulator(); w.show(); sys.exit(app.exec_())
if __name__=="__main__": run()
