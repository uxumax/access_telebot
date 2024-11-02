# Access Telebot

Access Telebot is a Telegram bot designed to facilitate the sale of subscriptions to private Telegram channels using your own cryptocurrency merchant. It allows you to accept USDT payments directly to your TRON address without any intermediaries.

## Features

- Sell subscriptions to private Telegram channels.
- Accept payments directly to your TRON address.
- No middlemen involved.

## Getting Started

This project is containerized using Docker, making it easy to build and start.

### Prerequisites

Ensure you have Docker Engine installed. If not, follow the installation guide [here](https://docs.docker.com/engine/install/). If you want to run Docker as a non-root user, do not forget about [this](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user).

### Installation

1. **Configure the .env file:**

   Add `TELEBOT_KEY` to the `.env` file before building and running the Docker containers.

2. **Build the Docker containers:**

   ```sh
   docker compose build
   ```

3. **Run the containers and start the bot:**

   ```sh
   docker compose up
   ```

   Wait approximately 30 seconds for all services to initialize. Once ready, you can start interacting with the bot for testing purposes.

### Admin Panel

The bot's Django admin panel should be available at `localhost:80/secret_way/admin`. You can change `secret_way` to any secret phrase in the `.env` file.

### Telegram Bot Setup

You have to set your Telegram bot as an administrator of the chat access that you are going to sell. After adding it as an administrator, the channel/chat will appear in the admin panel as a Chat model.

### Field encryption key

This key is important. Change it, save and put to safe place. Without this key you can loose you funds that you get with merchant selling accesses

## Note

This README is a work in progress. Additional details will be added later.
