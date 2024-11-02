# Access Telebot

Access Telebot is a Telegram bot designed to facilitate the sale of subscriptions to private Telegram channels using your own cryptocurrency merchant. It allows you to accept payments directly to your TRON address without any intermediaries.

## Features

- Sell subscriptions to private Telegram channels.
- Accept payments directly to your TRON address.
- No middlemen involved.

## Getting Started

This project is containerized using Docker, making it easy to build and start.

### Prerequisites

Ensure you have Docker Engine installed. If not, follow the installation guide [here](https://docs.docker.com/engine/install/). If you want run docker as non-root user do not forget about [this](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user)

### Installation

1. **Build the Docker containers:**

   ```sh
   docker compose build
   ```

2. **Run the containers and start the bot:**

   ```sh
   docker compose up
   ```

   Wait approximately 30 seconds for all services to initialize. Once ready, you can start interacting with the bot for testing purposes.

## Note

This README is a work in progress. Additional details will be added later.
