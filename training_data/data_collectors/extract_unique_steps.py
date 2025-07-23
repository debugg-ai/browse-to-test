#!/usr/bin/env python3
"""
Script to parse browser history JSON files and extract unique steps into a JSONL file.
Each step represents a unique interaction or state transition in the browser automation.
"""

import json
import hashlib
import os
from pathlib import Path
from typing import Dict, Set, List, Any
import argparse


def generate_step_hash(step: Dict[str, Any]) -> str:
    """
    Generate a unique hash for a step based on its content.
    Uses the model output action and current state to create a unique identifier.
    """
    # Extract key components for hashing
    hash_components = []
    
    # Include model output action if present
    if 'model_output' in step and 'action' in step['model_output']:
        action_str = json.dumps(step['model_output']['action'], sort_keys=True)
        hash_components.append(action_str)
    
    # Include current state evaluation and goal if present
    if 'model_output' in step and 'current_state' in step['model_output']:
        current_state = step['model_output']['current_state']
        if 'evaluation_previous_goal' in current_state:
            hash_components.append(current_state['evaluation_previous_goal'])
        if 'next_goal' in current_state:
            hash_components.append(current_state['next_goal'])
    
    # Include URL if present in state
    if 'state' in step and 'url' in step['state']:
        hash_components.append(step['state']['url'])
    
    # Include result content if present
    if 'result' in step:
        result_content = []
        for result in step['result']:
            if 'extracted_content' in result:
                result_content.append(result['extracted_content'])
        if result_content:
            hash_components.append('|'.join(result_content))
    
    # Create hash from combined components
    combined_string = '|'.join(hash_components)
    return hashlib.sha256(combined_string.encode('utf-8')).hexdigest()


def extract_steps_from_json(json_file_path: str) -> List[Dict[str, Any]]:
    """
    Extract steps from a single JSON file.
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract history array
        if 'history' in data and isinstance(data['history'], list):
            return data['history']
        else:
            print(f"Warning: No 'history' array found in {json_file_path}")
            return []
    
    except Exception as e:
        print(f"Error reading {json_file_path}: {e}")
        return []


def process_browser_history_files(input_dir: str, output_file: str) -> None:
    """
    Process all JSON files in the input directory and extract unique steps.
    """
    input_path = Path(input_dir)
    unique_steps = {}  # hash -> step
    step_hashes: Set[str] = set()
    total_steps = 0
    
    print(f"Processing JSON files in: {input_path}")
    
    # Find all JSON files
    json_files = list(input_path.glob("*.json"))
    
    if not json_files:
        print(f"No JSON files found in {input_path}")
        return
    
    print(f"Found {len(json_files)} JSON files")
    
    # Process each JSON file
    for json_file in json_files:
        print(f"Processing: {json_file.name}")
        steps = extract_steps_from_json(str(json_file))
        
        for step in steps:
            total_steps += 1
            step_hash = generate_step_hash(step)
            
            if step_hash not in step_hashes:
                step_hashes.add(step_hash)
                # Add metadata about source file
                step_with_metadata = {
                    **step,
                    "source_file": json_file.name,
                    "step_hash": step_hash
                }
                unique_steps[step_hash] = step_with_metadata
    
    print(f"Total steps processed: {total_steps}")
    print(f"Unique steps found: {len(unique_steps)}")
    
    # Write unique steps to JSONL file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for step in unique_steps.values():
            json.dump(step, f, ensure_ascii=False)
            f.write('\n')
    
    print(f"Unique steps written to: {output_path}")


def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Extract unique steps from browser history JSON files"
    )
    parser.add_argument(
        '--input-dir',
        default='../sample_json_flows',
        help='Directory containing JSON files (default: ../sample_json_flows)'
    )
    parser.add_argument(
        '--output-file',
        default='unique_steps.jsonl',
        help='Output JSONL file name (default: unique_steps.jsonl)'
    )
    
    args = parser.parse_args()
    
    # Resolve paths relative to script location
    script_dir = Path(__file__).parent
    input_dir = script_dir / args.input_dir
    output_file = script_dir / args.output_file
    
    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        return
    
    process_browser_history_files(str(input_dir), str(output_file))


if __name__ == "__main__":
    main() 