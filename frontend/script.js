const chatBox = document.getElementById("chat-box");
const input = document.getElementById("user-input");
const loading = document.getElementById("loading");
const sendButton = document.querySelector(".input-area .primary");
const speedControl = document.getElementById("speed");
const speedValue = document.getElementById("speed-value");
const mascot = document.querySelector(".mascot");

let lastBotText = "";
const speech = window.speechSynthesis;
let speechRate = 0.9;
let activeUtterance = null;
let activeMessageEl = null;
let activeWordIndex = -1;
let resumeMessageEl = null;
let resumeWordIndex = null;
let activeStartChar = 0;
let currentBubble = null;

const audioIcons = {
  idle: "🔊",
  playing: "⏸",
  paused: "▶"
};

if (speedControl && speedValue) {
  const updateSpeed = () => {
    speechRate = parseFloat(speedControl.value);
    speedValue.textContent = `${speechRate.toFixed(1)}x`;
  };
  speedControl.addEventListener("input", updateSpeed);
  updateSpeed();
}

function setInputDisabled(state) {
  input.disabled = state;
  sendButton.disabled = state;
}

// Add message to chat
function addMessage(text, sender) {
  let div;
  if (sender === "bot") {
    div = createMessage(text, "bot");
  } else {
    div = createMessage(text, "user");
  }

  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// Show / hide loading
function showLoading() {
  loading.classList.remove("hidden");
  chatBox.setAttribute("aria-busy", "true");
  setInputDisabled(true);
}

function hideLoading() {
  loading.classList.add("hidden");
  chatBox.setAttribute("aria-busy", "false");
  setInputDisabled(false);
}

// Send normal message
function sendMessage() {
  const msg = input.value.trim();
  if (!msg) return;

  addMessage(msg, "user");
  input.value = "";
  showLoading();

  fetch("http://localhost:5000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: msg
    })
  })
    .then(res => res.json())
    .then(data => handleReply(data))
    .catch(err => {
      hideLoading();
      addMessage("Nemo had trouble responding.", "bot");
      console.error(err);
    });
}

// Send quick button message
function sendQuick(text) {
  showLoading();

  fetch("http://localhost:5000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      action: text
    })
  })
    .then(res => res.json())
    .then(data => handleReply(data))
    .catch(err => {
      hideLoading();
      addMessage("Nemo had trouble responding.", "bot");
      console.error(err);
    });
}

// Handle bot reply
function handleReply(data) {
  hideLoading();
  lastBotText = "";

  if (data && typeof data.reply === "string" && data.reply.trim()) {
    addMessage(data.reply, "bot");
    lastBotText = data.reply;
    return;
  }

  if (!Array.isArray(data) || data.length === 0) {
    addMessage("I did not get a reply this time. Try again?", "bot");
    return;
  }

  data.forEach(item => {
    if (item.text) {
      addMessage(item.text, "bot");
      lastBotText += `${item.text} `;
    }
  });
}

