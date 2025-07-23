#!/usr/bin/env python3
"""
Script to convert unique browser steps into OpenAI training data.
Takes unique_steps.jsonl and generates Playwright code using OpenAI API.
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()



def extract_step_description(step: Dict[str, Any]) -> str:
    """
    Extract a human-readable description from a step for the user prompt.
    """
    description_parts = []
    
    # Extract current goal
    if 'model_output' in step and 'current_state' in step['model_output']:
        current_state = step['model_output']['current_state']
        if 'next_goal' in current_state:
            description_parts.append(current_state['next_goal'])
    
    # Extract actions performed
    if 'model_output' in step and 'action' in step['model_output']:
        actions = step['model_output']['action']
        action_descriptions = []
        
        for action in actions:
            if 'input_text' in action:
                text = action['input_text'].get('text', '')
                index = action['input_text'].get('index', '')
                action_descriptions.append(f"input '{text}' into field at index {index}")
            
            elif 'click_element_by_index' in action:
                index = action['click_element_by_index'].get('index', '')
                action_descriptions.append(f"click element at index {index}")
            
            elif 'go_to_url' in action:
                url = action['go_to_url'].get('url', '')
                action_descriptions.append(f"navigate to {url}")
            
            elif 'wait' in action:
                seconds = action['wait'].get('seconds', '')
                action_descriptions.append(f"wait {seconds} seconds")
            
            elif 'done' in action:
                text = action['done'].get('text', '')
                action_descriptions.append(f"complete task: {text}")
        
        if action_descriptions:
            description_parts.append("Actions: " + ", ".join(action_descriptions))
    
    # Extract results for context
    if 'result' in step:
        result_descriptions = []
        for result in step['result']:
            if 'extracted_content' in result:
                content = result['extracted_content']
                if content and not content.startswith('🕒'):  # Skip wait messages
                    result_descriptions.append(content)
        
        if result_descriptions:
            description_parts.append("Results: " + " | ".join(result_descriptions))
    
    # Extract URL context
    if 'state' in step and 'url' in step['state']:
        url = step['state']['url']
        if url and url != 'about:blank':
            description_parts.append(f"On page: {url}")
    
    # Combine all parts
    if description_parts:
        return ". ".join(description_parts)
    else:
        return "Perform browser automation step"


def extract_element_info(step: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract element information that can help with Playwright code generation.
    """
    elements = []
    
    if 'state' in step and 'interacted_element' in step['state']:
        for element in step['state']['interacted_element']:
            if element and isinstance(element, dict):
                element_info = {
                    'tag_name': element.get('tag_name', ''),
                    'xpath': element.get('xpath', ''),
                    'css_selector': element.get('css_selector', ''),
                    'attributes': element.get('attributes', {}),
                    'highlight_index': element.get('highlight_index', '')
                }
                elements.append(element_info)
    
    return elements


def create_playwright_prompt(step: Dict[str, Any]) -> str:
    """
    Create a detailed prompt for OpenAI to generate Playwright code.
    """
    description = extract_step_description(step)
    elements = extract_element_info(step)
    
    prompt_parts = [
        f"Generate Playwright code for this browser automation step: {step}",
    ]
    
    # Add action details
    # if 'model_output' in step and 'action' in step['model_output']:
    #     actions = step['model_output']['action']
    #     prompt_parts.append("Actions to perform:")
    #     for i, action in enumerate(actions, 1):
    #         prompt_parts.append(f"{i}. {json.dumps(action, indent=2)}")
    
    # # Add element details
    # if elements:
    #     prompt_parts.append("\nElements available:")
    #     for i, element in enumerate(elements, 1):
    #         if element['tag_name']:
    #             attrs = element['attributes']
    #             element_desc = f"{i}. {element['tag_name']}"
                
    #             # Add useful attributes
    #             if 'id' in attrs:
    #                 element_desc += f" id='{attrs['id']}'"
    #             if 'name' in attrs:
    #                 element_desc += f" name='{attrs['name']}'"
    #             if 'type' in attrs:
    #                 element_desc += f" type='{attrs['type']}'"
    #             if 'placeholder' in attrs:
    #                 element_desc += f" placeholder='{attrs['placeholder']}'"
                
    #             prompt_parts.append(element_desc)
    
    # # Add current URL
    # if 'state' in step and 'url' in step['state']:
    #     url = step['state']['url']
    #     if url and url != 'about:blank':
    #         prompt_parts.append(f"\nCurrent URL: {url}")
    
    prompt_parts.extend([
        "",
        "Generate concise, modern Playwright code using:",
        "- page.getByRole(), page.getByLabel(), page.getByText(), page.getByPlaceholder() when possible",
        "- page.locator() with CSS selectors as fallback",
        "- await expect() for assertions",
        "- Multiple lines for multiple actions",
        "- If the step is an iteration or a problem that does not progress the flow, return just a commented section with a summary of the step"
        "",
        "Return only the Playwright code, no explanations:"
    ])
    
    return "\n".join(prompt_parts)


