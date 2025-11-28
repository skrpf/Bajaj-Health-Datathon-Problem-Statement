# **🧾 AI-Powered Bill Extraction API**

### **🏆 HackRx Datathon Submission**

This repository contains a high-precision document extraction API designed to process multi-page medical and pharmacy bills. It utilizes **Multimodal Large Language Models (GPT-4o)** to visually analyze invoices, extract line-item details, and structure the data into a standardized JSON format while strictly avoiding double-counting of totals.

## **🚀 Key Features**

* **Multimodal Analysis:** Uses Vision AI to understand document layout, handling complex tables, blurred text, and non-standard fonts better than traditional OCR (Tesseract).  
* **Smart Parsing:** Automatically classifies pages into "Bill Detail", "Final Bill", or "Pharmacy".  
* **Double-Counting Prevention:** Implements a two-layer filter (System Prompt \+ Python Logic) to exclude "Subtotal", "Tax", "GST", and "Grand Total" rows, ensuring the AI-calculated total matches the actual bill total.  
* **PDF & Image Support:** Seamlessly handles direct image URLs and multi-page PDF documents.  
* **Strict Schema:** Powered by Pydantic to ensure the API response always matches the required Datathon JSON schema.

## **🛠️ Tech Stack**

* **Language:** Python 3.10  
* **Web Framework:** FastAPI  
* **AI Model:** OpenAI GPT-4o (Vision)  
* **Image Processing:** pdf2image, Pillow (PIL)  
* **Containerization:** Docker

## **🧠 Methodology & Logic**

### **1\. Visual Ingestion**

Instead of parsing text blindly, we convert PDF pages into high-resolution images. We feed these images to **GPT-4o**, allowing the model to "see" grid lines, column headers, and indented summaries just like a human auditor.

### **2\. Accuracy & Double-Counting Logic**

To satisfy the evaluation criteria (Total AI Extracted Amount ≈ Actual Bill Total), we use a strict extraction protocol:

1. **Prompt Engineering:** The LLM is explicitly instructed to **ignore** summary rows (Subtotal, Tax, Balance Due) and only extract physical line items.  
2. **Post-Processing Filter:** A Python-side filter scans extracted item names for keywords like "Total", "GST", "Amount Due" and removes them if the AI accidentally includes them.  
3. **Data Sanitization:** Cleans currency symbols ($, ₹) and standardizes numeric values.

## **⚙️ Local Setup & Installation**

### **Prerequisites**

* Python 3.10+  
* **Poppler** (Required for PDF processing):  
  * *Mac:* brew install poppler  
  * *Windows:* [Download Binary](https://www.google.com/search?q=http://blog.alivate.com.au/poppler-windows/) and add to PATH.  
  * *Linux:* sudo apt-get install poppler-utils

### **Step-by-Step Guide**

1. **Clone the Repository**
```
   git clone \[https://github.com/your-username/your-repo-name.git\](https://github.com/your-username/your-repo-name.git)  
   cd bill-extractor
```
2. **Create Virtual Environment**
``` 
   python \-m venv venv  
   \# Windows  
   venv\\Scripts\\activate  
   \# Mac/Linux  
   source venv/bin/activate
```
3. **Install Dependencies**
```
   pip install \-r requirements.txt
```
4. Configure API Key
```
   Create a .env file in the root directory:  
   OPENAI\_API\_KEY=sk-proj-your-key-here
```
5. **Run the Server**
```
   uvicorn main:app \--reload

   The API will be accessible at http://127.0.0.1:8000.
```
## **🐳 Docker Deployment (Recommended)**

Docker handles the system-level Poppler dependency automatically, making deployment to cloud platforms (Render, Railway, AWS) seamless.

1. **Build the Image**  
```
   docker build \-t bill-extractor .
```
2. **Run the Container**  
```
   docker run \-p 8000:8000 \--env-file .env bill-extractor
```
## **📡 API Usage**

### **Endpoint**
```
POST /extract-bill-data
```
### **Sample Request (cURL)**
```
curl \-X POST "\[http://127.0.0.1:8000/extract-bill-data\](http://127.0.0.1:8000/extract-bill-data)" \\  
     \-H "Content-Type: application/json" \\  
     \-d '{  
           "document": "\[https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample\_2.png\](https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample\_2.png)"  
         }'
```
### **Sample Response**
```
{  
    "is\_success": true,  
    "token\_usage": {  
        "total\_tokens": 1250,  
        "input\_tokens": 1000,  
        "output\_tokens": 250  
    },  
    "data": {  
        "pagewise\_line\_items": \[  
            {  
                "page\_no": "1",  
                "page\_type": "Bill Detail",  
                "bill\_items": \[  
                    {  
                        "item\_name": "Consultation Fee",  
                        "item\_amount": 500.0,  
                        "item\_rate": 500.0,  
                        "item\_quantity": 1.0  
                    }  
                \]  
            }  
        \],  
        "total\_item\_count": 1  
    }  
}
```
## **📂 Project Structure**
```
├── main.py              \# Application entry point & logic  
├── requirements.txt     \# Python dependencies  
├── Dockerfile           \# Deployment configuration  
├── .env                 \# API Keys (GitIgnored)  
└── README.md            \# Documentation  
```
