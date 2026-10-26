/**
 * Compiler Process Inspector Component.
 * Clean, standard tabbed inspector for 8 compiler stages.
 */

class CompilerInspector {
    constructor() {
        this.tabBtns = document.querySelectorAll('.stage-tab');
        this.tabPanes = document.querySelectorAll('.stage-pane');
        this.currentStageData = null;
        this.astViewMode = 'visual';

        this.init();
    }

    init() {
        // Tab switching
        this.tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const targetId = btn.getAttribute('data-tab');
                this.setActiveTab(targetId);
            });
        });

        // AST view toggles
        const btnVisual = document.getElementById('btn-ast-visual');
        const btnText = document.getElementById('btn-ast-text');
        const btnJson = document.getElementById('btn-ast-json');

        if (btnVisual && btnText && btnJson) {
            btnVisual.addEventListener('click', () => this.setAstView('visual'));
            btnText.addEventListener('click', () => this.setAstView('text'));
            btnJson.addEventListener('click', () => this.setAstView('json'));
        }

        // Copy current stage output
        const btnCopyStage = document.getElementById('btn-copy-stage');
        if (btnCopyStage) {
            btnCopyStage.addEventListener('click', () => this.copyActiveStageContent());
        }
    }

    setActiveTab(tabId) {
        this.tabBtns.forEach(btn => {
            const isMatch = btn.getAttribute('data-tab') === tabId;
            btn.classList.toggle('active', isMatch);
        });

        this.tabPanes.forEach(pane => {
            pane.classList.toggle('active', pane.id === tabId);
        });
    }

    setAstView(mode) {
        this.astViewMode = mode;
        const visual = document.getElementById('ast-visual-view');
        const text = document.getElementById('ast-text-view');
        const json = document.getElementById('ast-json-view');

        const btnVisual = document.getElementById('btn-ast-visual');
        const btnText = document.getElementById('btn-ast-text');
        const btnJson = document.getElementById('btn-ast-json');

        [btnVisual, btnText, btnJson].forEach(b => b.classList.remove('active'));

        visual.style.display = mode === 'visual' ? 'block' : 'none';
        text.style.display = mode === 'text' ? 'block' : 'none';
        json.style.display = mode === 'json' ? 'block' : 'none';

        if (mode === 'visual') btnVisual.classList.add('active');
        if (mode === 'text') btnText.classList.add('active');
        if (mode === 'json') btnJson.classList.add('active');
    }

    render(stages) {
        this.currentStageData = stages;

        // Stage 1: Tokens
        if (stages.stage_1_tokens) {
            this.renderTokens(stages.stage_1_tokens);
        }

        // Stage 2: Parse Tree
        if (stages.stage_2_parse_tree) {
            document.getElementById('parse-tree-text').textContent = stages.stage_2_parse_tree.text || '';
        }

        // Stage 3: AST
        if (stages.stage_3_ast) {
            this.renderAST(stages.stage_3_ast);
        }

        // Stage 4: Symbol Table & Diagnostics
        if (stages.stage_4_semantic) {
            this.renderSemantic(stages.stage_4_semantic);
        }

        // Stage 5: TAC
        if (stages.stage_5_tac) {
            document.getElementById('tac-code-view').textContent = stages.stage_5_tac.text || '';
        }

        // Stage 6: Optimization
        if (stages.stage_6_optimized) {
            this.renderOptimization(stages.stage_5_tac, stages.stage_6_optimized);
        }

        // Stage 7: Target Code
        if (stages.stage_7_target_code) {
            document.getElementById('target-assembly-view').textContent = stages.stage_7_target_code.text || '';
        }

        // Stage 8: VM Execution
        if (stages.stage_8_execution) {
            this.renderVM(stages.stage_8_execution);
        }
    }

    renderTokens(tokenData) {
        const tbody = document.getElementById('tokens-tbody');
        const countBadge = document.getElementById('token-count-badge');
        countBadge.textContent = `${tokenData.count} tokens`;

        if (!tokenData.tokens || tokenData.tokens.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="empty-cell">No tokens found.</td></tr>';
            return;
        }

        let html = '';
        tokenData.tokens.forEach((t, i) => {
            html += `
                <tr>
                    <td style="color: var(--text-muted);">${i + 1}</td>
                    <td><code>${t.type}</code></td>
                    <td style="font-family:'Fira Code', monospace;">${this.escapeHtml(t.value)}</td>
                    <td style="color: var(--text-muted); font-size: 11px;">L${t.line}:C${t.column}</td>
                </tr>
            `;
        });
        tbody.innerHTML = html;
    }

    renderAST(astData) {
        document.getElementById('ast-text-view').textContent = astData.text || '';
        document.getElementById('ast-json-view').textContent = JSON.stringify(astData.ast_dict, null, 2);

        const visualContainer = document.getElementById('ast-visual-view');
        visualContainer.innerHTML = '';
        if (astData.ast_dict) {
            const treeEl = this.createAstNodeElement(astData.ast_dict);
            visualContainer.appendChild(treeEl);
        } else {
            visualContainer.innerHTML = '<div class="empty-cell">No AST available</div>';
        }
    }

    createAstNodeElement(node) {
        const wrapper = document.createElement('div');
        wrapper.className = 'ast-node';

        const card = document.createElement('div');
        card.className = 'ast-node-card';

        const badge = document.createElement('span');
        badge.className = 'ast-badge';
        badge.textContent = node.type || 'Node';

        const title = document.createElement('span');
        title.className = 'ast-title';
        title.textContent = node.name || node.type || '';

        card.appendChild(badge);
        card.appendChild(title);
        wrapper.appendChild(card);

        if (node.children && node.children.length > 0) {
            const childrenContainer = document.createElement('div');
            childrenContainer.className = 'ast-children';
            node.children.forEach(child => {
                childrenContainer.appendChild(this.createAstNodeElement(child));
            });
            wrapper.appendChild(childrenContainer);

            card.addEventListener('click', (e) => {
                e.stopPropagation();
                const isHidden = childrenContainer.style.display === 'none';
                childrenContainer.style.display = isHidden ? 'block' : 'none';
                card.style.opacity = isHidden ? '1' : '0.6';
            });
        }

        return wrapper;
    }

    renderSemantic(semanticData) {
        const tbody = document.getElementById('symbols-tbody');
        const diagBox = document.getElementById('diagnostics-box');
        const diagList = document.getElementById('diagnostics-list');

        if (semanticData.diagnostics && semanticData.diagnostics.length > 0) {
            diagBox.style.display = 'block';
            let dHtml = '';
            semanticData.diagnostics.forEach(d => {
                const icon = d.severity === 'error' ? 'fa-circle-xmark' : 'fa-triangle-exclamation';
                dHtml += `<li><i class="fa-solid ${icon}"></i> Line ${d.line}: ${this.escapeHtml(d.message)}</li>`;
            });
            diagList.innerHTML = dHtml;
        } else {
            diagBox.style.display = 'none';
        }

        if (!semanticData.symbol_table || semanticData.symbol_table.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="empty-cell">No variables declared.</td></tr>';
            return;
        }

        let html = '';
        semanticData.symbol_table.forEach(s => {
            const refs = s.references && s.references.length > 0 ? s.references.map(r => `L${r}`).join(', ') : 'none';
            html += `
                <tr>
                    <td><strong>${this.escapeHtml(s.name)}</strong></td>
                    <td><code>${s.type}</code></td>
                    <td>${s.scope}</td>
                    <td>Line ${s.line_defined}</td>
                    <td style="color:var(--text-muted); font-size:11px;">${refs}</td>
                </tr>
            `;
        });
        tbody.innerHTML = html;
    }

    renderOptimization(tacData, optData) {
        document.getElementById('opt-orig-tac').textContent = tacData ? tacData.text : '';
        document.getElementById('opt-final-tac').textContent = optData.text || '';

        const logsList = document.getElementById('opt-logs-list');
        if (optData.optimization_logs && optData.optimization_logs.length > 0) {
            let html = '';
            optData.optimization_logs.forEach(log => {
                html += `<li>• ${this.escapeHtml(log)}</li>`;
            });
            logsList.innerHTML = html;
        } else {
            logsList.innerHTML = '<li><span style="color:var(--text-muted);">(No constant folding or optimizations applicable)</span></li>';
        }
    }

    renderVM(vmData) {
        const envContainer = document.getElementById('vm-env-vars');
        if (vmData.environment && Object.keys(vmData.environment).length > 0) {
            let html = '';
            for (const [k, v] of Object.entries(vmData.environment)) {
                html += `
                    <div class="env-chip">
                        <span class="env-chip-name">${this.escapeHtml(k)}</span>
                        <span>=</span>
                        <span>${this.escapeHtml(String(v))}</span>
                    </div>
                `;
            }
            envContainer.innerHTML = html;
        } else {
            envContainer.innerHTML = '<span class="empty-cell">No variables active in memory</span>';
        }

        const traceView = document.getElementById('vm-trace-view');
        if (vmData.trace && vmData.trace.length > 0) {
            traceView.textContent = `Completed in ${vmData.steps} steps:\n` + vmData.trace.join('\n');
        } else {
            traceView.textContent = '(No steps executed)';
        }
    }

    copyActiveStageContent() {
        const activePane = document.querySelector('.stage-pane.active');
        if (!activePane) return;

        let textToCopy = '';
        const rawCode = activePane.querySelector('.raw-code-box');
        if (rawCode && rawCode.style.display !== 'none') {
            textToCopy = rawCode.textContent;
        } else {
            textToCopy = activePane.innerText;
        }

        if (navigator.clipboard) {
            navigator.clipboard.writeText(textToCopy).then(() => {
                const btn = document.getElementById('btn-copy-stage');
                if (btn) {
                    const orig = btn.innerHTML;
                    btn.innerHTML = '<i class="fa-solid fa-check"></i>';
                    setTimeout(() => btn.innerHTML = orig, 1200);
                }
            });
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
