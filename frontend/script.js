const chatBox = document.getElementById("chat-box");

/* -----------------------------
   ADD MESSAGE TO CHAT
----------------------------- */
function addMessage(text, sender) {
  const msg = document.createElement("div");
  msg.className = `message ${sender}`;

  // 👇 KEY FIX: bot messages use innerHTML
  if (sender === "bot") {
    msg.innerHTML = makeWordsSpeakable(text);
  } else {
    msg.innerText = text;
  }

  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

/* -----------------------------
   SEND USER MESSAGE
----------------------------- */
function sendMessage() {
  const input = document.getElementById("user-input");
  const text = input.value.trim();
  if (!text) return;

  addMessage(text, "user");
  input.value = "";

  fetch("http://localhost:5000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: text })
  })
    .then(res => res.json())
    .then(data => addMessage(data.reply, "bot"));
}

/* -----------------------------
   QUICK ACTION BUTTONS
----------------------------- */
function sendQuickAction(action) {
  fetch("http://localhost:5000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action: action })
  })
    .then(res => res.json())
    .then(data => addMessage(data.reply, "bot"));
}

/* -----------------------------
   TEXT TO SPEECH (FULL MESSAGE)
----------------------------- */
let fullSpeech = null;

function speakLastBotMessage() {
  const bots = document.querySelectorAll(".bot");
  if (!bots.length) return;

  const speech = new SpeechSynthesisUtterance(
    bots[bots.length - 1].innerText
  );

  speech.rate = 0.85;
  speech.pitch = 1.1;

  speech.onstart = () => nemoTalking(true);
  speech.onend = () => nemoTalking(false);

  window.speechSynthesis.speak(speech);
}


function pauseSpeech() {
  if (window.speechSynthesis.speaking) {
    window.speechSynthesis.pause();
  }
}

function resumeSpeech() {
  if (window.speechSynthesis.paused) {
    window.speechSynthesis.resume();
  }
}

function stopSpeech() {
  window.speechSynthesis.cancel();
}

/* -----------------------------
   WORD-BY-WORD SPEAKING
----------------------------- */
let currentUtterance = null;

function speakWord(word) {
  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(word);
  utterance.rate = 0.8;
  utterance.pitch = 1.1;
  utterance.lang = "en-US";

  currentUtterance = utterance;
  window.speechSynthesis.speak(utterance);
}

/* -----------------------------
   MAKE WORDS CLICKABLE
----------------------------- */
function makeWordsSpeakable(text) {
  return text.split(/\s+/).map(word => {
    const clean = word.replace(/'/g, "");
    return `<span class="speak-word" onclick="speakWord('${clean}')">${word}</span>`;
  }).join(" ");
}

function nemoTalking(isTalking) {
  const nemo = document.getElementById("nemo");
  if (!nemo) return;

  nemo.style.animation = isTalking
    ? "float 1.5s ease-in-out infinite"
    : "float 3s ease-in-out infinite";
}

