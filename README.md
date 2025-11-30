# Document Intelligence helper

This folder contains a small Python utility that calls Azure Document Intelligence
to extract structured JSON from unstructured PDFs and images and then send to Azure OpenAI to get required JSON structured data based on semantic matching.

Files
- `parse_documents_ai.py` — script to analyze a file or directory. Supports recursion and writing JSON next to inputs.
- `requirements.txt` — Python dependencies for this script.

python -m venv .venv;
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

# Set env vars (examples)
DOCUMENT_INTELLIGENCE_ENDPOINT = https://<your-resource>.cognitiveservices.azure.com/
DOCUMENT_INTELLIGENCE_KEY = <your-key>
AZURE_OPENAI_ENDPOINT=https://<your-resource>.cognitiveservices.azure.com/
AZURE_OPENAI_KEY=<your-openAI-key>
AZURE_OPENAI_DEPLOYMENT=gpt-4o or your model name


# Recursively analyze a directory and write JSON next to each file
python .\parse_documents_ai.py

Notes
- The default model used is `prebuilt-document`. Provide `--model-id` to use a custom model.
- If you omit the key env var and have Azure AD auth configured locally, the script will attempt `DefaultAzureCredential`.
