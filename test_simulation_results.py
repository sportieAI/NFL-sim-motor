#!/usr/bin/env python3
"""
Test script for simulation_results.json implementation.

Validates that:
1. simulation_results.json can be generated
2. It conforms to the expected schema
3. Dashboard integration works
4. All required files are created
"""

import json
import os
import sys
from datetime import datetime

def test_simulation_results():
    """Run comprehensive tests for simulation results."""
    
    print("Testing simulation_results.json implementation...")
    print("=" * 50)
    
    tests_passed = 0
    tests_total = 6
    
    # Test 1: Check if simulation_results.json exists
    print("1. Checking if simulation_results.json exists...")
    if os.path.exists("simulation_results.json"):
        print("   ✓ simulation_results.json found")
        tests_passed += 1
    else:
        print("   ✗ simulation_results.json not found")
    
    # Test 2: Validate JSON structure
    print("2. Validating JSON structure...")
    try:
        with open("simulation_results.json", "r") as f:
            data = json.load(f)
        print("   ✓ Valid JSON format")
        tests_passed += 1
    except Exception as e:
        print(f"   ✗ Invalid JSON: {e}")
        return False
    
    # Test 3: Schema validation
    print("3. Validating schema compliance...")
    required_fields = ["simulation_id", "timestamp", "result"]
    schema_valid = True
    
    for field in required_fields:
        if field not in data:
            print(f"   ✗ Missing required field: {field}")
            schema_valid = False
    
    if schema_valid:
        print("   ✓ All required fields present")
        tests_passed += 1
    
    # Test 4: Check outputs directory structure
    print("4. Checking outputs directory structure...")
    if os.path.exists("outputs") and os.path.isdir("outputs"):
        sim_dirs = [d for d in os.listdir("outputs") if os.path.isdir(os.path.join("outputs", d))]
        if sim_dirs:
            print(f"   ✓ Found {len(sim_dirs)} simulation directories")
            tests_passed += 1
        else:
            print("   ✗ No simulation directories found")
    else:
        print("   ✗ Outputs directory not found")
    
    # Test 5: Dashboard compatibility
    print("5. Testing dashboard compatibility...")
    try:
        # Test with the most recent simulation
        sim_dirs = sorted([d for d in os.listdir("outputs") if os.path.isdir(os.path.join("outputs", d))], reverse=True)
        if sim_dirs:
            test_dir = os.path.join("outputs", sim_dirs[0])
            
            # Check required dashboard files
            required_files = ["simulation_output.json", "analytics_report.json", "summary.txt"]
            all_files_exist = True
            
            for file in required_files:
                file_path = os.path.join(test_dir, file)
                if not os.path.exists(file_path):
                    print(f"   ✗ Missing dashboard file: {file}")
                    all_files_exist = False
            
            if all_files_exist:
                # Test loading dashboard files
                with open(os.path.join(test_dir, "simulation_output.json")) as f:
                    sim_output = json.load(f)
                team_scores = {team["name"]: team["points"] for team in sim_output["teams"]}
                print(f"   ✓ Dashboard integration test passed - scores: {team_scores}")
                tests_passed += 1
    except Exception as e:
        print(f"   ✗ Dashboard compatibility test failed: {e}")
    
    # Test 6: Data consistency
    print("6. Testing data consistency...")
    try:
        # Check if data makes sense
        result = data["result"]
        teams = data["teams"]
        
        home_score = result["final_score"]["home"]
        away_score = result["final_score"]["away"]
        
        team_scores_match = (
            teams[0]["points"] == home_score and 
            teams[1]["points"] == away_score
        ) or (
            teams[0]["points"] == away_score and 
            teams[1]["points"] == home_score
        )
        
        if team_scores_match and len(data["plays"]) > 0:
            print("   ✓ Data consistency check passed")
            tests_passed += 1
        else:
            print("   ✗ Data consistency issues found")
    except Exception as e:
        print(f"   ✗ Data consistency test failed: {e}")
    
    # Summary
    print("=" * 50)
    print(f"Tests passed: {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print("🎉 All tests PASSED! simulation_results.json implementation is working correctly.")
        return True
    else:
        print("❌ Some tests FAILED. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = test_simulation_results()
    sys.exit(0 if success else 1)