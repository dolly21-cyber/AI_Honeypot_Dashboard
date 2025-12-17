RUN GUIDE (safe local mode)

1) Install dependencies:
   python -m pip install -r requirements.txt

2) (Optional) If you want local AI (recommended - Ollama/GPT4All), install and run Ollama per its docs.
   If Ollama is running at http://localhost:11434 and you pulled a model (e.g., llama3), the honeypot will try it.

3) Start the honeypot (in one terminal):
   python honeypot.py

   The honeypot listens on ports in config.json (default 127.0.0.1 only).

4) (Optional) In another terminal, run the simulator to generate sample interactions:
   python simulate_clients.py

5) Inspect logs in logs/port_<port>.jsonl

6) Launch the dashboard (in another terminal):
   streamlit run dashboard_app.py

7) To enable OpenAI instead of Ollama:
   - Set environment variable OPENAI_API_KEY (do not commit this key to version control)
     export OPENAI_API_KEY="sk-XXXX..."
   - Update config.json openai_model if desired.