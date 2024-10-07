import requests
import json
import time
import jdatetime
from telegram import Bot
import asyncio
from requests.exceptions import Timeout  # Import Timeout exception

# Your Telegram bot token
TELEGRAM_BOT_TOKEN = 'TELEGRAM_BOT_TOKEN'
TELEGRAM_CHANNEL_CHAT_ID = '@TELEGRAM_CHANNEL_CHAT_ID'

# test
# TELEGRAM_BOT_TOKEN = '6359966476:AAHVrcQXF-qj-PJfVfWqMDamw8qHGj1d51w'
# TELEGRAM_CHANNEL_CHAT_ID = '@pooryasn_bot'

def convert_to_persian_digits(number):
    persian_digits = {'0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴', '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'}
    return ''.join(persian_digits.get(char, char) for char in str(number))

async def fetch_depth_data():
    try:
        url = "https://api.nobitex.ir/market/stats?srcCurrency=usdt,btc&dstCurrency=rls,usdt"
        response = requests.get(url, timeout=5)  # Set a timeout of 5 seconds
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                stats = data.get("stats", {})

                usdt_rls = stats.get("usdt-rls", {})
                latest_usd = convert_to_persian_digits('{:,.0f}'.format(float(usdt_rls.get("latest", 0)) / 10))
                day_low_usd = convert_to_persian_digits('{:,.0f}'.format(float(usdt_rls.get("dayLow", 0)) / 10))
                day_high_usd = convert_to_persian_digits('{:,.0f}'.format(float(usdt_rls.get("dayHigh", 0)) / 10))
                day_change_usd = convert_to_persian_digits(usdt_rls.get("dayChange", "0"))
                
                btc_usdt = stats.get("btc-usdt", {})
                latest_btc = convert_to_persian_digits('{:,.0f}'.format(float(btc_usdt.get("latest", 0)) / 1))
                day_low_btc = convert_to_persian_digits('{:,.0f}'.format(float(btc_usdt.get("dayLow", 0)) / 1))
                day_high_btc = convert_to_persian_digits('{:,.0f}'.format(float(btc_usdt.get("dayHigh", 0)) / 1))
                day_change_btc = convert_to_persian_digits(btc_usdt.get("dayChange", "0"))

                # is_closed = usdt_rls.get("isClosed")
                # best_sell = usdt_rls.get("bestSell")
                # best_buy = usdt_rls.get("bestBuy")
                # volume_src = usdt_rls.get("volumeSrc")
                # volume_dst = usdt_rls.get("volumeDst")
                # mark = usdt_rls.get("mark")
                # day_open = usdt_rls.get("dayOpen")
                # day_close = usdt_rls.get("dayClose")

                return (latest_usd, day_low_usd, day_high_usd,day_change_usd,latest_btc,day_low_btc,day_high_btc,day_change_btc)
            else:
                print("Error: Status is not OK")
        else:
            print("Error: Unable to fetch data")
    except Timeout:
        print("Error: Request timed out")


async def fetch_history_data(coin):
    try:
        end_time = int(time.time())
        one_month_ago = end_time - (30 * 24 * 60 * 60)
        url = f"https://api.nobitex.ir/market/udf/history?symbol={coin}&resolution=D&from={one_month_ago}&to={end_time}"
        response = requests.get(url, timeout=10)  # Set a timeout of 5 seconds
        if response.status_code == 200:
            data = response.json()
            if data.get("s") == "ok":
                return data.get("h"), data.get("l")
            else:
                print("Error: Status is not OK")
        else:
            print("Error: Unable to fetch data")
    except Timeout:
        print("Error: Request timed out")


async def send_telegram_message(message):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_CHANNEL_CHAT_ID, text=message)

async def main():
    while True:
        try:
            stats = await fetch_depth_data()
            if stats:
                current_time = jdatetime.datetime.now()
                current_time_persian_digits = convert_to_persian_digits(current_time.strftime('%Y/%m/%d %H:%M:%S'))

                latest_usd, day_low_usd, day_high_usd,day_change_usd,latest_btc,day_low_btc,day_high_btc,day_change_btc = stats

                # Emoji characters
                arrow_up = "▲"
                arrow_down = "▼"
                money_bag = "💰"
                arrow_up_c = "📈"
                arrow_down_c = "📉"
                btc_symbol = "₿"
                dollar_sign = "💵"
                clock = "🕒"

                history_data_usdt = await fetch_history_data("usdtIRT")
                history_data_btc = await fetch_history_data("btcusdt")

                if history_data_usdt:
                    highest_monthly_value_usdt = convert_to_persian_digits('{:,.0f}'.format(max(history_data_usdt[0])))
                    lowest_monthly_value_usdt = convert_to_persian_digits('{:,.0f}'.format(min(history_data_usdt[1])))
                    highest_weekly_value_usdt = convert_to_persian_digits('{:,.0f}'.format(max(history_data_usdt[0][-7:])))
                    lowest_weekly_value_usdt = convert_to_persian_digits('{:,.0f}'.format(min(history_data_usdt[1][-7:])))

                if history_data_btc:
                    highest_monthly_value_btc = convert_to_persian_digits('{:,.0f}'.format(max(history_data_btc[0])))
                    lowest_monthly_value_btc = convert_to_persian_digits('{:,.0f}'.format(min(history_data_btc[1])))
                    highest_weekly_value_btc = convert_to_persian_digits('{:,.0f}'.format(max(history_data_btc[0][-7:])))
                    lowest_weekly_value_btc = convert_to_persian_digits('{:,.0f}'.format(min(history_data_btc[1][-7:])))


                message = (
                    f"{clock} {current_time_persian_digits}\n\n"
                    
                    f"قیمت USDT(دلار) {dollar_sign}\n"
                    f"{money_bag} آخرین قیمت: {latest_usd} تومان\n"
                    f"{arrow_up_c if float(day_change_usd) >= 0 else arrow_down_c} تغییرات ۲۴ ساعت: %{day_change_usd[1:]+'-' if day_change_usd.startswith('-') else day_change_usd}\n"
                    
                    f"۲۴ ساعت اخیر: {arrow_down}{day_low_usd} تومان / {arrow_up}{day_high_usd} تومان\n"
                    f"۷ روز اخیر: {arrow_down}{lowest_weekly_value_usdt} تومان / {arrow_up}{highest_weekly_value_usdt} تومان\n"
                    f"۳۰ روز اخیر: {arrow_down}{lowest_monthly_value_usdt} تومان / {arrow_up}{highest_monthly_value_usdt} تومان\n\n\n"
                    
                    f"قیمت Bitcoin {btc_symbol}\n"
                    f"{money_bag} آخرین قیمت: {latest_btc} دلار\n"
                    f"{arrow_up_c if float(day_change_btc) >= 0 else arrow_down_c} تغییرات ۲۴ ساعت: %{day_change_btc[1:]+'-' if day_change_btc.startswith('-') else day_change_btc}\n"
                    
                    f"۲۴ ساعت اخیر: {arrow_down}{day_low_btc} دلار / {arrow_up}{day_high_btc} دلار\n"
                    f"۷ روز اخیر: {arrow_down}{lowest_weekly_value_btc} دلار / {arrow_up}{highest_weekly_value_btc} دلار\n"
                    f"۳۰ روز اخیر: {arrow_down}{lowest_monthly_value_btc} دلار / {arrow_up}{highest_monthly_value_btc} دلار\n\n"
                    
                    f"@USDT_IRT_Live"
                )


                await send_telegram_message(message)
        except Exception as e:
            print(f"Error: {e}")
        await asyncio.sleep(300)


if __name__ == "__main__":
    asyncio.run(main())
