# 🚀 SG Security AI - Setup Completo

Guida completa per configurare SG Security AI senza Vercel, utilizzando solo GitHub e servizi cloud.

## 📋 Prerequisiti

- **Node.js 18+** installato
- **Git** installato
- **Account GitHub** attivo
- **Account Appwrite** (https://cloud.appwrite.io)
- **Account Viam** (https://app.viam.com)

## 🔧 Setup Step-by-Step

### 1. **Clona il Repository**

```bash
git clone https://github.com/gitgian74/VIGILAX.git
cd sg-security-ai
```

### 2. **Installa Dipendenze Frontend**

```bash
cd frontend
npm install
```

### 3. **Configura Variabili d'Ambiente**

```bash
# Copia il file di esempio
cp env.example .env.local

# Modifica .env.local con le tue credenziali
nano .env.local  # o usa il tuo editor preferito
```

### 4. **Configura Appwrite**

#### 4.1 Crea Progetto Appwrite
1. Vai su https://cloud.appwrite.io
2. Crea un nuovo progetto
3. Copia il **Project ID**

#### 4.2 Crea Database
1. Nel dashboard Appwrite, vai su **Databases**
2. Crea un nuovo database chiamato `sg-security-db`
3. Copia il **Database ID**

#### 4.3 Configura .env.local
```bash
VITE_APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1
VITE_APPWRITE_PROJECT_ID=your_project_id_here
VITE_APPWRITE_DATABASE_ID=your_database_id_here
```

### 5. **Configura Viam Robot**

#### 5.1 Crea Robot su Viam
1. Vai su https://app.viam.com
2. Crea un nuovo robot
3. Configura le camere
4. Copia l'**indirizzo del robot**

#### 5.2 Crea API Key
1. Nel dashboard Viam, vai su **API Keys**
2. Crea una nuova API Key
3. Copia **API Key** e **API Key ID**

#### 5.3 Configura .env.local
```bash
VITE_VIAM_ROBOT_ADDRESS=your_robot_address_here
VITE_VIAM_API_KEY=your_api_key_here
VITE_VIAM_API_KEY_ID=your_api_key_id_here
```

### 6. **Verifica Configurazione**

```bash
# Dalla cartella frontend
npm run check-config
```

Questo script verificherà:
- ✅ Presenza file .env.local
- ✅ Configurazione Appwrite
- ✅ Configurazione Viam
- ✅ Dipendenze installate
- ✅ Struttura progetto

### 7. **Avvia Development Server**

```bash
npm run dev
```

L'app sarà disponibile su: http://localhost:3000

## 🚀 Deployment

### Opzione 1: GitHub Pages (Consigliato)

1. **Push su GitHub**
   ```bash
   git add .
   git commit -m "Initial setup"
   git push origin main
   ```

2. **Configura GitHub Pages**
   - Vai nelle impostazioni del repository
   - Sezione **Pages**
   - Source: **GitHub Actions**

3. **Configura GitHub Secrets**
   - Vai in **Settings > Secrets and variables > Actions**
   - Aggiungi tutte le variabili da `.env.local`

### Opzione 2: Netlify

1. **Crea account Netlify** (https://netlify.com)
2. **Connetti repository GitHub**
3. **Configura build settings**:
   - Build command: `cd frontend && npm install && npm run build`
   - Publish directory: `frontend/dist`
4. **Configura variabili d'ambiente** nel dashboard

### Opzione 3: Vercel (se necessario)

1. **Crea account Vercel** (https://vercel.com)
2. **Importa repository**
3. **Configura variabili d'ambiente**
4. **Deploy automatico**

## 🔐 Sicurezza

### Variabili d'Ambiente

**NON COMMITTARE MAI** il file `.env.local`:

```bash
# .gitignore (già configurato)
.env
.env.local
.env.production
```

### Verifica Configurazione

Esegui sempre la verifica prima del deploy:

```bash
npm run check-config
```

## 📁 Struttura Progetto

```
sg-security-ai/
├── frontend/                 # React App
│   ├── src/
│   │   ├── components/      # Componenti UI
│   │   ├── pages/          # Pagine app
│   │   ├── hooks/          # Custom hooks
│   │   ├── services/       # Servizi API
│   │   ├── config/         # Configurazioni
│   │   └── types/          # TypeScript types
│   ├── public/             # File statici
│   ├── env.example         # Template variabili
│   └── package.json
├── api/                    # API Python
├── scripts/               # Script di setup
│   ├── check-config.js    # Verifica configurazione
│   └── setup-appwrite.js  # Setup Appwrite
└── docs/                  # Documentazione
```

## 🛠️ Troubleshooting

### Problemi Comuni

#### 1. **"File .env.local non trovato"**
```bash
cp env.example .env.local
```

#### 2. **"Variabili Appwrite non configurate"**
- Verifica Project ID e Database ID
- Controlla che l'endpoint sia corretto

#### 3. **"Variabili Viam non configurate"**
- Verifica indirizzo robot
- Controlla API Key e API Key ID

#### 4. **"Dipendenze mancanti"**
```bash
npm install
```

### Log di Debug

```bash
# Verifica configurazione completa
npm run check-config

# Log dettagliati
DEBUG=* npm run dev
```

## 📞 Supporto

Se hai problemi:

1. **Esegui la verifica**: `npm run check-config`
2. **Controlla i log**: Console browser e terminal
3. **Verifica credenziali**: Appwrite e Viam dashboard
4. **Controlla documentazione**: README.md e docs/

## ✅ Checklist Finale

- [ ] Repository clonato
- [ ] Dipendenze installate
- [ ] .env.local configurato
- [ ] Appwrite configurato
- [ ] Viam configurato
- [ ] Verifica configurazione passata
- [ ] App funzionante in locale
- [ ] Deploy configurato
- [ ] Variabili d'ambiente sicure

---

**🎉 Setup completato!** Il tuo sistema SG Security AI è pronto per l'uso. 