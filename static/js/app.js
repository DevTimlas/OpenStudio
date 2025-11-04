// OpenStudio Frontend JavaScript

class OpenStudioApp {
    constructor() {
        this.selectedAgent = null;
        this.isLoading = false;
        this.init();
    }

    init() {
        this.bindEvents();
        this.setupSmoothScrolling();
        this.initializeAgentButtons();
    }

    bindEvents() {
        // Agent selection buttons
        document.querySelectorAll('.agent-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const agent = e.target.closest('.agent-btn').dataset.agent;
                this.selectAgent(agent);
            });
        });

        // Form submission
        const form = document.getElementById('agent-form');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleFormSubmission();
            });
        }

        // Navigation smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    setupSmoothScrolling() {
        // Add smooth scrolling behavior
        document.documentElement.style.scrollBehavior = 'smooth';
    }

    initializeAgentButtons() {
        // Set initial state
        this.updateUI();
    }

    selectAgent(agentType) {
        this.selectedAgent = agentType;
        
        // Update button states
        document.querySelectorAll('.agent-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.agent === agentType) {
                btn.classList.add('active');
            }
        });

        // Update UI
        this.updateUI();
        this.updateAgentForm(agentType);
        
        // Add animation
        const selectedBtn = document.querySelector(`[data-agent="${agentType}"]`);
        if (selectedBtn) {
            selectedBtn.classList.add('slide-in');
            setTimeout(() => selectedBtn.classList.remove('slide-in'), 300);
        }
    }

    updateUI() {
        const agentNameEl = document.getElementById('selected-agent-name');
        const agentStatusEl = document.getElementById('agent-status');
        const userInput = document.getElementById('user-input');
        const submitBtn = document.getElementById('submit-btn');

        if (this.selectedAgent) {
            const agentNames = {
                'plotter': 'Plotter Agent',
                'worldbuilder': 'World Builder Agent',
                'writer': 'Writer Agent',
                'editor': 'Editor Agent'
            };

            agentNameEl.textContent = agentNames[this.selectedAgent];
            agentStatusEl.textContent = 'Ready';
            agentStatusEl.className = 'badge bg-success ms-2';
            
            userInput.disabled = false;
            submitBtn.disabled = false;
            
            userInput.placeholder = this.getPlaceholderText(this.selectedAgent);
        } else {
            agentNameEl.textContent = 'Select an Agent';
            agentStatusEl.textContent = 'Waiting';
            agentStatusEl.className = 'badge bg-secondary ms-2';
            
            userInput.disabled = true;
            submitBtn.disabled = true;
            userInput.placeholder = 'Select an agent first...';
        }
    }

    getPlaceholderText(agent) {
        const placeholders = {
            'plotter': 'Describe your story idea, genre, characters, or plot elements you\'d like help developing...',
            'worldbuilder': 'Describe the world, setting, or environment you\'d like to create for your story...',
            'writer': 'Provide an outline, scene description, or writing prompt you\'d like expanded into prose...',
            'editor': 'Paste the text you\'d like edited, refined, or improved...'
        };
        return placeholders[agent] || 'Describe what you\'d like help with...';
    }

    updateAgentForm(agentType) {
        const additionalFields = document.getElementById('additional-fields');
        additionalFields.innerHTML = '';

        // Add agent-specific fields
        const fields = this.getAgentFields(agentType);
        fields.forEach(field => {
            const fieldHtml = this.createFieldHTML(field);
            additionalFields.innerHTML += fieldHtml;
        });

        // Add fade-in animation
        additionalFields.classList.add('fade-in');
        setTimeout(() => additionalFields.classList.remove('fade-in'), 500);
    }

    getAgentFields(agentType) {
        const fieldConfigs = {
            'plotter': [
                {
                    type: 'select',
                    name: 'genre',
                    label: 'Story Genre',
                    options: ['Fantasy', 'Science Fiction', 'Mystery', 'Romance', 'Thriller', 'Historical Fiction', 'Contemporary Fiction'],
                    required: false
                },
                {
                    type: 'select',
                    name: 'length',
                    label: 'Story Length',
                    options: ['Short Story', 'Novella', 'Novel', 'Series'],
                    required: false
                }
            ],
            'worldbuilder': [
                {
                    type: 'select',
                    name: 'genre',
                    label: 'World Genre',
                    options: ['Fantasy', 'Science Fiction', 'Mystery', 'Romance', 'Thriller', 'Historical Fiction', 'Contemporary Fiction'],
                    required: false
                },
                {
                    type: 'select',
                    name: 'scope',
                    label: 'World Scope',
                    options: ['City/Town', 'Region', 'Country', 'Continent', 'Planet', 'Galaxy'],
                    required: false
                }
            ],
            'writer': [
                {
                    type: 'select',
                    name: 'genre',
                    label: 'Story Genre',
                    options: ['Fantasy', 'Science Fiction', 'Mystery', 'Romance', 'Thriller', 'Historical Fiction', 'Contemporary Fiction'],
                    required: false
                },
                {
                    type: 'select',
                    name: 'style',
                    label: 'Writing Style',
                    options: ['Descriptive', 'Dialogue-heavy', 'Action-packed', 'Atmospheric', 'Minimalist'],
                    required: false
                },
                {
                    type: 'select',
                    name: 'length',
                    label: 'Target Length',
                    options: ['Short Story', 'Novella', 'Novel', 'Series'],
                    required: false
                }
            ],
            'editor': [
                {
                    type: 'multiselect',
                    name: 'focus_areas',
                    label: 'Focus Areas',
                    options: ['Grammar', 'Style', 'Clarity', 'Flow', 'Character Development', 'Plot Consistency'],
                    required: false
                },
                {
                    type: 'checkbox',
                    name: 'preserve_style',
                    label: 'Preserve Original Style',
                    required: false
                }
            ]
        };

        return fieldConfigs[agentType] || [];
    }

    createFieldHTML(field) {
        let html = `<div class="additional-field">`;
        html += `<label class="form-label">${field.label}</label>`;

        switch (field.type) {
            case 'select':
                html += `<select class="form-select" name="${field.name}" ${field.required ? 'required' : ''}>`;
                html += `<option value="">Choose...</option>`;
                field.options.forEach(option => {
                    html += `<option value="${option}">${option}</option>`;
                });
                html += `</select>`;
                break;

            case 'multiselect':
                field.options.forEach(option => {
                    html += `<div class="form-check">`;
                    html += `<input class="form-check-input" type="checkbox" name="${field.name}" value="${option}" id="${field.name}_${option}">`;
                    html += `<label class="form-check-label" for="${field.name}_${option}">${option}</label>`;
                    html += `</div>`;
                });
                break;

            case 'checkbox':
                html += `<div class="form-check">`;
                html += `<input class="form-check-input" type="checkbox" name="${field.name}" id="${field.name}">`;
                html += `<label class="form-check-label" for="${field.name}">${field.label}</label>`;
                html += `</div>`;
                break;

            default:
                html += `<input type="text" class="form-control" name="${field.name}" ${field.required ? 'required' : ''}>`;
        }

        html += `</div>`;
        return html;
    }

    async handleFormSubmission() {
        if (this.isLoading) return;

        const userInput = document.getElementById('user-input').value.trim();
        if (!userInput) {
            this.showAlert('Please enter your request.', 'warning');
            return;
        }

        this.setLoading(true);
        
        try {
            const formData = this.collectFormData();
            const response = await this.sendRequest(formData);
            this.displayResponse(response);
        } catch (error) {
            console.error('Error:', error);
            this.showAlert('An error occurred while processing your request. Please try again.', 'danger');
        } finally {
            this.setLoading(false);
        }
    }

    collectFormData() {
        const form = document.getElementById('agent-form');
        const formData = new FormData(form);
        const data = {
            agent: this.selectedAgent,
            content: formData.get('user-input') || document.getElementById('user-input').value,
        };

        // Collect additional fields
        const additionalFields = document.getElementById('additional-fields');
        const inputs = additionalFields.querySelectorAll('input, select');
        
        inputs.forEach(input => {
            if (input.type === 'checkbox') {
                if (input.name === 'focus_areas') {
                    if (!data.focus_areas) data.focus_areas = [];
                    if (input.checked) {
                        data.focus_areas.push(input.value);
                    }
                } else {
                    data[input.name] = input.checked;
                }
            } else if (input.value) {
                data[input.name] = input.value;
            }
        });

        return data;
    }

    async sendRequest(data) {
        const endpoints = {
            'plotter': '/api/plot',
            'worldbuilder': '/api/worldbuild',
            'writer': '/api/write',
            'editor': '/api/edit'
        };

        const endpoint = endpoints[this.selectedAgent];
        if (!endpoint) {
            throw new Error('Invalid agent selected');
        }

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    displayResponse(response) {
        console.log('Response object received by displayResponse:', response);
        const responseArea = document.getElementById('response-area');
        
        let html = '<div class="response-content fade-in">';
        html += `<h6><i class="bi bi-check-circle me-2"></i>Response from ${this.selectedAgent.charAt(0).toUpperCase() + this.selectedAgent.slice(1)} Agent</h6>`;
        
        if (response.success) {
            if (typeof response.result === 'string') {
                html += `<div class="mb-3">${this.formatText(response.result)}</div>`;
            } else if (typeof response.result === 'object') {
                html += this.formatObjectResponse(response.result);
            }
            
            if (response.suggestions && response.suggestions.length > 0) {
                html += '<h6 class="mt-3"><i class="bi bi-lightbulb me-2"></i>Suggestions</h6>';
                html += '<ul class="list-unstyled">';
                response.suggestions.forEach(suggestion => {
                    html += `<li class="mb-2"><i class="bi bi-arrow-right me-2 text-primary"></i>${suggestion}</li>`;
                });
                html += '</ul>';
            }
        } else {
            html += `<div class="alert alert-danger">${response.error || 'An error occurred'}</div>`;
        }
        
        html += '</div>';
        responseArea.innerHTML = html;
        
        // Scroll to response
        responseArea.scrollTop = 0;
    }

    formatObjectResponse(obj) {
        let html = '';
        
        for (const [key, value] of Object.entries(obj)) {
            if (key === 'success' || key === 'error') continue;
            
            html += `<div class="mb-3">`;
            html += `<strong>${this.formatKey(key)}:</strong><br>`;
            
            if (Array.isArray(value)) {
                html += '<ul class="mt-2">';
                value.forEach(item => {
                    html += `<li>${typeof item === 'object' ? JSON.stringify(item, null, 2) : item}</li>`;
                });
                html += '</ul>';
            } else if (typeof value === 'object') {
                html += `<pre class="bg-light p-2 rounded mt-2">${JSON.stringify(value, null, 2)}</pre>`;
            } else if (typeof value === 'string') {
                html += `<div class="mt-2">${this.formatText(value)}</div>`;
            } else {
                html += `<div class="mt-2">${value}</div>`;
            }
            
            html += '</div>';
        }
        
        return html;
    }

    formatKey(key) {
        return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    formatText(text) {
        if (!text) return '';
        
        // Convert line breaks to HTML
        return text.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    }

    setLoading(loading) {
        this.isLoading = loading;
        const submitBtn = document.getElementById('submit-btn');
        const agentStatusEl = document.getElementById('agent-status');
        
        if (loading) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
            agentStatusEl.textContent = 'Working';
            agentStatusEl.className = 'badge bg-warning ms-2';
            
            // Show loading in response area
            const responseArea = document.getElementById('response-area');
            responseArea.innerHTML = `
                <div class="loading-spinner">
                    <div class="spinner-border text-primary me-3"></div>
                    <div class="loading-text">Your ${this.selectedAgent} agent is working on your request...</div>
                </div>
            `;
        } else {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="bi bi-send me-2"></i>Send Request';
            agentStatusEl.textContent = 'Ready';
            agentStatusEl.className = 'badge bg-success ms-2';
        }
    }

    showAlert(message, type = 'info') {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const responseArea = document.getElementById('response-area');
        responseArea.innerHTML = alertHtml + responseArea.innerHTML;
    }

    clearWorkspace() {
        document.getElementById('user-input').value = '';
        document.getElementById('additional-fields').innerHTML = '';
        document.getElementById('response-area').innerHTML = `
            <div class="text-center text-muted py-5">
                <i class="bi bi-chat-square-dots display-4 mb-3"></i>
                <p>Select an agent and submit a request to see the response here.</p>
            </div>
        `;
        
        // Reset agent selection
        document.querySelectorAll('.agent-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        this.selectedAgent = null;
        this.updateUI();
    }
}

// Global functions for HTML onclick handlers
function scrollToWorkspace() {
    document.getElementById('workspace').scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
}

function selectAgent(agentType) {
    if (window.app) {
        window.app.selectAgent(agentType);
        scrollToWorkspace();
    }
}

function clearWorkspace() {
    if (window.app) {
        window.app.clearWorkspace();
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new OpenStudioApp();
});

// Add some nice scroll effects
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 100) {
        navbar.style.background = 'rgba(99, 102, 241, 0.98)';
    } else {
        navbar.style.background = 'rgba(99, 102, 241, 0.95)';
    }
});