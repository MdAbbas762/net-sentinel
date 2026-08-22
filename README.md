# 🛡️ NetSentinel: Network Traffic Monitoring & Access Control System

NetSentinel is a Python-based application that acts as a security checkpoint between incoming clients and a protected service. It evaluates network requests against defined security rules and decides whether traffic should be allowed or denied.

The system acts as an intermediary between clients and a protected backend service. Incoming requests are inspected and evaluated against security rules before being either allowed to reach the backend or blocked by the firewall.

---

## 📖 Overview

The **Network Firewall Security Simulator** demonstrates how network requests can be monitored and controlled using custom security policies.

The firewall receives incoming client connections and applies multiple security checks, including:

* 🚦 Request rate limiting
* 🚫 IP blacklisting
* 🔐 Multi-Level Security (MLS) enforcement
* 👥 Trusted IP access control
* 📊 Real-time traffic monitoring
* 📝 Security event logging
* 🖥️ Administrative IP management

If a request passes the security checks, it is forwarded to the protected backend service. Otherwise, the firewall blocks the request and returns an HTTP `403 Forbidden` response.

The project also includes a **PyQt5-based administrative dashboard** and a **traffic simulator** for testing and demonstrating the firewall's behavior.

---

## ✨ Features

### 🚦 Rate Limiting

The firewall tracks incoming requests from individual IP addresses.

When an IP exceeds the configured request limit, it is automatically added to the blacklist and future requests from that address are blocked.

```python
RATE_LIMIT = 5
```

---

### 🚫 Automatic IP Blacklisting

IPs can be added to the blacklist automatically when suspicious behavior is detected, such as exceeding the configured request limit.

Once blacklisted, an IP is denied access until it is manually removed from the blacklist.

---

### 🔐 Multi-Level Security (MLS)

The system supports three security levels:

| Security Level | Value |
| -------------- | ----: |
| 🟢 Low         |   `1` |
| 🟡 Medium      |   `2` |
| 🔴 High        |   `3` |

Incoming requests can specify a security level using the `X-Sec-Level` HTTP header.

For example:

```http
X-Sec-Level: high
```

High-security requests are restricted to trusted IP addresses, demonstrating a basic implementation of multi-level access control.

---

### 👥 Trusted IP Access

Specific IP addresses can be configured as trusted sources.

Trusted IPs are allowed to access higher security levels that may be restricted for other clients.

Example:

```python
TRUSTED_IPS = {"127.0.0.1"}
```

---

### 🌐 Firewall Proxy

The firewall operates as a proxy between the client and a protected backend service.

```text
Client
   │
   ▼
┌───────────────────────┐
│   Firewall Server     │
│                       │
│  • Rate Limiting      │
│  • IP Blacklisting    │
│  • MLS Enforcement    │
│  • Access Control     │
└───────────┬───────────┘
            │
       ┌────┴────┐
       │         │
    BLOCK      ALLOW
       │         │
       ▼         ▼
  403 Response  Backend Service
```

Requests that pass all security checks are forwarded to the backend service.

Blocked requests receive:

```text
HTTP/1.1 403 Forbidden
```

---

### 🖥️ Administrative Dashboard

The project includes a desktop-based administrative dashboard built with **PyQt5**.

The dashboard allows an administrator to:

* 🔑 Authenticate using admin credentials
* 📊 Monitor firewall activity
* 📝 View security logs in real time
* 🚫 Manually block IP addresses
* ✅ Unblock previously blocked IP addresses
* 🔍 Review the reason behind each security event

The dashboard automatically refreshes to display newly generated firewall logs.

---

### 📊 Traffic Simulation

A built-in traffic simulator is included to demonstrate how the firewall handles different types of requests.

The simulator can generate traffic involving:

* Random IP addresses
* Trusted IP addresses
* Different security levels
* Allowed requests
* Blocked requests
* Rate-limit violations

This provides a controlled environment for testing and demonstrating the firewall's security rules.

---

### 📝 Real-Time Audit Logging

All important security events are recorded in:

```text
firewall_logs.txt
```

The system logs events such as:

* ✅ Allowed requests
* 🚫 Blocked requests
* 🚦 Rate-limit violations
* 🔐 Multi-level security violations
* ⛔ Manual IP blocking
* 🔓 IP unblocking
* ⚠️ Connection or processing errors

Example:

```text
[2025-12-17 13:14:44] BLOCKED: IP=192.168.56.101, Reason=Rate limit exceeded
```

