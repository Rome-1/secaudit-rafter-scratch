#!/usr/bin/env python3
"""
Script to reproduce the issue described in the PR.
This script tests different authentication and storage configurations
to ensure the fix works correctly.
"""
import os
import tempfile
import yaml
import subprocess
import time
import signal

def create_config_file(auth_config, storage_config):
    """Create a temporary config file with given auth and storage settings."""
    config = {
        'log': {'level': 'DEBUG'},
        'server': {
            'host': '127.0.0.1',
            'grpc_port': 9001,
            'http_port': 8081,
        },
        'authentication': auth_config,
        'storage': storage_config
    }
    
    # Create temporary file
    fd, path = tempfile.mkstemp(suffix='.yml', prefix='flipt_test_')
    with os.fdopen(fd, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    return path

def test_config(description, auth_config, storage_config, should_require_db=True):
    """Test a configuration and check if it starts without database."""
    print(f"\n--- Testing: {description} ---")
    
    config_path = create_config_file(auth_config, storage_config)
    try:
        # Try to start flipt with this configuration
        cmd = ['/app/bin/flipt', '--config', config_path]
        print(f"Running: {' '.join(cmd)}")
        
        # Start the process
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a bit for startup
        time.sleep(2)
        
        # Check if process is still running
        poll_result = proc.poll()
        
        if poll_result is None:
            # Process is still running, that's good
            print("✅ Process started successfully")
            proc.terminate()
            proc.wait(timeout=5)
            success = True
        else:
            # Process exited, check why
            stdout, stderr = proc.communicate()
            print("❌ Process exited early")
            print("STDOUT:", stdout[:500] + ("..." if len(stdout) > 500 else ""))
            print("STDERR:", stderr[:500] + ("..." if len(stderr) > 500 else ""))
            success = False
            
            # Look for database connection errors
            database_error = any(keyword in stderr.lower() for keyword in [
                'database', 'sql', 'connection', 'migrate', 'driver'
            ])
            
            if database_error and not should_require_db:
                print("❌ FAILED: Database connection attempted when it shouldn't be required")
            elif not database_error and should_require_db:
                print("⚠️  WARNING: Expected database error but didn't find one")
            elif database_error and should_require_db:
                print("✅ EXPECTED: Database connection required as expected")
            else:
                print("❓ UNCLEAR: Unexpected exit reason")
        
        return success
        
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False
    finally:
        # Clean up
        if os.path.exists(config_path):
            os.unlink(config_path)

def main():
    print("Testing JWT authentication with non-database storage configurations...")
    
    # First, build flipt if needed
    print("Building flipt...")
    try:
        subprocess.run(['make', 'build'], cwd='/app', check=True, capture_output=True)
        print("✅ Build successful")
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return
    
    # Test cases
    test_cases = [
        {
            'description': 'JWT + Local storage (should NOT require DB)',
            'auth_config': {
                'required': True,
                'methods': {
                    'jwt': {
                        'enabled': True,
                        'public_key_file': '/tmp/non_existent_key.pem'  # We'll handle validation error
                    }
                }
            },
            'storage_config': {
                'type': 'local',
                'local': {'path': '/tmp/flipt_test_flags'}
            },
            'should_require_db': False
        },
        {
            'description': 'JWT + Git storage (should NOT require DB)',
            'auth_config': {
                'required': True,
                'methods': {
                    'jwt': {
                        'enabled': True,
                        'jwks_url': 'https://example.com/.well-known/jwks.json'
                    }
                }
            },
            'storage_config': {
                'type': 'git',
                'git': {'repository': '/tmp/nonexistent', 'ref': 'main'}
            },
            'should_require_db': False
        },
        {
            'description': 'JWT + OCI storage (should NOT require DB)',
            'auth_config': {
                'required': True,
                'methods': {
                    'jwt': {
                        'enabled': True,
                        'jwks_url': 'https://example.com/.well-known/jwks.json'
                    }
                }
            },
            'storage_config': {
                'type': 'oci',
                'oci': {'repository': 'example.com/flags:latest'}
            },
            'should_require_db': False
        },
        {
            'description': 'Token + Local storage (should require DB)',
            'auth_config': {
                'required': True,
                'methods': {
                    'token': {
                        'enabled': True
                    }
                }
            },
            'storage_config': {
                'type': 'local',
                'local': {'path': '/tmp/flipt_test_flags'}
            },
            'should_require_db': True
        },
        {
            'description': 'No auth + Local storage (should NOT require DB)',
            'auth_config': {
                'required': False,
                'methods': {}
            },
            'storage_config': {
                'type': 'local',
                'local': {'path': '/tmp/flipt_test_flags'}
            },
            'should_require_db': False
        }
    ]
    
    # Create test directories
    os.makedirs('/tmp/flipt_test_flags', exist_ok=True)
    
    results = []
    for test_case in test_cases:
        success = test_config(
            test_case['description'],
            test_case['auth_config'],
            test_case['storage_config'],
            test_case['should_require_db']
        )
        results.append(success)
    
    print(f"\n--- Summary ---")
    print(f"Passed: {sum(results)}/{len(results)} tests")
    
    if all(results):
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed")

if __name__ == '__main__':
    main()