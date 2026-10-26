/**
 * Code Editor Component for Malayalam Educational Compiler IDE.
 * Manages line numbers, cursor position tracking, Tab key indentation,
 * auto-closing pairs, and cursor-targeted keyword insertions.
 */

class CodeEditor {
    constructor(textareaId, gutterId) {
        this.textarea = document.getElementById(textareaId);
        this.gutter = document.getElementById(gutterId);
        this.cursorPosEl = document.getElementById('cursor-pos');
        this.charCountEl = document.getElementById('char-count');
        this.lineCountEl = document.getElementById('line-count');
        this.langIndicatorEl = document.getElementById('lang-indicator');

        this.init();
    }

    init() {
        if (!this.textarea || !this.gutter) return;

        // Sync line numbers on input and scroll
        this.textarea.addEventListener('input', () => {
            this.updateLineNumbers();
            this.updateStatusBar();
        });

        this.textarea.addEventListener('scroll', () => {
            this.gutter.scrollTop = this.textarea.scrollTop;
        });

        // Track cursor position
        ['keyup', 'click', 'focus', 'select'].forEach(evt => {
            this.textarea.addEventListener(evt, () => this.updateStatusBar());
        });

        // Keybindings in editor
        this.textarea.addEventListener('keydown', (e) => this.handleKeyDown(e));

        // Initial render
        this.updateLineNumbers();
        this.updateStatusBar();
    }

    getValue() {
        return this.textarea.value;
    }

    setValue(text) {
        this.textarea.value = text;
        this.updateLineNumbers();
        this.updateStatusBar();
    }

    updateLineNumbers() {
        const lines = this.textarea.value.split('\n');
        const count = Math.max(lines.length, 1);
        let gutterHtml = '';
        for (let i = 1; i <= count; i++) {
            gutterHtml += `<div class="line-number">${i}</div>`;
        }
        this.gutter.innerHTML = gutterHtml;
    }

    updateStatusBar() {
        const val = this.textarea.value;
        const selStart = this.textarea.selectionStart || 0;
        const textBefore = val.substring(0, selStart);
        const lines = textBefore.split('\n');
        const currentLine = lines.length;
        const currentCol = lines[lines.length - 1].length + 1;

        if (this.cursorPosEl) this.cursorPosEl.textContent = `Ln ${currentLine}, Col ${currentCol}`;
        if (this.charCountEl) this.charCountEl.textContent = `${val.length} chars`;
        if (this.lineCountEl) this.lineCountEl.textContent = `${val.split('\n').length} lines`;

        // Check if code contains Malayalam characters (\u0D00-\u0D7F)
        const hasMalayalam = /[\u0D00-\u0D7F]/.test(val);
        if (this.langIndicatorEl) {
            this.langIndicatorEl.textContent = hasMalayalam ? 'Malayalam' : 'English';
        }
    }

    handleKeyDown(e) {
        // Tab key: Insert 4 spaces
        if (e.key === 'Tab') {
            e.preventDefault();
            const start = this.textarea.selectionStart;
            const end = this.textarea.selectionEnd;
            const val = this.textarea.value;
            const tabSpaces = '    ';

            this.textarea.value = val.substring(0, start) + tabSpaces + val.substring(end);
            this.textarea.selectionStart = this.textarea.selectionEnd = start + 4;
            this.updateLineNumbers();
            this.updateStatusBar();
            return;
        }

        // Auto-close quotes and brackets
        const pairs = {
            '(': ')',
            '"': '"',
            "'": "'",
        };

        if (pairs[e.key]) {
            const start = this.textarea.selectionStart;
            const end = this.textarea.selectionEnd;
            const val = this.textarea.value;

            // If text is selected, wrap it
            if (start !== end) {
                e.preventDefault();
                const selected = val.substring(start, end);
                const replacement = e.key + selected + pairs[e.key];
                this.textarea.value = val.substring(0, start) + replacement + val.substring(end);
                this.textarea.selectionStart = start + 1;
                this.textarea.selectionEnd = end + 1;
                this.updateStatusBar();
                return;
            }
        }
    }

    insertAtCursor(text) {
        const start = this.textarea.selectionStart;
        const end = this.textarea.selectionEnd;
        const val = this.textarea.value;

        this.textarea.value = val.substring(0, start) + text + val.substring(end);
        this.textarea.focus();
        this.textarea.selectionStart = this.textarea.selectionEnd = start + text.length;

        this.updateLineNumbers();
        this.updateStatusBar();
    }
}
