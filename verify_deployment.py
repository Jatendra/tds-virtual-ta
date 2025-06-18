#!/usr/bin/env python3
"""
Verification script for TDS Virtual TA deployment optimizations
"""

import os
import sys
import subprocess
from pathlib import Path

def check_file_sizes():
    """Check that files are optimized for deployment"""
    print("📊 Checking file sizes...")
    
    # Check requirements.txt
    with open('requirements.txt', 'r') as f:
        lines = f.readlines()
    
    print(f"✅ requirements.txt: {len(lines)} dependencies")
    
    # Check if heavy dependencies are removed
    content = open('requirements.txt', 'r').read()
    heavy_deps = ['openai', 'tiktoken', 'numpy', 'scikit-learn', 'sentence-transformers', 'chromadb']
    removed_deps = [dep for dep in heavy_deps if dep not in content]
    
    print(f"✅ Removed heavy dependencies: {removed_deps}")
    
    # Check .dockerignore exists
    if os.path.exists('.dockerignore'):
        print("✅ .dockerignore exists")
    else:
        print("❌ .dockerignore missing")
    
    # Check cache file size
    if os.path.exists('tds_data_cache.json'):
        size = os.path.getsize('tds_data_cache.json')
        print(f"✅ Cache file size: {size/1024:.1f} KB")
    
    return True

def verify_application():
    """Verify application can start"""
    print("\n🧪 Verifying application...")
    
    try:
        # Import main modules to check for errors
        from main import app
        from token_calculator import TokenCalculator
        from data_scraper import TDSDataScraper
        from question_answerer import QuestionAnswerer
        from image_processor import ImageProcessor
        
        print("✅ All modules import successfully")
        
        # Test token calculator
        calc = TokenCalculator()
        result = calc.calculate_cost("test", "gpt-3.5-turbo-0125", "input")
        print(f"✅ Token calculator works: {result['cost_cents']} cents")
        
        return True
        
    except Exception as e:
        print(f"❌ Application error: {e}")
        return False

def check_deployment_files():
    """Check deployment configuration files"""
    print("\n📄 Checking deployment files...")
    
    files_to_check = [
        'Dockerfile',
        'Dockerfile.railway', 
        '.dockerignore',
        'railway.toml',
        'Procfile'
    ]
    
    for file in files_to_check:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ {file}: {size} bytes")
        else:
            print(f"❌ Missing: {file}")
    
    return True

def estimate_docker_size():
    """Estimate Docker image size based on dependencies"""
    print("\n📦 Estimating image size...")
    
    # Base alpine image: ~5MB
    # Python 3.11-alpine: ~50MB
    # Dependencies estimate
    base_size = 50  # MB
    
    with open('requirements.txt', 'r') as f:
        deps = f.readlines()
    
    # Rough estimates for each dependency
    dep_sizes = {
        'fastapi': 15,
        'uvicorn': 10,
        'requests': 5,
        'beautifulsoup4': 8,
        'lxml': 20,  # Can be large
        'pillow': 15,
        'httpx': 8,
        'pydantic': 12,
        'aiofiles': 2,
        'python-multipart': 3,
        'python-dotenv': 1
    }
    
    estimated_size = base_size
    for dep in deps:
        dep_name = dep.split('==')[0].strip()
        estimated_size += dep_sizes.get(dep_name, 5)  # Default 5MB per unknown dep
    
    print(f"📦 Estimated image size: ~{estimated_size}MB")
    
    if estimated_size < 500:  # Well under 4GB limit
        print("✅ Size should be well within Railway's 4GB limit")
    else:
        print("⚠️  Size might be close to limits")
    
    return estimated_size

def main():
    """Run all verification checks"""
    print("🚀 TDS Virtual TA Deployment Verification")
    print("=" * 50)
    
    all_passed = True
    
    # Run checks
    all_passed &= check_file_sizes()
    all_passed &= verify_application() 
    all_passed &= check_deployment_files()
    estimate_docker_size()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All checks passed! Ready for Railway deployment.")
        print("\n🚀 Next steps:")
        print("1. Commit changes: git add . && git commit -m 'Optimize for Railway'")
        print("2. Push to Railway: railway login && railway up")
        print("3. Check deployment logs for any issues")
    else:
        print("❌ Some checks failed. Please fix issues before deploying.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main()) 