"""Code execution service supporting Judge0 API and safe local subprocess sandbox.
Ensures candidate code is NEVER executed directly inside the Flask main application process.
"""
import sys
import json
import time
import tempfile
import subprocess
import requests
from typing import List, Dict, Any
from flask import current_app

HARNESS_TEMPLATE = r'''# Candidate Code Test Runner Harness
import sys
import json

# Restricted Sandbox Preamble: block hazardous modules
blocked_modules = [
    'subprocess', 'os', 'socket', 'shutil', 'http', 'urllib', 
    'requests', 'ctypes', 'multiprocessing', 'threading', 'signal'
]

original_import = __builtins__.__import__ if hasattr(__builtins__, '__import__') else __import__

def safe_import(name, *args, **kwargs):
    for blocked in blocked_modules:
        if name == blocked or name.startswith(blocked + '.'):
            raise ImportError(f"Importing module '{name}' is restricted for security.")
    return original_import(name, *args, **kwargs)

if isinstance(__builtins__, dict):
    __builtins__['__import__'] = safe_import
else:
    setattr(__builtins__, '__import__', safe_import)

# User Code Execution
user_namespace = {}
user_code = __USER_CODE__
target_func_name = __FUNC_NAME__
test_cases = __TEST_CASES__

results = {
    "success": False,
    "error": None,
    "passed": 0,
    "total": len(test_cases),
    "details": []
}

try:
    exec(user_code, user_namespace)
except Exception as e:
    results["error"] = f"Syntax / Execution Error during definition: {type(e).__name__}: {str(e)}"
    print(json.dumps(results))
    sys.exit(0)

if target_func_name not in user_namespace or not callable(user_namespace[target_func_name]):
    results["error"] = f"Function '{target_func_name}' was not found or is not callable in submitted code."
    print(json.dumps(results))
    sys.exit(0)

target_func = user_namespace[target_func_name]

# Run each test case
for idx, tc in enumerate(test_cases, 1):
    inp = tc.get("input")
    expected = tc.get("expected")
    
    test_result = {
        "test": idx,
        "input": inp,
        "expected": expected,
        "actual": None,
        "passed": False,
        "error": None
    }
    
    try:
        if isinstance(inp, list):
            actual = target_func(*inp)
        elif isinstance(inp, dict):
            actual = target_func(**inp)
        else:
            actual = target_func(inp)
            
        test_result["actual"] = actual
        
        if actual == expected:
            test_result["passed"] = True
            results["passed"] += 1
        else:
            test_result["passed"] = False
    except Exception as e:
        test_result["error"] = f"Runtime Error: {type(e).__name__}: {str(e)}"
        test_result["passed"] = False
        
    results["details"].append(test_result)

results["success"] = (results["passed"] == len(test_cases))
print(json.dumps(results))
'''


