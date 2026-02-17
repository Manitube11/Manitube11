require('dotenv').config();
const { Telegraf, Markup } = require('telegraf');

const token = process.env.BOT_TOKEN;
if (!token) {
  throw new Error('BOT_TOKEN must be provided!');
}

const bot = new Telegraf(token);

bot.command('start', (ctx) => {
  ctx.reply(
    'Welcome! Click the button below to launch the Mini App.',
    Markup.inlineKeyboard([
      Markup.button.webApp('Launch App', process.env.WEB_APP_URL || 'https://google.com'),
    ])
  );
});

bot.launch();

// Enable graceful stop
process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));

console.log('Bot is running...');
