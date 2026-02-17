# Telegram Bot & Mini App Project

This project contains a **Telegram Bot** (backend) and a **Mini App** (frontend) built with modern technologies.

- **Bot:** Node.js, Telegraf
- **Mini App:** React, Vite, TypeScript, Tailwind CSS

## Prerequisites

- [Node.js](https://nodejs.org/) (v16 or higher)
- A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- A tunneling tool like [ngrok](https://ngrok.com/) (required to expose your local server to Telegram)

## Project Structure

- `/bot`: Contains the backend logic for the Telegram bot.
- `/web-app`: Contains the frontend React application for the Mini App.

## Setup Instructions

### 1. Setup the Bot

1.  Navigate to the `bot` directory:
    ```bash
    cd bot
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Copy the example environment file:
    ```bash
    cp .env.example .env
    ```
4.  Open `.env` and paste your bot token (from BotFather) into `BOT_TOKEN`:
    ```env
    BOT_TOKEN=YOUR_BOT_TOKEN_HERE
    WEB_APP_URL=YOUR_NGROK_URL
    ```
    **Important:** You will need to update `WEB_APP_URL` after you start ngrok (see Step 3).

### 2. Setup the Mini App

1.  Open a new terminal and navigate to the `web-app` directory:
    ```bash
    cd web-app
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start the development server:
    ```bash
    npm run dev
    ```
    This will usually start the app at `http://localhost:5173`.

### 3. Expose Localhost with Ngrok

Since Telegram Mini Apps require HTTPS, you need to expose your local `http://localhost:5173` to the internet.

1.  Install ngrok if you haven't already.
2.  Run the following command:
    ```bash
    ngrok http 5173
    ```
3.  Copy the HTTPS URL provided by ngrok (e.g., `https://abcd-1234.ngrok-free.app`).
4.  Paste this URL into `bot/.env` as the `WEB_APP_URL`:
    ```env
    WEB_APP_URL=https://abcd-1234.ngrok-free.app
    ```

### 4. Run the Bot

1.  Go back to the `bot` terminal.
2.  Start the bot:
    ```bash
    node index.js
    ```
3.  Open your bot in Telegram and send `/start`.
4.  Click the "Launch App" button. It should open your local Mini App!

## Customization

- **Frontend:** Edit `web-app/src/App.tsx` to change the UI. Tailwind CSS is configured for easy styling.
- **Backend:** Edit `bot/index.js` to add more bot commands or logic.

## Troubleshooting

- **White Screen in Telegram:** Ensure the `WEB_APP_URL` in `.env` is the correct HTTPS URL from ngrok.
- **Bot not responding:** Ensure the bot process is running (`node index.js`) and the token is correct.
