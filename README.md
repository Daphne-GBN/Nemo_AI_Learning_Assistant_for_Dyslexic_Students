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

                     ┌───────────────────────────┐
                     │            User           │
                     │   (Student / Learner)     │
                     └─────────────┬─────────────┘
                                   │
                         HTTP / User Input
                                   │
                 ┌─────────────────▼────────────────┐
                 │              Frontend            │
                 │      (HTML / CSS / JavaScript)   │
                 │   • Chat UI                      │
                 │   • Sends user messages          │
                 │   • Displays responses           │
                 └─────────────────┬────────────────┘
                                   │
                          REST API Calls
                                   │
                 ┌─────────────────▼─────────────────┐
                 │           Flask Backend           │
                 │           (API Gateway)           │
                 │   • Receives user queries         │
                 │   • Handles routing & validation  │
                 │   • Forwards requests to Rasa     │
                 └─────────────────┬─────────────────┘
                                   │
                         HTTP / JSON Payload
                                   │
                 ┌─────────────────▼─────────────────┐
                 │              Rasa Server          │
                 │        (Conversational AI)        │
                 │   • Intent classification         │
                 │   • Entity extraction             │
                 │   • Dialogue management           │
                 │   • Policy selection              │
                 └─────────────────┬─────────────────┘
                                   │
                         Predicted Response
                                   │
                 ┌─────────────────▼─────────────────┐
                 │           Response Flow           │
                 │  Rasa → Flask → Frontend → User   │
                 └───────────────────────────────────┘

## Components:

Frontend – User-friendly chat interface

Flask Backend – Bridges frontend and Rasa

Rasa – Intent detection, entities, dialogue flow

Environment Config – Secure handling of API keys and URLs

## Project Structure
              graph TD
    A[DP_PROG] --> B[Frontend]
    A --> C[Backend]
    A --> D[Rasa]
    A --> E[Config & Docs]

    B --> B1[index.html]
    B --> B2[script.js]
    B --> B3[style.css]

    C --> C1[app.py]

    D --> D1[data]
    D1 --> D1a[nlu.yml]
    D1 --> D1b[stories.yml]
    D --> D2[actions]
    D --> D3[config.yml]
    D --> D4[domain.yml]
    D --> D5[endpoints.yml]

    E --> E1[.gitignore]
    E --> E2[.env.example]
    E --> E3[README.md]

## How to Run the Project Locally
### 1.Clone the repository
git clone https://github.com/Daphne-GBN/Nemo_AI_Learning_Assistant_for_Dyslexic_Students.git
cd Nemo_AI_Learning_Assistant_for_Dyslexic_Students

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

->Multilingual support

## Contributors

Lead Developer: Daphne Grace Backiam Nathaniel 2023BCSE07066
Team Members: Arunima Banerjee 2023BCSE07039, Angiras Venugopal 2023BCSE07021 , Taksir Alam 2023BCSE0781

Project Type: Academic / Accessibility-focused AI system

## License
This project is developed for educational and research purposes.
