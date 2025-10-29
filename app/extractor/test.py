import google.generativeai as genai
genai.configure(api_key="AIzaSyDU72NOX7mDBqXFUXv-X8oncNXZF0RCzGs")
for m in genai.list_models():
    print(m.name)
