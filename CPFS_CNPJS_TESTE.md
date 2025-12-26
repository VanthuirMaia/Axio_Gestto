# 📋 CPFs e CNPJs para Teste

Use estes documentos VÁLIDOS para testar o sistema:

## ✅ CPFs Válidos (para teste)

```
111.444.777-35
123.456.789-09
987.654.321-00
000.000.001-91
```

**Formato sem máscara:**
```
11144477735
12345678909
98765432100
00000000191
```

---

## ✅ CNPJs Válidos (para teste)

```
11.222.333/0001-81
12.345.678/0001-95
00.000.000/0001-91
```

**Formato sem máscara:**
```
11222333000181
12345678000195
00000000000191
```

---

## ⚠️ IMPORTANTE

**Estes são CPFs/CNPJs de TESTE:**
- Passam na validação de dígitos verificadores
- NÃO são documentos reais
- Use APENAS em ambiente de desenvolvimento
- Em produção, integre com API da Receita Federal

---

## 🔒 Validação Implementada

### Atualmente (Desenvolvimento):
- ✅ Validação de formato (11 ou 14 dígitos)
- ✅ Validação de dígitos verificadores (algoritmo oficial)
- ✅ Verificação de sequências repetidas (111.111.111-11)
- ✅ Verificação de duplicidade no banco

### TODO para Produção:
- [ ] Integrar com API da Receita Federal
- [ ] Validar situação cadastral (ativo/inativo)
- [ ] Validar nome do titular
- [ ] Sistema anti-fraude
- [ ] Rate limiting em consultas

---

## 🧪 Como Testar

### Teste 1 - CPF Válido
```
Nome: João Silva
Email: joao@teste.com
Telefone: 11988887777
CPF: 111.444.777-35
```

### Teste 2 - CNPJ Válido
```
Nome: Barbearia Top Ltda
Email: contato@barbeariatop.com
Telefone: 11999998888
CNPJ: 11.222.333/0001-81
```

### Teste 3 - CPF Inválido (deve dar erro)
```
CPF: 111.111.111-11  ← Sequência repetida
```

### Teste 4 - CNPJ Inválido (deve dar erro)
```
CNPJ: 12.345.678/0001-00  ← Dígitos verificadores errados
```

---

## 📝 Geradores Online (caso precise mais)

**ATENÇÃO:** Use apenas para teste!

- **CPF:** https://www.4devs.com.br/gerador_de_cpf
- **CNPJ:** https://www.4devs.com.br/gerador_de_cnpj

Marque a opção "Somente válidos" para gerar documentos que passam na validação.
