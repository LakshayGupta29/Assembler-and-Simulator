#!/usr/bin/env python3
"""
Test script to validate all example programs work correctly.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ Success")
            return True
        else:
            print(f"  ✗ Failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    """Test all example programs."""
    print("Testing RISC-V Assembler and Simulator Examples")
    print("=" * 50)
    
    # Get the directory containing this script
    script_dir = Path(__file__).parent
    examples_dir = script_dir / "examples"
    
    if not examples_dir.exists():
        print("❌ Examples directory not found!")
        return False
    
    # Find all .asm files in examples directory
    asm_files = list(examples_dir.glob("*.asm"))
    
    if not asm_files:
        print("❌ No assembly files found in examples directory!")
        return False
    
    print(f"Found {len(asm_files)} example programs:")
    for f in asm_files:
        print(f"  - {f.name}")
    print()
    
    success_count = 0
    total_count = len(asm_files)
    
    # Create output directory for test results
    output_dir = script_dir / "test_output"
    output_dir.mkdir(exist_ok=True)
    
    for asm_file in asm_files:
        name = asm_file.stem
        bin_file = output_dir / f"{name}.bin"
        trace_file = output_dir / f"{name}_trace.txt"
        
        print(f"Testing {name}:")
        
        # Assemble
        assemble_cmd = f"python3 {script_dir}/Assembler.py {asm_file} {bin_file}"
        assemble_success = run_command(assemble_cmd, f"  Assembling {name}")
        
        if not assemble_success:
            continue
            
        # Simulate
        simulate_cmd = f"python3 {script_dir}/Simulator.py {bin_file} {trace_file}"
        simulate_success = run_command(simulate_cmd, f"  Simulating {name}")
        
        if assemble_success and simulate_success:
            success_count += 1
            print(f"  ✓ {name} completed successfully")
            print(f"    Binary: {bin_file}")
            print(f"    Trace: {trace_file}")
        else:
            print(f"  ✗ {name} failed")
        print()
    
    print("=" * 50)
    print(f"Results: {success_count}/{total_count} tests passed")
    
    if success_count == total_count:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)