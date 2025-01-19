# Skinport Price Monitor

[![Build and Push Docker Image](https://github.com/larskghf/skinport-notifier/actions/workflows/docker-build.yml/badge.svg)](https://github.com/larskghf/skinport-notifier/actions/workflows/docker-build.yml)

A Discord bot that monitors Skinport.com for CS2 item prices and sends notifications when items are listed below your target price or when new quantities become available.

## Features

- 🔍 Monitor specific CS2 items on Skinport
- 💰 Set price thresholds for notifications
- 📊 Track quantity changes
- 🔔 Discord webhook notifications with detailed information
- 🐳 Docker & Kubernetes support
- ⚡ Rate limit handling with automatic pausing
- 🔄 Regular price checks (configurable interval)

## Prerequisites

- Python 3.13+
- Skinport API credentials
- Discord webhook URL
- Docker (optional)
- Kubernetes (optional)

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/larskghf/skinport-notifier.git
cd skinport-notifier
```

2. Create a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file with your credentials:
```env
SKINPORT_API_KEY=your_api_key
SKINPORT_API_SECRET=your_api_secret
DISCORD_WEBHOOK_URL=your_webhook_url
```

5. Configure items to monitor in `config.py`:
```python
TARGET_ITEMS = {
    "★ Falchion Knife | Gamma Doppler (Factory New)": 350.00,  # Alert when below 350€
    "M4A4 | Etch Lord (Minimal Wear)": None,  # Monitor quantity & price
}
```

6. Run the bot:
```bash
python main.py
```

## Docker Usage

Pull and run the container:
```bash
docker run -d \
  -e SKINPORT_API_KEY=your_api_key \
  -e SKINPORT_API_SECRET=your_api_secret \
  -e DISCORD_WEBHOOK_URL=your_webhook_url \
  ghcr.io/larskghf/skinport-notifier:latest
```

## Kubernetes Deployment

1. Create secrets:
```bash
kubectl create secret generic skinport-bot-secrets \
  --from-literal=SKINPORT_API_KEY=your_api_key \
  --from-literal=SKINPORT_API_SECRET=your_api_secret \
  --from-literal=DISCORD_WEBHOOK_URL=your_webhook_url
```

2. Deploy the bot:
```bash
kubectl apply -f k8s/
```

## Configuration

### Environment Variables
- `SKINPORT_API_KEY` - Your Skinport API key
- `SKINPORT_API_SECRET` - Your Skinport API secret
- `DISCORD_WEBHOOK_URL` - Discord webhook URL for notifications

### Bot Settings (`config.py`)
- `TARGET_ITEMS` - Dictionary of items to monitor with optional price thresholds
- `CHECK_INTERVAL` - Time between checks in minutes (default: 5)
- `RATE_LIMIT_DELAY` - Pause duration when rate limit is hit (default: 60 minutes)

## Item Names

For a complete list of available item names that can be monitored, see [ITEMS.md](ITEMS.md).

## Discord Notifications

The bot sends notifications in the following cases:
- When an item's price drops below your set threshold
- When new items become available (for items without threshold)
- When the bot starts up (showing monitored items)
- When rate limits are hit (with resume time)

## Development

### Building from Source

```bash
# Build multi-arch Docker image
docker buildx build --platform linux/amd64,linux/arm64 -t your-tag .
```

### Git Hooks

This repository uses Git hooks for commit message validation. To set them up:

```bash
# Make the hook executable
chmod +x .githooks/commit-msg

# Configure Git to use the hooks directory
git config core.hooksPath .githooks
```

The hooks ensure that commit messages follow the [Conventional Commits](https://www.conventionalcommits.org/) format:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example commit messages:
```bash
feat: add new feature
fix(api): handle timeout errors
docs: update installation guide
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 