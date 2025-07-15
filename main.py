import os
from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from services import llm_service
import json

# Load environment variables
load_dotenv()

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(
    request: Request,
    message: str = Form(...),
    context: str = Form(""),
    streaming: str = Form("false")
):
    try:
        is_streaming = streaming.lower() == "true"
        print(f"Chat request - streaming: {is_streaming}, message: {message[:50]}...")
        messages = json.loads(context) if context else []
        
        if is_streaming:
            print("Using streaming response")
            # Return streaming response
            return StreamingResponse(
                llm_service.chat_stream(messages, message),
                media_type="text/plain"
            )
        else:
            print("Using regular response")
            # Return regular response
            answer = await llm_service.chat(messages, message)
            return JSONResponse({"answer": answer})
            
    except Exception as e:
        print(f"Chat error: {e}")
        return JSONResponse({"answer": f"Error: {str(e)}"}, status_code=500) 