#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste de cadastro via API
"""

import requests
import json

# Dados de teste
dados = {
    'nome_empresa': 'Barbearia do Pedro',
    'email_admin': 'pedro@teste.com',
    'telefone': '11977776666',
    'cnpj': '111.444.777-35',
    'plano': 'essencial',
    'gateway': 'stripe'
}

print("Enviando dados para API:")
print(json.dumps(dados, indent=2, ensure_ascii=False))
print("\n" + "="*60 + "\n")

# Fazer requisição
try:
    response = requests.post(
        'http://localhost:8000/api/create-tenant/',
        json=dados,
        timeout=10
    )

    print(f"Status Code: {response.status_code}")
    print(f"\nResposta:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

except Exception as e:
    print(f"Erro: {e}")
