import requests

def generar_envio_chilexpress(pedido):
    api_key = "2e0c68cccb5843c98dbe82043be00b59"  # API key sandbox o producción
    url = "https://sandbox-api.chilexpress.cl/v1/transport-orders"  # asegúrate de usar /v1/

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "client_tcc": "111111111",  # asegúrate de que este sea un TCC de prueba válido
        "reference": str(pedido.order_id),
        "origin_commune_code": "13101",
        "destination_commune_code": pedido.codigo_comuna_chilexpress,
        "package": {
            "weight": float(pedido.peso_total),
            "length": pedido.largo,
            "width": pedido.ancho,
            "height": pedido.alto
        },
        "content_description": "Pedido Bastian Autoparts"
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"Error al generar envío: {response.status_code} - {response.text}")