def run_via_judge0(harness_code: str, test_cases: List[Dict[str, Any]], time_limit: float = 3.0) -> Dict[str, Any]:
    """Execute harness via Judge0 API if configured."""
    import os
    api_key = ""
    api_host = "judge0-ce.p.rapidapi.com"
    try:
        api_key = current_app.config.get("JUDGE0_API_KEY", "")
        api_host = current_app.config.get("JUDGE0_API_HOST", "judge0-ce.p.rapidapi.com")
    except Exception:
        api_key = os.getenv("JUDGE0_API_KEY", "")
        api_host = os.getenv("JUDGE0_API_HOST", "judge0-ce.p.rapidapi.com")

    if not api_key:
        return {"attempted": False, "error": "No JUDGE0_API_KEY configured"}

    url = f"https://{api_host}/submissions?base64_encoded=false&wait=true"
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": api_host,
        "Content-Type": "application/json"
    }
    payload = {
        "language_id": 71,  # Python 3
        "source_code": harness_code,
        "cpu_time_limit": time_limit
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        if resp.status_code in (200, 201):
            data = resp.json()
            stdout = (data.get("stdout") or "").strip()
            stderr = (data.get("stderr") or "").strip()
            compile_output = (data.get("compile_output") or "").strip()

            if stdout:
                last_line = stdout.splitlines()[-1]
                try:
                    parsed = json.loads(last_line)
                    total = len(test_cases)
                    passed = parsed.get("passed", 0)
                    parsed["score"] = round((passed / total) * 20.0, 1) if total > 0 else 0.0
                    parsed["engine"] = "Judge0 Remote Cloud Sandbox"
                    parsed["attempted"] = True
                    return parsed
                except json.JSONDecodeError:
                    pass

            return {
                "attempted": True,
                "passed": 0,
                "total": len(test_cases),
                "score": 0.0,
                "details": [],
                "error": stderr or compile_output or stdout or "Judge0 execution failed to produce test results.",
                "engine": "Judge0 Remote Cloud Sandbox"
            }
        else:
            return {"attempted": False, "error": f"Judge0 API status {resp.status_code}: {resp.text}"}
    except Exception as e:
        return {"attempted": False, "error": f"Judge0 connection error: {str(e)}"}


def run_via_local_sandbox(harness_code: str, test_cases: List[Dict[str, Any]], time_limit: float = 2.0) -> Dict[str, Any]:
    """Execute harness via safe local subprocess sandbox with -I (isolated) and -s (no user site-packages)."""
    start_time = time.time()
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as temp_file:
        temp_file.write(harness_code)
        temp_file_path = temp_file.name

    try:
        proc = subprocess.run(
            [sys.executable, "-I", "-s", temp_file_path],
            capture_output=True,
            text=True,
            timeout=time_limit
        )
        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()

        if stdout:
            last_line = stdout.splitlines()[-1]
            try:
                data = json.loads(last_line)
                data["time_ms"] = elapsed_ms
                total = len(test_cases)
                passed = data.get("passed", 0)
                data["score"] = round((passed / total) * 20.0, 1) if total > 0 else 0.0
                data["engine"] = "Local Isolated Process Sandbox"
                return data
            except json.JSONDecodeError:
                pass

        return {
            "passed": 0,
            "total": len(test_cases),
            "score": 0.0,
            "details": [],
            "error": stderr or stdout or "Failed to parse test execution output.",
            "time_ms": elapsed_ms,
            "engine": "Local Isolated Process Sandbox"
        }
    except subprocess.TimeoutExpired:
        return {
            "passed": 0,
            "total": len(test_cases),
            "score": 0.0,
            "details": [],
            "error": f"Execution timed out. Code exceeded maximum limit of {time_limit} seconds.",
            "time_ms": round(time_limit * 1000, 2),
            "engine": "Local Isolated Process Sandbox"
        }
    except Exception as e:
        return {
            "passed": 0,
            "total": len(test_cases),
            "score": 0.0,
            "details": [],
            "error": f"Execution system error: {str(e)}",
            "time_ms": 0.0,
            "engine": "Local Isolated Process Sandbox"
        }
    finally:
        import os
        try:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        except Exception:
            pass


def run_python(
    code: str, 
    test_cases: List[Dict[str, Any]], 
    target_func_name: str = "reverse_words", 
    time_limit: float = 2.0
) -> Dict[str, Any]:
    """Execute candidate Python code against test cases.
    Attempts Judge0 first if configured; falls back safely to isolated local runner.
    """
    if not code or not code.strip():
        return {
            "passed": 0,
            "total": len(test_cases),
            "score": 0.0,
            "details": [],
            "error": "No code submitted.",
            "time_ms": 0.0,
            "engine": "None"
        }

    harness_code = (
        HARNESS_TEMPLATE
        .replace("__USER_CODE__", json.dumps(code))
        .replace("__FUNC_NAME__", json.dumps(target_func_name))
        .replace("__TEST_CASES__", json.dumps(test_cases))
    )

    # 1. Try Judge0 if configured
    judge0_result = run_via_judge0(harness_code, test_cases, time_limit=time_limit)
    if judge0_result.get("attempted"):
        return judge0_result

    # 2. Fall back to local isolated process sandbox
    return run_via_local_sandbox(harness_code, test_cases, time_limit=time_limit)
