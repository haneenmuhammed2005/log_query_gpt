from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

print(" Testing LangChain with Ollama...")

llm = ChatOllama(
    model="llama3.1:8b",
    base_url="http://localhost:11434"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("user", "Explain what a log file is in one sentence.")
])

chain = prompt | llm | StrOutputParser()

try:
    response = chain.invoke({})
    print(f" Response: {response}")
except Exception as e:
    print(f" Error: {e}")
