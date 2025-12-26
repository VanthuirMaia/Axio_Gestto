"""
Validadores para CPF e CNPJ
"""

def validar_cpf(cpf):
    """
    Valida formato e dígitos verificadores de CPF

    Args:
        cpf: string com CPF (apenas números)

    Returns:
        bool: True se válido, False se inválido
    """
    # Remove caracteres não numéricos
    cpf = ''.join(filter(str.isdigit, cpf))

    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False

    # Verifica se todos os dígitos são iguais (ex: 111.111.111-11)
    if cpf == cpf[0] * 11:
        return False

    # Calcula primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto

    if int(cpf[9]) != digito1:
        return False

    # Calcula segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto

    if int(cpf[10]) != digito2:
        return False

    return True


def validar_cnpj(cnpj):
    """
    Valida formato e dígitos verificadores de CNPJ

    Args:
        cnpj: string com CNPJ (apenas números)

    Returns:
        bool: True se válido, False se inválido
    """
    # Remove caracteres não numéricos
    cnpj = ''.join(filter(str.isdigit, cnpj))

    # Verifica se tem 14 dígitos
    if len(cnpj) != 14:
        return False

    # Verifica se todos os dígitos são iguais
    if cnpj == cnpj[0] * 14:
        return False

    # Calcula primeiro dígito verificador
    multiplicadores1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * multiplicadores1[i] for i in range(12))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto

    if int(cnpj[12]) != digito1:
        return False

    # Calcula segundo dígito verificador
    multiplicadores2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * multiplicadores2[i] for i in range(13))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto

    if int(cnpj[13]) != digito2:
        return False

    return True


def validar_cpf_cnpj(documento):
    """
    Valida CPF ou CNPJ automaticamente

    Args:
        documento: string com CPF ou CNPJ (com ou sem máscara)

    Returns:
        tuple: (bool valido, str tipo, str documento_limpo, str mensagem_erro)
    """
    # Remove caracteres não numéricos
    doc_limpo = ''.join(filter(str.isdigit, documento))

    # Verifica tamanho
    if len(doc_limpo) == 11:
        # É CPF
        if validar_cpf(doc_limpo):
            return (True, 'cpf', doc_limpo, '')
        else:
            return (False, 'cpf', doc_limpo, 'CPF inválido. Verifique os números digitados.')

    elif len(doc_limpo) == 14:
        # É CNPJ
        if validar_cnpj(doc_limpo):
            return (True, 'cnpj', doc_limpo, '')
        else:
            return (False, 'cnpj', doc_limpo, 'CNPJ inválido. Verifique os números digitados.')

    else:
        return (False, 'desconhecido', doc_limpo, 'CPF deve ter 11 dígitos e CNPJ deve ter 14 dígitos.')


# TODO: Em produção, adicionar validações extras:
# - Consultar CPF/CNPJ na Receita Federal (API)
# - Verificar se está ativo
# - Validar nome do titular
# - Anti-fraude (verificar se não é CPF de teste conhecido)
