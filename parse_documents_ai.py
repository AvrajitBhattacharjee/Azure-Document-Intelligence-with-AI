import os
import json
from dotenv import load_dotenv
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI

# Load environment variables
load_dotenv()

# Initialize clients
di_endpoint = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT")
di_key = os.getenv("DOCUMENT_INTELLIGENCE_KEY")
di_client = DocumentIntelligenceClient(endpoint=di_endpoint, credential=AzureKeyCredential(di_key))

openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
openai_key = os.getenv("AZURE_OPENAI_KEY")
openai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
openai_client = AzureOpenAI(
    azure_endpoint=openai_endpoint,
    api_key=openai_key,
    api_version="2025-01-01-preview"  # Use latest for structured outputs
)

# Your list of keys for extraction
KEYS = ["invoice_number", "MAWB", "HAWB", "Name"]  # Customize this

# System prompt for OpenAI (enforces JSON schema)
SYSTEM_PROMPT = """
You are an expert at extracting data from unstructured documents. Given the Markdown content from a PDF, extract values for the following keys only: {keys}.
- Match keys semantically (e.g., 'Invoice No' matches 'invoice_number').
- If a value is not found, use null.
- Output ONLY valid JSON in this exact schema like keys are sent.
- Values should be strings; parse numbers/dates as strings.
- Do not add extra fields or explanations.
""".format(keys=", ".join(KEYS))

def extract_from_pdf(pdf_path):
    """Extract Markdown from PDF using Document Intelligence."""
    with open(pdf_path, "rb") as f:
         poller = di_client.begin_analyze_document(
            "prebuilt-layout", 
            f,
            output_content_format="markdown"
        )
    result: AnalyzeResult = poller.result()
    
    # Get Markdown content (handles text, tables, structure)
    markdown_content = ""
    if result.content:
        markdown_content = result.content
    
    return markdown_content

def get_structured_json(markdown_content, filename):
    """Use OpenAI to extract JSON for keys."""
    user_prompt = f"Extract data from this document Markdown:\n\n{markdown_content}\n\nFilename: {filename}"
    
    response = openai_client.chat.completions.create(
        model=openai_deployment,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}  # Enforces JSON output (GPT-4o+)
    )
    
    # Parse JSON from response
    try:
        extracted_json = json.loads(response.choices[0].message.content)
        extracted_json["filename"] = filename  # Add metadata
        return extracted_json
    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON", "filename": filename}

# Main processing loop
pdf_folder = "C:/Python+node+react workspace/Azure AI document Intelligence/Input Samples/Scanned/"  # Update path
results = []

for filename in os.listdir(pdf_folder):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(pdf_folder, filename)
        print(f"Processing {filename}...")
        
        markdown = extract_from_pdf(pdf_path)
        print(f"OpenAI call started for {filename}...")
        json_data = get_structured_json(markdown, filename)
        results.append(json_data)

# Save batch results as JSON array
with open("output.json", "w") as f:
    json.dump(results, f, indent=4)

print("Extraction complete. Check output.json")