#!/usr/bin/env python3
"""
Automated test suite for Legal Document Analyzer
Runs all tests from tests.json and reports pass rate
"""
import sys
import os
import json
import time
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.safety import safety_checker
from backend.gemini_client import gemini_client


def load_tests():
    """Load test cases from tests.json"""
    with open('tests.json', 'r') as f:
        return json.load(f)['tests']


def run_single_test(test):
    """Run a single test case"""
    test_id = test['id']
    test_name = test['name']
    input_text = test['input']
    expected_patterns = test.get('expected_patterns', [])
    should_trigger_tool = test.get('should_trigger_tool', False)
    should_fail = test.get('should_fail', False)

    print(f"\n{'-'*100}\n")
    print(f"Test: {test_id} - {test_name}")
    print(f"Description: {test.get('description', 'N/A')}")

    start_time = time.time()

    # Safety check
    valid, error_msg = safety_checker.validate_input(input_text)

    if should_fail:
        if not valid:
            print(f"PASS - Correctly rejected: {error_msg}")
            return True, time.time() - start_time
        print("FAIL - Should have been rejected but wasn't")
        return False, time.time() - start_time

    if not valid:
        print(f"FAIL - Validation error: {error_msg}")
        return False, time.time() - start_time

    # Run analysis
    summary, terms_looked_up, usage = gemini_client.analyze_document(input_text)
    summary_lower = summary.lower()

    patterns_found = [p for p in expected_patterns if p.lower() in summary_lower]
    patterns_missing = [p for p in expected_patterns if p.lower() not in summary_lower]

    tool_triggered = len(terms_looked_up) > 0
    tool_check_passed = (tool_triggered == should_trigger_tool) or not should_trigger_tool

    pattern_pass_threshold = len(expected_patterns) * 0.5
    patterns_pass = len(patterns_found) >= pattern_pass_threshold

    overall_pass = patterns_pass and tool_check_passed

    # Results
    print("\nResults:")
    print(f"   Patterns found: {len(patterns_found)}/{len(expected_patterns)}")

    for p in patterns_found:
        print(f"      YES {p}")
    for p in patterns_missing:
        print(f"      NO {p}")

    print(f"\n   Tool usage: {'PASSED' if tool_check_passed else 'FAILED'}")
    print(f"      Expected: {should_trigger_tool}, Actual: {tool_triggered}")

    if terms_looked_up:
        print(f"      Terms: {', '.join(terms_looked_up)}")

    print(f"\n   Tokens used: {usage.get('total_tokens', 0)}")

    elapsed = time.time() - start_time
    print(f"   Time: {elapsed:.2f}s")

    if overall_pass:
        print("\nPASS")
    else:
        print("\nFAIL")
        if not patterns_pass:
            print(f"   Reason: Only {len(patterns_found)}/{len(expected_patterns)} patterns found")
        if not tool_check_passed:
            print("   Reason: Tool usage mismatch")

    return overall_pass, elapsed


def main():
    """Run all tests and report results"""
    print("\nTesting...")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tests = load_tests()
    print(f"\nLoaded {len(tests)} test cases\n")

    results = []
    total_time = 0

    for test in tests:
        passed, elapsed = run_single_test(test)
        results.append({
            'id': test['id'],
            'name': test['name'],
            'passed': passed,
            'time': elapsed
        })
        total_time += elapsed

        time.sleep(7)

    passed_count = sum(1 for r in results if r['passed'])
    failed_count = len(results) - passed_count
    pass_rate = (passed_count / len(results)) * 100

    print("\nTEST SUMMARY")
    print(f"\nTotal tests: {len(results)}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {failed_count}")
    print(f"Pass rate: {pass_rate:.1f}%")
    print(f"Total time: {total_time:.2f}s")
    print(f"Average time per test: {total_time/len(results):.2f}s")

    if failed_count > 0:
        print("\nFailed tests:")
        for r in results:
            if not r['passed']:
                print(f"   - {r['id']}: {r['name']}")

    results_file = 'test_results.json'
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(results),
            'passed': passed_count,
            'failed': failed_count,
            'pass_rate': pass_rate,
            'total_time': total_time,
            'results': results
        }, f, indent=2)

    print(f"\nResults saved to: {results_file}")

    sys.exit(0 if pass_rate >= 80 else 1)


if __name__ == "__main__":
    main()
