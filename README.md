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

   Add `TELEBOT_KEY` and `TRONGRID_API_KEY` to the `.env` file before building and running the Docker containers. TronGrid key can get [here](https://www.trongrid.io/register)

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

The bot's Django admin panel should be available at `localhost:80/secret_way/admin`. You can change `secret_way` to any secret phrase in the `.env` file. Also you can find default Django admin login and password there

### Telegram Bot Setup

Do not create Chat models manually. At first you have to set your Telegram bot as an administrator of the chat access that you are going to sell. After adding it as an administrator, the channel/chat will appear in the admin panel as a `Chat` model. After this you can create `Subsciption` models with preferred periods and prices

### Field encryption key

The `FIELD_ENCRYPTION_KEY` in the `.env` file is very important. Change it before building and running, save it, and store it in a safe place. Without this key, you could lose the funds you receive from merchant sales.

### Tron Address Model

This model contains addresses and private keys of TRON chain wallets. New wallet creates automatically when all others are busy.

### Using Django Manage from the Host

You can execute Django management commands (`python3 manage.py`) directly from the Docker host without needing to access the web container's shell. Simply use the script `docker/manage.sh <command>`. For example:

```bash
docker/manage.sh generate_field_encryption_key
```

Please ensure that all Docker Compose services are running. A list of all available commands can be found in `docs/commands.md`.

### Exporting Tron Wallets

To manage your USDT, you need to export your TRON wallets for use in a regular crypto app. Use the following command to export all wallets with their private keys:

```
docker/manage.sh export_tron_wallets
```

After exporting, you can copy the private keys and import them into the [TronLink Wallet](https://www.tronlink.org/) for management. You can continue to use these wallets to receive payments even after importing them into the that app.

## Note

This README is a work in progress. Additional details will be added later.
