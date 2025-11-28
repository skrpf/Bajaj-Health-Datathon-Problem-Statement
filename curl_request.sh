curl -X POST "http://127.0.0.1:8000/extract-bill-data" \
     -H "Content-Type: application/json" \
     -d '{"document": "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png?sv=2025-07-05"}'