#!/usr/bin/env python
import sys
import subprocess
import pkg_resources

def check_requirements():
    with open('requirements.txt', 'r') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    missing = []
    for requirement in requirements:
        try:
            pkg_resources.require(requirement)
            print(f" {requirement}")
        except pkg_resources.DistributionNotFound:
            missing.append(requirement)
            print(f" {requirement}")
        except pkg_resources.VersionConflict as e:
            print(f"  Version conflict: {e}")
    
    if missing:
        print(f"\n Missing packages: {', '.join(missing)}")
        print("\nInstall with: pip install -r requirements.txt")
        return False
    
    print("\n All requirements satisfied!")
    return True

if __name__ == "__main__":
    if check_requirements():
        sys.exit(0)
    else:
        sys.exit(1)