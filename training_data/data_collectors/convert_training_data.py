#!/usr/bin/env python3
"""
Script to convert browse_to_test_real_examples.jsonl to a simple messages format.

Current format:
{"input": "Navigate to the login page at https://example.com/login", "output": "await page.goto('https://example.com/login');"}

Target format:
{
  "messages": [
    { "role": "user", "content": "What is the weather in San Francisco?" },
    { "role": "assistant", "content": "whatever the output should be" }
  ]
}
"""

import json
import argparse
from pathlib import Path


def convert_entry(entry: dict) -> dict:
    """Convert a single entry from the original format to the target format."""
    input_text = entry["input"]
    output_code = entry["output"]
    
    return {
        "messages": [
            {
                "role": "user",
                "content": input_text
            },
            {
                "role": "assistant",
                "content": output_code
            }
        ]
    }


def convert_jsonl_file(input_file: Path, output_file: Path) -> None:
    """Convert the entire JSONL file to the new format."""
    converted_entries = []
    
    print(f"Reading from: {input_file}")
    
    # Read and convert each line
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
                
            try:
                entry = json.loads(line)
                converted_entry = convert_entry(entry)
                converted_entries.append(converted_entry)
            except json.JSONDecodeError as e:
                print(f"Error parsing line {line_num}: {e}")
                continue
    
    print(f"Successfully converted {len(converted_entries)} entries")
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in converted_entries:
            json.dump(entry, f, ensure_ascii=False)
            f.write('\n')
    
    print(f"Output written to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Convert browse_to_test training data format")
    parser.add_argument(
        "--input", 
        type=Path, 
        default="browse_to_test_real_examples.jsonl",
        help="Input JSONL file (default: browse_to_test_real_examples.jsonl)"
    )
    parser.add_argument(
        "--output", 
        type=Path, 
        default="browse_to_test_converted.jsonl",
        help="Output JSONL file (default: browse_to_test_converted.jsonl)"
    )
    
    args = parser.parse_args()
    
    if not args.input.exists():
        print(f"Error: Input file {args.input} does not exist")
        return 1
    
    try:
        convert_jsonl_file(args.input, args.output)
        print("Conversion completed successfully!")
        return 0
    except Exception as e:
        print(f"Error during conversion: {e}")
        return 1


if __name__ == "__main__":
    exit(main()) 