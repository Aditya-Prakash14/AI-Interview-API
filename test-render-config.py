#!/usr/bin/env python3
"""
Test script to validate Render deployment configuration
"""
import os
import sys
import yaml

def test_render_yaml():
    """Test render.yaml configuration"""
    print("🔍 Testing render.yaml configuration...")
    
    if not os.path.exists("render.yaml"):
        print("❌ render.yaml not found")
        return False
    
    try:
        with open("render.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        # Check services
        if "services" not in config:
            print("❌ No services defined in render.yaml")
            return False
        
        service = config["services"][0]
        
        # Check required fields
        required_fields = ["name", "env", "buildCommand", "startCommand"]
        for field in required_fields:
            if field not in service:
                print(f"❌ Missing required field: {field}")
                return False
        
        # Check environment variables
        if "envVars" in service:
            env_vars = {var["key"]: var for var in service["envVars"]}
            required_env_vars = ["SECRET_KEY", "OPENAI_API_KEY", "ADMIN_PASSWORD"]
            
            for var in required_env_vars:
                if var not in env_vars:
                    print(f"❌ Missing required environment variable: {var}")
                    return False
        
        # Check database
        if "databases" not in config:
            print("❌ No database defined in render.yaml")
            return False
        
        print("✅ render.yaml configuration is valid")
        return True
        
    except yaml.YAMLError as e:
        print(f"❌ Invalid YAML syntax: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading render.yaml: {e}")
        return False

def test_requirements():
    """Test requirements-prod.txt"""
    print("🔍 Testing requirements-prod.txt...")
    
    if not os.path.exists("requirements-prod.txt"):
        print("❌ requirements-prod.txt not found")
        return False
    
    try:
        with open("requirements-prod.txt", "r") as f:
            requirements = f.read()
        
        required_packages = ["fastapi", "uvicorn", "psycopg2-binary", "sqlalchemy"]
        
        for package in required_packages:
            if package not in requirements:
                print(f"❌ Missing required package: {package}")
                return False
        
        print("✅ requirements-prod.txt is valid")
        return True
        
    except Exception as e:
        print(f"❌ Error reading requirements-prod.txt: {e}")
        return False

def test_production_app():
    """Test production app exists"""
    print("🔍 Testing production app...")
    
    if not os.path.exists("app/main_prod.py"):
        print("❌ app/main_prod.py not found")
        return False
    
    print("✅ Production app found")
    return True

def test_config():
    """Test configuration files"""
    print("🔍 Testing configuration...")
    
    if not os.path.exists("app/config_prod.py"):
        print("❌ app/config_prod.py not found")
        return False
    
    print("✅ Production configuration found")
    return True

def main():
    """Run all tests"""
    print("🚀 Testing Render deployment configuration")
    print("=" * 50)
    
    tests = [
        test_render_yaml,
        test_requirements,
        test_production_app,
        test_config
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your app is ready for Render deployment.")
        print("📋 Next steps:")
        print("   1. Push your code to GitHub")
        print("   2. Go to render.com and create a new web service")
        print("   3. Connect your GitHub repository")
        print("   4. Set your OPENAI_API_KEY environment variable")
        print("   5. Deploy!")
        return True
    else:
        print("❌ Some tests failed. Please fix the issues before deploying.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
