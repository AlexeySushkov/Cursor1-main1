# Ask AI Anything - Web Chat Application

A ChatGPT-like web application that provides AI-powered answers using FastAPI and OpenAI GPT-4o-mini.

## Features

- 🤖 AI-powered chat interface
- 💬 Conversation context preservation
- 📱 Responsive, minimalistic UI
- ⚡ Fast API backend with FastAPI

## Prerequisites: Install Python, pip, and Uvicorn

1. **Install Python (Recommended: 3.10 or 3.11):**
   - Download from the official site: https://www.python.org/downloads/
   - During installation, check the box "Add Python to PATH".
   - Verify installation:
     ```bash
     python --version
     ```

2. **Install pip (if not included):**
   - Most Python installers include pip by default.
   - To check:
     ```bash
     python -m pip --version
     ```
   - If pip is missing, install it:
     ```bash
     python -m ensurepip --upgrade
     ```

3. **Install Uvicorn (ASGI server):**
   - After installing Python and pip, run:
     ```bash
     pip install uvicorn
     ```

4. **Install python-multipart (for form data support in FastAPI):**
   - Required for handling file uploads and form data in FastAPI.
     ```bash
     pip install python-multipart
     ```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.env` file in the root directory with your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

**Get API Key:**
- **OpenAI API**: Get your key at [platform.openai.com](https://platform.openai.com)

### 3. Run the Application

```bash
uvicorn main:app --reload
```

Open your browser and go to: http://localhost:8000

## Project Structure

```
├── main.py              # FastAPI application entry point
├── services.py          # OpenAI service class
├── requirements.txt     # Python dependencies
├── .env                 # API key (create this file)
├── .gitignore          # Git ignore rules
├── templates/
│   └── index.html      # Main chat interface
└── static/
    ├── style.css       # Minimalistic styling
    └── chat.js         # Frontend JavaScript
```

## How It Works

1. **User Input**: User sends a question through the chat interface
2. **Context Processing**: Previous conversation context is maintained
3. **AI Response**: OpenAI GPT-4o-mini generates an answer based on conversation history
4. **Display**: Response is shown in the chat interface

## Technologies Used

- **Backend**: FastAPI (Python 3.11)
- **Frontend**: HTML, CSS, JavaScript
- **AI**: OpenAI GPT-4o-mini
- **Styling**: Custom CSS with minimalistic design

## Security Notes

- Never commit your `.env` file to version control
- Keep your API key secure and private
- The `.gitignore` file is configured to exclude sensitive files 

Update 15.07.2025