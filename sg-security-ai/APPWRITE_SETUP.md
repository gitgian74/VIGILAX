# 🚀 Setup Appwrite per SG Security AI

## Passaggi Manuali Richiesti

Poiché l'SDK client di Appwrite non permette di creare database e collezioni, dovrai configurare tutto manualmente dalla console.

### 1. Accedi ad Appwrite Console

1. Vai su: <https://cloud.appwrite.io/console>
2. Accedi al progetto `6883392f00125f63c596`

### 2. Crea il Database

1. Clicca su **Databases** nel menu laterale
2. Clicca **Create database**
3. **Nome**: `SG Security Database`
4. **ID** (opzionale): lascia vuoto per generarlo automaticamente
5. Clicca **Create**
6. **IMPORTANTE**: Copia il Database ID generato

### 3. Crea le Collections

Per ogni collection, segui questi passaggi:

1. Nel database appena creato, clicca **Create collection**
2. Inserisci l'ID e il nome della collection
3. Clicca **Create**
4. Poi aggiungi gli attributi uno per uno

#### Collection 1: users

- **ID**: `users`
- **Nome**: `Users`

**Attributi da aggiungere:**

1. **email**
   - Type: Email
   - Required: ✓

2. **name**
   - Type: String
   - Size: 255
   - Required: ✓

3. **role**
   - Type: String
   - Size: 50
   - Required: ✓
   - Default value: `user`

4. **avatar**
   - Type: URL
   - Required: ✗

5. **phone**
   - Type: String
   - Size: 20
   - Required: ✗

6. **notificationPreferences**
   - Type: String
   - Size: 5000
   - Required: ✓
   - Default value: `{}`

#### Collection 2: security_events

- **ID**: `security_events`
- **Nome**: `Security Events`

**Attributi da aggiungere:**

1. **type** (String, 50, required)
2. **timestamp** (DateTime, required)
3. **cameraName** (String, 100, required)
4. **cameraDisplayName** (String, 100, required)
5. **zone** (String, 100, optional)
6. **confidence** (Float, min: 0, max: 1, required)
7. **severity** (String, 20, required)
8. **details** (String, 5000, required)
9. **videoBufferId** (String, 255, optional)
10. **snapshotId** (String, 255, optional)
11. **processed** (Boolean, required, default: false)
12. **notificationsSent** (Boolean, required, default: false)
13. **acknowledgedBy** (String, 255, optional)
14. **acknowledgedAt** (DateTime, optional)

### 4. Configura i Permessi

Per la collection `users`:

1. Vai su **Settings** della collection
2. In **Permissions**, aggiungi:
   - **Read**: Any
   - **Create**: Users
   - **Update**: Users (document level)
   - **Delete**: Users (document level)

### 5. Crea i Buckets per lo Storage

1. Vai su **Storage** nel menu laterale
2. Crea bucket **event-videos**:
   - Max file size: 100 MB
   - Allowed extensions: `mp4`, `avi`, `mov`, `mkv`
3. Crea bucket **event-snapshots**:
   - Max file size: 10 MB
   - Allowed extensions: `jpg`, `jpeg`, `png`, `webp`

### 6. Configura il file .env.local

Crea il file `frontend/.env.local`:

```env
VITE_APPWRITE_ENDPOINT=https://fra.cloud.appwrite.io/v1
VITE_APPWRITE_PROJECT_ID=6883392f00125f63c596
VITE_APPWRITE_DATABASE_ID=IL_TUO_DATABASE_ID_QUI
```

### 7. Testa la Connessione

```bash
cd frontend
npm install
npm run dev
```

## Verifica Setup

Una volta completato il setup, l'applicazione dovrebbe:

1. ✅ Mostrare la pagina di login
2. ✅ Permettere la registrazione di nuovi utenti
3. ✅ Salvare i profili utente nel database
4. ✅ Gestire l'autenticazione correttamente

## Troubleshooting

### Errore "Database not found"
- Verifica che il Database ID in `.env.local` sia corretto

### Errore "Collection not found"
- Assicurati che tutte le collections siano state create con gli ID esatti

### Errore "Missing required attribute"
- Controlla che tutti gli attributi required siano stati aggiunti alle collections

## Note

- I database e le collections possono essere creati solo dalla Console o con Server SDK + API Key
- Il Client SDK è limitato per motivi di sicurezza
- Una volta configurato, il sistema gestirà automaticamente utenti e dati