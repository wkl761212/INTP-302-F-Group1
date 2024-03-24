import requests

API_URL = "https://api-inference.huggingface.co/models/selvakumarcts/sk_invoice_receipts"
headers = {"Authorization": f"Bearer {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}"}

def query(filename):
    with open(filename, "rb") as f:
        data = f.read()
    response = requests.post(API_URL, headers=headers, data=data)
    return response.json()

output = query("cats.jpg")