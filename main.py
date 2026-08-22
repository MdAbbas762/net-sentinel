import threading
from app.core.firewall import run as run_firewall
from app.interface.dashboard import run as run_dashboard
from app.simulation.traffic_simulator import run as run_simulator

def main():
    print("\nNetwork Firewall Security Simulator")
    print("1. Start Firewall Server")
    print("2. Launch Admin Dashboard")
    print("3. Run Traffic Simulator")
    print("4. Exit")
    choice=input("Select an option: ").strip()
    if choice=="1": run_firewall()
    elif choice=="2": run_dashboard()
    elif choice=="3": run_simulator()
    else: print("Goodbye.")

if __name__=="__main__": main()
