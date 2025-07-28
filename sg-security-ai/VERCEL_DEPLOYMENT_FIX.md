# 🔧 Risoluzione Problemi Deployment Vercel - SG Security AI

## 📋 Problemi Identificati

### 1. **Configurazione Vercel Incompleta**
Il file `vercel.json` era configurato solo per le API Python e non gestiva il frontend React.

### 2. **Mancanza Build Command**
Non era specificato come buildare il frontend durante il deployment.

### 3. **File Ignorati**
Il `.vercelignore` escludeva troppi file necessari per il build del frontend.

### 4. **Routing SPA Non Configurato**
Mancavano le rewrites per gestire il routing di React Router.

## ✅ Soluzioni Applicate

### 1. **Aggiornato vercel.json**
```json
{
  "buildCommand": "cd frontend && npm install && npm run build && cp -r dist/* ../",
  "outputDirectory": ".",
  "framework": null,
  "functions": {
    "api/index.py": {
      "runtime": "@vercel/python@3.0.0"
    },
    "api/mcp.py": {
      "runtime": "@vercel/python@3.0.0"
    }
  },
  "rewrites": [
    {
      "source": "/api/mcp",
      "destination": "/api/mcp.py"
    },
    {
      "source": "/api/(.*)",
      "destination": "/api/index.py"
    },
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### 2. **Aggiornato .vercelignore**
- Mantenuto `frontend/` per permettere il build
- Inclusi i file di configurazione necessari
- Esclusi solo i file non necessari per il deployment

## 🚀 Prossimi Passi per il Deploy

### 1. **Configura le Variabili d'Ambiente su Vercel**
Nel dashboard di Vercel, aggiungi:
```
VITE_APPWRITE_ENDPOINT=https://fra.cloud.appwrite.io/v1
VITE_APPWRITE_PROJECT_ID=6883392f00125f63c596
VITE_APPWRITE_DATABASE_ID=sg-security-db
```

### 2. **Deploy**
```bash
# Commit le modifiche
git add vercel.json .vercelignore
git commit -m "Fix: Configurazione Vercel per frontend e API"
git push

# O fai un redeploy manuale dal dashboard Vercel
```

### 3. **Verifica il Deployment**
Dopo il deploy, controlla:
- ✅ L'app si carica correttamente su `https://[tuo-progetto].vercel.app`
- ✅ Le API rispondono su `/api/*`
- ✅ Il routing SPA funziona (prova a navigare direttamente a `/login`)
- ✅ Le variabili d'ambiente sono caricate (controlla la console del browser)

## 🔍 Troubleshooting

### Se il build fallisce:
1. Verifica i log di build su Vercel
2. Controlla che `cd frontend && npm install && npm run build` funzioni localmente
3. Assicurati che tutte le dipendenze siano nel `package.json`

### Se l'app non si carica:
1. Controlla che l'output directory contenga `index.html` e `assets/`
2. Verifica le rewrites nel `vercel.json`
3. Controlla i log delle funzioni su Vercel

### Se le API non funzionano:
1. Verifica che le funzioni Python siano configurate correttamente
2. Controlla che `requirements.txt` sia presente (se necessario)
3. Verifica i log delle funzioni nel dashboard Vercel

## 📝 Note Importanti

- Il build avviene nella cartella `frontend/` e poi i file vengono copiati nella root
- Le API Python in `/api/` continuano a funzionare come serverless functions
- Il routing SPA è gestito redirigendo tutte le richieste non-API a `index.html`
- Assicurati di configurare le variabili d'ambiente prima del deploy 