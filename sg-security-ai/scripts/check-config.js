#!/usr/bin/env node

/**
 * Script per verificare la configurazione di SG Security AI
 * Controlla che tutte le API key e configurazioni siano presenti
 */

const fs = require('fs');
const path = require('path');

// Colori per console
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function error(message) {
  log(`❌ ${message}`, 'red');
}

function success(message) {
  log(`✅ ${message}`, 'green');
}

function warning(message) {
  log(`⚠️ ${message}`, 'yellow');
}

function info(message) {
  log(`ℹ️ ${message}`, 'blue');
}

// Verifica file .env.local
function checkEnvFile() {
  const envPath = path.join(__dirname, '../frontend/.env.local');
  
  if (!fs.existsSync(envPath)) {
    error('File .env.local non trovato!');
    info('Copia env.example in .env.local e configura le variabili');
    return false;
  }
  
  success('File .env.local trovato');
  return true;
}

// Verifica variabili Appwrite
function checkAppwriteConfig() {
  const envPath = path.join(__dirname, '../frontend/.env.local');
  
  if (!fs.existsSync(envPath)) {
    error('Impossibile verificare Appwrite: .env.local non trovato');
    return false;
  }
  
  const envContent = fs.readFileSync(envPath, 'utf8');
  const lines = envContent.split('\n');
  
  const requiredVars = [
    'VITE_APPWRITE_ENDPOINT',
    'VITE_APPWRITE_PROJECT_ID',
    'VITE_APPWRITE_DATABASE_ID'
  ];
  
  let allPresent = true;
  
  requiredVars.forEach(varName => {
    const line = lines.find(l => l.startsWith(varName + '='));
    if (!line) {
      error(`Variabile ${varName} mancante`);
      allPresent = false;
    } else {
      const value = line.split('=')[1]?.trim();
      if (!value || value === 'your_appwrite_project_id_here' || value === 'your_appwrite_database_id_here') {
        warning(`Variabile ${varName} non configurata (valore di default)`);
        allPresent = false;
      } else {
        success(`Variabile ${varName} configurata`);
      }
    }
  });
  
  return allPresent;
}

// Verifica variabili Viam
function checkViamConfig() {
  const envPath = path.join(__dirname, '../frontend/.env.local');
  
  if (!fs.existsSync(envPath)) {
    error('Impossibile verificare Viam: .env.local non trovato');
    return false;
  }
  
  const envContent = fs.readFileSync(envPath, 'utf8');
  const lines = envContent.split('\n');
  
  const requiredVars = [
    'VITE_VIAM_ROBOT_ADDRESS',
    'VITE_VIAM_API_KEY',
    'VITE_VIAM_API_KEY_ID'
  ];
  
  let allPresent = true;
  
  requiredVars.forEach(varName => {
    const line = lines.find(l => l.startsWith(varName + '='));
    if (!line) {
      error(`Variabile ${varName} mancante`);
      allPresent = false;
    } else {
      const value = line.split('=')[1]?.trim();
      if (!value || value.includes('your_viam_')) {
        warning(`Variabile ${varName} non configurata (valore di default)`);
        allPresent = false;
      } else {
        success(`Variabile ${varName} configurata`);
      }
    }
  });
  
  return allPresent;
}

// Verifica dipendenze
function checkDependencies() {
  const packageJsonPath = path.join(__dirname, '../frontend/package.json');
  
  if (!fs.existsSync(packageJsonPath)) {
    error('package.json non trovato');
    return false;
  }
  
  const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
  
  // Verifica dipendenze principali
  const requiredDeps = ['react', 'vite', '@vitejs/plugin-react'];
  let allPresent = true;
  
  requiredDeps.forEach(dep => {
    if (!packageJson.dependencies?.[dep] && !packageJson.devDependencies?.[dep]) {
      error(`Dipendenza ${dep} mancante`);
      allPresent = false;
    } else {
      success(`Dipendenza ${dep} presente`);
    }
  });
  
  return allPresent;
}

// Verifica struttura cartelle
function checkProjectStructure() {
  const requiredDirs = [
    '../frontend/src',
    '../frontend/public',
    '../frontend/src/components',
    '../frontend/src/pages',
    '../api'
  ];
  
  let allPresent = true;
  
  requiredDirs.forEach(dir => {
    const fullPath = path.join(__dirname, dir);
    if (!fs.existsSync(fullPath)) {
      error(`Cartella ${dir} mancante`);
      allPresent = false;
    } else {
      success(`Cartella ${dir} presente`);
    }
  });
  
  return allPresent;
}

// Verifica file di configurazione
function checkConfigFiles() {
  const requiredFiles = [
    '../frontend/vite.config.ts',
    '../frontend/tsconfig.json',
    '../frontend/tailwind.config.js',
    '../frontend/env.example'
  ];
  
  let allPresent = true;
  
  requiredFiles.forEach(file => {
    const fullPath = path.join(__dirname, file);
    if (!fs.existsSync(fullPath)) {
      error(`File ${file} mancante`);
      allPresent = false;
    } else {
      success(`File ${file} presente`);
    }
  });
  
  return allPresent;
}

// Main function
function main() {
  log('\n🔍 VERIFICA CONFIGURAZIONE SG SECURITY AI', 'bright');
  log('==========================================\n', 'bright');
  
  let allChecksPassed = true;
  
  // Verifica struttura progetto
  log('📁 VERIFICA STRUTTURA PROGETTO', 'cyan');
  if (!checkProjectStructure()) allChecksPassed = false;
  
  log('\n📦 VERIFICA DIPENDENZE', 'cyan');
  if (!checkDependencies()) allChecksPassed = false;
  
  log('\n⚙️ VERIFICA FILE DI CONFIGURAZIONE', 'cyan');
  if (!checkConfigFiles()) allChecksPassed = false;
  
  log('\n🔐 VERIFICA VARIABILI AMBIENTE', 'cyan');
  if (!checkEnvFile()) allChecksPassed = false;
  
  log('\n☁️ VERIFICA CONFIGURAZIONE APPWRITE', 'cyan');
  if (!checkAppwriteConfig()) allChecksPassed = false;
  
  log('\n🤖 VERIFICA CONFIGURAZIONE VIAM', 'cyan');
  if (!checkViamConfig()) allChecksPassed = false;
  
  // Risultato finale
  log('\n' + '='.repeat(50), 'bright');
  if (allChecksPassed) {
    log('🎉 TUTTE LE VERIFICHE SUPERATE!', 'green');
    log('Il progetto è configurato correttamente.', 'green');
  } else {
    log('⚠️ ALCUNE VERIFICHE FALLITE', 'yellow');
    log('Controlla i messaggi sopra e correggi i problemi.', 'yellow');
    log('\n📋 PROSSIMI PASSI:', 'blue');
    log('1. Copia env.example in .env.local', 'blue');
    log('2. Configura le credenziali Appwrite', 'blue');
    log('3. Configura le credenziali Viam', 'blue');
    log('4. Installa le dipendenze: npm install', 'blue');
    log('5. Avvia il progetto: npm run dev', 'blue');
  }
  log('='.repeat(50), 'bright');
}

// Esegui se chiamato direttamente
if (require.main === module) {
  main();
}

module.exports = {
  checkEnvFile,
  checkAppwriteConfig,
  checkViamConfig,
  checkDependencies,
  checkProjectStructure,
  checkConfigFiles
}; 