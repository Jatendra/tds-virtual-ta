#!/usr/bin/env python3
"""
TDS Virtual TA Evaluation Script
Runs evaluation tests based on the promptfoo configuration
"""

import requests
import json
import time
import yaml
from typing import Dict, List, Any
import sys

class TDSEvaluator:
    def __init__(self, config_file: str):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.base_url = "http://localhost:8000/api/"
        self.results = []
    
    def run_evaluation(self):
        """Run all evaluation tests"""
        print("🚀 Starting TDS Virtual TA Evaluation")
        print("=" * 50)
        
        # Health check first
        if not self._health_check():
            print("❌ Health check failed. Make sure the API is running.")
            return False
        
        print("✅ API is healthy. Running tests...\n")
        
        # Run each test
        for i, test in enumerate(self.config.get('tests', []), 1):
            print(f"Test {i}: {test['vars']['question'][:50]}...")
            print("-" * 60)
            
            result = self._run_single_test(test)
            self.results.append(result)
            
            self._print_test_result(result)
            print()
        
        # Print summary
        self._print_summary()
        return True
    
    def _health_check(self) -> bool:
        """Check if the API is running"""
        try:
            response = requests.get("http://localhost:8000/health", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def _run_single_test(self, test: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test case"""
        question = test['vars']['question']
        
        # Prepare request
        payload = {"question": question}
        if 'image' in test['vars']:
            payload['image'] = test['vars']['image']
        
        # Make request
        start_time = time.time()
        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=35  # Slightly more than 30s limit
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Run assertions
                assertion_results = self._run_assertions(test.get('assert', []), response_data, response_time)
                
                return {
                    'question': question,
                    'status': 'PASS' if all(assertion_results.values()) else 'FAIL',
                    'response_time': response_time,
                    'response_data': response_data,
                    'assertions': assertion_results
                }
            else:
                return {
                    'question': question,
                    'status': 'ERROR',
                    'response_time': response_time,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                'question': question,
                'status': 'ERROR',
                'error': str(e)
            }
    
    def _run_assertions(self, assertions: List[Dict], response_data: Dict, response_time: float) -> Dict[str, bool]:
        """Run all assertions for a test"""
        results = {}
        
        for assertion in assertions:
            assertion_type = assertion.get('type')
            
            if assertion_type == 'is-json':
                # Check if response matches JSON schema
                results['is_json'] = self._check_json_schema(response_data, assertion.get('value', {}))
            
            elif assertion_type == 'javascript':
                # Check response time (simplified)
                if 'latencyMs < 30000' in assertion.get('value', ''):
                    results['response_time'] = response_time < 30.0
            
            elif assertion_type == 'contains':
                # Check if response contains specific text
                transform = assertion.get('transform', '')
                value = assertion.get('value', '')
                
                if 'output.answer' in transform:
                    results[f'contains_{value[:20]}'] = value.lower() in response_data.get('answer', '').lower()
                elif 'JSON.stringify(output.links)' in transform:
                    links_str = json.dumps(response_data.get('links', []))
                    results[f'contains_link_{value[:20]}'] = value in links_str
            
            elif assertion_type == 'llm-rubric':
                # Simplified rubric check - look for key concepts
                transform = assertion.get('transform', '')
                value = assertion.get('value', '')
                
                if 'output.answer' in transform:
                    answer = response_data.get('answer', '').lower()
                    if 'gpt-3.5-turbo-0125' in value.lower():
                        results['gpt_model_check'] = 'gpt-3.5-turbo-0125' in answer
                    elif 'docker' in value.lower() and 'podman' in value.lower():
                        results['docker_podman_check'] = 'docker' in answer or 'podman' in answer
                    elif "doesn't know" in value.lower():
                        results['unknown_info_check'] = any(phrase in answer for phrase in [
                            "don't have information", "not available", "not yet available"
                        ])
        
        return results
    
    def _check_json_schema(self, data: Dict, schema: Dict) -> bool:
        """Simple JSON schema validation"""
        required_fields = schema.get('required', [])
        
        # Check required fields exist
        for field in required_fields:
            if field not in data:
                return False
        
        # Check answer is string
        if 'answer' in data and not isinstance(data['answer'], str):
            return False
        
        # Check links is array of objects with url and text
        if 'links' in data:
            if not isinstance(data['links'], list):
                return False
            for link in data['links']:
                if not isinstance(link, dict) or 'url' not in link or 'text' not in link:
                    return False
        
        return True
    
    def _print_test_result(self, result: Dict[str, Any]):
        """Print the result of a single test"""
        status = result['status']
        if status == 'PASS':
            print("✅ PASSED")
        elif status == 'FAIL':
            print("❌ FAILED")
        else:
            print("🔥 ERROR")
        
        if 'response_time' in result:
            print(f"⏱️  Response time: {result['response_time']:.2f}s")
        
        if 'response_data' in result:
            answer = result['response_data'].get('answer', '')
            print(f"📝 Answer: {answer[:100]}{'...' if len(answer) > 100 else ''}")
            
            links = result['response_data'].get('links', [])
            print(f"🔗 Links: {len(links)} provided")
        
        if 'assertions' in result:
            passed_assertions = sum(1 for v in result['assertions'].values() if v)
            total_assertions = len(result['assertions'])
            print(f"✅ Assertions: {passed_assertions}/{total_assertions} passed")
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
    
    def _print_summary(self):
        """Print evaluation summary"""
        print("=" * 50)
        print("📊 EVALUATION SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['status'] == 'PASS')
        failed_tests = sum(1 for r in self.results if r['status'] == 'FAIL')
        error_tests = sum(1 for r in self.results if r['status'] == 'ERROR')
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"🔥 Errors: {error_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Average response time
        response_times = [r.get('response_time', 0) for r in self.results if 'response_time' in r]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            print(f"⏱️  Average Response Time: {avg_time:.2f}s")
        
        print("\n🎯 All tests completed!")

def main():
    config_file = "project-tds-virtual-ta-promptfoo.yaml"
    
    evaluator = TDSEvaluator(config_file)
    success = evaluator.run_evaluation()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 