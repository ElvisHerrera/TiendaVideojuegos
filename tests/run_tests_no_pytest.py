"""
Simple test runner (no pytest required) — discovers test_ functions
in files under tests/ and runs them, printing a short summary.

Usage:
    python3 tests/run_tests_no_pytest.py

This is a convenience helper for environments where pytest is not
available or can't be installed (e.g., restricted systems).
"""
import importlib.util
import os
import sys
import traceback


def run_tests_in_file(path: str):
    name = os.path.splitext(os.path.basename(path))[0]
    # ensure project root is on sys.path so test modules can import project packages
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore

    tests = [getattr(module, a) for a in dir(module) if a.startswith("test_")]
    passed = failed = 0
    for func in tests:
        try:
            func()
            print(f"OK    {name}.{func.__name__}")
            passed += 1
        except AssertionError:
            print(f"FAIL  {name}.{func.__name__}")
            traceback.print_exc()
            failed += 1
        except Exception:
            print(f"ERROR {name}.{func.__name__}")
            traceback.print_exc()
            failed += 1

    return passed, failed


def main():
    tests_dir = os.path.dirname(__file__)
    files = [
        os.path.join(tests_dir, f)
        for f in os.listdir(tests_dir)
        if f.startswith("test_") and f.endswith(".py")
    ]

    total_ok = total_fail = 0
    for f in files:
        ok, fail = run_tests_in_file(f)
        total_ok += ok
        total_fail += fail

    print("\nSummary:\n")
    print(f"Passed: {total_ok}")
    print(f"Failed: {total_fail}")

    if total_fail > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
