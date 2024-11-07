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

   - Set `TELEBOT_KEY` and `TRONGRID_API_KEY` in the `.env` file before building and running the Docker containers. TronGrid key can get [here](https://www.trongrid.io/register)
   - The `FIELD_ENCRYPTION_KEY` file is very important. Change it, save it, and store it in a safe place. Without this key, you could lose the funds you receive from merchant sales.

2. **Build the Docker containers:**

   ```sh
   docker compose build
   ```

3. **Run the containers and start the bot:**

   ```sh
   docker compose up
   ```

   Wait approximately 30 seconds for all services to initialize. Once ready, you can start interacting with the bot for testing purposes. Note that Nginx port `8082` and Postgres port `5445` should be free on your docker host machine otherwise feel free change them to any in `.env`.

### Admin Panel

The bot's Django admin panel should be available at `localhost:8082/secret_way/admin`. You can change `secret_way` to any secret phrase in the `.env` file. Also you can find default Django admin login and password there

### Add Chats and Create Subscriptions

A Chat model represents your private channel or group that you intend to sell access to. Do not manually create Chat instances. First, set your Telegram bot as an administrator of your private channel or group. Once added as an administrator, the channel or group will appear in the admin panel as a `Chat` model instance. After this, you can manually create `Subscription` instances with your preferred periods and prices. Trial periods supported.

<img src="./docs/images/create_subscription_instance.png?raw=true" width="600"/>

### Tron Address Model

This table contains addresses and private keys of TRON chain wallets. New wallet creates automatically when all others are busy.

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

### Changing Text of Bot Messages 

Use can use Translations to change bot messages text. At first generate your first translation with name `easy`

```bash
docker/manage.sh make_translations easy
```

You can find the generated translations in the Django admin under the `messenger.Translation` instances. Here, you can modify them by filling in the `TO_TEXT` for each original `FROM_TEXT`. Set your `TRANSLATION_NAME` in the .env file, and restart the entire project or just the `web` service when you're finished.

## Note

This README is a work in progress. Additional details will be added later.
