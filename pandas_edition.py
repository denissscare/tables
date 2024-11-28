import pandas as pd
import requests

def fetch_trades(url: str) -> pd.DataFrame:
    response = requests.get(url)
    return pd.DataFrame(response.json())

def group_by_orderno(trades: pd.DataFrame) -> pd.DataFrame:
    return trades.groupby('orderno').agg(
        currentpos=('currentpos', 'last'),
        buysell=('buysell', 'last'),
        value=('value', 'sum'),
        price=('price', 'sum'),
        quantity=('quantity', 'sum'),
        time=('time', 'last'),
        comission=('comission', 'sum')
    ).reset_index()

def calculate_profit(opening_value, closing_value, opening_commission, closing_commission, trade_type: str) -> float:
    if trade_type == 'long':
        return closing_value - opening_value - (opening_commission + closing_commission)
    elif trade_type == 'short':
        return opening_value - closing_value - (opening_commission + closing_commission)
    return 0.0

def process_trade(open_trade: pd.Series, close_trade: pd.Series, trade_type: str) -> dict:
    opening_value = open_trade['value']
    closing_value = close_trade['value']
    opening_commission = open_trade['comission']
    closing_commission = close_trade['comission']

    profit = calculate_profit(opening_value, closing_value, opening_commission, closing_commission, trade_type)

    return {
        'Дата открытия': open_trade['time'],
        'Дата закрытия': close_trade['time'],
        'Цена открытия': opening_value,
        'Цена закрытия': closing_value,
        'Прибыль': round(profit, 2),
    }

def get_close_trades(groups_trades: pd.DataFrame) -> list[dict]:
    closed_trades = []
    checked_trades = set()
  
    long_trades = groups_trades[groups_trades['buysell'] == 'B']
    short_trades = groups_trades[groups_trades['buysell'] == 'S']

    for _, open_trade in long_trades.iterrows():
        if open_trade['orderno'] in checked_trades:
            continue

        if open_trade['currentpos'] != 0:
            close_trade = short_trades[
                (short_trades['quantity'] == abs(open_trade['currentpos'])) &
                (short_trades['currentpos'] == 0)
            ].head(1)

            if not close_trade.empty:
                close_trade = close_trade.iloc[0]
                closed_trades.append(process_trade(open_trade, close_trade, 'long'))
                checked_trades.add(open_trade['orderno'])
                checked_trades.add(close_trade['orderno'])

    for _, open_trade in short_trades.iterrows():
        if open_trade['orderno'] in checked_trades:
            continue

        if open_trade['currentpos'] != 0:
            close_trade = long_trades[
                (long_trades['quantity'] == abs(open_trade['currentpos'])) &
                (long_trades['currentpos'] == 0)
            ].head(1)

            if not close_trade.empty:
                close_trade = close_trade.iloc[0]
                closed_trades.append(process_trade(open_trade, close_trade, 'short'))
                checked_trades.add(open_trade['orderno'])
                checked_trades.add(close_trade['orderno'])

    return closed_trades

def calculate_metrics(closed_trades: list[dict], starting_capital: float = 100_000) -> dict:
    total_profit = sum(trade['Прибыль'] for trade in closed_trades if trade['Прибыль'] > 0)
    total_loss = sum(trade['Прибыль'] for trade in closed_trades if trade['Прибыль'] < 0)

    profit_factor = total_profit / abs(total_loss) if abs(total_loss) > 0 else float('inf')
    return_metric = total_profit - abs(total_loss) if total_loss != 0 else float('inf')
    return_percent = return_metric / starting_capital

    return {
        "Profit Factor": round(profit_factor, 2),
        "Return": round(return_metric, 2),
        "Return %": round(return_percent, 2),
    }

def main():
    trades = fetch_trades('https://api.meridian.trade/api/trades/test_data')
    groups_trades = group_by_orderno(trades)
    close_trades = get_close_trades(groups_trades)

    metrics = calculate_metrics(close_trades)

    data = {'id': '',
            'data': {'closeTrades': close_trades, 'metrics': metrics}
            }
    response = requests.post('https://api.meridian.trade/api/test_data', json=data)
    if response.status_code == 200:
        print("Успешно отправлено:", response.json())
    else:
        print("Ошибка:", response.status_code, response.text)

if __name__ == '__main__':
    main()
