import pandas as pd
import requests
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
#комментарий для пулл реквеста

class CryptoData:
    def __init__(self):
        self.api_url = "https://api.coinlore.net/api/tickers/"
        self.data_file = "crypto_data.xlsx"
        self.conversion_rates = {
            'USD': 1,
            'BYN': 3.101,
            'RUB': 85.1455,
            'CNY': 7.3275,
            'EUR': 0.9254
        }

    def fetch_coins(self):
        try:
            response = requests.get(self.api_url)
            response.raise_for_status()
            data = response.json()
            coins = data['data']
            df_coins = pd.DataFrame(coins)
            return df_coins
        except requests.RequestException as e:
            print(f"Ошибка при загрузке данных: {e}")
            return None

    def convert_currency(self, amount, currency):
        if currency in self.conversion_rates:
            return amount * self.conversion_rates[currency]
        else:
            raise ValueError("Неизвестная валюта")

    def save_to_excel(self, df_coins):
        df_filtered = df_coins[['id', 'symbol', 'name', 'rank', 'price_usd']].copy()
        for currency in ['BYN', 'RUB', 'CNY', 'EUR']:
            df_filtered[currency] = df_filtered['price_usd'].apply(lambda x: self.convert_currency(float(x), currency))

        with pd.ExcelWriter(self.data_file) as writer:
            df_filtered.to_excel(writer, sheet_name='Crypto Data', index=False)
        print(f"Данные сохранены в {self.data_file}")

    def plot_price_trends(self, top_n=10):
        df_coins = self.fetch_coins()
        if df_coins is not None:
            df_coins['price_usd'] = df_coins['price_usd'].astype(float)
            top_coins = df_coins.nlargest(top_n, 'price_usd')

            # Создаем график
            plt.figure(figsize=(12, 6))
            plt.title("Изменение цен 10 самых дорогих криптовалют")
            plt.xlabel("Время")
            plt.ylabel("Цена (USD)")

            # Добавляем линии для каждой криптовалюты
            for index, row in top_coins.iterrows():
                initial_price = row['price_usd'] * (1 + float(row['percent_change_7d']) / 100)
                price_1h = row['price_usd'] * (1 + float(row['percent_change_1h']) / 100)
                price_24h = row['price_usd'] * (1 + float(row['percent_change_24h']) / 100)
                current_price = row['price_usd']

                # Позиции по оси X (0 - начальная, 1 - 1 час, 2 - 24 часа, 3 - 7 дней)
                x_values = [0, 1, 2, 3]
                y_values = [initial_price, price_1h, price_24h, current_price]

                plt.plot(x_values, y_values, marker='o', label=row['name'])

            plt.xticks([0, 1, 2, 3], ['начальная цена', 'через 1 час', 'через 24 часа', 'через неделю'])
            plt.legend()
            plt.grid()
            plt.tight_layout()
            plt.show()


if __name__ == "__main__":
    crypto = CryptoData()
    df_coins = crypto.fetch_coins()  # Получить список монет

    if df_coins is not None:
        crypto.save_to_excel(df_coins)  # Сохранить в один файл
        crypto.plot_price_trends()  # Построить график изменения цен