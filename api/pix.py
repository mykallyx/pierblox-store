import json
import requests
import uuid

def handler(request):
    # CORS handling for preflight
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        }

    if request.method != 'POST':
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        body = json.loads(request.body)
        amount = body.get('amount')
        description = body.get('description', 'Pedido PierBlox')
        payment_id = body.get('payment_id') # If checking status
        
        # Token do Mercado Pago
        access_token = "APP_USR-1598174317006783-071901-9a069520bee2070399bb41e01d5d0c6c-2373373406"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # Status Check Mode
        if payment_id:
            r = requests.get(f"https://api.mercadopago.com/v1/payments/{payment_id}", headers=headers)
            return {
                'statusCode': r.status_code,
                'headers': {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'},
                'body': json.dumps(r.json())
            }
        
        # Create Payment Mode
        payload = {
            "transaction_amount": float(amount),
            "description": description,
            "payment_method_id": "pix",
            "payer": {"email": "cliente@pierblox.com"}
        }
        headers["X-Idempotency-Key"] = str(uuid.uuid4())
        
        r = requests.post("https://api.mercadopago.com/v1/payments", json=payload, headers=headers)
        
        return {
            'statusCode': r.status_code,
            'headers': {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'},
            'body': json.dumps(r.json())
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
