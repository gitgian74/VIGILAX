// SG Security AI - Main Application JavaScript

class SecurityApp {
    constructor() {
        this.currentUser = null;
        this.accessToken = null;
        this.sessionToken = null;
        this.currentPage = 'dashboard';
        this.cameras = [];
        this.users = [];
        
        this.init();
    }

    init() {
        // Check if user is already logged in
        this.accessToken = localStorage.getItem('access_token');
        this.sessionToken = localStorage.getItem('session_token');
        
        if (this.accessToken) {
            this.validateToken();
        } else {
            this.showLogin();
        }
        
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Login form
        document.getElementById('loginForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });

        // Toggle password visibility
        document.getElementById('togglePassword').addEventListener('click', () => {
            const passwordInput = document.getElementById('password');
            const icon = document.querySelector('#togglePassword i');
            
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                icon.className = 'fas fa-eye-slash';
            } else {
                passwordInput.type = 'password';
                icon.className = 'fas fa-eye';
            }
        });

        // Navigation
        document.querySelectorAll('[data-page]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = e.currentTarget.getAttribute('data-page');
                this.navigateToPage(page);
            });
        });

        // Logout
        document.getElementById('logoutBtn').addEventListener('click', () => {
            this.handleLogout();
        });

        // Profile form
        document.getElementById('profileForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.updateProfile();
        });

        // Password form
        document.getElementById('passwordForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.changePassword();
        });

        // Camera modal
        document.getElementById('addCameraBtn')?.addEventListener('click', () => {
            this.showCameraModal();
        });

        document.getElementById('saveCameraBtn').addEventListener('click', () => {
            this.saveCamera();
        });

        // User modal
        document.getElementById('addUserBtn')?.addEventListener('click', () => {
            this.showUserModal();
        });

        document.getElementById('saveUserBtn').addEventListener('click', () => {
            this.saveUser();
        });
    }

    // Authentication Methods
    async handleLogin() {
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const errorDiv = document.getElementById('loginError');

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (response.ok) {
                this.accessToken = data.access_token;
                this.sessionToken = data.session_token;
                this.currentUser = data.user;

                localStorage.setItem('access_token', this.accessToken);
                localStorage.setItem('session_token', this.sessionToken);
                localStorage.setItem('current_user', JSON.stringify(this.currentUser));

                this.showMainApp();
                this.loadDashboard();
            } else {
                errorDiv.textContent = data.error || 'Errore di login';
                errorDiv.classList.remove('d-none');
            }
        } catch (error) {
            console.error('Login error:', error);
            errorDiv.textContent = 'Errore di connessione al server';
            errorDiv.classList.remove('d-none');
        }
    }

    async validateToken() {
        try {
            const response = await this.apiCall('/api/auth/profile', 'GET');
            
            if (response.ok) {
                const data = await response.json();
                this.currentUser = data.user;
                localStorage.setItem('current_user', JSON.stringify(this.currentUser));
                this.showMainApp();
                this.loadDashboard();
            } else {
                this.handleLogout();
            }
        } catch (error) {
            console.error('Token validation error:', error);
            this.handleLogout();
        }
    }

    async handleLogout() {
        try {
            await this.apiCall('/api/auth/logout', 'POST', {
                session_token: this.sessionToken
            });
        } catch (error) {
            console.error('Logout error:', error);
        }

        this.accessToken = null;
        this.sessionToken = null;
        this.currentUser = null;

        localStorage.removeItem('access_token');
        localStorage.removeItem('session_token');
        localStorage.removeItem('current_user');

        this.showLogin();
    }

    // UI Navigation Methods
    showLogin() {
        document.getElementById('loadingScreen').classList.add('d-none');
        document.getElementById('loginPage').classList.remove('d-none');
        document.getElementById('mainApp').classList.add('d-none');
    }

    showMainApp() {
        document.getElementById('loadingScreen').classList.add('d-none');
        document.getElementById('loginPage').classList.add('d-none');
        document.getElementById('mainApp').classList.remove('d-none');

        // Update user info in navbar
        document.getElementById('currentUsername').textContent = this.currentUser.username;

        // Show/hide admin elements
        const adminElements = document.querySelectorAll('.admin-only');
        const superAdminElements = document.querySelectorAll('.super-admin-only');

        if (this.currentUser.role === 'super_admin') {
            adminElements.forEach(el => el.classList.remove('d-none'));
            superAdminElements.forEach(el => el.classList.remove('d-none'));
        } else if (this.currentUser.role === 'admin') {
            adminElements.forEach(el => el.classList.remove('d-none'));
            superAdminElements.forEach(el => el.classList.add('d-none'));
        } else {
            adminElements.forEach(el => el.classList.add('d-none'));
            superAdminElements.forEach(el => el.classList.add('d-none'));
        }
    }

    navigateToPage(page) {
        // Hide all pages
        document.querySelectorAll('.page-content').forEach(p => p.classList.add('d-none'));
        
        // Show selected page
        document.getElementById(page + 'Page').classList.remove('d-none');
        
        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-page="${page}"]`).classList.add('active');
        
        this.currentPage = page;
        
        // Load page content
        switch (page) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'cameras':
                this.loadCameras();
                break;
            case 'recordings':
                this.loadRecordings();
                break;
            case 'users':
                this.loadUsers();
                break;
            case 'profile':
                this.loadProfile();
                break;
        }
    }

    // API Helper Method
    async apiCall(url, method = 'GET', data = null) {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        if (this.accessToken) {
            options.headers['Authorization'] = `Bearer ${this.accessToken}`;
        }

        if (data) {
            options.body = JSON.stringify(data);
        }

        return fetch(url, options);
    }

    // Dashboard Methods
    async loadDashboard() {
        try {
            // Load cameras
            const camerasResponse = await this.apiCall('/api/cameras');
            if (camerasResponse.ok) {
                const camerasData = await camerasResponse.json();
                this.cameras = camerasData.cameras;
                this.updateDashboardStats();
                this.renderCameraGrid();
            }
        } catch (error) {
            console.error('Error loading dashboard:', error);
        }
    }

    updateDashboardStats() {
        const totalCameras = this.cameras.length;
        const activeCameras = this.cameras.filter(c => c.is_active).length;
        const recordingCameras = this.cameras.filter(c => c.recording_enabled).length;

        document.getElementById('totalCameras').textContent = totalCameras;
        document.getElementById('activeStreams').textContent = activeCameras;
        document.getElementById('recordingCameras').textContent = recordingCameras;
        document.getElementById('aiEvents').textContent = '0'; // Placeholder
    }

    renderCameraGrid() {
        const grid = document.getElementById('cameraGrid');
        grid.innerHTML = '';

        this.cameras.forEach(camera => {
            const cameraCard = this.createCameraCard(camera);
            grid.appendChild(cameraCard);
        });
    }

    createCameraCard(camera) {
        const card = document.createElement('div');
        card.className = 'camera-feed';
        
        card.innerHTML = `
            <div class="camera-header">
                <h5 class="camera-title">${camera.name}</h5>
                <div class="camera-status">
                    <span class="status-indicator ${camera.is_active ? '' : 'offline'}"></span>
                    <small>${camera.is_active ? 'Online' : 'Offline'}</small>
                </div>
            </div>
            <div class="camera-video">
                ${camera.is_active ? 
                    '<i class="fas fa-play-circle fa-3x"></i><br>Click per avviare stream' : 
                    '<i class="fas fa-exclamation-triangle fa-2x"></i><br>Camera offline'
                }
            </div>
            <div class="camera-controls">
                <div class="camera-info">
                    <small>${camera.location} • ${camera.resolution} • ${camera.fps}fps</small>
                </div>
                <div class="camera-actions">
                    <button class="btn btn-sm btn-primary" onclick="app.startStream('${camera.id}')">
                        <i class="fas fa-play"></i>
                    </button>
                    <button class="btn btn-sm btn-secondary" onclick="app.takeSnapshot('${camera.id}')">
                        <i class="fas fa-camera"></i>
                    </button>
                </div>
            </div>
        `;

        return card;
    }

    // Camera Methods
    async loadCameras() {
        try {
            const response = await this.apiCall('/api/cameras');
            if (response.ok) {
                const data = await response.json();
                this.cameras = data.cameras;
                this.renderCamerasTable();
            }
        } catch (error) {
            console.error('Error loading cameras:', error);
        }
    }

    renderCamerasTable() {
        const container = document.getElementById('camerasTable');
        
        let html = `
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nome</th>
                        <th>Posizione</th>
                        <th>Stato</th>
                        <th>Risoluzione</th>
                        <th>FPS</th>
                        <th>Registrazione</th>
                        <th>AI</th>
                        <th>Azioni</th>
                    </tr>
                </thead>
                <tbody>
        `;

        this.cameras.forEach(camera => {
            html += `
                <tr>
                    <td><code>${camera.id}</code></td>
                    <td>${camera.name}</td>
                    <td>${camera.location || '-'}</td>
                    <td>
                        <span class="badge ${camera.is_active ? 'bg-success' : 'bg-danger'}">
                            ${camera.is_active ? 'Attiva' : 'Inattiva'}
                        </span>
                    </td>
                    <td>${camera.resolution}</td>
                    <td>${camera.fps}</td>
                    <td>
                        <i class="fas ${camera.recording_enabled ? 'fa-check text-success' : 'fa-times text-danger'}"></i>
                    </td>
                    <td>
                        <i class="fas ${camera.ai_analysis_enabled ? 'fa-check text-success' : 'fa-times text-danger'}"></i>
                    </td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="app.editCamera('${camera.id}')">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-info" onclick="app.viewCamera('${camera.id}')">
                            <i class="fas fa-eye"></i>
                        </button>
                        ${this.currentUser.role === 'super_admin' ? 
                            `<button class="btn btn-sm btn-danger" onclick="app.deleteCamera('${camera.id}')">
                                <i class="fas fa-trash"></i>
                            </button>` : ''
                        }
                    </td>
                </tr>
            `;
        });

        html += '</tbody></table>';
        container.innerHTML = html;
    }

    // User Methods
    async loadUsers() {
        if (this.currentUser.role !== 'super_admin' && this.currentUser.role !== 'admin') {
            return;
        }

        try {
            const response = await this.apiCall('/api/users');
            if (response.ok) {
                const data = await response.json();
                this.users = data.users;
                this.renderUsersTable();
            }
        } catch (error) {
            console.error('Error loading users:', error);
        }
    }

    renderUsersTable() {
        const container = document.getElementById('usersTable');
        
        let html = `
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Ruolo</th>
                        <th>Stato</th>
                        <th>Ultimo Accesso</th>
                        <th>Azioni</th>
                    </tr>
                </thead>
                <tbody>
        `;

        this.users.forEach(user => {
            html += `
                <tr>
                    <td>${user.id}</td>
                    <td>${user.username}</td>
                    <td>${user.email}</td>
                    <td>
                        <span class="role-${user.role}">
                            ${this.getRoleDisplayName(user.role)}
                        </span>
                    </td>
                    <td>
                        <span class="badge ${user.is_active ? 'bg-success' : 'bg-danger'}">
                            ${user.is_active ? 'Attivo' : 'Inattivo'}
                        </span>
                    </td>
                    <td>${user.last_login ? new Date(user.last_login).toLocaleString('it-IT') : 'Mai'}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="app.editUser(${user.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-warning" onclick="app.toggleUserStatus(${user.id})">
                            <i class="fas ${user.is_active ? 'fa-ban' : 'fa-check'}"></i>
                        </button>
                        ${this.currentUser.role === 'super_admin' && user.id !== this.currentUser.id ? 
                            `<button class="btn btn-sm btn-danger" onclick="app.deleteUser(${user.id})">
                                <i class="fas fa-trash"></i>
                            </button>` : ''
                        }
                    </td>
                </tr>
            `;
        });

        html += '</tbody></table>';
        container.innerHTML = html;
    }

    getRoleDisplayName(role) {
        const roles = {
            'super_admin': 'Super Admin',
            'admin': 'Amministratore',
            'user': 'Utente'
        };
        return roles[role] || role;
    }

    // Profile Methods
    loadProfile() {
        if (!this.currentUser) return;

        document.getElementById('profileUsername').value = this.currentUser.username;
        document.getElementById('profileEmail').value = this.currentUser.email;
        document.getElementById('profileRole').value = this.getRoleDisplayName(this.currentUser.role);
    }

    async updateProfile() {
        const email = document.getElementById('profileEmail').value;

        try {
            const response = await this.apiCall('/api/auth/profile', 'PUT', { email });
            
            if (response.ok) {
                const data = await response.json();
                this.currentUser = data.user;
                localStorage.setItem('current_user', JSON.stringify(this.currentUser));
                this.showAlert('Profilo aggiornato con successo', 'success');
            } else {
                const error = await response.json();
                this.showAlert(error.error || 'Errore nell\'aggiornamento del profilo', 'danger');
            }
        } catch (error) {
            console.error('Error updating profile:', error);
            this.showAlert('Errore di connessione', 'danger');
        }
    }

    async changePassword() {
        const newPassword = document.getElementById('newPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;

        if (newPassword !== confirmPassword) {
            this.showAlert('Le password non coincidono', 'danger');
            return;
        }

        if (newPassword.length < 6) {
            this.showAlert('La password deve essere di almeno 6 caratteri', 'danger');
            return;
        }

        try {
            const response = await this.apiCall('/api/auth/profile', 'PUT', { 
                password: newPassword 
            });
            
            if (response.ok) {
                document.getElementById('passwordForm').reset();
                this.showAlert('Password cambiata con successo', 'success');
            } else {
                const error = await response.json();
                this.showAlert(error.error || 'Errore nel cambio password', 'danger');
            }
        } catch (error) {
            console.error('Error changing password:', error);
            this.showAlert('Errore di connessione', 'danger');
        }
    }

    // Camera Actions
    async startStream(cameraId) {
        try {
            const response = await this.apiCall(`/api/cameras/${cameraId}/stream`);
            if (response.ok) {
                const data = await response.json();
                this.showAlert(`Stream avviato per ${cameraId}`, 'success');
                // TODO: Implement actual video streaming
            } else {
                const error = await response.json();
                this.showAlert(error.error || 'Errore nell\'avvio dello stream', 'danger');
            }
        } catch (error) {
            console.error('Error starting stream:', error);
            this.showAlert('Errore di connessione', 'danger');
        }
    }

    async takeSnapshot(cameraId) {
        try {
            const response = await this.apiCall(`/api/cameras/${cameraId}/snapshot`);
            if (response.ok) {
                this.showAlert(`Snapshot acquisito per ${cameraId}`, 'success');
            } else {
                const error = await response.json();
                this.showAlert(error.error || 'Errore nell\'acquisizione snapshot', 'danger');
            }
        } catch (error) {
            console.error('Error taking snapshot:', error);
            this.showAlert('Errore di connessione', 'danger');
        }
    }

    // Utility Methods
    showAlert(message, type = 'info') {
        // Create alert element
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alert.style.cssText = 'top: 20px; right: 20px; z-index: 1050; max-width: 400px;';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alert);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 5000);
    }

    // Placeholder methods for future implementation
    loadRecordings() {
        console.log('Loading recordings...');
    }

    showCameraModal(cameraId = null) {
        console.log('Show camera modal:', cameraId);
    }

    saveCamera() {
        console.log('Save camera');
    }

    showUserModal(userId = null) {
        console.log('Show user modal:', userId);
    }

    saveUser() {
        console.log('Save user');
    }

    editCamera(cameraId) {
        console.log('Edit camera:', cameraId);
    }

    viewCamera(cameraId) {
        console.log('View camera:', cameraId);
    }

    deleteCamera(cameraId) {
        console.log('Delete camera:', cameraId);
    }

    editUser(userId) {
        console.log('Edit user:', userId);
    }

    toggleUserStatus(userId) {
        console.log('Toggle user status:', userId);
    }

    deleteUser(userId) {
        console.log('Delete user:', userId);
    }
}

// Initialize the application
const app = new SecurityApp();

// Hide loading screen after initialization
setTimeout(() => {
    document.getElementById('loadingScreen').classList.add('d-none');
}, 1500);

