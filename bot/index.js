try {
  require('dotenv').config();
} catch (e) {
  if (e.code === 'MODULE_NOT_FOUND') {
    console.error('\x1b[31m%s\x1b[0m', 'Error: "dotenv" module not found.');
    console.error('Please run "npm install" in this directory to install dependencies.');
    process.exit(1);
  } else {
    throw e;
  }
}

let Telegraf, Markup;
try {
  const telegraf = require('telegraf');
  Telegraf = telegraf.Telegraf;
  Markup = telegraf.Markup;
} catch (e) {
  if (e.code === 'MODULE_NOT_FOUND') {
    console.error('\x1b[31m%s\x1b[0m', 'Error: "telegraf" module not found.');
    console.error('Please run "npm install" in this directory to install dependencies.');
    process.exit(1);
  } else {
    throw e;
  }
}

const token = process.env.BOT_TOKEN;
if (!token) {
  console.error('\x1b[31m%s\x1b[0m', 'Error: BOT_TOKEN is missing in .env file.');
  console.error('Please create a .env file in the "bot" directory with BOT_TOKEN=your_token_here');
  // We can't proceed without a token, but let's try to not crash immediately if we want to be nice?
  // No, Telegraf needs it.
  process.exit(1);
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
