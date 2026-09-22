from pathlib import Path
from ollama import chat


question = """
I changed my university password this morning.
Now my Windows laptop won't connect to campus Wi-Fi,
but my phone still works.
"""

selected_files = [
    ##Use only the files that are relevant to the question.
    "knowledge/wifi_setup.txt",
    "knowledge/password_changes.txt",
    "knowledge/service_status.txt"
]


context = ""

## Write a for loop to go through all the files in selected_files and read their contents into the context variable.
for filename in selected_files:
    file_path = Path(filename)
    if file_path.exists():
        context += file_path.read_text()
        context += "\n\n"

## Call Qwen with the student's question and the context you created above.
system_prompt = "You are a university IT support assistant. Use the provided context to help the student."
user_prompt = f"Student question:\n{question}\n\nContext:\n{context}"

response = chat(
    model="qwen3:8b",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
)


print(
    "Context characters:",
    len(context)
)
print(response.message.content)