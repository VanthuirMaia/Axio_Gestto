# Como Testar o PWA - Gestto

## ✅ Correções Aplicadas

1. **Manifest servido com view dedicada** → Content-Type correto: `application/manifest+json`
2. **URL corrigida** → `/manifest.json` (via Django view)
3. **Ícones dos shortcuts corrigidos** → Apontam para ícones existentes
4. **URLs dos shortcuts corrigidos** → `/app/agendamentos/...`

---

## 🧪 Passo a Passo para Testar

### 1. **Reiniciar o Servidor**

No terminal PowerShell:
```powershell
# Se estiver rodando, pare (Ctrl+C)
python manage.py runserver
```

### 2. **Abrir o Navegador**

Acesse: **http://localhost:8000**

### 3. **Abrir DevTools (F12)**

#### **Aba Application > Manifest**

Deve mostrar:
```
Name: Gestto - Gestão de Agendamentos
Short name: Gestto
Start URL: /
Theme color: #667eea
Background color: #ffffff
Display: standalone
Orientation: portrait-primary
```

✅ **8 ícones** devem aparecer (48x48 até 512x512)

✅ **2 shortcuts**:
- Novo Agendamento
- Calendário

#### **Aba Application > Service Workers**

Deve mostrar:
```
Status: activated and running
Source: /service-worker.js
```

#### **Aba Console**

Procure por:
```
✅ Service Worker registrado com sucesso: /
💡 PWA pode ser instalado
```

---

## 🔍 Verificar Manifest Manualmente

Acesse diretamente: **http://localhost:8000/manifest.json**

Deve mostrar o JSON completo com todos os ícones.

---

## 📱 Instalar o PWA

### **No Desktop (Chrome/Edge)**

1. Procure o ícone **➕** ou **⬇️** na barra de endereço (lado direito)
2. Clique em **"Instalar Gestto"**
3. O app abre em janela separada (sem barra de endereço)

**OU**

1. Menu do navegador (⋮)
2. **"Instalar Gestto..."**

### **No Android (Chrome)**

1. Menu ⋮ > **"Instalar app"** ou **"Adicionar à tela inicial"**
2. Confirme
3. Ícone aparece na tela do celular com a logo Gestto

### **No iPhone (Safari)**

1. Compartilhar > **"Adicionar à Tela de Início"**
2. Edite o nome se quiser
3. Toque em "Adicionar"

---

## 🐛 Troubleshooting

### Problema: "Manifest no detected"

**Solução 1 - Force Refresh:**
```
Ctrl + Shift + R
```

**Solução 2 - Limpar Cache:**
1. F12 > Application
2. Clear storage > Clear site data
3. Recarregue a página

**Solução 3 - Verificar Console:**
1. F12 > Console
2. Procure por erros relacionados a manifest
3. Se houver erro 404, confira se o servidor está rodando

### Problema: Service Worker não registra

1. F12 > Application > Service Workers
2. Marque **"Update on reload"**
3. Clique em **"Unregister"** se houver worker antigo
4. Recarregue (Ctrl+R)

### Problema: Botão de instalação não aparece

**Requisitos para instalar:**
- ✅ Manifest válido
- ✅ Service worker registrado
- ✅ HTTPS OU localhost
- ✅ Ícones 192x192 e 512x512 presentes
- ✅ Start URL válida

**Verifique no DevTools:**
1. F12 > Console
2. Procure por erros ou avisos
3. Certifique-se de que não há mensagens vermelhas

---

## ✨ Funcionalidades do PWA

### **Instalado**
- Ícone na tela inicial (desktop/mobile)
- Abre em janela standalone (sem navegador)
- Aparece na lista de apps do sistema

### **Offline**
- Páginas visitadas funcionam sem internet
- Service worker faz cache automático
- Mostra página customizada quando offline

### **Atalhos (Android)**
- Pressione e segure o ícone
- Aparecem:
  - ⚡ Novo Agendamento
  - 📅 Calendário

### **Atualizações Automáticas**
- Nova versão detectada automaticamente
- Prompt para atualizar
- Sem necessidade de App Store

---

## 📊 Verificar Instalação

### **DevTools > Application > Storage**

Cache Storage deve mostrar:
```
gestto-v1
  ├─ /
  ├─ /static/css/custom.css
  ├─ /static/js/sidebar.js
  └─ ... (arquivos cacheados)
```

### **Network Tab**

1. Navegue por algumas páginas
2. Marque **"Offline"**
3. Recarregue
4. Deve funcionar (busca do cache)

---

## 🎯 Checklist Final

- [ ] Manifest detectado (F12 > Application > Manifest)
- [ ] Service Worker rodando (F12 > Application > Service Workers)
- [ ] Console mostra "✅ Service Worker registrado"
- [ ] Botão de instalação aparece na barra de endereço
- [ ] PWA instala corretamente
- [ ] App abre em janela standalone
- [ ] Ícone correto (logo Gestto) aparece
- [ ] Funcionalidade offline funciona
- [ ] Atalhos aparecem (Android)

---

**Se todos os itens estiverem ✅, o PWA está funcionando perfeitamente!** 🎉
