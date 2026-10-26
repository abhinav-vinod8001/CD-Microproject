"""
Groq API Code Converter & Educational Multi-Language Transpiler.
Translates educational Malayalam code into Python, Java, and C,
translating keywords, variable names, and producing educational insights
and replacement dictionaries.
"""

import os
import re
import json
from typing import Dict, Any, List, Optional
from .tokens import MALAYALAM_KEYWORDS, TokenType

# Optional Groq client import
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


# Comprehensive Malayalam to English vocabulary dictionary for variables & terms
MALAYALAM_VAR_VOCAB: Dict[str, str] = {
    "തുക": "sum",
    "സംഖ്യ": "num",
    "സംഖ്യ1": "num1",
    "സംഖ്യ2": "num2",
    "സംഖ്യകൾ": "numbers",
    "ഘടകം": "factorial",
    "എണ്ണം": "count",
    "ആകെ": "total",
    "ഫലം": "result",
    "പേര്": "name",
    "വയസ്സ്": "age",
    "ഗുണനഫലം": "product",
    "ശിഷ്ടം": "remainder",
    "ഹരണഫലം": "quotient",
    "വില": "value",
    "പദം": "term",
    "അടുത്തത്": "next_val",
    "പഴയത്": "prev_val",
    "സൂചിക": "index",
    "വലുത്": "max_val",
    "ചെറുത്": "min_val",
    "ശരാശരി": "average",
    "ശരി": "true",
    "തെറ്റ്": "false",
}


def romanize_malayalam(text: str) -> str:
    """Fallback phonetics converter for Malayalam identifiers not in dictionary."""
    char_map = {
        'അ': 'a', 'ആ': 'aa', 'ഇ': 'i', 'ഈ': 'ee', 'ഉ': 'u', 'ഊ': 'oo',
        'ഋ': 'ri', 'എ': 'e', 'ഏ': 'ae', 'ഐ': 'ai', 'ഒ': 'o', 'ഓ': 'oa', 'ഔ': 'au',
        'ക': 'k', 'ഖ': 'kh', 'ഗ': 'g', 'ഘ': 'gh', 'ങ': 'ng',
        'ച': 'ch', 'ഛ': 'chh', 'ജ': 'j', 'ഝ': 'jh', 'ഞ': 'nj',
        'ട': 't', 'ഠ': 'th', 'ഡ': 'd', 'ഢ': 'dh', 'ണ': 'n',
        'ത': 'th', 'ഥ': 'thh', 'ദ': 'd', 'ധ': 'dh', 'ന': 'n',
        'പ': 'p', 'ഫ': 'f', 'ബ': 'b', 'ഭ': 'bh', 'മ': 'm',
        'യ': 'y', 'ര': 'r', 'ല': 'l', 'വ': 'v', 'ശ': 'sh', 'ഷ': 'sh', 'സ': 's', 'ഹ': 'h',
        'ള': 'l', 'ഴ': 'zh', 'റ': 'r',
        'ാ': 'aa', 'ി': 'i', 'ീ': 'ee', 'ു': 'u', 'ൂ': 'oo', 'ൃ': 'ri',
        'െ': 'e', 'േ': 'ae', 'ൈ': 'ai', 'ൊ': 'o', 'ോ': 'oa', 'ൌ': 'au',
        '്': '', 'ം': 'm', 'ഃ': 'h'
    }
    result = []
    for ch in text:
        result.append(char_map.get(ch, ch if re.match(r'[a-zA-Z0-9_]', ch) else ''))
    clean = "".join(result).strip('_')
    return clean if clean else "var"


def extract_malayalam_identifiers(code: str) -> List[str]:
    """Extracts unique Malayalam identifiers from source code, ignoring comments and strings."""
    # Strip comments and string literals
    cleaned_lines = []
    for line in code.split('\n'):
        # Strip comments
        if '#' in line:
            line = line.split('#', 1)[0]
        if '//' in line:
            line = line.split('//', 1)[0]
        # Strip strings
        line = re.sub(r'\"(?:[^\"\\]|\\.)*\"|\'(?:[^\'\\]|\\.)*\'', '', line)
        cleaned_lines.append(line)

    cleaned_code = "\n".join(cleaned_lines)
    malayalam_regex = re.compile(r'[\u0D00-\u0D7F\u200C\u200D]+')
    words = malayalam_regex.findall(cleaned_code)
    # Filter out Malayalam keywords
    idents = []
    for w in words:
        if w not in MALAYALAM_KEYWORDS and w not in idents:
            idents.append(w)
    return idents


