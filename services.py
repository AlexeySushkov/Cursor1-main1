import os
import httpx
from typing import List, Dict, AsyncGenerator
from dotenv import load_dotenv
import json
import markdown2

# Load environment variables from .env file
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print("OPENAI_API_KEY :",OPENAI_API_KEY)
if not OPENAI_API_KEY:
    print("⚠️  WARNING: OPENAI_API_KEY not found in .env file")
    print("   Please create .env file with: OPENAI_API_KEY=your_key_here")
    print("   The application will start but chat won't work without the key")
    OPENAI_API_KEY = "dummy_key"  # Allow app to start

class LLMService:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def format_response(self, text: str) -> str:
        """Convert markdown text to HTML"""
        try:
            print(f"Raw response from OpenAI: {text[:200]}...")
            
            # Check if response already contains markdown
            has_markdown = any(marker in text for marker in ['**', '*', '`', '#', '- ', '>', '|'])
            
            if not has_markdown:
                print("No markdown detected, adding basic formatting...")
                # Add basic formatting to plain text
                lines = text.split('\n')
                formatted_lines = []
                for line in lines:
                    line = line.strip()
                    if line:
                        # Make first line a header if it's short
                        if len(formatted_lines) == 0 and len(line) < 100:
                            formatted_lines.append(f"### {line}")
                        else:
                            formatted_lines.append(line)
                text = '\n\n'.join(formatted_lines)
            
            formatted = markdown2.markdown(text, extras=['fenced-code-blocks', 'tables', 'code-friendly'])
            print(f"Formatted HTML: {formatted[:500]}...")
            print(f"HTML length: {len(formatted)}")
            print(f"Contains h3 tag: {'<h3>' in formatted}")
            print(f"Contains strong tag: {'<strong>' in formatted}")
            return formatted
        except Exception as e:
            print(f"Formatting error: {e}")
            return text

    async def chat(self, messages: List[Dict], user_question: str) -> str:
        if self.api_key == "dummy_key":
            return "❌ Error: OpenAI API key not configured. Please add OPENAI_API_KEY to your .env file"
        
        try:
            # Simple chat without internet search
            system_prompt = (
                "You are a helpful AI assistant. "
                "Always use only Markdown for formatting. "
                "Never use HTML tags or inline styles. "
                "Do NOT use <span>, <font>, <div>, or style attributes. "
                "Use only Markdown syntax for headings, lists, code, etc. "
                "Examples: \n"
                "- # Заголовок 1\n"
                "- ## Заголовок 2\n"
                "- **жирный** и *курсив* текст\n"
                "- `код` и ```блок кода```\n"
                "- - списки\n"
                "- > цитаты\n"
                "- [ссылки](https://example.com)\n"
                "Не используй HTML и не добавляй цвет или фон через style!"
            )
            full_messages = [
                {"role": "system", "content": system_prompt},
                *messages,
                {"role": "user", "content": user_question}
            ]
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": full_messages,
                "max_tokens": 512,
                "temperature": 0.7
            }
            
            print(f"Regular chat request - model: {self.model}, messages count: {len(full_messages)}")
            
            async with httpx.AsyncClient() as client:
                resp = await client.post(self.base_url, headers=headers, json=payload, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                raw_response = data["choices"][0]["message"]["content"].strip()
                return self.format_response(raw_response)
                
        except Exception as e:
            print(f"Regular chat error: {e}")
            return f"❌ Error in regular chat: {str(e)}"

    async def chat_stream(self, messages: List[Dict], user_question: str) -> AsyncGenerator[str, None]:
        if self.api_key == "dummy_key":
            yield "❌ Error: OpenAI API key not configured. Please add OPENAI_API_KEY to your .env file"
            return
        
        try:
            system_prompt = (
                "You are a helpful AI assistant. Answer questions based on your knowledge. "
                "Be informative, accurate, and helpful. IMPORTANT: Always use markdown formatting for better readability. "
                "Examples of how to format your responses:\n"
                "- Use **bold text** for emphasis and important points\n"
                "- Use *italic text* for terms and definitions\n"
                "- Use `inline code` for code snippets and technical terms\n"
                "- Use ```\ncode blocks\n``` for longer code examples\n"
                "- Use bullet points (- item) for lists\n"
                "- Use ### Headers for organizing content\n"
                "- Use > for quotes or important notes\n"
                "Always format your responses with appropriate markdown syntax."
            )
            full_messages = [
                {"role": "system", "content": system_prompt},
                *messages,
                {"role": "user", "content": user_question}
            ]
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": full_messages,
                "max_tokens": 512,
                "temperature": 0.7,
                "stream": True
            }
            
            async with httpx.AsyncClient() as client:
                async with client.stream("POST", self.base_url, headers=headers, json=payload, timeout=30) as resp:
                    resp.raise_for_status()
                    async for line in resp.aiter_lines():
                        line = line.strip()
                        if not line:
                            continue
                        if line.startswith("data: "):
                            data = line[6:]  # Remove "data: " prefix
                            if data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                if "choices" in chunk and chunk["choices"]:
                                    delta = chunk["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        yield delta["content"]
                            except json.JSONDecodeError as e:
                                print(f"JSON decode error: {e}, data: {data}")
                                continue
                        else:
                            print(f"Unexpected line format: {line}")
                            
        except Exception as e:
            print(f"Streaming error: {e}")
            yield f"❌ Error during streaming: {str(e)}"

llm_service = LLMService(OPENAI_API_KEY)
