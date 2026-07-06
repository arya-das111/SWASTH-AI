import subprocess
import sys
import os

def run_test_script(path):
    print(f"\n>>> RUNNING TEST: {os.path.basename(path)}...")
    try:
        res = subprocess.run(
            [sys.executable, path],
            capture_output=True,
            text=True,
            check=True
        )
        print(res.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ TEST FAILED: {os.path.basename(path)}")
        print("--- Output ---")
        print(e.stdout)
        print("--- Error ---")
        print(e.stderr)
        return False

def main():
    print("=" * 60)
    print("      SWASTH AI - INTEGRATION TEST VERIFICATION SUITE      ")
    print("=" * 60)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    api_dir = os.path.join(base_dir, "apps", "api")
    
    test_files = [
        os.path.join(api_dir, "test_ai_endpoints.py"),
        os.path.join(api_dir, "test_translation_offline.py"),
        os.path.join(api_dir, "test_fhir_dpdp.py")
    ]
    
    success_count = 0
    total_tests = len(test_files)
    
    for test in test_files:
        if run_test_script(test):
            success_count += 1
            
    print("=" * 60)
    print(f"VERIFICATION SUMMARY: {success_count}/{total_tests} SUITES PASSED")
    print("=" * 60)
    
    if success_count == total_tests:
        print("ALL SYSTEMS OPERATIONAL - READY FOR PROVISIONING")
        sys.exit(0)
    else:
        print("SOME SYSTEMS FAILED VERIFICATION - REVIEW ERROR LOGS")
        sys.exit(1)

if __name__ == "__main__":
    main()
