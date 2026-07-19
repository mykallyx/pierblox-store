import json
import requests
import uuid

# Configurações do Mercado Pago
ACCESS_TOKEN = "APP_USR-1598174317006783-071901-9a069520bee2070399bb41e01d5d0c6c-2373373406"

def handler(request):
    # Log de depuração básico (visível no painel da Vercel)
    print(f"Request Method: {request.method}")

    # Headers CORS base
    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, X-Idempotency-Key',
        'Content-Type': 'application/json'
    }

    # Resposta para Preflight (OPTIONS)
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': ''
        }

    # Apenas POST é permitido para gerar ou consultar
    if request.method != 'POST':
        return {
            'statusCode': 405,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Method not allowed. Use POST.'})
        }
    
    try:
        # Tenta ler o corpo da requisição
        raw_body = request.body.decode('utf-8') if hasattr(request.body, 'decode') else request.body
        print(f"Raw body: {raw_body}")
        
        body = json.loads(raw_body)
        amount = body.get('amount')
        description = body.get('description', 'Pedido PierBlox')
        payment_id = body.get('payment_id')
        
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        # --- CASO 1: Verificar Status do Pagamento ---
        if payment_id:
            print(f"Checking status for payment: {payment_id}")
            r = requests.get(f"https://api.mercadopago.com/v1/payments/{payment_id}", headers=headers)
            return {
                'statusCode': r.status_code,
                'headers': cors_headers,
                'body': json.dumps(r.json())
            }
        
        # --- CASO 2: Criar Novo Pagamento Pix ---
        if not amount:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Amount is required'})
            }

        payload = {
            "transaction_amount": float(amount),
            "description": description,
            "payment_method_id": "pix",
            "payer": {
                "email": "cliente@pierblox.com",
                "first_name": "Cliente",
                "last_name": "PierBlox"
            }
        }
        
        # Idempotency Key é obrigatória para evitar cobranças duplicadas
        headers["X-Idempotency-Key"] = str(uuid.uuid4())
        
        print(f"Creating payment for amount: {amount}")
        r = requests.post("https://api.mercadopago.com/v1/payments", json=payload, headers=headers)
        
        return {
            'statusCode': r.status_code,
            'headers': cors_headers,
            'body': json.dumps(r.json())
        }

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Internal Server Error', 'details': str(e)})
        }
