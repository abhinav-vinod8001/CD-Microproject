/**
 * Educational Multi-Language Studio Controller
 * Manages conversion of Malayalam programs to Python, Java, and C using Groq API
 * or high-accuracy offline educational transpiler, with variable replacement dictionaries
 * and educational concept comparisons.
 */

class EducationalStudio {
    constructor(editor) {
        this.editor = editor;
        this.activeLang = 'python'; // 'python' | 'java' | 'c' | 'all'
        this.cachedResult = null;
        this.lastConvertedCode = null;

        // Modal Elements
        this.modal = document.getElementById('multilang-modal');
        this.keyModal = document.getElementById('groq-key-modal');
        this.engineBadge = document.getElementById('multilang-engine-badge');
        this.noticeBanner = document.getElementById('multilang-notice-banner');
        this.noticeText = document.getElementById('multilang-notice-text');
        this.loadingState = document.getElementById('multilang-loading');
        this.contentArea = document.getElementById('multilang-content-area');

        // Views
        this.twoColGrid = document.getElementById('code-compare-grid');
        this.threeWayGrid = document.getElementById('three-way-grid');
        this.origCodeView = document.getElementById('edu-orig-code');
        this.targetCodeView = document.getElementById('edu-target-code');
        this.targetColTitle = document.getElementById('target-col-title');
        this.targetColBadge = document.getElementById('target-col-badge');

        this.pyCodeView = document.getElementById('edu-code-python');
        this.javaCodeView = document.getElementById('edu-code-java');
        this.cCodeView = document.getElementById('edu-code-c');

        // Dictionary & Notes
        this.dictTbody = document.getElementById('edu-dict-tbody');
        this.dictCountBadge = document.getElementById('edu-dict-count');
        this.notesPython = document.getElementById('edu-notes-python');
        this.notesJava = document.getElementById('edu-notes-java');
        this.notesC = document.getElementById('edu-notes-c');
        this.notesSummary = document.getElementById('edu-notes-summary');

        // Key modal elements
        this.keyInput = document.getElementById('groq-api-key-input');
        this.modelSelect = document.getElementById('groq-model-select');
        this.keyStatus = document.getElementById('key-status-message');
        this.keyBtnText = document.getElementById('groq-key-btn-text');

        this.init();
    }

