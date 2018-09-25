from module.Algo_Trading_OMX30.Algo_Trading_OMX30.OMX30 import Omx30
from module.Algo_Trading_Strategy.Algo_Trading_Strategy.algo_trading_strategy import Strategies
import pickle

PORTFOLIO_FILE = 'Portfolio.pickle'
ORDER_LIST = 'order_list.txt'

class Portfolio:
    def __init__(self, omx30_update = False, money = 0):
        omx30 = Omx30(update=omx30_update)
        self.stock = Strategies(omx30).stock
        self.portfolio = self.get_portfolio(money)
        self.old_portfolio = {}#self.get_old_portfolio()
        self.buy_dict = self.get_buy_dict()
        self.sell_dict = self.get_sell_dict()


    def print_action_list(self):
        order_str = "### BUY ORDERS ###\n"
        for company, amount in self.buy_dict.items():
            order_str += '{}: {}\n'.format(company, amount)
        order_str += "\n### SELL ORDERS ###\n"
        for company, amount in self.sell_dict.items():
            order_str += '{}: {}\n'.format(company, amount)
        with open(ORDER_LIST, 'w+') as f:
            f.write(order_str)


    def get_sell_dict(self):
        sell_d = {}
        portfolio = self.portfolio
        old_portfolio = self.old_portfolio
        sell_companies = list(set(old_portfolio.keys()) - set(portfolio.keys()))
        old_companies = list(set(portfolio.keys()).intersection(old_portfolio.keys()))
        for company in portfolio.keys():
            if company in old_companies:
                if portfolio[company] < old_portfolio[company]:
                    sell_d[company] =  old_portfolio[company] - portfolio[company]
            if company in sell_companies:
                sell_d[company] = old_portfolio[company]
        return sell_d

    def get_buy_dict(self):
        buy_d = {}
        portfolio = self.portfolio
        old_portfolio = self.old_portfolio
        new_companies = list(set(portfolio.keys()) - set(old_portfolio.keys()))
        old_companies = list(set(portfolio.keys()).intersection(old_portfolio.keys()))
        for company in portfolio.keys():
            if company in old_companies:
                if portfolio[company] > old_portfolio[company]:
                    buy_d[company] = portfolio[company] - old_portfolio[company]
            if company in new_companies:
                buy_d[company] = portfolio[company]
        return buy_d

    def get_old_portfolio(self):
        return self.read_file(PORTFOLIO_FILE)

    def get_investment_list(self):
        investment_l = []
        for company in self.stock.keys():
            df = self.stock[company]
            if df.ix[df.shape[0] - 1, 'signal'] == 1.0:
                investment_l.append(company)
        return investment_l

    def get_portfolio(self, money):
        investment_d = {}
        investment_l = self.get_investment_list()
        money_left = money
        company_cnt = len(investment_l)

        for company in investment_l:
            df = self.stock[company]
            close_price = df.ix[df.shape[0] - 1, 'Close']
            investment_per_stock = money_left / company_cnt
            stock_cnt = int(investment_per_stock/close_price)
            if stock_cnt != 0:
                money_left = money_left - stock_cnt * close_price
                investment_d[company] = stock_cnt
            company_cnt = company_cnt - 1
        self.write_file(investment_d, PORTFOLIO_FILE)
        return investment_d

    def write_file(self, obj, file):
        with open(file, 'wb+') as f:
            pickle.dump(obj, f)

    def read_file(self, file):
        with open(file, 'rb') as f:
            return pickle.load(f)

if __name__=="__main__":
    p = Portfolio(money=5000)
    print('sell dict:{}'.format(p.sell_dict))
    print('buy dict: {}'.format(p.buy_dict))
    p.print_action_list()

