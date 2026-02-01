import mplfinance as mpf
import pandas as pd
import os
from PIL import Image, ImageDraw, ImageFont

class Visualizer:
    def __init__(self):
        self.charts_dir = "charts"
        if not os.path.exists(self.charts_dir):
            os.makedirs(self.charts_dir)

    def generate_chart(self, df, symbol):
        """
        Generates a candlestick chart with EMA indicators and saves it as a PNG.
        Returns the file path.
        """
        if df.empty:
            return None

        # Prepare Dataframe for mplfinance
        plot_df = df.copy()

        # Check if 'Date' is a column (due to reset_index in data_feed)
        if 'Date' in plot_df.columns:
            plot_df['Date'] = pd.to_datetime(plot_df['Date'])
            plot_df.set_index('Date', inplace=True)
        elif 'index' in plot_df.columns: # fallback if column name differs
             plot_df['index'] = pd.to_datetime(plot_df['index'])
             plot_df.set_index('index', inplace=True)

        # Slice last 60 candles for clarity
        plot_df = plot_df.tail(60)

        # Create custom style
        mc = mpf.make_marketcolors(up='#00ff00', down='#ff0000', inherit=True)
        s  = mpf.make_mpf_style(base_mpf_style='nightclouds', marketcolors=mc)

        # Add EMA plots if they exist
        add_plots = []
        if 'EMA_50' in plot_df.columns:
            add_plots.append(mpf.make_addplot(plot_df['EMA_50'], color='cyan', width=1.5))
        if 'EMA_200' in plot_df.columns:
            add_plots.append(mpf.make_addplot(plot_df['EMA_200'], color='yellow', width=1.5))

        filename = f"{symbol.replace('/', '').replace(' ', '_')}_chart.png"
        filepath = os.path.join(self.charts_dir, filename)

        try:
            mpf.plot(
                plot_df,
                type='candle',
                style=s,
                title=f"\n{symbol} - VIP Analysis",
                volume=True,
                addplot=add_plots,
                savefig=filepath
            )
            return filepath
        except Exception as e:
            print(f"[Visualizer] Error creating chart: {e}")
            return None

    def generate_signal_card(self, signal_data):
        """
        Generates a graphic card for the signal using Pillow.
        Returns file path.
        """
        width, height = 800, 400
        # Dark Background
        img = Image.new('RGB', (width, height), color=(10, 20, 30))
        draw = ImageDraw.Draw(img)

        # Colors
        green = (0, 255, 127)
        red = (255, 69, 0)
        white = (255, 255, 255)

        # Determine Color based on Type
        is_buy = 'BUY' in signal_data['Type']
        main_color = green if is_buy else red

        # Draw Border
        draw.rectangle([(10, 10), (width-10, height-10)], outline=main_color, width=5)

        # Fonts (Fallback to default if custom ttf not found)
        try:
            # Attempt to load a bold font (Arial or generic)
            font_title = ImageFont.truetype("arialbd.ttf", 60)
            font_large = ImageFont.truetype("arial.ttf", 40)
            font_med = ImageFont.truetype("arial.ttf", 30)
        except IOError:
            font_title = ImageFont.load_default()
            font_large = ImageFont.load_default()
            font_med = ImageFont.load_default()

        # Text Content
        title_text = f"VIP {signal_data['Type']} SIGNAL"
        symbol_text = signal_data['Symbol']
        entry_text = f"ENTRY: ${signal_data['Entry']:,.2f}"

        # Draw Title
        draw.text((50, 50), title_text, fill=main_color, font=font_title)

        # Draw Symbol
        draw.text((50, 130), symbol_text, fill=white, font=font_large)

        # Draw Entry
        draw.text((50, 200), entry_text, fill=white, font=font_med)

        # Draw TP/SL
        draw.text((400, 200), f"TP1: ${signal_data['TP1']:,.2f}", fill=green, font=font_med)
        draw.text((400, 250), f"TP2: ${signal_data['TP2']:,.2f}", fill=green, font=font_med)
        draw.text((400, 300), f"SL:  ${signal_data['StopLoss']:,.2f}", fill=red, font=font_med)

        # Footer
        draw.text((50, 340), "ManiTube AI Bot", fill=(100, 100, 100), font=font_med)

        filename = f"card_last.png"
        filepath = os.path.join(self.charts_dir, filename)
        img.save(filepath)
        return filepath

if __name__ == "__main__":
    # Test
    viz = Visualizer()
    print("Visualizer Initialized.")
