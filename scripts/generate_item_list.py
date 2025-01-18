#!/usr/bin/env python3
import json
import glob
import os

def generate_item_list():
    # Find the most recent items JSON file
    json_files = glob.glob("items_*.json")
    if not json_files:
        print("No items JSON file found!")
        return
    
    latest_file = max(json_files)
    
    # Read and parse the JSON file
    with open(latest_file, 'r', encoding='utf-8') as f:
        items = json.load(f)
    
    # Extract and sort unique market_hash_names
    market_hash_names = sorted(set(item['market_hash_name'] for item in items))
    
    # Generate markdown content
    markdown_content = """# Available Skinport Items

This is a list of all available item names that can be used for monitoring. The list is automatically generated from the Skinport API.

## How to Use
1. Copy the exact item name you want to monitor
2. Add it to your `config.py` in the `TARGET_ITEMS` dictionary
3. Set an optional price threshold or `None` for full monitoring

## Available Items
"""
    
    # Add items to markdown
    for name in market_hash_names:
        markdown_content += f"- `{name}`\n"
    
    # Add footer with timestamp
    with open(latest_file, 'r', encoding='utf-8') as f:
        timestamp = latest_file.replace('items_', '').replace('.json', '')
        markdown_content += f"\n\n*Last updated: {timestamp}*"
    
    # Write to ITEMS.md
    with open("ITEMS.md", 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"Generated ITEMS.md with {len(market_hash_names)} items")

if __name__ == "__main__":
    generate_item_list() 