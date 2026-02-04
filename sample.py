# save as generate_arch_diagram.py
from graphviz import Digraph

dot = Digraph("NEMO_System", format="png")
dot.attr(rankdir="TB", bgcolor="white", fontsize="12", fontname="Arial")

# Styles
def node(id_, label, fill, shape="box"):
    dot.node(
        id_,
        label,
        shape=shape,
        style="rounded,filled",
        fillcolor=fill,
        color="#3d3d3d",
        fontname="Arial",
        fontsize="11",
        margin="0.15,0.08"
    )

def edge(a, b, label=""):
    dot.edge(a, b, label=label, color="#4a4a4a", arrowsize="0.8", fontsize="10")

# Nodes
node("Student1", "Student", "#ffffff", "circle")
node("Frontend", "Frontend\n(HTML/CSS/JS)", "#f6d365")
node("Backend", "Backend\n(Flask)", "#7f6cd6")
node("RasaWebhook", "POST /webhooks/rest/webhook", "#2f6fb6")
node("Rasa", "Rasa Server", "#7f6cd6")
node("Ollama", "Ollama API", "#4caf6a")
node("Student2", "Student", "#ffffff", "circle")

# Flow
edge("Student1", "Frontend", "1  Type message / click Simpler")
edge("Frontend", "Backend", "2  POST /chat (message or action)")
edge("Backend", "RasaWebhook", "3a  Small talk intent")
edge("RasaWebhook", "Rasa", "Response text")
edge("Backend", "Ollama", "3b  Learning / Simplify")
edge("Ollama", "Backend", "Generated reply")
edge("Backend", "Frontend", "4  JSON { reply: \"...\" }")
edge("Frontend", "Student2", "5  Render + TTS / Word highlight")

# Output
dot.render("nemo_architecture", cleanup=True)
print("Saved as nemo_architecture.png")
