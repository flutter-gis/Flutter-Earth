#!/usr/bin/env python3
"""
Quick Start Script for Flutter Earth
Bypasses heavy operations for faster startup
"""
import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

def setup_minimal_logging():
    """Setup minimal logging to reduce overhead"""
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    log_file = logs_dir / f"quick_start_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.WARNING,  # Reduced logging level
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, mode='w', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def quick_auth_check():
    """Quick auth check without heavy imports"""
    try:
        auth_dir = Path("C:/FE Auth")
        auth_config = auth_dir / "auth_config.json"
        
        if auth_config.exists():
            with open(auth_config, 'r') as f:
                config = json.load(f)
            
            project_id = config.get('project_id', '')
            key_file = config.get('key_file', '')
            
            if project_id and key_file and Path(key_file).exists():
                return {
                    "status": "auth_ready",
                    "message": "Authentication credentials found",
                    "initialized": False,
                    "auth_ready": True
                }
        
        return {
            "status": "auth_required",
            "message": "Authentication required",
            "initialized": False,
            "auth_ready": False
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Quick auth check failed: {e}",
            "initialized": False,
            "auth_ready": False
        }

def main():
    """Quick start main function"""
    logger = setup_minimal_logging()
    logger.info("=== Flutter Earth Quick Start ===")
    
    print("🚀 Flutter Earth - Quick Start")
    print("=" * 40)
    
    # Quick auth check
    auth_result = quick_auth_check()
    print(f"🔐 Auth Status: {auth_result['status']}")
    
    print("\n📱 Starting Electron app...")
    print("   The app will load faster with minimal initialization.")
    print("   Heavy operations will be deferred until needed.")
    
    # Start Electron app
    try:
        import subprocess
        import os
        
        # Change to frontend directory
        os.chdir("frontend")
        
        # Start Electron with minimal logging
        process = subprocess.Popen([
            "npm", "start"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("✅ Electron app started successfully!")
        print("   The application should open shortly.")
        print("\n💡 Tips for better performance:")
        print("   - Close other applications to free up memory")
        print("   - Ensure you have at least 2GB of free disk space")
        print("   - Run 'python performance_optimizer.py' if issues persist")
        
        return 0
        
    except Exception as e:
        print(f"❌ Failed to start Electron app: {e}")
        print("\n🔧 Alternative startup methods:")
        print("   1. Navigate to frontend/ and run: npm start")
        print("   2. Run: run_desktop.bat")
        print("   3. Run: python main.py")
        
        return 1

if __name__ == "__main__":
    sys.exit(main()) 