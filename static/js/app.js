/**
 * Main Web IDE Controller for Malayalam Online Compiler.
 * Manages Editor, Terminal, Inspector, Quick Ribbons, Translation,
 * and Theme (Light/Dark mode).
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Components
    const editor = new CodeEditor('code-editor', 'editor-gutter');
    const terminal = new Terminal();
    const inspector = new CompilerInspector();
    const educationalStudio = new EducationalStudio(editor);

    // Default code matching standard compiler start
    const DEFAULT_CODE = `# മലയാളം പ്രോഗ്രാം (Malayalam Program)
x = 10
y = 20
z = x + y
കാണിക്കുക z
`;

    editor.setValue(DEFAULT_CODE);

    // 2. Theme Toggle (Dark / Light Mode)
    initTheme();

    // 3. Load Samples from Backend
    fetchSamples();

    // 4. Quick Keyword Insertion Toolbar
    document.querySelectorAll('.kw-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const textToInsert = btn.getAttribute('data-insert');
            if (textToInsert) {
                editor.insertAtCursor(textToInsert);
            }
        });
    });

    // 5. Run Button & Execution
    const btnRun = document.getElementById('btn-run');
    if (btnRun) {
        btnRun.addEventListener('click', () => executeCode(false));
    }

    // 6. Show Compiler Stages Button
    const btnInspect = document.getElementById('btn-toggle-inspector');
    if (btnInspect) {
        btnInspect.addEventListener('click', () => {
            executeCode(true);
        });
    }

    // 7. Translation Buttons
    const btnTransEng = document.getElementById('btn-translate-eng');
    const btnTransMal = document.getElementById('btn-translate-mal');

    if (btnTransEng) {
        btnTransEng.addEventListener('click', () => translateCode('to_english'));
    }

    if (btnTransMal) {
        btnTransMal.addEventListener('click', () => translateCode('to_malayalam'));
    }

    // 8. Editor Control Buttons
    const btnCopy = document.getElementById('btn-copy-code');
    if (btnCopy) {
        btnCopy.addEventListener('click', () => {
            if (navigator.clipboard) {
                navigator.clipboard.writeText(editor.getValue()).then(() => {
                    const orig = btnCopy.innerHTML;
                    btnCopy.innerHTML = '<i class="fa-solid fa-check"></i>';
                    setTimeout(() => btnCopy.innerHTML = orig, 1200);
                });
            }
        });
    }

    const btnClear = document.getElementById('btn-clear-code');
    if (btnClear) {
        btnClear.addEventListener('click', () => {
            editor.setValue('');
        });
    }

    const btnReset = document.getElementById('btn-reset-code');
    if (btnReset) {
        btnReset.addEventListener('click', () => {
            editor.setValue(DEFAULT_CODE);
        });
    }

    // 9. Global Keyboard Shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl+Enter or Cmd+Enter -> Run
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            executeCode(false);
            return;
        }

        // Ctrl+Shift+E -> Translate to English
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === 'E' || e.key === 'e')) {
            e.preventDefault();
            translateCode('to_english');
            return;
        }

        // Ctrl+Shift+M -> Translate to Malayalam
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && (e.key === 'M' || e.key === 'm')) {
            e.preventDefault();
            translateCode('to_malayalam');
            return;
        }
    });

    // 10. Resizable Split Panes
    setupPaneResizer();

    // -------------------------------------------------------------
    // Helper Functions
    // -------------------------------------------------------------

    function initTheme() {
        const toggleBtn = document.getElementById('btn-theme-toggle');
        const themeIcon = document.getElementById('theme-icon');
        const themeText = document.getElementById('theme-text');

        // Check stored theme or default to dark
        const savedTheme = localStorage.getItem('ide_theme') || 'dark';
        applyTheme(savedTheme);

        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                const current = document.documentElement.getAttribute('data-theme') || 'dark';
                const nextTheme = current === 'dark' ? 'light' : 'dark';
                applyTheme(nextTheme);
                localStorage.setItem('ide_theme', nextTheme);
            });
        }

        function applyTheme(theme) {
            document.documentElement.setAttribute('data-theme', theme);
            if (theme === 'light') {
                if (themeIcon) themeIcon.className = 'fa-solid fa-sun';
                if (themeText) themeText.textContent = 'Light';
            } else {
                if (themeIcon) themeIcon.className = 'fa-solid fa-moon';
                if (themeText) themeText.textContent = 'Dark';
            }
        }
    }

    let activeInputs = [];

    async function executeCode(focusInspector = false, customInputs = null) {
        const code = editor.getValue();
        if (!code || !code.trim()) {
            terminal.displayError({
                error_stage: 'Input Validation',
                error: 'Editor is empty. Please enter code to run.',
            });
            return;
        }

        if (customInputs === null) {
            // Fresh run: start with any pre-filled stdin lines if provided
            activeInputs = [...terminal.getStdinValues()];
        } else {
            activeInputs = customInputs;
        }

        terminal.setRunning();

        try {
            const resp = await fetch('/api/inspect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code, inputs: activeInputs }),
            });

            const data = await resp.json();

            // Check if program is waiting for user input
            if (data.needs_input) {
                const outSoFar = data.stages?.stage_8_execution?.output || '';
                terminal.displayOutput(outSoFar);

                if (data.stages) {
                    inspector.render(data.stages);
                }

                // Prompt user live inline in the terminal
                terminal.setAwaitingInput(data.input_request, (enteredVal) => {
                    activeInputs.push(enteredVal);
                    executeCode(focusInspector, activeInputs);
                });
                return;
            }

            if (data.success) {
                terminal.setSuccess(data.execution_time_ms);
                const outText = data.stages?.stage_8_execution?.output || '';
                terminal.displayOutput(outText);

                // Render all 8 compiler stages
                if (data.stages) {
                    inspector.render(data.stages);
                }

                if (focusInspector) {
                    const inspectorCard = document.getElementById('inspector-card');
                    if (inspectorCard) {
                        inspectorCard.scrollIntoView({ behavior: 'smooth' });
                    }
                }
            } else {
                terminal.setError(data.execution_time_ms);
                terminal.displayError(data);

                // Still render partial stages if available before error
                if (data.stages) {
                    inspector.render(data.stages);
                }
            }
        } catch (err) {
            terminal.setError();
            terminal.displayError({
                error_stage: 'Server Error',
                error: err.message || 'Failed to communicate with compiler backend.',
            });
        }
    }

    async function translateCode(direction) {
        const code = editor.getValue();
        if (!code || !code.trim()) return;

        try {
            const resp = await fetch('/api/translate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code, direction }),
            });

            const data = await resp.json();
            if (data.success && data.translated_code) {
                editor.setValue(data.translated_code);

                const targetBtn = direction === 'to_english' ? btnTransEng : btnTransMal;
                if (targetBtn) {
                    const origHtml = targetBtn.innerHTML;
                    targetBtn.innerHTML = '<i class="fa-solid fa-check"></i> Translated';
                    setTimeout(() => targetBtn.innerHTML = origHtml, 1200);
                }
            }
        } catch (err) {
            console.error('Translation error:', err);
        }
    }

    async function fetchSamples() {
        const select = document.getElementById('sample-select');
        if (!select) return;

        try {
            const resp = await fetch('/api/samples');
            const data = await resp.json();
            if (data.samples && data.samples.length > 0) {
                data.samples.forEach(s => {
                    const opt = document.createElement('option');
                    opt.value = s.id;
                    opt.textContent = s.title;
                    opt.dataset.code = s.code;
                    select.appendChild(opt);
                });

                select.addEventListener('change', () => {
                    const selected = select.options[select.selectedIndex];
                    if (selected && selected.dataset.code) {
                        editor.setValue(selected.dataset.code);
                        executeCode(false);
                    }
                });
            }
        } catch (err) {
            console.warn('Could not load sample programs:', err);
        }
    }

    function setupPaneResizer() {
        const resizer = document.getElementById('pane-resizer');
        const editorPane = document.getElementById('pane-editor');
        const container = document.getElementById('ide-workspace');

        if (!resizer || !editorPane || !container) return;

        let isDragging = false;

        resizer.addEventListener('mousedown', () => {
            isDragging = true;
            resizer.classList.add('resizing');
            document.body.style.cursor = 'col-resize';
            document.body.style.userSelect = 'none';
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            const containerRect = container.getBoundingClientRect();
            const offset = e.clientX - containerRect.left;
            const percentage = (offset / containerRect.width) * 100;

            if (percentage > 20 && percentage < 80) {
                editorPane.style.flex = `0 0 ${percentage}%`;
            }
        });

        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                resizer.classList.remove('resizing');
                document.body.style.cursor = '';
                document.body.style.userSelect = '';
            }
        });
    }
});
