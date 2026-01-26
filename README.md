## Nemo – AI Learning Assistant for Dyslexic Students

DP Nemo is an AI-powered accessibility chatbot designed to support students with dyslexia by providing simplified, conversational, and structured learning assistance.
It combines Rasa (NLU & dialogue management), a Flask backend, and a lightweight frontend UI to deliver an interactive learning experience.

This project focuses on clarity, reduced cognitive load, and accessibility-first design.

## Project Objectives

Assist dyslexic students with easy-to-understand explanations

Reduce reading overload using short, structured responses

Enable conversational learning instead of static content

Build a modular, scalable AI system suitable for academic deployment

## System Architecture (High Level)

User (Browser)
     ↓
Frontend (HTML/CSS/JS)
     ↓
Flask Backend (API Layer)
     ↓
Rasa Server (NLU + Dialogue)
     ↓
Response back to User

## Components:

Frontend – User-friendly chat interface

Flask Backend – Bridges frontend and Rasa

Rasa – Intent detection, entities, dialogue flow

Environment Config – Secure handling of API keys and URLs

## Project Structure
DP_PROG/
│
├── backend/
│   └── app.py
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── rasa/
│   ├── data/
│   │   ├── nlu.yml
│   │   └── stories.yml
│   ├── actions/
│   ├── config.yml
│   ├── domain.yml
│   └── endpoints.yml
│
├── .gitignore
├── .env.example
└── README.md

## How to Run the Project Locally
### 1.Clone the repository
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

### 2.Set up Python environment
python -m venv venv
venv\Scripts\activate   # Windows

pip install -r requirements.txt

##3 3.Run Rasa
cd rasa
rasa train
rasa run --enable-api


### 4️.Run Flask backend
cd backend
python app.py

### 5.Open Frontend
Open frontend/index.html in your browser.

Environment Variables

### Create a .env file (not committed):
RASA_URL=http://localhost:5005
OPENAI_API_KEY=your_api_key_here

🌱 Accessibility Considerations

Simple sentence structures

Reduced jargon

Predictable conversational flow

Friendly, encouraging responses

Designed keeping dyslexic cognitive patterns in mind

## Future Enhancements

->Text-to-speech support

->Reading-level adaptation

->Personalized learning paths

->Analytics for learning progress

Multilingual support

## Contributors

Lead Developer: Daphne Grace Backiam Nathaniel 2023BCSE07066
Team Members: Arunima Banerjee 2023BCSE07039, Angiras Venugopal 2023BCSE07021 , Taksir Alam 2023BCSE0781

Project Type: Academic / Accessibility-focused AI system

## License
This project is developed for educational and research purposes.
