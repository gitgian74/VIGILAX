# 📋 Guida Setup SG Security AI

## 🚀 Setup Rapido

### 1. Prerequisiti
- Node.js 18+
- Account Appwrite Cloud (https://cloud.appwrite.io)
- Account Viam Robotics (opzionale, per le telecamere)

### 2. Configurazione Appwrite

#### 2.1 Crea un nuovo progetto
1. Vai su https://cloud.appwrite.io/console
2. Crea un nuovo progetto
3. Copia il **Project ID** (es: `6883392f00125f63c596`)

#### 2.2 Crea il database
1. Nel progetto, vai su **Databases**
2. Clicca **Create database**
3. Nome: `sg-security-db`
4. Copia il **Database ID**

#### 2.3 Crea le collections

Devi creare queste collections con gli attributi specificati:

##### Collection: `users`
```
- email (email, required)
- name (string, required, size: 255)
- role (string, required, size: 50, default: "user")
- avatar (url, optional, size: 2000)
- phone (string, optional, size: 20)
- notificationPreferences (string, required, size: 5000, default: "{}")
```

##### Collection: `security_events`
```
- type (string, required, size: 50)
- timestamp (datetime, required)
- cameraName (string, required, size: 100)
- cameraDisplayName (string, required, size: 100)
- zone (string, optional, size: 100)
- confidence (double, required, min: 0, max: 1)
- severity (string, required, size: 20)
- details (string, required, size: 5000)
- videoBufferId (string, optional, size: 255)
- snapshotId (string, optional, size: 255)
- processed (boolean, required, default: false)
- notificationsSent (boolean, required, default: false)
- acknowledgedBy (string, optional, size: 255)
- acknowledgedAt (datetime, optional)
```

##### Altre collections (vedi `scripts/setup-appwrite-db.js` per lo schema completo):
- `security_zones`
- `security_rules`
- `notifications`
- `recordings`
- `system_logs`

### 3. Configurazione Storage (Buckets)

Crea questi buckets:

1. **event-videos**
   - Max file size: 100MB
   - Allowed extensions: mp4, avi, mov, mkv

2. **event-snapshots**
   - Max file size: 10MB
   - Allowed extensions: jpg, jpeg, png, webp

### 4. Configurazione Teams (Ruoli)

Crea questi teams:
- `super-admins` - Super amministratori
- `admins` - Amministratori
- `users` - Utenti standard

### 5. Configurazione Frontend

#### 5.1 Crea il file `.env.local` nella cartella frontend:
```bash
cd frontend
cp .env.example .env.local
```

#### 5.2 Modifica `.env.local`:
```env
# Appwrite Config
VITE_APPWRITE_ENDPOINT=https://fra.cloud.appwrite.io/v1
VITE_APPWRITE_PROJECT_ID=il-tuo-project-id
VITE_APPWRITE_DATABASE_ID=il-tuo-database-id

# Viam Config (opzionale)
VITE_VIAM_API_KEY=la-tua-api-key
VITE_VIAM_API_KEY_ID=il-tuo-api-key-id
```

### 6. Installazione e Avvio

```bash
# Installa dipendenze
npm install

# Avvia in development
npm run dev
```

### 7. Test Registrazione Utente

1. Apri http://localhost:3000
2. Il form di login dovrebbe apparire
3. Per testare la registrazione, puoi modificare temporaneamente la pagina Login per aggiungere un link di registrazione

### 8. Primo Utente Admin

Per creare il primo super admin:
1. Registra un utente normale tramite l'app
2. Vai su Appwrite Console > Authentication > Users
3. Trova l'utente creato
4. Vai su Teams > super-admins
5. Aggiungi l'utente al team

## 🔧 Troubleshooting

### Errore "missing scope (account)"
- Assicurati che le permissions delle collections permettano la lettura/scrittura agli utenti autenticati

### Errore "Database not found"
- Verifica che il Database ID in `.env.local` sia corretto
- Controlla che tutte le collections siano state create

### Errore di connessione
- Verifica l'endpoint (usa `fra.cloud.appwrite.io` per Frankfurt)
- Controlla che il Project ID sia corretto

## 📝 Note

- Il sistema è progettato per gestire telecamere Viam Robotics
- Le notifiche richiedono la configurazione di Twilio (opzionale)
- Il sistema di AI per il rilevamento eventi richiede un modello ML configurato