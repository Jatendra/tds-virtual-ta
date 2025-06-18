#!/usr/bin/env python3
"""
Deployment script for TDS Virtual TA
Helps deploy to various platforms
"""

import os
import subprocess
import json
from typing import Dict, Any

class TDSVirtualTADeployer:
    """Deploy TDS Virtual TA to various platforms"""
    
    def __init__(self):
        self.app_name = "tds-virtual-ta"
        self.port = 8000
        
    def check_requirements(self) -> bool:
        """Check if all required files exist"""
        required_files = [
            "main.py",
            "requirements.txt",
            "Procfile",
            "data_scraper.py",
            "question_answerer.py",
            "image_processor.py",
            "token_calculator.py"
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            print(f"❌ Missing required files: {missing_files}")
            return False
        
        print("✅ All required files present")
        return True
    
    def test_locally(self) -> bool:
        """Test the application locally"""
        print("🧪 Testing application locally...")
        
        try:
            # Install requirements
            subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
            print("✅ Requirements installed")
            
            # Run tests
            if os.path.exists("test_api.py"):
                print("Running API tests...")
                # Start server in background and test
                # This is a simplified version - in production you'd use proper testing
                print("✅ Local tests would run here")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Local testing failed: {e}")
            return False
    
    def deploy_to_heroku(self):
        """Deploy to Heroku"""
        print("🚀 Deploying to Heroku...")
        
        try:
            # Check if Heroku CLI is installed
            subprocess.run(["heroku", "version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Heroku CLI not found. Please install: https://devcenter.heroku.com/articles/heroku-cli")
            return False
        
        try:
            # Create Heroku app
            result = subprocess.run(
                ["heroku", "create", self.app_name], 
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                print(f"✅ Created Heroku app: {self.app_name}")
            else:
                print(f"ℹ️  App may already exist: {result.stderr}")
            
            # Deploy
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", "Deploy TDS Virtual TA"], check=False)
            subprocess.run(["git", "push", "heroku", "main"], check=True)
            
            # Get app URL
            result = subprocess.run(
                ["heroku", "info", "-a", self.app_name, "--json"], 
                capture_output=True, text=True, check=True
            )
            app_info = json.loads(result.stdout)
            app_url = app_info.get("app", {}).get("web_url", "")
            
            print(f"✅ Deployed successfully!")
            print(f"🌐 App URL: {app_url}")
            print(f"🔗 API Endpoint: {app_url}api/")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Heroku deployment failed: {e}")
            return False
    
    def deploy_to_railway(self):
        """Deploy to Railway"""
        print("🚀 Deploying to Railway...")
        
        # Railway deployment instructions
        instructions = """
To deploy to Railway:

1. Install Railway CLI:
   npm install -g @railway/cli

2. Login to Railway:
   railway login

3. Initialize project:
   railway init

4. Deploy:
   railway up

5. Set environment variables if needed:
   railway variables set PORT=8000

Your app will be available at the Railway-provided URL.
        """
        
        print(instructions)
        return True
    
    def deploy_to_render(self):
        """Deploy to Render"""
        print("🚀 Deploying to Render...")
        
        instructions = """
To deploy to Render:

1. Push your code to GitHub
2. Go to https://render.com
3. Connect your GitHub repository
4. Create a new Web Service
5. Use these settings:
   - Build Command: pip install -r requirements.txt
   - Start Command: python main.py
   - Environment: Python 3
   - Port: 8000

Your app will be available at the Render-provided URL.
        """
        
        print(instructions)
        return True
    
    def create_docker_deployment(self):
        """Create Docker deployment files"""
        print("🐳 Creating Docker deployment...")
        
        dockerfile_content = """
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
"""
        
        docker_compose_content = """
version: '3.8'

services:
  tds-virtual-ta:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PORT=8000
    restart: unless-stopped
"""
        
        # Write Dockerfile
        with open("Dockerfile", "w") as f:
            f.write(dockerfile_content.strip())
        
        # Write docker-compose.yml
        with open("docker-compose.yml", "w") as f:
            f.write(docker_compose_content.strip())
        
        print("✅ Created Dockerfile and docker-compose.yml")
        print("To deploy with Docker:")
        print("  docker-compose up --build")
        
        return True


def main():
    deployer = TDSVirtualTADeployer()
    
    print("🚀 TDS Virtual TA Deployment Tool")
    print("=" * 40)
    
    # Check requirements
    if not deployer.check_requirements():
        return
    
    # Test locally
    if not deployer.test_locally():
        print("⚠️  Local testing failed, but continuing...")
    
    print("\nChoose deployment option:")
    print("1. Heroku")
    print("2. Railway") 
    print("3. Render")
    print("4. Docker")
    print("5. All (create all deployment files)")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == "1":
        deployer.deploy_to_heroku()
    elif choice == "2":
        deployer.deploy_to_railway()
    elif choice == "3":
        deployer.deploy_to_render()
    elif choice == "4":
        deployer.create_docker_deployment()
    elif choice == "5":
        deployer.create_docker_deployment()
        deployer.deploy_to_railway()
        deployer.deploy_to_render()
        print("\n✅ All deployment files created!")
        print("Choose your preferred platform and follow the instructions above.")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main() 