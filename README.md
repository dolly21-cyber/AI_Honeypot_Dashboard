# AI-Powered Honeypot with Real-Time Dashboard

This project implements a **multi-service honeypot** that simulates **SSH, FTP, and HTTP services**. It uses a local AI model to generate realistic attacker responses and visualizes attack data in **real-time** using a Streamlit dashboard.

---

## 🚀 Features
- Multi-port honeypot (SSH, FTP, HTTP)  
- AI-based realistic attacker responses using **Ollama**  
- JSON-based logging of attacks  
- Real-time analytics dashboard with **Streamlit**

---

## 🛠 Technologies Used
- **Python**  
- **Ollama** (Local AI model)  
- **Streamlit** (Dashboard)  
- Linux / Windows compatible

---

## ⚡ How to Run
1. Clone the repository:
```bash
git clone https://github.com/your-username/AI-Honeypot-Dashboard.git
cd AI-Honeypot-Dashboard
2.Install dependencies:
pip install -r requirements.txt
3.Run the honeypot:
python honeypot.py
4.Run the dashboard:
streamlit run dashboard_app.py