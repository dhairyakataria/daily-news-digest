from langchain_nvidia_ai_endpoints import ChatNVIDIA
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatNVIDIA(
    model="meta/llama-3.3-70b-instruct",
    api_key=os.getenv("NVIDIA_API_KEY") or os.getenv("NVIVIA_API_KEY"),
    temperature=0.2,
    top_p=0.7,
    max_tokens=1024,
)
