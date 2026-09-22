from pathlib import Path
from ollama import chat
import json



question = """
I changed my university password this morning.
Now my Windows laptop won't connect to campus Wi-Fi,
but my phone still works.
"""

## WRITE ##
state_file = Path("state.json")
if state_file.exists():
    with open(state_file, "r") as file:
        state = json.load(file)
else:
 state = {
    "problem": question,
    "wi_fi_status": "unknown",
    "service_status_checked": False
}

with open("state.json", "w") as file:
    json.dump(
        state,
        file,
        indent=2
    )

with open("state.json", "r") as file:
    state = json.load(file)

print("Initial state:", state)


## SELECT CONTEXT FILES BASED ON QUESTION
## Create the function that takes the student's question, takes some keywords and chooses the relevant files from the knowledge base. Return a list of the selected files.
## For example, if the question has the kyeword "print" or "printer", then the function should return the file "knowledge/printer_setup.txt" in a list.
def select_context(question):
    question_lower = question.lower()
    selected = []
    if "wi-fi" in question_lower or "wifi" in question_lower:
        selected.append("knowledge/wifi_setup.txt")
    if "password" in question_lower:
        selected.append("knowledge/password_changes.txt")
    selected.append("knowledge/service_status.txt")
    return selected



selected_files = select_context(question)

## READ SELECTED FILES and add their contents to the context variable.
context = ""
for filename in selected_files:
    file_path = Path(filename)
    if file_path.exists():
        context += file_path.read_text()
        context += "\n\n"

print("Selected files:", selected_files)
print("Context length before compression:", len(context))


## 
## COMPRESS CONTEXT
## Add logic to compress the context from above by calling Qwen with "context" and the "question" as the parameter
## The response from Qwen should be the compressed context. Store it in a variable called "compressed_context" 

def compress_context(context, question):
     system_prompt = "You are an expert at summarizing technical support information. Extract only the most relevant details from the context to answer the question. Keep it concise."
     user_prompt = "Question:\n" + question + "\n\nContext:\n" + context + "\n\nProvide a short summary of the relevant information only."
    
     response = chat(
        model="qwen3:8b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
     return response.message.content


compressed_context = compress_context(context, question)



## Print the length of the compressed context
print("Compressed context length:", len(compressed_context))

## Now, call Qwen again with the compressed context and the student's question. Store the response in a variable called "response" and print the response from Qwen.
## Ensure the model produces a structured output 
system_prompt = """You are a university IT support assistant. Based on the compressed context, provide a diagnosis and solution for the student. 
Output must be a valid JSON object with the following structure:
{
    "diagnosis": "string",
    "solution": ["step1", "step2", ...],
    "wifi_service_status": "operational" or "unknown"
}
Only output JSON, no other text.
"""
user_prompt = "Student question:\n" + question + "\n\nCompressed context:\n" + compressed_context

response = chat(
    model="qwen3:8b",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
)

print("Final response:")
print(response.message.content)

## WRITE the above output in an artifact called "state"
try:
    result_json = json.loads(response.message.content)
    state["diagnosis"] = result_json.get("diagnosis", "")
    state["solution"] = result_json.get("solution", [])
    state["wifi_service_status"] = result_json.get("wifi_service_status", "unknown")
    state["service_status_checked"] = True
    with open("state.json", "w") as file:
        json.dump(state, file, indent=2)
    print("State updated and saved to state.json")
except json.JSONDecodeError:
    print("Could not parse JSON from response, saving raw text.")
    state["raw_response"] = response.message.content
    with open("state.json", "w") as file:
        json.dump(state, file, indent=2)
## Update the rest of the code so that it uses the "state" artifact as part of the context. 
## It is important to ensure that the model uses only the relevant parts from the "state" artifact and not the entire artifact.
## For this, you may have to think of a good structure for the "state" artifact and how to use it in the context.
diagnostic_state = {
    "problem": question,
    "device": "Windows laptop",
    "wifi_status": state.get("wifi_service_status", "unknown"),
    "diagnosis": state.get("diagnosis", ""),
    "solution": state.get("solution", [])
}

report_state = {
    "total_wifi_cases": 37,
    "resolved_cases": 29,
    "unresolved_cases": 8
}

with open("diagnostic_state.json", "w") as file:
    json.dump(diagnostic_state, file, indent=2)

with open("report_state.json", "w") as file:
    json.dump(report_state, file, indent=2)

print("Isolated states saved: diagnostic_state.json and report_state.json")

