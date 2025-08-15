#!/usr/bin/env python3
"""
Dimension (dim) Sensitivity Analysis for Salinas Dataset
This script runs experiments with different dim values: 64, 128, 256, 512
Compatible with Windows, Cursor IDE, and conda environments
"""

import os
import json
import subprocess
import sys
import shutil
import glob
from datetime import datetime
import time

def load_config(config_path):
    """Load JSON configuration file"""
    with open(config_path, 'r') as f:
        return json.load(f)

def save_config(config_path, config_data):
    """Save JSON configuration file"""
    with open(config_path, 'w') as f:
        json.dump(config_data, f, indent=4)

def update_dim(config_path, dim_value):
    """Update dim value in net section of config file"""
    print(f"Updating dim to {dim_value} in {config_path}")
    
    config_data = load_config(config_path)
    config_data['net']['dim'] = dim_value
    save_config(config_path, config_data)
    
    print(f"Updated net dim to: {dim_value}")

def find_latest_file(directory, pattern):
    """Find the most recently created file matching pattern"""
    if not os.path.exists(directory):
        return None
    
    files = glob.glob(os.path.join(directory, pattern))
    if not files:
        return None
    
    # Get the most recent file by creation time
    latest_file = max(files, key=os.path.getctime)
    return latest_file

def rename_output_files(dim_value):
    """Rename output files with dim identifier"""
    dim_id = f"dim_{dim_value}"
    print(f"Renaming output files with dim identifier: {dim_id}")
    
    # Rename results file
    results_dir = "results"
    latest_result = find_latest_file(results_dir, "Salinas_Hyper2DRoPE_Classification_Model*.json")
    
    if latest_result:
        base_name = os.path.splitext(os.path.basename(latest_result))[0]
        new_result_name = f"{base_name}_{dim_id}.json"
        new_result_path = os.path.join(results_dir, new_result_name)
        
        shutil.move(latest_result, new_result_path)
        print(f"Renamed result file to: {new_result_name}")
    else:
        print("Warning: No result file found to rename")
    
    # Rename checkpoint file
    checkpoints_dir = "checkpoints"
    latest_checkpoint = find_latest_file(checkpoints_dir, "*.pth")
    
    if latest_checkpoint:
        base_name = os.path.splitext(os.path.basename(latest_checkpoint))[0]
        new_checkpoint_name = f"{base_name}_{dim_id}.pth"
        new_checkpoint_path = os.path.join(checkpoints_dir, new_checkpoint_name)
        
        shutil.move(latest_checkpoint, new_checkpoint_path)
        print(f"Renamed checkpoint file to: {new_checkpoint_name}")
    else:
        print("Warning: No checkpoint file found to rename")

def run_experiment(dim_value):
    """Run a single experiment with given dim value"""
    print(f"\n{'='*50}")
    print(f"Running experiment with dim: {dim_value}")
    print(f"{'='*50}")
    
    config_file = os.path.join("configs", "hyper2Drope.json")
    
    # Update configuration
    update_dim(config_file, dim_value)
    
    # Verify the update
    config_data = load_config(config_file)
    current_dim = config_data['net']['dim']
    print(f"Verified dim in config: {current_dim}")
    
    # Run the experiment
    print("Starting training...")
    start_time = time.time()
    
    try:
        # Run python main.py with default arguments
        result = subprocess.run([
            sys.executable, "main.py", 
            "--config", "hyper2Drope.json",
            "--dataset", "Salinas", 
            "--model", "Hyper2DRoPE"
        ], capture_output=True, text=True, timeout=7200)  # 2 hour timeout
        
        if result.returncode == 0:
            end_time = time.time()
            duration = end_time - start_time
            print(f"Experiment completed successfully in {duration:.2f} seconds")
            
            # Rename output files
            rename_output_files(dim_value)
            print("Files renamed successfully")
            return True
        else:
            print(f"Error: Experiment failed for dim {dim_value}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"Error: Experiment timed out for dim {dim_value}")
        return False
    except Exception as e:
        print(f"Error: Exception occurred during experiment: {str(e)}")
        return False

def main():
    """Main function to run all dim experiments"""
    print("Starting dim sensitivity analysis for Salinas dataset...")
    print("Dim values: 64, 128, 256, 512")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    config_file = os.path.join("configs", "hyper2Drope.json")
    
    # Create backup of original config
    backup_file = f"{config_file}.backup"
    shutil.copy2(config_file, backup_file)
    print(f"Created backup of original config file: {backup_file}")
    
    # Create output directories if they don't exist
    os.makedirs("results", exist_ok=True)
    os.makedirs("checkpoints", exist_ok=True)
    
    # Dim values to test
    dim_values = [64, 128, 256, 512]
    successful_experiments = []
    failed_experiments = []
    
    try:
        for dim_value in dim_values:
            success = run_experiment(dim_value)
            
            if success:
                successful_experiments.append(dim_value)
                print(f"Experiment dim_{dim_value} completed successfully")
            else:
                failed_experiments.append(dim_value)
                print(f"Experiment dim_{dim_value} failed")
                
                # Ask user if they want to continue
                response = input(f"Experiment failed for dim {dim_value}. Continue with remaining experiments? (y/n): ")
                if response.lower() != 'y':
                    print("Stopping experiments as requested.")
                    break
            
            print()  # Add blank line between experiments
            
    except KeyboardInterrupt:
        print("\nExperiments interrupted by user.")
    
    finally:
        # Restore original configuration
        print("Restoring original configuration...")
        shutil.copy2(backup_file, config_file)
        os.remove(backup_file)
        
        # Print summary
        print(f"\n{'='*50}")
        print("EXPERIMENT SUMMARY")
        print(f"{'='*50}")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Successful experiments: {len(successful_experiments)}")
        print(f"Failed experiments: {len(failed_experiments)}")
        
        if successful_experiments:
            print(f"Successful dim values: {successful_experiments}")
        
        if failed_experiments:
            print(f"Failed dim values: {failed_experiments}")
        
        print(f"Results files are in: results/")
        print(f"Checkpoint files are in: checkpoints/")
        print("Original configuration has been restored.")

if __name__ == "__main__":
    main()