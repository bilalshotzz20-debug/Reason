# 🧠 Reason: Advanced Medical Diagnostics & Reasoning Engine

An end-to-end Generative AI web application designed to assist in early disease detection, rare condition diagnosis, and critical emergency triage. Built to act as a reliable "second opinion" tool for patients and healthcare professionals globally.

🔗 **Live Demo:** [Add your Streamlit Link Here]

## 🌍 The Global Problem
Worldwide, millions of people suffer from rare diseases and complex medical conditions that are frequently misdiagnosed. Furthermore, in emergency situations, patients often panic and delay seeking immediate medical help while researching their symptoms online. Access to specialized, safe, and immediate medical reasoning is highly unequal globally.

## 💡 The Solution
**Reason** bridges this gap. It uses advanced Large Language Models (LLMs) to analyze reported symptoms and cross-reference them with vast medical knowledge in real-time. 

More importantly, it features a **Python-level Emergency Fail-Safe system**. If life-threatening symptoms are detected, the system immediately overrides the AI to prioritize emergency action before suggesting any medical tests.

## 🚀 Key Features
*   🚨 **Emergency Fail-Safe (Red Flag Override):** A custom Python-level keyword detector that identifies life-threatening symptoms (e.g., chest pain, stroke signs) and instantly triggers a pulsing, high-visibility emergency banner urging the user to call 911/1122.
*   **Intelligent Symptom Analysis:** Converts unstructured text (symptoms) into structured medical hypotheses using Llama 3.
*   **Actionable Insights:** Provides the top 3 possible conditions, urgency levels, and specific tests to request from a doctor.
*   **Ultra-Fast Inference:** Powered by Groq's LPU inference engine, generating complex medical reasoning reports in under 2 seconds.
*   **Clean Clinical UI:** A sleek, responsive dashboard (with Light/Dark modes) built for both laptops and mobile devices.
*   **Secure Architecture:** Uses Streamlit Secrets for secure API key management, ensuring zero backend costs and user privacy.

## 🛠️ Tech Stack
*   **Frontend:** Streamlit (Custom CSS for Clinical UI)
*   **AI Engine:** Groq API (Running `openai/gpt-oss-120b` / Llama 3 models)
*   **Language:** Python
*   **Safety Protocol:** Custom Python Keyword Matching & Regex (for Emergency Override)

## 💻 How to Run This Project Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/bilalshotzz20-debug/Reason.git
