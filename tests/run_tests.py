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

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.safety import safety_checker
from backend.gemini_client import gemini_client

def load_tests():
    """Load test cases from tests.json"""
    with open('tests.json', 'r') as f:
        data = json.load(f)
    return data['tests']

def run_single_test(test):
    """Run a single test case"""
    test_id = test['id']
    test_name = test['name']
    input_text = test['input']
    expected_patterns = test.get('expected_patterns', [])
    should_trigger_tool = test.get('should_trigger_tool', False)
    should_fail = test.get('should_fail', False)
    
    print(f"\n{'='*60}")
    print(f"Test: {test_id} - {test_name}")
    print(f"Description: {test.get('description', 'N/A')}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        # First check safety
        valid, error_msg = safety_checker.validate_input(input_text)
        
        if should_fail:
            # This test should fail validation
            if not valid:
                print(f"✅ PASS - Correctly rejected: {error_msg}")
                return True, time.time() - start_time
            else:
                print(f"❌ FAIL - Should have been rejected but wasn't")
                return False, time.time() - start_time
        
        if not valid:
            print(f"❌ FAIL - Validation error: {error_msg}")
            return False, time.time() - start_time
        
        # Run analysis
        summary, terms_looked_up, usage = gemini_client.analyze_document(input_text)
        
        # Check if expected patterns are in summary
        summary_lower = summary.lower()
        patterns_found = []
        patterns_missing = []
        
        for pattern in expected_patterns:
            if pattern.lower() in summary_lower:
                patterns_found.append(pattern)
            else:
                patterns_missing.append(pattern)
        
        # Check tool usage
        tool_triggered = len(terms_looked_up) > 0
        tool_check_passed = (tool_triggered == should_trigger_tool) or not should_trigger_tool
        
        # Determine pass/fail
        # Pass if at least 50% of expected patterns found
        pattern_pass_threshold = len(expected_patterns) * 0.5
        patterns_pass = len(patterns_found) >= pattern_pass_threshold
        
        overall_pass = patterns_pass and tool_check_passed
        
        # Print results
        print(f"\n📊 Results:")
        print(f"   Patterns found: {len(patterns_found)}/{len(expected_patterns)}")
        for pattern in patterns_found:
            print(f"      ✓ {pattern}")
        for pattern in patterns_missing:
            print(f"      ✗ {pattern}")
        
        print(f"\n   Tool usage: {'✓' if tool_check_passed else '✗'}")
        print(f"      Expected: {should_trigger_tool}, Actual: {tool_triggered}")
        if terms_looked_up:
            print(f"      Terms: {', '.join(terms_looked_up)}")
        
        print(f"\n   Tokens used: {usage.get('total_tokens', 0)}")
        
        elapsed = time.time() - start_time
        print(f"   Time: {elapsed:.2f}s")
        
        if overall_pass:
            print(f"\n✅ PASS")
        else:
            print(f"\n❌ FAIL")
            if not patterns_pass:
                print(f"   Reason: Only {len(patterns_found)}/{len(expected_patterns)} patterns found")
            if not tool_check_passed:
                print(f"   Reason: Tool usage mismatch")
        
        return overall_pass, elapsed
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n❌ FAIL - Exception: {str(e)}")
        return False, elapsed

def main():
    """Run all tests and report results"""
    print("="*60)
    print("🧪 Legal Document Analyzer - Test Suite")
    print("="*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load tests
    tests = load_tests()
    print(f"\nLoaded {len(tests)} test cases\n")
    
    # Run all tests
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
        
        # Small delay between tests to avoid rate limiting
        time.sleep(7)
    
    # Summary
    print("\n" + "="*60)
    print("📈 TEST SUMMARY")
    print("="*60)
    
    passed_count = sum(1 for r in results if r['passed'])
    failed_count = len(results) - passed_count
    pass_rate = (passed_count / len(results)) * 100
    
    print(f"\nTotal tests: {len(results)}")
    print(f"Passed: {passed_count} ✅")
    print(f"Failed: {failed_count} ❌")
    print(f"Pass rate: {pass_rate:.1f}%")
    print(f"Total time: {total_time:.2f}s")
    print(f"Average time per test: {total_time/len(results):.2f}s")
    
    # Failed tests detail
    if failed_count > 0:
        print(f"\n❌ Failed tests:")
        for r in results:
            if not r['passed']:
                print(f"   - {r['id']}: {r['name']}")
    
    # Save results to file
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
    
    print(f"\n📄 Results saved to: {results_file}")
    
    # Exit with appropriate code
    sys.exit(0 if pass_rate >= 80 else 1)

if __name__ == "__main__":
    main()