def offline_transpile(code: str) -> Dict[str, Any]:
    """
    High-quality offline educational transpiler when Groq API key is not present.
    Generates Python, Java, and C versions, with variable replacement dictionary
    and educational notes.
    """
    # 1. Identify and translate Malayalam variables
    raw_idents = extract_malayalam_identifiers(code)
    var_map: Dict[str, str] = {}
    used_names = set()

    for ident in raw_idents:
        if ident in MALAYALAM_VAR_VOCAB:
            eng = MALAYALAM_VAR_VOCAB[ident]
        else:
            eng = romanize_malayalam(ident)
        # Avoid collision
        candidate = eng
        counter = 1
        while candidate in used_names:
            candidate = f"{eng}_{counter}"
            counter += 1
        used_names.add(candidate)
        var_map[ident] = candidate

    # 2. Build dictionary table items
    dictionary = []
    # Add keywords with Malayalam educational explanations
    kw_info = [
        ("കാണിക്കുക", "print / printf / println", "കീവേഡ് (Keyword)", "കൺസോളിൽ ഔട്ട്പുട്ട് പ്രിന്റ് ചെയ്യാൻ ഉപയോഗിക്കുന്നു (Python-ൽ print, C-ൽ printf, Java-ൽ println)."),
        ("വായിക്കുക", "input / scanf / Scanner", "കീവേഡ് (Keyword)", "ഉപയോക്താവിൽ നിന്നും ഇൻപുട്ട് സ്വീകരിക്കാൻ ഉപയോഗിക്കുന്നു (Python-ൽ input, C-ൽ scanf, Java-ൽ Scanner)."),
        ("എങ്കിൽ", "if", "കീവേഡ് (Keyword)", "വ്യവസ്ഥ ശരിയാണോ എന്ന് പരിശോധിക്കുന്നതിനുള്ള കണ്ടീഷണൽ സ്റ്റേറ്റ്മെന്റ് (if)."),
        ("അല്ലെങ്കിൽ", "else", "കീവേഡ് (Keyword)", "വ്യവസ്ഥ തെറ്റായാൽ പ്രവർത്തിക്കുന്ന ബദൽ ബ്രാഞ്ച് (else)."),
        ("ആവർത്തിക്കുക", "while", "കീവേഡ് (Keyword)", "ഒരു വ്യവസ്ഥ ശരിയായിരിക്കുന്നിടത്തോളം ആവർത്തിച്ച് പ്രവർത്തിക്കുന്ന ലൂപ്പ് (while loop)."),
        ("അവസാനിപ്പിക്കുക", "end / } / indentation", "കീവേഡ് (Keyword)", "കോഡ് ബ്ലോക്ക് അല്ലെങ്കിൽ ലൂപ്പ് അവസാനിപ്പിക്കുന്നു (C/Java-ൽ {}, Python-ൽ indentation)."),
        ("ശരി", "True / true / 1", "ലിറ്ററൽ (Literal)", "ബൂളിയൻ സത്യം അഥവാ ശരിയായ അവസ്ഥയെ സൂചിപ്പിക്കുന്നു."),
        ("തെറ്റ്", "False / false / 0", "ലിറ്ററൽ (Literal)", "ബൂളിയൻ അസത്യം അഥവാ തെറ്റായ അവസ്ഥയെ സൂചിപ്പിക്കുന്നു."),
        ("ഒപ്പം", "and / &&", "ഓപ്പറേറ്റർ (Operator)", "രണ്ട് വ്യവസ്ഥകളും ഒരേസമയം ശരിയാകണമെന്ന് നിഷ്കർഷിക്കുന്ന ലോജിക്കൽ AND."),
        ("അഥവാ", "or / ||", "ഓപ്പറേറ്റർ (Operator)", "ഏതെങ്കിലും ഒരു വ്യവസ്ഥ ശരിയായാൽ മതിയെന്ന ലോജിക്കൽ OR."),
        ("അല്ല", "not / !", "ഓപ്പറേറ്റർ (Operator)", "വ്യവസ്ഥയുടെ ഫലത്തെ വിപരീതമാക്കുന്ന ലോജിക്കൽ NOT."),
    ]
    for orig, trans, ktype, role in kw_info:
        if orig in code:
            dictionary.append({
                "original": orig,
                "translated": trans,
                "type": ktype,
                "role": role,
            })

    for mal_var, eng_var in var_map.items():
        dictionary.append({
            "original": mal_var,
            "translated": eng_var,
            "type": "വേരിയബിൾ (Variable)",
            "role": f"മലയാളത്തിലെ '{mal_var}' എന്ന വേരിയബിളിനെ അന്താരാഷ്ട്ര പ്രോഗ്രാമിംഗ് രീതിയിൽ '{eng_var}' എന്ന് മാറ്റിയിരിക്കുന്നു.",
        })

    # 3. Line by line parsing for Python, Java, C
    py_lines = []
    java_body = []
    c_body = []

    has_input = False
    declared_vars_c = set()
    declared_vars_java = set()

    lines = code.split('\n')
    indent_level = 0

    for line in lines:
        stripped = line.strip()
        leading_spaces = len(line) - len(line.lstrip())
        indent_str = "    " * (leading_spaces // 4)

        if not stripped:
            py_lines.append("")
            java_body.append("")
            c_body.append("")
            continue

        if stripped.startswith('#') or stripped.startswith('//'):
            cmt = stripped.lstrip('#/ ').strip()
            # Replace variables inside comment if needed
            for m, e in var_map.items():
                cmt = cmt.replace(m, e)
            py_lines.append(f"{indent_str}# {cmt}")
            java_body.append(f"{indent_str}// {cmt}")
            c_body.append(f"{indent_str}// {cmt}")
            continue

        # Handle 'അവസാനിപ്പിക്കുക' (end)
        if stripped == "അവസാനിപ്പിക്കുക":
            if indent_level > 0:
                indent_level -= 1
            cur_indent = "    " * indent_level
            # In Python, end is just closing indentation (no token needed)
            java_body.append(f"{cur_indent}}}")
            c_body.append(f"{cur_indent}}}")
            continue

        # Handle 'അല്ലെങ്കിൽ' (else)
        if stripped == "അല്ലെങ്കിൽ":
            cur_indent = "    " * max(0, indent_level - 1)
            py_lines.append(f"{cur_indent}else:")
            java_body.append(f"{cur_indent}}} else {{")
            c_body.append(f"{cur_indent}}} else {{")
            continue

        # Handle 'എങ്കിൽ' (if)
        if stripped.startswith("എങ്കിൽ "):
            cond = stripped[len("എങ്കിൽ "):].strip()
            # Replace operators & vars
            for m, e in var_map.items():
                cond = cond.replace(m, e)
            cond = cond.replace("ശരി", "True").replace("തെറ്റ്", "False")
            cond_py = cond.replace("ഒപ്പം", "and").replace("അഥവാ", "or").replace("അല്ല ", "not ")
            cond_c = cond.replace("ഒപ്പം", "&&").replace("അഥവാ", "||").replace("അല്ല ", "!")

            cur_indent = "    " * indent_level
            py_lines.append(f"{cur_indent}if {cond_py}:")
            java_body.append(f"{cur_indent}if ({cond_c}) {{")
            c_body.append(f"{cur_indent}if ({cond_c}) {{")
            indent_level += 1
            continue

        # Handle 'ആവർത്തിക്കുക' (while)
        if stripped.startswith("ആവർത്തിക്കുക "):
            cond = stripped[len("ആവർത്തിക്കുക "):].strip()
            for m, e in var_map.items():
                cond = cond.replace(m, e)
            cond = cond.replace("ശരി", "True").replace("തെറ്റ്", "False")
            cond_py = cond.replace("ഒപ്പം", "and").replace("അഥവാ", "or").replace("അല്ല ", "not ")
            cond_c = cond.replace("ഒപ്പം", "&&").replace("അഥവാ", "||").replace("അല്ല ", "!")

            cur_indent = "    " * indent_level
            py_lines.append(f"{cur_indent}while {cond_py}:")
            java_body.append(f"{cur_indent}while ({cond_c}) {{")
            c_body.append(f"{cur_indent}while ({cond_c}) {{")
            indent_level += 1
            continue

        # Handle 'വായിക്കുക' (input)
        if stripped.startswith("വായിക്കുക "):
            has_input = True
            var_name = stripped[len("വായിക്കുക "):].strip()
            eng_var = var_map.get(var_name, var_name)

            cur_indent = "    " * indent_level
            py_lines.append(f"{cur_indent}{eng_var} = int(input())")

            if eng_var not in declared_vars_java:
                java_body.append(f"{cur_indent}int {eng_var} = scanner.nextInt();")
                declared_vars_java.add(eng_var)
            else:
                java_body.append(f"{cur_indent}{eng_var} = scanner.nextInt();")

            if eng_var not in declared_vars_c:
                c_body.append(f"{cur_indent}int {eng_var};")
                c_body.append(f"{cur_indent}scanf(\"%d\", &{eng_var});")
                declared_vars_c.add(eng_var)
            else:
                c_body.append(f"{cur_indent}scanf(\"%d\", &{eng_var});")
            continue

        # Handle 'കാണിക്കുക' (print)
        if stripped.startswith("കാണിക്കുക"):
            expr = stripped[len("കാണിക്കുക"):].strip()
            for m, e in var_map.items():
                expr = expr.replace(m, e)

            cur_indent = "    " * indent_level
            py_lines.append(f"{cur_indent}print({expr})")
            java_body.append(f"{cur_indent}System.out.println({expr});")

            # Simple C printf formatting heuristic
            if expr.startswith('"') and expr.endswith('"'):
                c_body.append(f'{cur_indent}printf({expr});\n{cur_indent}printf("\\n");')
            elif '+' in expr and '"' in expr:
                # String concatenation
                c_body.append(f'{cur_indent}// Note: C requires formatted string\n{cur_indent}printf("%s\\n", {expr.replace("+", "")});')
            else:
                c_body.append(f'{cur_indent}printf("%d\\n", (int)({expr}));')
            continue

        # Handle Assignment: var = expr
        if '=' in stripped:
            parts = stripped.split('=', 1)
            left = parts[0].strip()
            right = parts[1].strip()

            eng_left = var_map.get(left, left)
            eng_right = right
            for m, e in var_map.items():
                eng_right = eng_right.replace(m, e)

            cur_indent = "    " * indent_level
            py_lines.append(f"{cur_indent}{eng_left} = {eng_right}")

            if eng_left not in declared_vars_java:
                java_body.append(f"{cur_indent}int {eng_left} = {eng_right};")
                declared_vars_java.add(eng_left)
            else:
                java_body.append(f"{cur_indent}{eng_left} = {eng_right};")

            if eng_left not in declared_vars_c:
                c_body.append(f"{cur_indent}int {eng_left} = {eng_right};")
                declared_vars_c.add(eng_left)
            else:
                c_body.append(f"{cur_indent}{eng_left} = {eng_right};")
            continue

        # Catch-all
        cur_indent = "    " * indent_level
        py_lines.append(f"{cur_indent}{stripped}")
        java_body.append(f"{cur_indent}{stripped};")
        c_body.append(f"{cur_indent}{stripped};")

    # Assemble complete target code
    # 1. Python Code
    python_code = "\n".join(py_lines)

    # 2. Java Code
    java_indent = "        "
    scanner_import = "import java.util.Scanner;\n\n" if has_input else ""
    scanner_init = f"{java_indent}Scanner scanner = new Scanner(System.in);\n" if has_input else ""
    java_body_str = "\n".join(f"{java_indent}{line}" if line else "" for line in java_body)
    java_code = f"""{scanner_import}public class Main {{
    public static void main(String[] args) {{
{scanner_init}{java_body_str}
    }}
}}"""

    # 3. C Code
    c_indent = "    "
    c_body_str = "\n".join(f"{c_indent}{line}" if line else "" for line in c_body)
    c_code = f"""#include <stdio.h>

int main() {{
{c_body_str}
    return 0;
}}"""

    # Educational comparison notes written in Malayalam for teaching students
    educational_notes = {
        "python_notes": "പൈത്തൺ (Python 3): വളരെ ലളിതവും എളുപ്പത്തിൽ വായിക്കാവുന്നതുമായ വാക്യഘടന (syntax). വേരിയബിളുകൾക്ക് 'int', 'float' തുടങ്ങിയ ഡാറ്റാ ടൈപ്പുകൾ പ്രത്യേകം പറയേണ്ടതില്ല (Dynamic Typing). കോഡ് ബ്ലോക്കുകൾ തിരിക്കാൻ 'അവസാനിപ്പിക്കുക' അല്ലെങ്കിൽ ബ്രേസുകൾക്ക് ({}) പകരം കൃത്യമായ അകലം (Indentation) ആണ് ഉപയോഗിക്കുന്നത്. print(), input() എന്നീ ബിൽറ്റ്-ഇൻ ഫംഗ്ഷനുകൾ ഉപയോഗിക്കുന്നു.",
        "java_notes": "ജാവ (Java): ഒബ്ജക്റ്റ് ഓറിയന്റഡ് (OOP) ഭാഷയാണ്. എല്ലാ കോഡുകളും 'public class Main' എന്ന ക്ലാസ്സിനുള്ളിലാണ് എഴുതേണ്ടത്. വേരിയബിളുകൾ ഉണ്ടാക്കുമ്പോൾ 'int x = 10;' എന്ന് ഡാറ്റാ ടൈപ്പ് മുൻകൂട്ടി പ്രഖ്യാപിക്കണം. കൺസോളിൽ നിന്നും ഇൻപുട്ട് സ്വീകരിക്കാൻ 'Scanner' ഒബ്ജക്റ്റും, ഔട്ട്പുട്ടിനായി 'System.out.println()' ഉം ഉപയോഗിക്കുന്നു. ബ്ലോക്കുകൾ {} ബ്രേസുകളിൽ അടയാളപ്പെടുത്തുന്നു.",
        "c_notes": "സി പ്രോഗ്രാമിംഗ് (C99): കമ്പ്യൂട്ടർ മെമ്മറിയോടും ഹാർഡ്‌വെയറിനോടും ചേർന്ന് നിൽക്കുന്ന ക്ലാസിക് ഭാഷ. പ്രോഗ്രാം ആരംഭിക്കുന്നത് '#include <stdio.h>' എന്ന ലൈബ്രറിയോടെയും 'int main()' ഫംഗ്ഷനോടെയുമാണ്. വേരിയബിൾ പ്രിന്റ് ചെയ്യാനും സ്കാൻ ചെയ്യാനും '%d' (പൂർണ്ണസംഖ്യകൾക്ക്), '%f' തുടങ്ങിയ ഫോർമാറ്റ് സ്പെസിഫയറുകൾ നിർബന്ധമാണ്. എല്ലാ സ്റ്റേറ്റ്മെന്റുകളും അർദ്ധവിരാമത്തിൽ (;) അവസാനിക്കണം.",
        "concept_summary": "താരതമ്യ സംഗ്രഹം: നിങ്ങൾ മലയാളത്തിൽ ചിന്തിച്ചുണ്ടാക്കിയ അതേ അൽഗോരിതവും യുക്തിയും തന്നെയാണ് യഥാർത്ഥത്തിൽ പൈത്തൺ, ജാവ, സി എന്നീ പ്രമുഖ ഭാഷകളിലും പ്രവർത്തിക്കുന്നത്. 'കാണിക്കുക' എന്നത് C-ൽ printf-ഉം Java-ൽ System.out.println-ഉം Python-ൽ print-ഉം ആകുമ്പോൾ, 'വായിക്കുക' എന്നത് scanf, scanner.nextInt, input എന്നിങ്ങനെ മാറുന്നു. ഈ താരതമ്യത്തിലൂടെ ലോകോത്തര പ്രോഗ്രാമിംഗ് ഭാഷകൾ വളരെ എളുപ്പത്തിൽ മലയാളത്തിലൂടെ പഠിച്ചെടുക്കാം!"
    }

    return {
        "engine": "offline_rules",
        "python": python_code,
        "java": java_code,
        "c": c_code,
        "dictionary": dictionary,
        "educational_notes": educational_notes,
    }


# Supported Non-Llama Groq Models (Qwen & GPT-OSS series)
NON_LLAMA_MODELS = [
    "qwen/qwen3.8-27b",        # Qwen 3.8 multilingual & reasoning
    "openai/gpt-oss-120b",     # OpenAI GPT-OSS 120B reasoning & code
    "qwen-qwq-32b",            # Qwen QwQ 32B deep math & coding
    "openai/gpt-oss-20b",      # OpenAI GPT-OSS 20B fast reasoning
]
DEFAULT_MODEL = "qwen/qwen3.8-27b"


def convert_code_multilang(
    code: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main entry point for multi-language educational conversion.
    Uses non-Llama Groq models (Qwen & GPT-OSS) by default.
    Generates educational explanations IN MALAYALAM so students can learn easily.
    Falls back gracefully to intelligent offline AST/rule transpiler.
    """
    if not code or not code.strip():
        return {
            "success": False,
            "error": "No Malayalam code provided for conversion."
        }

    # Resolve selected model (prioritize user choice, default to Qwen 3.8)
    chosen_model = model or DEFAULT_MODEL
    models_to_try = [chosen_model]
    for m in NON_LLAMA_MODELS:
        if m not in models_to_try:
            models_to_try.append(m)

    # Resolve API Key: passed argument > environment > .env
    groq_key = api_key or os.environ.get("GROQ_API_KEY")
    if not groq_key:
        env_path = os.path.join(os.getcwd(), ".env")
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("GROQ_API_KEY="):
                            groq_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                            break
            except Exception:
                pass

    if GROQ_AVAILABLE and groq_key:
        system_prompt = """You are an expert computer science educator who teaches programming to students IN MALAYALAM (മലയാളത്തിൽ പഠിപ്പിക്കുന്ന അധ്യാപകൻ).
Your task is to take code written in an educational Malayalam programming language and convert it into 3 standard industrial programming languages: Python 3, Java, and C (C99), while providing all teaching notes, concept guides, and dictionary roles IN MALAYALAM.

MALAYALAM LANGUAGE SPECIFICATION:
1. Keywords:
   - 'കാണിക്കുക' -> print / display output
   - 'വായിക്കുക' -> read user input into variable (e.g. 'വായിക്കുക x' means input x)
   - 'എങ്കിൽ' -> if condition
   - 'അല്ലെങ്കിൽ' -> else branch
   - 'ആവർത്തിക്കുക' -> while loop
   - 'അവസാനിപ്പിക്കുക' -> end (closes if block or while loop)
   - 'ശരി' -> true boolean literal
   - 'തെറ്റ്' -> false boolean literal
   - 'ഒപ്പം' -> and (logical conjunction)
   - 'അഥവാ' -> or (logical disjunction)
   - 'അല്ല' -> not (logical negation)

2. Variables:
   - Variables may be in Malayalam script (e.g., തുക, സംഖ്യ, ഘടകം, എണ്ണം, പേര്, വയസ്സ്).
   - YOU MUST TRANSLATE all Malayalam variable names to standard, idiomatic, meaningful English names in the generated code (e.g., 'തുക' -> 'sum', 'സംഖ്യ' -> 'number', 'ഘടകം' -> 'factorial', 'എണ്ണം' -> 'count', 'പേര്' -> 'name', etc.).

3. CRITICAL INSTRUCTION: EXPLANATIONS IN MALAYALAM (വിശദീകരണങ്ങൾ നിർബന്ധമായും മലയാളത്തിൽ ആയിരിക്കണം):
   - The generated code itself must be standard Python, Java, and C (compilable and clean).
   - BUT the 'role' description in the 'dictionary' and all 'educational_notes' (c_notes, java_notes, python_notes, concept_summary) MUST BE WRITTEN IN CLEAR, NATURAL MALAYALAM (മലയാളത്തിൽ) so a Malayalam student can easily learn and understand how the code works!

JSON Schema to return:
{
  "python": "<complete Python 3 code>",
  "java": "<complete Java class Main code>",
  "c": "<complete C99 code>",
  "dictionary": [
    {
      "original": "തുക",
      "translated": "sum",
      "type": "വേരിയബിൾ",
      "role": "ഇതിന്റെ ഉപയോഗവും പ്രവർത്തനവും മലയാളത്തിൽ ലളിതമായി വിശദീകരിക്കുക."
    }
  ],
  "educational_notes": {
    "c_notes": "സി ഭാഷയിലെ പ്രധാന ആശയങ്ങൾ മലയാളത്തിൽ (ഡാറ്റാ ടൈപ്പ്, %d ഫോർമാറ്റ് സ്പെസിഫയറുകൾ, {} ബ്രേസുകൾ, ലൈബ്രറികൾ).",
    "java_notes": "ജാവയിലെ പ്രധാന ആശയങ്ങൾ മലയാളത്തിൽ (ക്ലാസ് ഘടന public class Main, Scanner ഇൻപുട്ട്, System.out.println).",
    "python_notes": "പൈത്തണിലെ പ്രധാന ആശയങ്ങൾ മലയാളത്തിൽ (ഇൻഡന്റേഷൻ, ഡൈനാമിക് ടൈപ്പിംഗ്, print, input).",
    "concept_summary": "മലയാളം പ്രോഗ്രാമിലെ ആശയങ്ങൾ ഈ മൂന്ന് ഭാഷകളിലും എങ്ങനെ പ്രവർത്തിക്കുന്നു എന്ന സമഗ്രമായ താരതമ്യം മലയാളത്തിൽ."
  }
}
"""

        user_prompt = f"""ദയവായി താഴെ നൽകിയിരിക്കുന്ന മലയാളം പ്രോഗ്രാമിനെ Python, Java, C എന്നിവയിലേക്ക് പരിഭാഷപ്പെടുത്തുകയും, ഒരു വിദ്യാർത്ഥിക്ക് മനസ്സിലാകുന്ന വിധത്തിൽ എല്ലാ വിശദീകരണങ്ങളും (educational notes & dictionary roles) മലയാളത്തിൽ നൽകുകയും ചെയ്യുക:

```malayalam
{code}
```

മുകളിലെ നിർദ്ദേശങ്ങൾ പാലിച്ചുകൊണ്ട് സാധുവായ ഒരു JSON ഒബ്ജക്റ്റ് മാത്രമായി മറുപടി നൽകുക:
{{
  "python": "<Python 3 code>",
  "java": "<Java class Main code>",
  "c": "<C99 code>",
  "dictionary": [
    {{"original": "...", "translated": "...", "type": "വേരിയബിൾ|കീവേഡ്|ഓപ്പറേറ്റർ", "role": "..."}}
  ],
  "educational_notes": {{
    "c_notes": "...",
    "java_notes": "...",
    "python_notes": "...",
    "concept_summary": "..."
  }}
}}
"""
        last_error = None
        client = Groq(api_key=groq_key)

        for current_model in models_to_try:
            try:
                response = client.chat.completions.create(
                    model=current_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.2,
                    max_tokens=2500,
                )

                raw_content = response.choices[0].message.content
                parsed = json.loads(raw_content)

                return {
                    "success": True,
                    "engine": "groq",
                    "model": current_model,
                    "python": parsed.get("python", ""),
                    "java": parsed.get("java", ""),
                    "c": parsed.get("c", ""),
                    "dictionary": parsed.get("dictionary", []),
                    "educational_notes": parsed.get("educational_notes", {}),
                }

            except Exception as e:
                last_error = e
                continue

        # If all Groq attempts fail, fallback to offline transpiler
        offline_result = offline_transpile(code)
        offline_result["success"] = True
        offline_result["groq_error"] = str(last_error)
        offline_result["notice"] = f"Groq API call attempted with non-Llama models ({', '.join(models_to_try)}) but encountered: {str(last_error)}. Displaying offline educational transpiler output."
        return offline_result

    # Offline transpiler fallback (No key configured)
    offline_result = offline_transpile(code)
    offline_result["success"] = True
    offline_result["notice"] = "Converted via Built-in Educational Transpiler. You can provide your Groq API Key to enable Groq Qwen/GPT-OSS contextual AI translation."
    return offline_result

