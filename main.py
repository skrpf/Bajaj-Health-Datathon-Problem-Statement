import os
import io
import json
import base64
import requests
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pdf2image import convert_from_bytes
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# --- 2. Define The Exact JSON Schema Required ---
class BillItem(BaseModel):
    item_name: str
    item_amount: float
    item_rate: float
    item_quantity: float

class PageData(BaseModel):
    page_no: str
    page_type: str 
    bill_items: List[BillItem]

class ExtractionData(BaseModel):
    pagewise_line_items: List[PageData]
    total_item_count: int

class TokenUsage(BaseModel):
    total_tokens: int
    input_tokens: int
    output_tokens: int

class APIResponse(BaseModel):
    is_success: bool
    token_usage: TokenUsage
    data: ExtractionData

class APIRequest(BaseModel):
    document: str

# --- 3. Helper Functions ---

def download_file(url: str) -> bytes:
    """Downloads the file from the provided URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.content
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to download document: {str(e)}")

def encode_image(image: Image.Image) -> str:
    """Converts a PIL Image to a base64 string."""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# --- 4. The Brain: LLM Extraction Logic ---

SYSTEM_PROMPT = """
You are an expert Invoice Data Extraction AI. 
Tasks:
1. Extract line items from the bill image provided.
2. Output JSON with keys: "item_name", "item_amount" (net total for that line), "item_rate", "item_quantity".
3. Identify page type: "Bill Detail", "Final Bill", or "Pharmacy".

CRITICAL RULES TO AVOID DOUBLE COUNTING:
- ONLY extract physical goods or services provided.
- DO NOT extract rows labeled: "Subtotal", "Total", "GST", "VAT", "Tax", "Discount", "Balance Due", "Grand Total", or "Round Off".
- If a row is a summary of previous items, IGNORE IT.
- If quantity is missing, infer it as 1.0. 
- Return strict JSON format.
"""

def process_page_with_llm(base64_img: str, page_num: int):
    """Sends image to OpenAI and parses response."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o", # Best for vision/OCR
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": [
                    {"type": "text", "text": f"Extract line items for Page {page_num}."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                ]}
            ],
            response_format={"type": "json_object"},
            temperature=0.0 # Strict extraction, no creativity
        )
        
        content = json.loads(response.choices[0].message.content)
        return content, response.usage
    except Exception as e:
        print(f"Error processing page {page_num}: {e}")
        # Return empty structure on failure to keep process alive
        return {"items": [], "page_type": "Unknown"}, None

# --- 5. The API Endpoint ---

@app.post("/extract-bill-data", response_model=APIResponse)
async def extract_bill_data(request: APIRequest):
    
    # A. Download
    file_bytes = download_file(request.document)
    
    # B. Convert PDF/Image to PIL Images
    images = []
    if request.document.lower().endswith(".pdf"):
        images = convert_from_bytes(file_bytes)
    else:
        images = [Image.open(io.BytesIO(file_bytes))]

    pagewise_data = []
    total_tokens = 0
    in_tokens = 0
    out_tokens = 0
    total_items = 0

    # C. Loop through pages
    for i, img in enumerate(images):
        page_num = i + 1
        base64_img = encode_image(img)
        
        # Call AI
        llm_data, usage = process_page_with_llm(base64_img, page_num)
        
        # Track Tokens
        if usage:
            total_tokens += usage.total_tokens
            in_tokens += usage.prompt_tokens
            out_tokens += usage.completion_tokens

        # D. Parse and Clean Data
        raw_items = llm_data.get("items", []) # Expecting LLM to return key "items"
        page_type = llm_data.get("page_type", "Bill Detail")
        
        clean_items = []
        for item in raw_items:
            # Double check filter for "Total" keywords just in case AI missed it
            name = str(item.get("item_name", "")).lower()
            if any(x in name for x in ["total", "subtotal", "amount due"]):
                continue

            clean_items.append(BillItem(
                item_name=item.get("item_name", "Unknown"),
                item_amount=float(item.get("item_amount", 0.0)),
                item_rate=float(item.get("item_rate", 0.0)),
                item_quantity=float(item.get("item_quantity", 1.0))
            ))
        
        pagewise_data.append(PageData(
            page_no=str(page_num),
            page_type=page_type,
            bill_items=clean_items
        ))
        total_items += len(clean_items)

    # E. Final Response
    return APIResponse(
        is_success=True,
        token_usage=TokenUsage(
            total_tokens=total_tokens,
            input_tokens=in_tokens,
            output_tokens=out_tokens
        ),
        data=ExtractionData(
            pagewise_line_items=pagewise_data,
            total_item_count=total_items
        )
    )