These logs provide an audit trail that can be used to monitor and analyze firewall activity.

---

# 🏗️ System Architecture

The project consists of three main components.

```text
                         ┌─────────────────┐
                         │     Client      │
                         └────────┬────────┘
                                  │
                                  ▼
                     ┌────────────────────────┐
                     │    Firewall Server     │
                     │                        │
                     │  • Rate Limiting       │
                     │  • IP Blacklisting     │
                     │  • MLS Enforcement     │
                     │  • Request Filtering   │
                     └────────────┬───────────┘
                                  │
                     ┌────────────┴────────────┐
                     │                         │
                   BLOCK                     ALLOW
                     │                         │
                     ▼                         ▼
              HTTP 403 Response        Backend Service


     ┌──────────────────────┐
     │  Admin Dashboard     │
     │      (PyQt5)         │
     └──────────┬───────────┘
                │
                ▼
     ┌──────────────────────┐
     │ Admin Control Server │
     │                      │
     │   BLOCK / UNBLOCK    │
     └──────────────────────┘
```

---

## 🔄 Request Processing Flow

Every incoming request goes through the following security process:

```text
Incoming Request
       │
       ▼
Identify Client IP
       │
       ▼
Check Rate Limit
       │
       ├── Limit Exceeded ─────────► Add IP to Blacklist
       │                                  │
       ▼                                  ▼
Check Blacklist ◄───────────────────── BLOCK
       │
       ▼
Read Security Level
       │
       ▼
Apply MLS Policy
       │
       ├── Policy Violation ─────────► BLOCK
       │
       ▼
     ALLOW
       │
       ▼
Forward Request to Backend
```

---

# 📁 Project Structure

```text
network-firewall-security-simulator/
│
├── 📁 logs/
│   └── firewall_logs.txt
│
├── 📁 src/
│   ├── firewall_server.py
│   ├── firewall_gui.py
│   └── firewall_simulator.py
│
├── requirements.txt
└── README.md
```

### 📄 `firewall_server.py`

The core firewall component responsible for:

* Accepting incoming TCP connections
* Inspecting incoming requests
* Tracking request counts
* Applying rate limits
* Managing blacklisted IPs
* Enforcing Multi-Level Security policies
* Forwarding allowed requests to the backend
* Blocking unauthorized requests
* Recording security events
* Handling administrative commands

---

### 🖥️ `firewall_gui.py`

The administrative dashboard responsible for:

* Admin authentication
* Real-time firewall log monitoring
* Manual IP blocking
* Manual IP unblocking
* Communication with the firewall's admin control server

---

### 🧪 `firewall_simulator.py`

A standalone simulation application that generates sample traffic and demonstrates the firewall's security behavior.

It is useful for testing:

* Rate limiting
* IP blacklisting
* Multi-Level Security
* Trusted IP access
* Allowed and blocked traffic

---

### 📝 `logs/firewall_logs.txt`

Contains recorded firewall events and provides an audit trail of system activity.

---

# 🛠️ Technology Stack

| Technology                   | Purpose                                  |
| ---------------------------- | ---------------------------------------- |
| 🐍 Python                    | Core application development             |
| 🌐 Socket Programming        | TCP communication and firewall proxy     |
| 🧵 Threading                 | Concurrent connection handling           |
| 🖥️ PyQt5                    | Administrative graphical interface       |
| 📦 `collections.defaultdict` | Request tracking                         |
| 🔗 HTTP                      | Request forwarding and response handling |
| 📝 File Logging              | Security event auditing                  |

---

# ⚙️ Requirements

Before running the project, make sure you have:

* Python **3.8 or later**
* `pip`
* PyQt5

Install the required dependency using:

```bash
pip install -r requirements.txt
```

---

