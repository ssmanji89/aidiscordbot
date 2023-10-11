
# Discord Bot with OpenAI Integration

## Overview

This Discord bot is designed to integrate with OpenAI's GPT-3 API to provide automated responses to user queries. 
It's built using Python and the discord.py library and comes containerized with Docker for easy deployment.

## Features

- Automated ticket creation and management via Discord commands.
- Integration with OpenAI's GPT-3 for intelligent responses.
- SQLite database for persistent storage of tickets and a knowledge base.
- Dockerized for consistent environment and easy deployment.

## Prerequisites

- Python 3.8 or higher
- Docker
- Discord Bot Token
- OpenAI API Key

## Getting Started

### Clone the Repository

```bash
git clone https://github.com/ssmanji89/aidiscordbot
cd aidiscordbot
```

### Local Setup

1. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```
2. Set your Discord Bot Token and OpenAI API Key as environment variables:
    ```bash
    export DISCORD_BOT_TOKEN=your_discord_bot_token
    export OPENAI_API_KEY=your_openai_api_key
    ```
3. Run the bot:
    ```bash
    python run.py
    ```

### Docker Setup

1. Build the Docker image:
    ```bash
    docker build -t aidiscordbot .
    ```
2. Run the Docker container:
    ```bash
    docker run -e DISCORD_BOT_TOKEN=your_token -e OPENAI_API_KEY=your_key aidiscordbot
    ```

## Commands

- `!ticket [query]`: Creates a new ticket with the given query and responds with a message.

## Contributing

If you'd like to contribute, please fork the repository and use a feature branch. Pull requests are warmly welcome.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments

- The discord.py library for providing the framework for building this bot.
- OpenAI for their GPT-3 API.

