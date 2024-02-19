import os
from dotenv import load_dotenv
from backpack import BpxClient


def get_orderbook_imbalance(orderBook, depth_to_calculate):

    max_bids_depth = len(orderBook['bids'])
    max_asks_depth = len(orderBook['asks'])

    depth_to_calculate = int(min([max_bids_depth, max_asks_depth, depth_to_calculate]))

    bids = orderBook['bids'][-1 * depth_to_calculate:]
    asks = orderBook['asks'][:depth_to_calculate]

    bids_vols = sum([float(i[1]) for i in bids])
    asks_vols = sum([float(i[1]) for i in asks])

    orderbookImbalance = (bids_vols - asks_vols) / (bids_vols + asks_vols)

    return orderbookImbalance


if __name__ == '__main__':

    load_dotenv()

    API_KEY = os.getenv('API_KEY')
    API_SECRET = os.getenv('API_SECRET')

    symbol_to_trade = os.getenv('SYMBOL_TO_TRADE')
    max_base_currency_to_hold = float(os.getenv('MAX_BASE_CURRENCY_TO_HOLD'))
    orderbook_imbalance_threshold = float(os.getenv('ORDERBOOK_IMBALANCE_THRESHOLD'))
    single_order_size = os.getenv('SINGLE_ORDER_SIZE')
    orderbook_depth_to_use = float(os.getenv('ORDERBOOK_DEPTH_TO_USE'))

    bpxClient = BpxClient(api_key=API_KEY, api_secret=API_SECRET)

    while True:

        balance = bpxClient.balances()
        token_balance = 0
        base_currency = symbol_to_trade.replace("_USDC", "")

        if base_currency not in balance:
            token_balance = 0
        else:
            token_balance = float(balance[base_currency]['available'])

        order_book = bpxClient.depth(symbol_to_trade)

        best_bid_price = order_book['bids'][-1][0]
        best_ask_price = order_book['asks'][0][0]

        orderbook_imbalance = get_orderbook_imbalance(order_book, orderbook_depth_to_use)

        if (orderbook_imbalance > orderbook_imbalance_threshold) & (token_balance < max_base_currency_to_hold):
            print(token_balance)
            response = bpxClient.sendOrder(symbol_to_trade, "Bid", "Limit", "IOC", single_order_size, str(best_ask_price))
            print(response.text)

        elif (orderbook_imbalance < orderbook_imbalance_threshold * -1):
            print(token_balance)
            response = bpxClient.sendOrder(symbol_to_trade, "Ask", "Limit", "IOC", single_order_size, str(best_bid_price))
            print(response.text)



