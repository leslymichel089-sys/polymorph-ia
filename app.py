from flask import Flask, request, jsonify, send_from_directory
from google import genai
import os
import json

app = Flask(__name__, static_folder='static')

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client_gemini = genai.Client(api_key=GEMINI_API_KEY)

MEMORY_FILE = "memoire.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"faits": []}

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

SYSTEM_PROMPT = """Tu es POLYMORPHIA, une IA autonome et puissaante creee par PDG Lesly Michel de Lesly Tech LLC.
Tu t appelles POLYMORPHIA et uniquement POLYMORPHIA.
Reponds avec calme, clarte et profondeur. Parle en francais et creole haitien par defaut.
Si l utilisateur te confie quelque chose d important, retiens-le avec: [MEMOIRE: info]"""

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    memory = load_memory()
    faits = "\n".join(f"- {f}" for f in memory["faits"]) if memory["faits"] else "Aucun souvenir."
    full_prompt = f"{SYSTEM_PROMPT}\n\nCe que tu sais: {faits}\n\nUtilisateur: {message}"
    response = client_gemini.models.generate_content(
        model='gemini-2.0-flash-lite',
        contents=full_prompt
    )
    answer = response.text
    lines = answer.split("\n")
    clean = []
    for line in lines:
        if line.startswith("[MEMOIRE:") and line.endswith("]"):
            fait = line[9:-1].strip()
            if fait not in memory["faits"]:
                memory["faits"].append(fait)
                save_memory(memory)
        else:
            clean.append(line)
    return jsonify({"response": "\n".join(clean).strip()})

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
