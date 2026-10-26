/**
 * Terminal & Console Output Component for Malayalam Compiler IDE.
 * Native CLI terminal behavior matching standard Python/C programming output.
 * Inline inputs are typed directly into the terminal stream on Enter.
 */

class Terminal {
    constructor() {
        this.bodyEl = document.getElementById('terminal-body');
        this.outputEl = document.getElementById('terminal-output');
        this.statusBadgeEl = document.getElementById('execution-badge');
        this.timeBadgeEl = document.getElementById('exec-time-badge');
        this.stdinDrawerEl = document.getElementById('stdin-drawer');
        this.stdinInputEl = document.getElementById('stdin-input');
        this.btnToggleStdin = document.getElementById('btn-toggle-stdin');
        this.btnClear = document.getElementById('btn-clear-terminal');

        this.init();
    }

    init() {
        if (this.btnToggleStdin) {
            this.btnToggleStdin.addEventListener('click', () => {
                const isOpen = this.stdinDrawerEl.style.display !== 'none';
                this.stdinDrawerEl.style.display = isOpen ? 'none' : 'block';
                if (!isOpen && this.stdinInputEl) {
                    this.stdinInputEl.focus();
                }
            });
        }

        if (this.btnClear) {
            this.btnClear.addEventListener('click', () => this.clear());
        }

        // Clicking anywhere in the terminal console focuses active inline input
        if (this.bodyEl) {
            this.bodyEl.addEventListener('click', () => {
                const activeInput = document.getElementById('terminal-cli-input');
                if (activeInput) {
                    activeInput.focus();
                }
            });
        }
    }

    getStdinValues() {
        if (!this.stdinInputEl) return [];
        const raw = this.stdinInputEl.value.trim();
        if (!raw) return [];
        return raw.split('\n').map(s => s.trim()).filter(Boolean);
    }

    setRunning() {
        this.statusBadgeEl.className = 'badge-status badge-running';
        this.statusBadgeEl.textContent = 'RUNNING';
        this.timeBadgeEl.style.display = 'none';
    }

    setSuccess(timeMs) {
        this.statusBadgeEl.className = 'badge-status badge-success';
        this.statusBadgeEl.textContent = 'SUCCESS';
        this.timeBadgeEl.textContent = `${timeMs} ms`;
        this.timeBadgeEl.style.display = 'inline-block';
    }

    setError(timeMs) {
        this.statusBadgeEl.className = 'badge-status badge-error';
        this.statusBadgeEl.textContent = 'ERROR';
        if (timeMs !== undefined) {
            this.timeBadgeEl.textContent = `${timeMs} ms`;
            this.timeBadgeEl.style.display = 'inline-block';
        }
    }

    setReady() {
        this.statusBadgeEl.className = 'badge-status badge-ready';
        this.statusBadgeEl.textContent = 'READY';
    }

    /**
     * Standard native terminal inline input (like Python input() or C scanf()).
     * No popups, no separate windows, no submit buttons.
     */
    setAwaitingInput(inputRequest, onSubmitCallback) {
        this.setRunning();

        const welcome = document.querySelector('.terminal-welcome');
        if (welcome) welcome.style.display = 'none';

        // Remove any stale inputs
        const oldInput = document.getElementById('terminal-cli-input');
        if (oldInput) oldInput.parentElement?.remove();

        const inputWrapper = document.createElement('span');
        inputWrapper.className = 'cli-inline-wrapper';

        const inputField = document.createElement('input');
        inputField.type = 'text';
        inputField.id = 'terminal-cli-input';
        inputField.className = 'cli-inline-input';
        inputField.autocomplete = 'off';
        inputField.spellcheck = false;

        inputWrapper.appendChild(inputField);
        this.outputEl.appendChild(inputWrapper);

        inputField.focus();

        inputField.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                const val = inputField.value;

                // Replace input element with normal typed terminal text
                inputWrapper.remove();
                this.outputEl.appendChild(document.createTextNode(val + '\n'));

                if (onSubmitCallback) {
                    onSubmitCallback(val);
                }
            }
        });

        if (this.bodyEl) {
            this.bodyEl.scrollTop = this.bodyEl.scrollHeight;
        }
    }

    displayOutput(output) {
        const welcome = document.querySelector('.terminal-welcome');
        if (welcome) welcome.style.display = 'none';

        if (!output || output.trim() === '') {
            this.outputEl.textContent = '';
            return;
        }

        // Display plain terminal text without HTML tags for 100% natural CLI look
        this.outputEl.textContent = output.endsWith('\n') ? output : (output + '\n');
        if (this.bodyEl) {
            this.bodyEl.scrollTop = this.bodyEl.scrollHeight;
        }
    }

    displayError(errorObj) {
        const welcome = document.querySelector('.terminal-welcome');
        if (welcome) welcome.style.display = 'none';

        const stage = errorObj.error_stage || 'Compiler Error';
        const msg = errorObj.error || 'Unknown error occurred.';
        const line = errorObj.line ? ` [Line ${errorObj.line}]` : '';

        this.outputEl.innerHTML = `
            <div class="term-error">
                <strong><i class="fa-solid fa-circle-exclamation"></i> ${this.escapeHtml(stage)}${line}:</strong>
                <p style="margin-top: 4px;">${this.escapeHtml(msg)}</p>
            </div>
        `;
    }

    clear() {
        this.outputEl.innerHTML = '';
        this.setReady();
        const welcome = document.querySelector('.terminal-welcome');
        if (welcome) welcome.style.display = 'block';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
