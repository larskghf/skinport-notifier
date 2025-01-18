import time
import hmac
import hashlib
import requests
import schedule
import json
import argparse
from datetime import datetime, UTC
from config import *

# Dictionary to store the last known state for each item
last_known_states = {}

# Global flag for JSON saving
should_save_json = False

def generate_signature(method: str, path: str, body: str = "") -> str:
    """Generate signature for Skinport API authentication."""
    timestamp = str(int(time.time()))
    message = f"{method}{path}{timestamp}{body}"
    signature = hmac.new(
        SKINPORT_API_SECRET.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    return timestamp, signature

def send_rate_limit_notification():
    """Send a notification to Discord when rate limit is hit."""
    embed = {
        "title": "⚠️ Rate Limit Hit",
        "description": "The Skinport API rate limit has been reached.",
        "color": 15158332,  # Red color
        "fields": [
            {
                "name": "🕐 Pause Duration",
                "value": f"{RATE_LIMIT_DELAY // 60} minutes",
                "inline": True
            },
            {
                "name": "⏰ Resume Time",
                "value": f"<t:{int(time.time() + RATE_LIMIT_DELAY)}:R>",  # Discord timestamp, shows "in X minutes"
                "inline": True
            }
        ],
        "timestamp": datetime.now(UTC).isoformat()
    }
    
    payload = {
        "embeds": [embed]
    }
    
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    if response.status_code != 204:
        print(f"Error sending rate limit notification: {response.status_code}")

def get_skinport_items():
    """Fetch items from Skinport API."""
    method = "GET"
    path = "/items"
    timestamp, signature = generate_signature(method, path)
    
    headers = {
        "X-API-Key": SKINPORT_API_KEY,
        "X-Signature": signature,
        "X-Timestamp": timestamp,
        "Accept": "application/json",
        "Accept-Encoding": "br",  # Request Brotli compression
        "User-Agent": "Skinport-Bot/1.0"
    }
    
    params = {
        "currency": "EUR",
        "app_id": "730"  # CS:GO App ID
    }
    
    response = requests.get(
        f"{SKINPORT_API_URL}{path}",
        headers=headers,
        params=params
    )
    
    if response.status_code == 200:
        items = response.json()
        
        # Save items to JSON file only if flag is set
        if should_save_json:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"items_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(items, f, indent=2, ensure_ascii=False)
                print(f"Saved items to {filename}")
            
        return items
    elif response.status_code == 429:  # Rate limit hit
        print(f"Rate limit hit. Pausing for {RATE_LIMIT_DELAY // 60} minutes...")
        send_rate_limit_notification()
        time.sleep(RATE_LIMIT_DELAY)
        return None
    else:
        print(f"Error fetching items: {response.status_code}")
        if response.text:
            print(f"Error details: {response.text}")
        return None

def send_discord_notification(item, changes):
    """Send notification to Discord webhook."""
    change_descriptions = []
    
    if 'quantity_change' in changes:
        quantity_change = changes['quantity_change']
        change_descriptions.append(f"Quantity increased by {quantity_change}")
    
    if 'price_change' in changes:
        old_price = changes['price_change']['old']
        new_price = changes['price_change']['new']
        price_diff = old_price - new_price
        
        if 'threshold' in changes['price_change']:
            threshold = changes['price_change']['threshold']
            change_descriptions.append(f"💰 Price dropped below €{threshold:.2f} threshold!")
            change_descriptions.append(f"Price decreased by €{price_diff:.2f} (from €{old_price:.2f} to €{new_price:.2f})")
        else:
            change_descriptions.append(f"Price decreased by €{price_diff:.2f} (from €{old_price:.2f} to €{new_price:.2f})")
    
    embed = {
        "title": "🔔 New Listing Alert!",
        "description": f"**{item['market_hash_name']}**\n" + "\n".join(change_descriptions),
        "color": 5814783,
        "fields": [
            {
                "name": "Current Price",
                "value": f"€{item['min_price']:.2f}",
                "inline": True
            },
            {
                "name": "Suggested Price",
                "value": f"€{item['suggested_price']:.2f}",
                "inline": True
            },
            {
                "name": "Available Quantity",
                "value": str(item['quantity']),
                "inline": True
            }
        ],
        "timestamp": datetime.now(UTC).isoformat(),
        "url": item['market_page']
    }
    
    payload = {
        "embeds": [embed]
    }
    
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    if response.status_code != 204:
        print(f"Error sending Discord notification: {response.status_code}")

def check_for_new_items():
    """Check for target items on Skinport."""
    items = get_skinport_items()
    if not items:
        return
    
    # Create a dictionary for faster item lookup
    items_dict = {item['market_hash_name']: item for item in items}
    
    # Check each target item
    for target_item, price_threshold in TARGET_ITEMS.items():
        if target_item in items_dict:
            item = items_dict[target_item]
            current_state = {
                'quantity': item['quantity'],
                'min_price': item['min_price']
            }
            
            last_state = last_known_states.get(target_item)
            changes = {}
            
            if last_state is not None:
                # If no price threshold is set, check both quantity and price
                if price_threshold is None:
                    # Check for quantity increase
                    if current_state['quantity'] > last_state['quantity']:
                        changes['quantity_change'] = current_state['quantity'] - last_state['quantity']
                    
                    # Check for any price decrease
                    if current_state['min_price'] < last_state['min_price']:
                        changes['price_change'] = {
                            'old': last_state['min_price'],
                            'new': current_state['min_price']
                        }
                
                # If price threshold is set, only check for prices below threshold
                else:
                    # Check if price dropped below threshold
                    if current_state['min_price'] < price_threshold and (
                        last_state['min_price'] >= price_threshold or  # Price just dropped below threshold
                        current_state['min_price'] < last_state['min_price']  # Price decreased further while below threshold
                    ):
                        changes['price_change'] = {
                            'old': last_state['min_price'],
                            'new': current_state['min_price'],
                            'threshold': price_threshold
                        }
                
                # Send notification if there are any relevant changes
                if changes:
                    print(f"Changes detected for {target_item}:")
                    if 'quantity_change' in changes:
                        print(f"- Quantity increased by {changes['quantity_change']}")
                    if 'price_change' in changes:
                        print(f"- Price decreased from €{changes['price_change']['old']:.2f} to €{changes['price_change']['new']:.2f}")
                        if 'threshold' in changes['price_change']:
                            print(f"  (Below threshold of €{changes['price_change']['threshold']:.2f})")
                    send_discord_notification(item, changes)
            
            # Update the last known state
            last_known_states[target_item] = current_state
            
            # Print status message
            if last_state is None:
                status = f"Initial state for {target_item}: {current_state['quantity']} items at €{current_state['min_price']:.2f}"
                if price_threshold is not None:
                    status += f" (Threshold: €{price_threshold:.2f})"
                print(status)
            else:
                status = f"Current state for {target_item}: {current_state['quantity']} items at €{current_state['min_price']:.2f}"
                if price_threshold is not None:
                    status += f" (Threshold: €{price_threshold:.2f})"
                print(status)
        else:
            print(f"Item not found: {target_item}")

def send_startup_notification():
    """Send a startup notification to Discord with monitoring overview."""
    # Create a formatted list of monitored items with their thresholds
    monitored_items = []
    for item, threshold in TARGET_ITEMS.items():
        if threshold is None:
            monitored_items.append(f"• **{item}**\n  └ Monitoring quantity & price changes")
        else:
            monitored_items.append(f"• **{item}**\n  └ Alert when price drops below €{threshold:.2f}")
    
    embed = {
        "title": "🚀 Skinport Monitor Started",
        "description": "Bot has been started and is monitoring the following items:",
        "color": 3066993,  # Green color
        "fields": [
            {
                "name": "📊 Monitored Items",
                "value": "\n".join(monitored_items),
                "inline": False
            },
            {
                "name": "⏱️ Check Interval",
                "value": f"Every {CHECK_INTERVAL} minute{'s' if CHECK_INTERVAL != 1 else ''}",
                "inline": True
            },
            {
                "name": "💾 JSON Saving",
                "value": "Enabled" if should_save_json else "Disabled",
                "inline": True
            }
        ],
        "timestamp": datetime.now(UTC).isoformat(),
        "thumbnail": {
            "url": "https://skinport.com/static/logo/skinport.png"
        }
    }
    
    payload = {
        "embeds": [embed]
    }
    
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    if response.status_code != 204:
        print(f"Error sending startup notification: {response.status_code}")

def main():
    """Main function to run the bot."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Skinport Item Monitor')
    parser.add_argument('--save-json', action='store_true', help='Save API responses to JSON files')
    args = parser.parse_args()
    
    # Set global flag
    global should_save_json
    should_save_json = args.save_json
    
    print("Starting Skinport Monitor Bot...")
    if should_save_json:
        print("JSON saving is enabled")
    print(f"Monitoring {len(TARGET_ITEMS)} items:")
    for item in TARGET_ITEMS:
        print(f"- {item}")
    print(f"Check interval: {CHECK_INTERVAL} minutes")
    
    # Send startup notification
    send_startup_notification()
    
    # Schedule the check to run every X minutes
    schedule.every(CHECK_INTERVAL).minutes.do(check_for_new_items)
    
    # Run initial check
    check_for_new_items()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main() 