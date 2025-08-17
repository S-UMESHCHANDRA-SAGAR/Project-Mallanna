# server.py
from flask import Flask, request, jsonify
import subprocess, shlex, math, time

app = Flask(__name__)

# === Replace this with your real LLM call ===
def call_llm(prompt: str) -> str:
    # placeholder LLM logic: simple hard-coded responses for demo
    if "time" in prompt.lower():
        return f"The time is {time.ctime()}."
    if "calculate" in prompt.lower():
        # extract simple expression after 'calculate'
        expr = prompt.lower().split("calculate",1)[1].strip()
        try:
            result = eval(expr, {"__builtins__":None}, {"math":math})
            return f"Result: {result}"
        except Exception as e:
            return "Sorry, I couldn't evaluate that expression."
    return "I heard you. (Replace call_llm with a real LLM)."

# === Action router ===
def run_action(intent: str, params: dict):
    # keep actions small and controlled
    if intent == "open_url":
        url = params.get("url")
        # This example just returns the action; don't auto-open on server
        return {"status":"ok", "action":"open_url", "url":url}
    if intent == "run_shell":
        # CAUTION: extremely dangerous to run arbitrary shell commands.
        cmd = params.get("cmd")
        safe_cmds = ["echo hello", "uptime"]
        if cmd in safe_cmds:
            out = subprocess.check_output(shlex.split(cmd)).decode()
            return {"status":"ok","output":out}
        else:
            return {"status":"rejected", "reason":"unsafe command"}
    return {"status":"unknown_intent"}

# Simple endpoint: send user text, get response (LLM + possible action)
@app.route("/api/command", methods=["POST"])
def command():
    data = request.json or {}
    text = data.get("text", "")
    # naive intent detection (replace with proper NLU)
    if text.lower().startswith("open "):
        # user said: "open https://..."
        url = text.split(" ",1)[1].strip()
        action_res = run_action("open_url", {"url": url})
        return jsonify({"type":"action","result":action_res})
    # otherwise ask LLM
    llm_reply = call_llm(text)
    return jsonify({"type":"reply","text": llm_reply})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