def call_openai_api(client: OpenAI, prompt: str, max_retries: int = 3) -> Optional[str]:
    """
    Call OpenAI API with retry logic.
    """
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in Playwright test automation. Generate clean, modern Playwright code that follows best practices. Use semantic selectors when possible."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"OpenAI API error (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                return None
    
    return None


def process_steps_to_training_data(input_file: str, output_file: str, api_key: str) -> None:
    """
    Process unique steps and generate OpenAI training data.
    """
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Read input file
    with open(input_file, 'r', encoding='utf-8') as f:
        steps = [json.loads(line.strip()) for line in f if line.strip()]
    
    print(f"Processing {len(steps)} unique steps...")
    
    training_data = []
    successful_generations = 0
    
    for i, step in enumerate(steps, 1):
        print(f"Processing step {i}/{len(steps)}...")
        
        # Generate user description
        # user_description = extract_step_description(step)
        
        # Create detailed prompt for OpenAI
        playwright_prompt = create_playwright_prompt(step)
        
        # Call OpenAI API
        playwright_code = call_openai_api(client, playwright_prompt)
        playwright_code = playwright_code.split("```javascript")[1].split("```")[0]
        
        if playwright_code:
            # Create training data entry
            training_entry = {
                "messages": [
                    {
                        "role": "user",
                        "content": json.dumps(step, indent=2)
                    },
                    {
                        "role": "assistant", 
                        "content": playwright_code
                    }
                ]
            }
            
            training_data.append(training_entry)
            successful_generations += 1
            
            print(f"{training_entry}")
            # Add some delay to avoid rate limiting
            time.sleep(0.1)
        else:
            print(f"Failed to generate Playwright code for step {i}")

        if successful_generations >= 5:
            break
    
    print(f"Successfully generated {successful_generations}/{len(steps)} training examples")
    
    # Write output file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for entry in training_data:
            json.dump(entry, f, ensure_ascii=False)
            f.write('\n')
    
    print(f"Training data written to: {output_path}")


def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Generate OpenAI training data from unique browser steps"
    )
    parser.add_argument(
        '--input-file',
        default='unique_steps.jsonl',
        help='Input JSONL file with unique steps (default: unique_steps.jsonl)'
    )
    parser.add_argument(
        '--output-file',
        default='playwright_training_data.jsonl',
        help='Output JSONL file for training data (default: playwright_training_data.jsonl)'
    )
    parser.add_argument(
        '--api-key',
        help='OpenAI API key (or set OPENAI_API_KEY environment variable)'
    )
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OpenAI API key required. Set OPENAI_API_KEY environment variable or use --api-key")
        return
    
    # Resolve paths relative to script location
    script_dir = Path(__file__).parent
    input_file = script_dir / args.input_file
    output_file = script_dir / args.output_file
    
    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        return
    
    process_steps_to_training_data(str(input_file), str(output_file), api_key)


if __name__ == "__main__":
    main() 