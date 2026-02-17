require('dotenv').config();
const { Telegraf, Markup } = require('telegraf');

const token = process.env.BOT_TOKEN;
if (!token) {
  console.error('Error: BOT_TOKEN is missing in .env file.');
  console.error('Please create a .env file in the "bot" directory with BOT_TOKEN=your_token_here');
  // We can't proceed without a token, but let's try to not crash immediately if we want to be nice?
  // No, Telegraf needs it.
  throw new Error('BOT_TOKEN must be provided!');
}

const bot = new Telegraf(token);

const webAppUrl = process.env.WEB_APP_URL || 'https://google.com';

bot.command('start', (ctx) => {
  ctx.reply(
    '🚀 *Welcome to the Future of Earnings!*\n\n' +
    'Discover our exclusive platform designed to maximize your potential.\n' +
    'Click below to access your dashboard, manage your wallet, and explore premium deals.\n\n' +
    '👇 *Start Your Journey Now!*',
    {
      parse_mode: 'Markdown',
      ...Markup.inlineKeyboard([
        Markup.button.webApp('🚀 Open Dashboard', webAppUrl),
      ])
    }
  );
});

bot.launch();

// Enable graceful stop
process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));

console.log('Bot is running...');
console.log(`Web App URL configured as: ${webAppUrl}`);
