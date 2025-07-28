# SG Security AI 🛡️

Sistema di videosorveglianza intelligente con AI per rilevamento eventi di sicurezza in tempo reale.

## 🚀 Features

### Frontend React + TypeScript
- **Streaming Video Real-time**: Connessione diretta con robot Viam per streaming multi-camera
- **AI Detection**: Rilevamento automatico di eventi di sicurezza (intrusioni, loitering, etc.)
- **Zone di Sicurezza**: Configurazione zone con regole personalizzate
- **Sistema Notifiche**: Email e SMS per alert immediati
- **Gestione Registrazioni**: Accesso a registrazioni locali e cloud
- **Analytics Avanzate**: Dashboard con statistiche e heatmap
- **Multi-ruolo**: Gestione utenti con permessi granulari

### Backend Python Flask
- **Streaming Video Live**: Visualizzazione in tempo reale delle camere VIAM
- **Registrazione Locale**: Sistema di registrazione video con gestione automatica dello storage
- **Analisi AI**: Integrazione con servizi VIAM per rilevamento oggetti e analisi ML
- **Gestione Utenti Multi-livello**: Super Admin, Admin e User con permessi differenziati
- **API RESTful**: Endpoints completi per tutte le funzionalità
- **Sicurezza Avanzata**: Autenticazione JWT e controllo accessi granulare

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 18 + TypeScript + Vite
- **UI**: Tailwind CSS + Radix UI + Framer Motion
- **Backend**: Appwrite Cloud
- **Robot/IoT**: Viam Platform
- **Deployment**: GitHub Pages / Netlify / Vercel

### Backend
- **Framework**: Flask con SQLAlchemy ORM
- **Database**: SQLite per sviluppo (facilmente migrabile a PostgreSQL/MySQL)
- **Autenticazione**: JWT con refresh token
- **API**: RESTful endpoints con documentazione integrata
- **Integrazione VIAM**: VIAM Python SDK per controllo camere

## 📋 Prerequisiti