function createMessage(text, sender) {
  const div = document.createElement("div");
  div.className = `message ${sender === "bot" ? "bot-msg" : "user-msg"}`;
  div.dataset.fullText = text;

  const wordRanges = [];
  const wordRegex = /[\p{L}\p{N}]+(?:['’][\p{L}\p{N}]+)*/gu;
  let lastIndex = 0;
  let match;

  while ((match = wordRegex.exec(text)) !== null) {
    const start = match.index;
    const end = start + match[0].length;

    if (start > lastIndex) {
      div.appendChild(document.createTextNode(text.slice(lastIndex, start)));
    }

    const wordSpan = document.createElement("span");
    wordSpan.className = "word";
    wordSpan.textContent = match[0];
    wordSpan.dataset.wordIndex = wordRanges.length.toString();
    if (sender === "bot") {
      wordSpan.addEventListener("click", () => pronounceWord(wordSpan.textContent, div, wordSpan));
    }
    div.appendChild(wordSpan);

    wordRanges.push({ start, end });
    lastIndex = end;
  }

  if (lastIndex < text.length) {
    div.appendChild(document.createTextNode(text.slice(lastIndex)));
  }

  div._wordRanges = wordRanges;

  const audioButton = document.createElement("button");
  audioButton.className = "bubble-audio";
  audioButton.type = "button";
  audioButton.textContent = audioIcons.idle;
  audioButton.setAttribute("aria-label", "Read aloud");
  audioButton.addEventListener("click", () => toggleBubbleSpeech(div));
  div.appendChild(audioButton);

  return div;
}

function clearHighlights(el) {
  if (!el) return;
  const active = el.querySelector(".word.active");
  if (active) active.classList.remove("active");
  activeWordIndex = -1;
}

function highlightWord(el, index) {
  if (!el) return;
  if (activeWordIndex === index) return;
  clearHighlights(el);
  const target = el.querySelector(`.word[data-word-index="${index}"]`);
  if (target) {
    target.classList.add("active");
    activeWordIndex = index;
    resumeMessageEl = el;
    resumeWordIndex = index;
    el.dataset.resumeIndex = index.toString();
  }
}

function getWordIndexAtChar(ranges, charIndex) {
  for (let i = 0; i < ranges.length; i += 1) {
    if (charIndex >= ranges[i].start && charIndex < ranges[i].end) {
      return i;
    }
  }
  return -1;
}

// Text-to-speech
function speak(text) {
  speakMessage(text, activeMessageEl);
}

function speakMessage(text, messageEl, startChar = 0) {
  if (!speech) return;
  speech.cancel();
  activeUtterance = new SpeechSynthesisUtterance(text);
  activeUtterance.rate = speechRate;
  activeMessageEl = messageEl || activeMessageEl;
  activeStartChar = startChar;

  clearHighlights(activeMessageEl);
  setCurrentBubble(activeMessageEl, "playing");

  if (activeMessageEl && Array.isArray(activeMessageEl._wordRanges)) {
    activeUtterance.onboundary = event => {
      if (event.name !== "word") return;
      const idx = getWordIndexAtChar(
        activeMessageEl._wordRanges,
        event.charIndex + activeStartChar
      );
      if (idx !== -1) highlightWord(activeMessageEl, idx);
    };
  }

  activeUtterance.onstart = () => setMascotSpeaking(true);
  activeUtterance.onend = () => {
    clearHighlights(activeMessageEl);
    setMascotSpeaking(false);
    setCurrentBubble(activeMessageEl, "idle");
  };

  speech.speak(activeUtterance);
}

function pronounceWord(word, messageEl, spanEl) {
  if (!speech || !word) return;
  speech.cancel();
  activeMessageEl = messageEl;
  clearHighlights(activeMessageEl);
  if (spanEl) spanEl.classList.add("active");

  activeUtterance = new SpeechSynthesisUtterance(word);
  activeUtterance.rate = speechRate;
  resumeMessageEl = messageEl;
  resumeWordIndex = parseInt(spanEl?.dataset.wordIndex || "0", 10);
  messageEl.dataset.resumeIndex = resumeWordIndex.toString();
  setCurrentBubble(messageEl, "playing");
  activeUtterance.onstart = () => setMascotSpeaking(true);
  activeUtterance.onend = () => {
    if (spanEl) spanEl.classList.remove("active");
    setMascotSpeaking(false);
    setCurrentBubble(messageEl, "idle");
  };
  speech.speak(activeUtterance);
}

function readLast() {
  if (resumeMessageEl && resumeWordIndex !== null) {
    speakFromWordIndex(resumeMessageEl, resumeWordIndex);
    return;
  }
  if (lastBotText) speakMessage(lastBotText, chatBox.lastElementChild);
}

function stopSpeech() {
  speech.cancel();
  setMascotSpeaking(false);
  setCurrentBubble(currentBubble, "idle");
}

function speakFromWordIndex(messageEl, wordIndex) {
  if (!messageEl || !messageEl._wordRanges || !messageEl.dataset.fullText) return;
  const ranges = messageEl._wordRanges;
  if (wordIndex < 0 || wordIndex >= ranges.length) return;
  const startChar = ranges[wordIndex].start;
  const text = messageEl.dataset.fullText.slice(startChar);
  speakMessage(text, messageEl, startChar);
  resumeMessageEl = messageEl;
  resumeWordIndex = wordIndex;
  messageEl.dataset.resumeIndex = wordIndex.toString();
}

function setMascotSpeaking(isSpeaking) {
  if (!mascot) return;
  mascot.classList.toggle("speaking", isSpeaking);
}

function toggleBubbleSpeech(messageEl) {
  if (!messageEl) return;
  const state = getBubbleState(messageEl);

  if (currentBubble && currentBubble !== messageEl) {
    speech.cancel();
    setCurrentBubble(currentBubble, "idle");
  }

  if (currentBubble !== messageEl) {
    currentBubble = messageEl;
    const resumeIndex = parseInt(messageEl.dataset.resumeIndex || "0", 10);
    if (!Number.isNaN(resumeIndex) && resumeIndex > 0) {
      speakFromWordIndex(messageEl, resumeIndex);
    } else {
      speakMessage(messageEl.dataset.fullText || messageEl.textContent, messageEl);
    }
    return;
  }

  if (state === "playing") {
    speech.pause();
    setCurrentBubble(messageEl, "paused");
    setMascotSpeaking(false);
    return;
  }

  if (state === "paused") {
    speech.resume();
    setCurrentBubble(messageEl, "playing");
    setMascotSpeaking(true);
    return;
  }

  const resumeIndex = parseInt(messageEl.dataset.resumeIndex || "0", 10);
  if (!Number.isNaN(resumeIndex) && resumeIndex > 0) {
    speakFromWordIndex(messageEl, resumeIndex);
  } else {
    speakMessage(messageEl.dataset.fullText || messageEl.textContent, messageEl);
  }
}

function setCurrentBubble(messageEl, state) {
  if (!messageEl) return;
  currentBubble = messageEl;
  setBubbleState(messageEl, state);
}

function setBubbleState(messageEl, state) {
  const button = messageEl.querySelector(".bubble-audio");
  if (!button) return;
  button.dataset.state = state;
  button.textContent = audioIcons[state] || audioIcons.idle;
}

function getBubbleState(messageEl) {
  const button = messageEl.querySelector(".bubble-audio");
  return button?.dataset.state || "idle";
}
