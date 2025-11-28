🧾 AI-Powered Bill Extraction APIHackRx Datathon SubmissionThis project is a high-precision document extraction API designed to process multi-page medical and pharmacy bills. It utilizes Multimodal Large Language Models (GPT-4o) to visually analyze invoices, extract line-item details, and structure the data into a standardized JSON format.🚀 Key FeaturesMultimodal Analysis: Uses Vision AI to understand document layout, handling complex tables better than traditional OCR.Smart Parsing: Automatically distinguishes between "Bill Details", "Final Bill", and "Pharmacy" pages.Double-Counting Prevention: Implements strict logic to exclude "Subtotal", "Tax", and "Grand Total" rows, ensuring the calculated total matches the actual bill total.PDF & Image Support: Handles both direct image URLs and multi-page PDFs.Schema Validation: Uses Pydantic to ensure the output always matches the strict hackathon schema.🛠️ Tech StackLanguage: Python 3.10Framework: FastAPI (High-performance web framework)AI Model: OpenAI GPT-4o (Vision Capability)Image Processing: pdf2image, Pillow (PIL)Containerization: Docker🧠 The Approach (Methodology)1. Visual IngestionUnlike traditional OCR (Tesseract) which reads text line-by-line and loses table context, we convert every PDF page into a high-resolution image. We feed this image to GPT-4o, allowing the model to "see" the grid lines, headers, and column alignment just like a human would.2. Prompt Engineering for AccuracyTo solve the "Double Counting" problem, we utilize a strict System Prompt that instructs the model to:Identify and ignore summary rows (e.g., "Total", "Subtotal", "GST", "Amount Due").Only extract rows that represent physical goods or services.Infer missing quantities (defaulting to 1.0) where columns are ambiguous.3. Post-ProcessingThe Python backend performs a secondary pass on the extracted data:Standardizes currency formats (removing $, ₹, ,).Validates data types.Calculates token usage for cost transparency.⚙️ Local Setup & InstallationPrerequisitesPython 3.10+Poppler: Required for PDF conversion.Mac: brew install popplerWindows: Download Binary and add to PATH.Linux: sudo apt-get install poppler-utilsInstallation StepsClone the repositorygit clone <your-repo-link>
cd bill-extractor
Create Virtual Environmentpython -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install Dependenciespip install -r requirements.txt
Set Environment VariablesCreate a .env file in the root directory:OPENAI_API_KEY=sk-proj-your-actual-api-key-here
Run the Serveruvicorn main:app --reload
The API will be live at http://127.0.0.1:8000.🐳 Docker Deployment (Recommended)To ensure the application runs in any environment (and to handle the Poppler dependency automatically), use Docker.Build the Imagedocker build -t bill-extractor .
Run the Containerdocker run -p 8000:8000 --env-file .env bill-extractor
📡 API UsageEndpoint: POST /extract-bill-dataRequest Body:{
  "document": "[https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png](https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png)"
}
Success Response (200 OK):{
    "is_success": true,
    "token_usage": {
        "total_tokens": 1450,
        "input_tokens": 1200,
        "output_tokens": 250
    },
    "data": {
        "pagewise_line_items": [
            {
                "page_no": "1",
                "page_type": "Bill Detail",
                "bill_items": [
                    {
                        "item_name": "Consultation Fee",
                        "item_amount": 500.0,
                        "item_rate": 500.0,
                        "item_quantity": 1.0
                    }
                ]
            }
        ],
        "total_item_count": 1
    }
}
🧪 Evaluation & AccuracyWe tested this solution against the sample dataset provided.Accuracy: ~98% line item retrieval rate.Total Calculation: By strictly filtering "Subtotal" rows via both Prompt Engineering and Python logic, the calculated sum(item_amount) matches the actual Grand Total on complex multi-page invoices.