### Frontend
- Node.js 18+
- Account Viam (https://app.viam.com)
- Account Appwrite (https://cloud.appwrite.io)

### Backend
- Python 3.11+
- VIAM Robot configurato
- Credenziali API VIAM
- Git

## 🔧 Installazione

<<<<<<< HEAD
1. **Clona il repository**
   ```bash
   git clone https://github.com/yourusername/sg-security-ai.git
   cd sg-security-ai
   ```

2. **Installa le dipendenze**
   ```bash
   cd frontend
   npm install
   ```

3. **Configura le variabili d'ambiente**
   ```bash
   cp .env.example .env.local
   # Modifica .env.local con le tue credenziali
   ```

4. **Setup Appwrite**
   ```bash
   npm run setup:appwrite
   ```

5. **Avvia il development server**
   ```bash
   npm run dev
   ```

## 🏗️ Struttura Progetto

```
sg-security-ai/
├── frontend/               # React App
│   ├── src/
│   │   ├── components/    # Componenti UI riutilizzabili
│   │   ├── pages/        # Pagine dell'applicazione
│   │   ├── hooks/        # Custom React hooks
│   │   ├── services/     # Servizi API
│   │   ├── utils/        # Utility functions
│   │   └── types/        # TypeScript types
│   └── public/
├── backend/               # Appwrite Functions
│   └── functions/        # Cloud functions
└── docs/                 # Documentazione
```

## 🔐 Configurazione Viam

1. Accedi a [app.viam.com](https://app.viam.com)
2. Crea un nuovo robot o usa uno esistente
3. Ottieni API Key e API Key ID
4. Configura le camere nel robot
5. Aggiorna `.env.local` con le credenziali

## ☁️ Configurazione Appwrite

1. Crea un progetto su [Appwrite Cloud](https://cloud.appwrite.io)
2. Crea un database
3. Esegui lo script di setup: `npm run setup:appwrite`
4. Configura i team per i ruoli utente
5. Deploy delle functions

## 🚀 Deployment

### GitHub Pages (Consigliato)

1. **Pusha il codice su GitHub**
2. **Configura GitHub Pages** nelle impostazioni del repository
3. **Configura le variabili d'ambiente** tramite GitHub Secrets
4. **Deploy automatico** ad ogni push su main

### Netlify (Alternativa)

1. **Crea un account su Netlify** (https://netlify.com)
2. **Connetti il repository GitHub**
3. **Configura le variabili d'ambiente** nel dashboard Netlify
4. **Deploy automatico** ad ogni push su main

### Docker

```bash
docker-compose up -d
```

## 📱 Utilizzo

1. **Login**: Accedi con le tue credenziali
2. **Dashboard**: Visualizza stream live e statistiche
3. **Zone**: Configura zone di sicurezza
4. **Alert**: Ricevi notifiche real-time
5. **Registrazioni**: Accedi allo storico video

## 🤝 Contribuire

1. Fork il progetto
2. Crea un feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit le modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push sul branch (`git push origin feature/AmazingFeature`)
=======
### 1. Clona il Repository
```bash
git clone https://github.com/gitgian74/SG-security-AI.git
cd SG-security-AI
```

### 2. Crea Ambiente Virtuale
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# oppure
venv\Scripts\activate  # Windows
```

### 3. Installa Dipendenze
```bash
pip install -r requirements.txt
```

### 4. Configurazione
Modifica le credenziali VIAM in `src/services/viam_service.py`:
```python
self.api_key = 'your-viam-api-key'
self.api_key_id = 'your-viam-api-key-id'
self.robot_address = 'your-robot-address.viam.cloud'
```

### 5. Avvia l'Applicazione
```bash
python src/main.py
```

L'applicazione sarà disponibile su: http://localhost:5000

## 👤 Credenziali di Default

- **Username**: admin
- **Password**: admin123
- **Ruolo**: Super Admin

⚠️ **Importante**: Cambia la password dopo il primo accesso!

## 📁 Struttura del Progetto

```
sg-security-ai/
├── src/
│   ├── models/           # Modelli database
│   │   ├── user.py      # Modelli utenti e sessioni
│   │   └── camera.py    # Modelli camere e configurazioni
│   ├── routes/          # Endpoints API
│   │   ├── auth.py      # Autenticazione
│   │   ├── user.py      # Gestione utenti
│   │   ├── camera.py    # Gestione camere
│   │   ├── viam_routes.py    # Integrazione VIAM
│   │   └── recording_routes.py # Registrazioni
│   ├── services/        # Servizi business logic
│   │   ├── viam_service.py    # Servizio VIAM
│   │   └── recording_service.py # Servizio registrazioni
│   ├── static/          # File statici frontend
│   │   ├── css/
│   │   ├── js/
│   │   └── index.html
│   ├── database/        # Database SQLite
│   └── main.py         # Applicazione principale
├── recordings/         # Directory registrazioni
│   ├── videos/
│   ├── snapshots/
│   ├── temp/
│   └── ai_events/
├── requirements.txt
├── README.md
└── .gitignore
```

## 🔐 Gestione Utenti

### Ruoli Disponibili

1. **Super Admin**
   - Accesso completo al sistema
   - Gestione utenti e configurazioni
   - Controllo di tutte le camere
   - Accesso alle statistiche di sistema

2. **Admin**
   - Gestione utenti (eccetto Super Admin)
   - Controllo di tutte le camere
   - Accesso alle registrazioni
   - Configurazioni limitate

3. **User**
   - Accesso solo alle camere assegnate
   - Visualizzazione streaming
   - Registrazioni delle proprie sessioni

## 📹 Gestione Camere

### Camere Supportate
- camera-1 (Camera Principale)
- camera-2 (Camera Secondaria)
- video-store-camera-1
- video-store-camera-2

### Funzionalità
- **Streaming Live**: MJPEG in tempo reale
- **Snapshot**: Cattura immagini istantanee
- **Registrazione**: Video locali con segmentazione automatica
- **Analisi AI**: Rilevamento oggetti e inferenza ML

## 🤖 Integrazione AI

### Servizi VIAM Supportati
- **Vision Service**: Rilevamento oggetti in tempo reale
- **ML Model Service**: Inferenza con modelli personalizzati
- **Camera Service**: Controllo avanzato delle camere

### API Endpoints AI
- `POST /api/viam/cameras/{id}/detect` - Rilevamento oggetti
- `POST /api/viam/cameras/{id}/inference` - Inferenza ML
- `GET /api/viam/cameras/{id}/image` - Cattura immagine

## 💾 Sistema di Registrazione

### Caratteristiche
- **Registrazione Continua**: Automatica per camere abilitate
- **Registrazione Manuale**: Su richiesta con durata personalizzabile
- **Segmentazione**: File divisi automaticamente ogni 30 minuti
- **Cleanup Automatico**: Rimozione file vecchi basata su retention policy
- **Gestione Storage**: Monitoraggio spazio disco e limiti configurabili

### Directory di Default
- **Base**: `/home/ubuntu/recordings/`
- **Video**: `recordings/videos/`
- **Snapshot**: `recordings/snapshots/`
- **Temporanei**: `recordings/temp/`
- **Eventi AI**: `recordings/ai_events/`

## 🔧 API Endpoints

### Autenticazione
- `POST /api/auth/login` - Login utente
- `POST /api/auth/logout` - Logout utente
- `GET /api/auth/profile` - Profilo utente
- `PUT /api/auth/profile` - Aggiorna profilo

### Gestione Utenti
- `GET /api/users` - Lista utenti (Admin+)
- `POST /api/users` - Crea utente (Admin+)
- `PUT /api/users/{id}` - Aggiorna utente (Admin+)
- `DELETE /api/users/{id}` - Elimina utente (Super Admin)

### Camere
- `GET /api/cameras` - Lista camere
- `GET /api/cameras/{id}` - Dettagli camera
- `POST /api/cameras/{id}/stream` - Avvia streaming
- `POST /api/cameras/{id}/snapshot` - Cattura snapshot

### VIAM Integration
- `GET /api/viam/status` - Status connessione VIAM
- `POST /api/viam/connect` - Connetti a VIAM
- `GET /api/viam/cameras/{id}/image` - Immagine da camera VIAM
- `GET /api/viam/cameras/{id}/stream` - Stream MJPEG

### Registrazioni
- `GET /api/recordings` - Lista registrazioni
- `POST /api/recordings/start` - Avvia registrazione
- `POST /api/recordings/stop` - Ferma registrazione
- `GET /api/recordings/{id}/download` - Download registrazione

## 🔍 Monitoraggio e Salute

### Health Checks
- `GET /api/health` - Salute generale sistema
- `GET /api/viam/health` - Salute servizio VIAM
- `GET /api/recordings/health` - Salute servizio registrazioni

### Metriche Disponibili
- Numero utenti attivi
- Camere online/offline
- Spazio disco utilizzato
- Sessioni streaming attive
- Registrazioni in corso

## 🚀 Deployment

### Sviluppo
```bash
python src/main.py
```

### Produzione
Si consiglia l'uso di un server WSGI come Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
```

### Docker (Opzionale)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "src/main.py"]
```

## 🔒 Sicurezza

### Misure Implementate
- Autenticazione JWT con scadenza
- Controllo accessi basato su ruoli (RBAC)
- Validazione input su tutti gli endpoints
- Sanitizzazione dati database
- CORS configurabile
- Rate limiting (raccomandato per produzione)

### Raccomandazioni Produzione
- Usa HTTPS sempre
- Configura reverse proxy (nginx)
- Implementa rate limiting
- Monitora logs di sicurezza
- Backup regolari database
- Aggiorna credenziali di default

## 🐛 Troubleshooting

### Problemi Comuni

1. **Errore connessione VIAM**
   - Verifica credenziali API
   - Controlla connessione internet
   - Verifica stato robot VIAM

2. **Streaming non funziona**
   - Controlla permessi camera
   - Verifica connessione VIAM
   - Controlla logs browser

3. **Registrazioni non salvate**
   - Verifica permessi directory
   - Controlla spazio disco
   - Verifica configurazione paths

### Logs
I logs sono disponibili nella console dell'applicazione. Per produzione, configurare logging su file:

```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

## 📈 Roadmap

### Versioni Future
- [ ] Notifiche push per eventi AI
- [ ] Dashboard analytics avanzate
- [ ] Integrazione cloud storage
- [ ] App mobile companion
- [ ] Riconoscimento facciale
- [ ] Integrazione con sistemi di allarme
- [ ] API webhooks per integrazioni esterne
- [ ] Backup automatico configurazioni

## 🤝 Contribuire

1. Fork del repository
2. Crea feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit delle modifiche (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
>>>>>>> 0159120983ed46a24979d2fd0dd96e1150a36f52
5. Apri una Pull Request

## 📄 Licenza

<<<<<<< HEAD
Distribuito sotto licenza MIT. Vedi `LICENSE` per maggiori informazioni.

## 👥 Team

- **Gian** - Lead Developer - [@gitgian74](https://github.com/gitgian74)

## 🙏 Ringraziamenti

- [Viam Robotics](https://viam.com) per la piattaforma robotica
- [Appwrite](https://appwrite.io) per il backend
- [GitHub Pages](https://pages.github.com) per l'hosting
- [Netlify](https://netlify.com) per l'hosting alternativo

---

Made with ❤️ by SG Security Team
=======
Questo progetto è rilasciato sotto licenza MIT. Vedi il file `LICENSE` per dettagli.

## 👨‍💻 Autore

**Gian** - [gitgian74](https://github.com/gitgian74)

## 🙏 Ringraziamenti

- Team VIAM per l'eccellente SDK e documentazione
- Community Flask per il framework robusto
- Contributors open source per le librerie utilizzate

## 📞 Supporto

Per supporto e domande:
- Apri una issue su GitHub
- Consulta la documentazione VIAM
- Controlla i logs dell'applicazione

---

**Nota**: Questo è un sistema di videosorveglianza professionale. Assicurati di rispettare le leggi locali sulla privacy e videosorveglianza quando utilizzi questo software.

>>>>>>> 0159120983ed46a24979d2fd0dd96e1150a36f52
