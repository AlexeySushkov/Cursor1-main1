import os
import openai
from dotenv import load_dotenv

load_dotenv()
print("OPENAI_API_KEY :",os.getenv("OPENAI_API_KEY"))
openai.api_key = os.getenv("OPENAI_API_KEY")

try:    
    models = openai.models.list()
    print("Ключ работает. Доступные модели:")
    for model in models.data:
        print(model.id)
except Exception as e:
    print("Ошибка:", e)
