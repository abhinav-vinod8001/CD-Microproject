"""
Flask Web Application for Malayalam Educational Compiler Web IDE.
Provides RESTful APIs for compilation, multi-stage pipeline inspection,
bidirectional translation, and sample programs.
"""

import os
from flask import Flask, render_template, request, jsonify
from compiler.pipeline import inspect_pipeline, compile_and_run
from compiler.translator import translate_code
from compiler.groq_converter import convert_code_multilang, GROQ_AVAILABLE

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # Ensure Malayalam Unicode strings are preserved in JSON

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'sample_programs')


def load_samples():
    samples = []
    if os.path.exists(SAMPLES_DIR):
        for fname in sorted(os.listdir(SAMPLES_DIR)):
            if fname.endswith('.mal'):
                filepath = os.path.join(SAMPLES_DIR, fname)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                # Extract first line title
                first_line = content.split('\n')[0].replace('#', '').strip()
                samples.append({
                    "id": fname.replace('.mal', ''),
                    "title": first_line or fname,
                    "filename": fname,
                    "code": content,
                })
    return samples


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/samples', methods=['GET'])
def get_samples():
    return jsonify({"samples": load_samples()})


@app.route('/api/run', methods=['POST'])
def run_code():
    data = request.get_json(force=True, silent=True) or {}
    code = data.get('code', '')
    raw_inputs = data.get('inputs', [])

    if isinstance(raw_inputs, str):
        # Split by newlines or comma
        inputs = [line.strip() for line in raw_inputs.split('\n') if line.strip()]
    else:
        inputs = [str(x).strip() for x in raw_inputs if str(x).strip()]

    result = compile_and_run(code, inputs=inputs)
    return jsonify(result)


@app.route('/api/inspect', methods=['POST'])
def inspect_code():
    data = request.get_json(force=True, silent=True) or {}
    code = data.get('code', '')
    raw_inputs = data.get('inputs', [])

    if isinstance(raw_inputs, str):
        inputs = [line.strip() for line in raw_inputs.split('\n') if line.strip()]
    else:
        inputs = [str(x).strip() for x in raw_inputs if str(x).strip()]

    result = inspect_pipeline(code, inputs=inputs)
    return jsonify(result)


@app.route('/api/translate', methods=['POST'])
def translate():
    data = request.get_json(force=True, silent=True) or {}
    code = data.get('code', '')
    direction = data.get('direction', 'to_english')

    if direction not in ('to_english', 'to_malayalam'):
        return jsonify({"error": "Invalid direction. Must be 'to_english' or 'to_malayalam'"}), 400

    try:
        translated = translate_code(code, direction=direction)
        return jsonify({
            "success": True,
            "direction": direction,
            "translated_code": translated,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


from compiler.groq_converter import convert_code_multilang, GROQ_AVAILABLE, NON_LLAMA_MODELS, DEFAULT_MODEL


@app.route('/api/convert-multilang', methods=['POST'])
def convert_multilang():
    """
    Converts Malayalam code to Python, Java, and C using Groq API
    (or offline educational transpiler if key is missing/unreachable).
    Supports non-Llama models: Qwen 3.8 / QwQ and OpenAI GPT-OSS.
    """
    data = request.get_json(force=True, silent=True) or {}
    code = data.get('code', '')
    api_key = data.get('api_key') or request.headers.get('X-Groq-Api-Key')
    model = data.get('model')

    if not code or not code.strip():
        return jsonify({"success": False, "error": "No Malayalam code provided."}), 400

    result = convert_code_multilang(code, api_key=api_key, model=model)
    return jsonify(result)


@app.route('/api/groq-status', methods=['GET'])
def groq_status():
    """Checks whether Groq API client is available, configured, and returns supported models."""
    has_env_key = bool(os.environ.get('GROQ_API_KEY'))
    if not has_env_key:
        env_path = os.path.join(os.getcwd(), '.env')
        if os.path.exists(env_path):
            try:
                with open(env_path, 'r', encoding='utf-8') as f:
                    has_env_key = 'GROQ_API_KEY' in f.read()
            except Exception:
                pass

    return jsonify({
        "groq_package_available": GROQ_AVAILABLE,
        "has_server_api_key": has_env_key,
        "default_model": DEFAULT_MODEL,
        "available_models": NON_LLAMA_MODELS,
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    app.run(host='0.0.0.0', port=port, debug=True)