# 🚀 Getting Started

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/YourUsername/network-firewall-security-simulator.git
```

Navigate to the project directory:

```bash
cd network-firewall-security-simulator
```

---

## 2️⃣ Create a Virtual Environment

Creating a virtual environment is recommended.

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Running the Project

The project contains multiple components that can be run independently.

## 🛡️ Start the Firewall Server

Run:

```bash
python src/firewall_server.py
```

The firewall server listens for incoming client connections on:

```text
0.0.0.0:9090
```

Allowed traffic is forwarded to the configured backend service:

```text
127.0.0.1:8080
```

The administrative control server runs locally on:

```text
127.0.0.1:9999
```

---

## 🖥️ Start the Administrative Dashboard

Open a separate terminal and run:

```bash
python src/firewall_gui.py
```

The application will display an administrator login window.

### Demo Credentials

```text
Username: admin
Password: 123
```

Once authenticated, the dashboard allows you to monitor logs and manually manage blocked IP addresses.

---

## 🧪 Run the Traffic Simulator

To simulate firewall traffic, run:

```bash
python src/firewall_simulator.py
```

The simulator provides a graphical interface where you can start traffic simulation and observe how different requests are allowed or blocked.

---

# 🔐 Security Controls

## 🚦 Rate Limiting

The firewall tracks the number of requests received from each IP address.

```python
RATE_LIMIT = 5
```

Once the request count exceeds the configured limit, the IP is automatically blacklisted.

---

## 🚫 IP Blacklisting

The blacklist is used to deny requests from blocked IP addresses.

An IP can be added to the blacklist:

* Automatically after exceeding the rate limit
* Manually through the administrative dashboard

An administrator can also remove an IP from the blacklist.

---

## 🔐 Multi-Level Security

The firewall evaluates the requested security level using the following HTTP header:

```http
X-Sec-Level: high
```

Supported levels are:

```text
low
medium
high
```

The corresponding internal values are:

```text
low    → 1
medium → 2
high   → 3
```

High-level access is restricted to trusted IP addresses.

---

# 🧪 Testing the Firewall

The firewall can be tested using the included simulator or external tools such as `curl`.

## Basic Request

```bash
curl http://127.0.0.1:9090
```

---

## Test a Security Level

For example, to send a request with a high security level:

```bash
curl -H "X-Sec-Level: high" http://127.0.0.1:9090
```

If the requesting IP is not trusted, the firewall should reject the request.

---

## Test Rate Limiting

Send multiple requests to trigger the rate limit:

```bash
for i in $(seq 1 10); do
    curl -I http://127.0.0.1:9090
done
```

After exceeding the configured request limit, the firewall will block the IP and return:

```text
HTTP/1.1 403 Forbidden
```

---

# 📋 Audit Logging

Firewall activity is recorded using the following format:

```text
[TIMESTAMP] EVENT: IP=ADDRESS, Reason=REASON
```

Example:

```text
[2025-12-17 13:14:44] BLOCKED: IP=192.168.56.101, Reason=Rate limit exceeded
```

This provides a clear record of security-related events and helps demonstrate basic network auditing concepts.

---

# 🖥️ Administrative Controls

The graphical dashboard communicates with the firewall server through a local administrative socket.

The following actions are supported:

```text
BLOCK <IP>
```

and:

```text
UNBLOCK <IP>
```

For example:

```text
BLOCK 192.168.1.100
```

or:

```text
UNBLOCK 192.168.1.100
```

Each manual action is also recorded in the firewall logs.

---

# 🎓 Learning Objectives

This project demonstrates practical concepts related to:

* 🌐 Network socket programming
* 🔗 TCP client-server communication
* 🛡️ Firewall and proxy concepts
* 🚦 Rate limiting
* 🚫 IP blacklisting
* 🔐 Access control and Multi-Level Security
* 🧵 Concurrent programming with threads
* 🖥️ GUI-based system administration
* 📝 Security event logging
* 🧪 Network traffic simulation
* 🔍 Basic security auditing

---

# ⚠️ Current Limitations

This project is intended as an educational network security simulation and has several limitations that would need to be addressed before production use.

Current limitations include:

* In-memory blacklist storage
* In-memory request tracking
* Hardcoded demonstration credentials
* Basic HTTP request parsing
* No persistent database
* No advanced packet inspection
* No TLS/HTTPS inspection
* No configurable rate-limit time window
* No role-based access control
* No production-grade authentication system

---

# 🚧 Future Improvements

Potential improvements for future versions include:

* 💾 Persistent firewall rules
* 🗄️ Database-backed audit logs
* ⏱️ Configurable rate-limit windows
* 🔑 Secure password hashing
* 👥 Role-based administrator access
* 🔒 HTTPS/TLS support
* 🔍 Advanced request inspection
* 🌐 IP range and CIDR-based rules
* 📊 Traffic analytics and visualization
* 🔔 Real-time security alerts
* 📧 Email notifications
* 🔌 REST API for remote administration
* 🐳 Docker deployment
* 🧪 Automated security testing