    init() {
        // 1. Check for stored Groq API Key and Model
        const savedKey = this.getStoredApiKey();
        if (savedKey) {
            this.keyInput.value = savedKey;
            this.updateKeyButtonBadge(true);
        } else {
            this.checkServerGroqStatus();
        }

        const savedModel = this.getStoredModel();
        if (this.modelSelect && savedModel) {
            this.modelSelect.value = savedModel;
        }

        // 2. Wire up Modal Open / Close
        const btnOpen = document.getElementById('btn-open-multilang');
        if (btnOpen) {
            btnOpen.addEventListener('click', () => this.openStudio());
        }

        const btnClose = document.getElementById('btn-close-multilang');
        if (btnClose) {
            btnClose.addEventListener('click', () => this.closeStudio());
        }

        const btnDismiss = document.getElementById('btn-dismiss-multilang');
        if (btnDismiss) {
            btnDismiss.addEventListener('click', () => this.closeStudio());
        }

        // Close on backdrop click
        if (this.modal) {
            this.modal.addEventListener('click', (e) => {
                if (e.target === this.modal) this.closeStudio();
            });
        }

        // 3. Tab Navigation (Python / Java / C / Side-by-Side)
        document.querySelectorAll('.edu-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                const lang = tab.getAttribute('data-lang');
                this.switchLanguageTab(lang);
            });
        });

        // 4. Action Buttons
        const btnRefresh = document.getElementById('btn-refresh-multilang');
        if (btnRefresh) {
            btnRefresh.addEventListener('click', () => this.fetchConversion(true));
        }

        const btnCopy = document.getElementById('btn-copy-converted');
        if (btnCopy) {
            btnCopy.addEventListener('click', () => this.copyActiveCode(btnCopy));
        }

        // 5. Groq Key Modal Controls
        const btnOpenKey = document.getElementById('btn-open-groq-key');
        if (btnOpenKey) {
            btnOpenKey.addEventListener('click', () => this.openKeyModal());
        }

        const btnCloseKey = document.getElementById('btn-close-key-modal');
        if (btnCloseKey) {
            btnCloseKey.addEventListener('click', () => this.closeKeyModal());
        }

        const btnSaveKey = document.getElementById('btn-save-key');
        if (btnSaveKey) {
            btnSaveKey.addEventListener('click', () => this.saveApiKey());
        }

        const btnClearKey = document.getElementById('btn-clear-key');
        if (btnClearKey) {
            btnClearKey.addEventListener('click', () => this.clearApiKey());
        }

        // ESC to close modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                if (this.keyModal && this.keyModal.style.display !== 'none') {
                    this.closeKeyModal();
                } else if (this.modal && this.modal.style.display !== 'none') {
                    this.closeStudio();
                }
            }
        });
    }

    getStoredApiKey() {
        try {
            return localStorage.getItem('malayalam_groq_api_key') || '';
        } catch {
            return '';
        }
    }

    getStoredModel() {
        try {
            return localStorage.getItem('malayalam_groq_model') || 'qwen/qwen3.8-27b';
        } catch {
            return 'qwen/qwen3.8-27b';
        }
    }

    setStoredModel(model) {
        try {
            if (model) {
                localStorage.setItem('malayalam_groq_model', model.trim());
            }
        } catch (e) {
            console.error('LocalStorage error:', e);
        }
    }

    setStoredApiKey(key) {
        try {
            if (key) {
                localStorage.setItem('malayalam_groq_api_key', key.trim());
            } else {
                localStorage.removeItem('malayalam_groq_api_key');
            }
        } catch (e) {
            console.error('LocalStorage error:', e);
        }
    }

    updateKeyButtonBadge(hasKey) {
        if (this.keyBtnText) {
            this.keyBtnText.textContent = hasKey ? 'Groq Key (Active)' : 'Groq Key';
        }
    }

    async checkServerGroqStatus() {
        try {
            const resp = await fetch('/api/groq-status');
            const data = await resp.json();
            if (data.has_server_api_key) {
                this.updateKeyButtonBadge(true);
            }
        } catch {
            // Quietly ignore
        }
    }

    openStudio() {
        if (!this.modal) return;
        this.modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';

        const currentCode = this.editor.getValue();
        // If code changed or not converted yet, perform conversion
        if (!this.cachedResult || this.lastConvertedCode !== currentCode) {
            this.fetchConversion(false);
        } else {
            this.render();
        }
    }

    closeStudio() {
        if (!this.modal) return;
        this.modal.style.display = 'none';
        document.body.style.overflow = '';
    }

    openKeyModal() {
        if (!this.keyModal) return;
        this.keyInput.value = this.getStoredApiKey();
        if (this.modelSelect) {
            this.modelSelect.value = this.getStoredModel();
        }
        this.keyStatus.style.display = 'none';
        this.keyModal.style.display = 'flex';
        this.keyInput.focus();
    }

    closeKeyModal() {
        if (!this.keyModal) return;
        this.keyModal.style.display = 'none';
    }

    saveApiKey() {
        const val = this.keyInput.value.trim();
        const chosenModel = this.modelSelect ? this.modelSelect.value : 'qwen/qwen3.8-27b';

        if (val && !val.startsWith('gsk_')) {
            this.keyStatus.className = 'key-status error';
            this.keyStatus.textContent = 'Warning: Standard Groq API keys usually start with "gsk_". Saving anyway...';
            this.keyStatus.style.display = 'block';
        }

        this.setStoredApiKey(val);
        this.setStoredModel(chosenModel);
        this.updateKeyButtonBadge(!!val);

        this.keyStatus.className = 'key-status success';
        this.keyStatus.textContent = val ? `Saved! Using ${chosenModel}` : 'Key removed.';
        this.keyStatus.style.display = 'block';

        setTimeout(() => {
            this.closeKeyModal();
            // Re-convert with new key & model if studio is open
            if (this.modal.style.display !== 'none') {
                this.fetchConversion(true);
            }
        }, 800);
    }

    clearApiKey() {
        this.keyInput.value = '';
        this.setStoredApiKey('');
        this.updateKeyButtonBadge(false);
        this.keyStatus.className = 'key-status info';
        this.keyStatus.textContent = 'Saved key cleared. Built-in educational transpiler will be used.';
        this.keyStatus.style.display = 'block';
    }

    async fetchConversion(forceRefresh = false) {
        const code = this.editor.getValue();
        if (!code || !code.trim()) {
            alert('Please write or load a Malayalam program in the editor first!');
            return;
        }

        const chosenModel = this.getStoredModel();
        const modelShortName = chosenModel.includes('/') ? chosenModel.split('/')[1] : chosenModel;

        this.loadingState.style.display = 'flex';
        const loadingText = document.getElementById('multilang-loading-text');
        if (loadingText) {
            loadingText.textContent = `Analyzing program with Groq AI (${modelShortName})...`;
        }

        this.contentArea.style.opacity = '0.3';
        this.noticeBanner.style.display = 'none';

        const apiKey = this.getStoredApiKey();

        try {
            const resp = await fetch('/api/convert-multilang', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(apiKey ? { 'X-Groq-Api-Key': apiKey } : {})
                },
                body: JSON.stringify({
                    code: code,
                    api_key: apiKey || undefined,
                    model: chosenModel
                })
            });

            const data = await resp.json();

            if (data.success) {
                this.cachedResult = data;
                this.lastConvertedCode = code;
                this.render();
            } else {
                this.showNotice(data.error || 'Failed to convert code.', 'error');
            }
        } catch (err) {
            console.error('Conversion fetch error:', err);
            this.showNotice('Network error connecting to compiler backend.', 'error');
        } finally {
            this.loadingState.style.display = 'none';
            this.contentArea.style.opacity = '1';
        }
    }

    switchLanguageTab(lang) {
        this.activeLang = lang;

        document.querySelectorAll('.edu-tab').forEach(tab => {
            if (tab.getAttribute('data-lang') === lang) {
                tab.classList.add('active');
            } else {
                tab.classList.remove('active');
            }
        });

        this.renderCodeViews();
    }

    showNotice(text, type = 'info') {
        if (!this.noticeBanner || !this.noticeText) return;
        this.noticeText.textContent = text;
        this.noticeBanner.className = `notice-banner ${type}`;
        this.noticeBanner.style.display = 'flex';
    }

    render() {
        if (!this.cachedResult) return;

        const res = this.cachedResult;

        // 1. Engine Badge & Notice
        if (res.engine === 'groq') {
            const m = res.model || this.getStoredModel();
            const modelLabel = m.includes('qwen') ? 'Groq Qwen' : (m.includes('gpt-oss') ? 'Groq GPT-OSS' : 'Groq AI');
            const cleanModel = m.includes('/') ? m.split('/')[1] : m;
            this.engineBadge.textContent = `${modelLabel} (${cleanModel})`;
            this.engineBadge.className = 'badge badge-success';
        } else {
            this.engineBadge.textContent = 'Built-in Educational Transpiler';
            this.engineBadge.className = 'badge badge-ready';
        }

        if (res.notice) {
            this.showNotice(res.notice, res.groq_error ? 'warning' : 'info');
        } else if (res.groq_error) {
            this.showNotice(`Groq note: ${res.groq_error}. Used offline educational engine.`, 'warning');
        }

        // 2. Render Original Malayalam Code
        if (this.origCodeView) {
            this.origCodeView.textContent = this.lastConvertedCode || this.editor.getValue();
        }

        // 3. Render Target Code based on active tab
        this.renderCodeViews();

        // 4. Render Replaced Variables & Keywords Dictionary
        this.renderDictionary(res.dictionary || []);

        // 5. Render Educational Notes
        this.renderEducationalNotes(res.educational_notes || {});
    }

    renderCodeViews() {
        if (!this.cachedResult) return;
        const res = this.cachedResult;

        if (this.activeLang === 'all') {
            // Show 3-Way Grid
            if (this.twoColGrid) this.twoColGrid.style.display = 'none';
            if (this.threeWayGrid) {
                this.threeWayGrid.style.display = 'grid';
                if (this.pyCodeView) this.pyCodeView.textContent = res.python || '# No Python code';
                if (this.javaCodeView) this.javaCodeView.textContent = res.java || '// No Java code';
                if (this.cCodeView) this.cCodeView.textContent = res.c || '// No C code';
            }
        } else {
            // Show Two-Column Grid (Original vs Selected Target)
            if (this.threeWayGrid) this.threeWayGrid.style.display = 'none';
            if (this.twoColGrid) this.twoColGrid.style.display = 'grid';

            if (this.activeLang === 'python') {
                this.targetColTitle.innerHTML = '<i class="fa-brands fa-python"></i> Converted Python 3 Code';
                this.targetColBadge.textContent = 'Python 3';
                this.targetCodeView.textContent = res.python || '# Python conversion pending';
            } else if (this.activeLang === 'java') {
                this.targetColTitle.innerHTML = '<i class="fa-brands fa-java"></i> Converted Java (Main.java)';
                this.targetColBadge.textContent = 'Java 17+';
                this.targetCodeView.textContent = res.java || '// Java conversion pending';
            } else if (this.activeLang === 'c') {
                this.targetColTitle.innerHTML = '<i class="fa-solid fa-c"></i> Converted C Code (C99)';
                this.targetColBadge.textContent = 'C99 Standard';
                this.targetCodeView.textContent = res.c || '// C conversion pending';
            }
        }
    }

    renderDictionary(dictItems) {
        if (!this.dictTbody) return;
        this.dictTbody.innerHTML = '';

        if (!dictItems || dictItems.length === 0) {
            this.dictTbody.innerHTML = '<tr><td colspan="4" class="empty-cell">No variables replaced in this program.</td></tr>';
            if (this.dictCountBadge) this.dictCountBadge.textContent = '0 items';
            return;
        }

        if (this.dictCountBadge) {
            this.dictCountBadge.textContent = `${dictItems.length} items mapped`;
        }

        dictItems.forEach(item => {
            const tr = document.createElement('tr');

            // Malayalam Original
            const tdOrig = document.createElement('td');
            tdOrig.className = 'dict-orig-cell';
            tdOrig.textContent = item.original || '';

            // English Translated
            const tdTrans = document.createElement('td');
            tdTrans.className = 'dict-trans-cell';
            const codeEl = document.createElement('code');
            codeEl.textContent = item.translated || '';
            tdTrans.appendChild(codeEl);

            // Classification Badge
            const tdType = document.createElement('td');
            const badge = document.createElement('span');
            const typeStr = (item.type || 'variable').toLowerCase();
            badge.className = `dict-badge dict-${typeStr}`;
            badge.textContent = item.type || 'variable';
            tdType.appendChild(badge);

            // Role / Educational Context
            const tdRole = document.createElement('td');
            tdRole.className = 'dict-role-cell';
            tdRole.textContent = item.role || 'Program symbol';

            tr.appendChild(tdOrig);
            tr.appendChild(tdTrans);
            tr.appendChild(tdType);
            tr.appendChild(tdRole);

            this.dictTbody.appendChild(tr);
        });
    }

    renderEducationalNotes(notes) {
        if (this.notesPython) {
            this.notesPython.textContent = notes.python_notes || 'Dynamic typing without type keywords; significant indentation for control scope.';
        }
        if (this.notesJava) {
            this.notesJava.textContent = notes.java_notes || 'Requires object-oriented class structure (public class Main), static types, and Scanner for stream input.';
        }
        if (this.notesC) {
            this.notesC.textContent = notes.c_notes || 'Static typed C99 code with #include <stdio.h>, explicit scanf/printf format specifiers (%d), and curly braces {}.';
        }
        if (this.notesSummary) {
            const summary = notes.concept_summary || 'The Malayalam educational language provides an intuitive gateway to programming concepts before stepping into industry languages like Python, Java, and C.';
            this.notesSummary.innerHTML = `<strong>Concept Bridge:</strong> ${summary}`;
        }
    }

    copyActiveCode(btn) {
        if (!this.cachedResult) return;

        let codeToCopy = '';
        if (this.activeLang === 'python') {
            codeToCopy = this.cachedResult.python;
        } else if (this.activeLang === 'java') {
            codeToCopy = this.cachedResult.java;
        } else if (this.activeLang === 'c') {
            codeToCopy = this.cachedResult.c;
        } else {
            codeToCopy = `=== PYTHON 3 ===\n${this.cachedResult.python}\n\n=== JAVA ===\n${this.cachedResult.java}\n\n=== C ===\n${this.cachedResult.c}`;
        }

        if (navigator.clipboard && codeToCopy) {
            navigator.clipboard.writeText(codeToCopy).then(() => {
                const origHtml = btn.innerHTML;
                btn.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
                setTimeout(() => btn.innerHTML = origHtml, 1200);
            });
        }
    }
}

// Export for app initialization
window.EducationalStudio = EducationalStudio;
