#!/usr/bin/env python3
"""
Test script for AI3D Studio API
"""
import requests
import json

def test_generation():
    try:
        # Test health endpoint
        print("Testing health endpoint...")
        health_response = requests.get("http://127.0.0.1:5000/health")
        print(f"Health Status: {health_response.status_code}")
        print(f"Health Response: {health_response.json()}")
        
        # Test generation endpoint
        print("\nTesting generation endpoint...")
        generation_data = {
            "prompt": "a red cube",
            "complexity": 5
        }
        
        gen_response = requests.post(
            "http://127.0.0.1:5000/api/generate",
            json=generation_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Generation Status: {gen_response.status_code}")
        if gen_response.status_code == 200:
            result = gen_response.json()
            print(f"Generation Response: {json.dumps(result, indent=2)}")
            
            # Test download
            if result.get('success'):
                job_id = result.get('job_id')
                print(f"\nTesting download for job {job_id}...")
                download_response = requests.get(f"http://127.0.0.1:5000/api/download/{job_id}")
                print(f"Download Status: {download_response.status_code}")
                if download_response.status_code == 200:
                    print("Download successful!")
                    with open(f"test_model_{job_id}.obj", "wb") as f:
                        f.write(download_response.content)
                    print(f"Saved as test_model_{job_id}.obj")
                else:
                    print(f"Download failed: {download_response.text}")
        else:
            print(f"Generation failed: {gen_response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_generation()
