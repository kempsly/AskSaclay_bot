### 📌 **README.md**

```md
# 🤖 AskSaclayAI: Your AI Assistant for University Paris-Saclay

![AskSaclayAI](assets/asksaclayai_banner.png)  

🚀 Welcome to **AskSaclayAI**, an AI-powered chatbot designed to assist students, researchers, and staff at **University Paris-Saclay**. Whether you need academic information, campus details, or research assistance, AskSaclayAI is here to help!

---

## 🌟 Features

✅ **User Authentication** – Secure login and sign-up using Firebase  
✅ **AI Chatbot** – Get instant responses using **LangChain & OpenAI**  
✅ **Document Search** – Retrieve information from PDFs, Google, Websites, Wikipedia, ArXiv, and more  
✅ **Video Transcription** – Extract text from YouTube videos  
✅ **Multi-Source Search** – Integrated with **Google Search, DuckDuckGo, Wikipedia**  
✅ **Database Support** – Supports **ChromaDB, FAISS, FIREBASE, MySQL, SQLite**  
✅ **Beautiful UI** – Built with **Streamlit** for an intuitive experience  

---

## 🛠️ Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/kempsly/AskSaclay_bot.git
cd AskSaclay_bot
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Set Up Environment Variables  
Create a `.env` file in the project root and add your Firebase & OpenAI credentials:

```env
FIREBASE_API_KEY="your_api_key"
FIREBASE_AUTH_DOMAIN="your_project.firebaseapp.com"
FIREBASE_PROJECT_ID="your_project_id"
FIREBASE_STORAGE_BUCKET="your_bucket"
FIREBASE_MESSAGING_SENDER_ID="your_sender_id"
FIREBASE_APP_ID="your_app_id"
OPENAI_API_KEY="your_openai_api_key"
```

### 4️⃣ Run the App
```bash
streamlit run app_bot.py
```

---

## 📂 **Project Structure**

```
📂 AskSaclayAI
│── 📜 app_bot.py          # Main Streamlit application
│── 📜 auth.py             # Authentication logic (Firebase)
│── 📜 firebase_config.py  # Firebase setup
│── 📜 bot.py              # AI chatbot logic
│── 📜 requirements.txt     # Project dependencies
│── 📜 README.md           # Project documentation
|── 📜 .gitignore
│── 📂 assets              # Images & logos
└── 📂 pdf_data                # PDF/Document storage
```

---

## 🖥️ **Screenshots**

🔹 **Login Screen**  
![Login](assets/login_screen.png)  

🔹 **Chat Interface**  
![Chat](assets/asksaclayai_banner.png)  

---

## 🤝 Contributing

We welcome contributions! Feel free to fork the repo, submit pull requests, or suggest features.  

---

## 📜 License

This project is licensed under the MIT License.

---

💡 **Made with ❤️ for Université Paris-Saclay!**  
🚀 **Have a question? Reach out!** 
```

--- 
