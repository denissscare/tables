from collections import defaultdict
import requests
import json
from typing import Any

def fetch_trades(url: str) -> list[dict]:
  response = requests.get(url)
  return response.json()
  
def group_by_orderno(trades: list) -> dict[str, dict[str, list]]:
  orders:dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
  
  for trade in trades:
    order = orders[trade['orderno']]
    
    order['currentpos'] = trade['currentpos']
    order['buysell'] = trade['buysell']
    
    order['value'].append(trade['value'])
    order['price'].append(trade['price'])
    order['quantity'].append(trade['quantity'])
    order['time'] = trade['time']
    order['comission'].append(trade['comission'])
    
  return {key: dict(value) for key, value in orders.items()}


def calculate_profit(opening_value, closing_value, opening_commission, closing_commission, trade_type: str) -> float:
  if trade_type == 'long':
    return closing_value - opening_value - (opening_commission + closing_commission)
  elif trade_type == 'short':
    return opening_value - closing_value - (opening_commission + closing_commission)
  return 0.0

def process_trade(ID, open_trade, close_trade, trade_type: str) -> dict:
    opening_time = open_trade['time']
    closing_time = close_trade['time']
    opening_value = sum(open_trade['value'])
    closing_value = sum(close_trade['value'])
    opening_commission = sum(open_trade['comission'])
    closing_commission = sum(close_trade['comission'])
    
    profit = calculate_profit(opening_value, closing_value, opening_commission, closing_commission, trade_type)
    
    return {
        'ID': ID,
        'Дата открытия': opening_time,
        'Дата закрытия': closing_time,
        'Цена открытия': opening_value,
        'Цена закрытия': closing_value,
        'Прибыль': round(profit, 2),
    }

def get_close_trades(groups_trades: dict) -> list[dict]:
    closed_trades = []
    checked_trades = set()
    ID = 1
    
    for elem, open_trade in groups_trades.items():
        if elem in checked_trades:
            continue
        
        if open_trade['currentpos'] != 0:
            trade_type = 'short' if open_trade['buysell'] == 'S' else 'long'
            for close_elem, close_trade in groups_trades.items():
                if (
                    close_elem != elem and
                    close_elem not in checked_trades and
                    close_trade['buysell'] != open_trade['buysell'] and
                    close_trade['currentpos'] == 0 and
                    sum(close_trade['quantity']) == abs(open_trade['currentpos'])
                ):
                    closed_trades.append(process_trade(ID, open_trade, close_trade, trade_type))
                    ID += 1
                    checked_trades.add(elem)
                    checked_trades.add(close_elem)
                    break
    
    return closed_trades

def calculate_metrics(closed_trades: list[dict], starting_capital: float = 100_000) -> dict:
  total_profit = 0
  total_loss = 0
  
  for trade in closed_trades:
    profit = trade['Прибыль']
    if profit > 0:
      total_profit += profit
    else:
      total_loss += profit
  
  print(f'Total Profit: {total_profit}\nTotal Loss: {total_loss}')
  
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
  
  print(metrics)
  
  data = {'id': '72N6LvBOj',
          'data': {'closeTrades':close_trades,'metrics': metrics}
          }
  
  print(data)
  
  response = requests.post('https://api.meridian.trade/api/test_data', json=data)
  if response.status_code == 200:
    print("Успешно отправлено:", response.json())
  else:
    print("Ошибка:", response.status_code, response.text)
  
  
  
if __name__ == '__main__':
  main()