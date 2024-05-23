import numpy as np
import pandas as pd


class BuyAndHold:
    def __init__(self, df, V_0, L) -> None:
        '''
        Constructor for the BuyAndHold class

        Parameters:
        df : DataFrame of the stock data
        V_0 : Initial investment
        L : Leverage
        '''
        self.signals = None
        self.df = df
        self.V_0 = V_0
        self.L = L
        self.theta_0 = self.V_0 * self.L
        self.theta = [self.theta_0]  # Strategy: A sequence of dollar values of stock
        self.cap_V = [0]  # Capital Money in the money market: without risk-free rate
        self.PnL = [0]  # Profit and Loss
        self.stock_hold = [self.theta_0 / self.df['Adj Close'][0]]  # Stock holding

    def generate_signals(self):
        '''
        Generate signals for the strategy
        '''
        self.signals = pd.DataFrame(index=self.df.index)
        self.signals['Signal'] = 1
        self.signals['Position'] = self.signals['Signal'].diff()

    def execute_strategy(self):
        '''
        Execute the strategy
        '''
        for i in range(1, len(self.df)):
            theta_t = self.stock_hold[i-1] * self.df['Adj Close'][i]
            # if |theta| > theta_0
            if abs(theta_t) > self.theta_0:
                cap_V_t = abs(theta_t) - self.theta_0
                PnL_t = self.df['Return/Unit'][i] * theta_t
                theta_t = self.theta_0 * self.signals['Signal'][i]
                hold_t = theta_t / self.df['Adj Close'][i]
            # if theta_0 - V_0 < |theta| <= theta_0
            elif abs(theta_t) <= self.theta_0 and abs(theta_t) > self.theta_0 - self.V_0:
                cap_V_t = 0
                hold_t = self.stock_hold[-1]
                PnL_t = self.df['Return/Unit'][i] * theta_t
            # if |theta| <= theta_0 - V_0
            else:
                cap_V_t = abs(theta_t) - self.theta_0
                theta_t = 0
                hold_t = 0
                PnL_t = 0
                break
            self.cap_V.append(cap_V_t)
            self.theta.append(theta_t)
            self.stock_hold.append(hold_t)
            self.PnL.append(PnL_t)

    def run(self):
        '''
        Run the strategy
        '''
        self.generate_signals()
        self.execute_strategy()
    
    def get_signals(self):
        '''
        Get the signals for the strategy
        '''
        return np.array(self.signals['Signal'])
    
    def get_theta(self):
        '''
        Get the dollar values of stock
        '''
        self.theta.extend([0] * (len(self.df) - len(self.theta)))
        self.df['theta'] = self.theta[:len(self.df)]
        return self.df['theta']
    
    def get_stock_hold(self):
        '''
        Get the stock holding
        '''
        self.stock_hold.extend([0] * (len(self.df) - len(self.stock_hold)))
        self.df['Stock Holding'] = self.stock_hold[:len(self.df)]
        return self.df['Stock Holding']
    
    def get_cap_V(self):
        '''
        Get the capital money in the money market
        '''
        self.cap_V.extend([0] * (len(self.df) - len(self.cap_V)))
        self.df['Capital Money'] = self.cap_V[:len(self.df)]
        return self.df['Capital Money']
    
    def get_PnL(self):
        '''
        Get the profit and loss
        '''
        # merge the PnL to the length of the stock data
        self.PnL.extend([0] * (len(self.df) - len(self.PnL)))
        self.df['PnL'] = self.PnL[:len(self.df)]
        return self.df['PnL']
    
    def get_cumulative_PnL(self):
        '''
        Get the cumulative profit and loss
        '''
        self.df['Cumulative PnL'] = np.cumsum(self.get_PnL())
        return self.df['Cumulative PnL']
    
    def get_V_0(self):
        '''
        Get the initial investment
        '''
        return self.V_0
    
    def get_L(self):
        '''
        Get the leverage
        '''
        return self.L
    
    def get_theta_0(self):
        '''
        Get the initial dollar value of stock
        '''
        return self.theta_0
    
    def get_df(self):
        '''
        Get the DataFrame of the stock data
        '''
        return self.df

    def get_turnover_dollars(self):
        '''
        Get the turnover dollars
        '''
        theta = self.get_theta()
        self.df['delta_theta'] = (theta - theta.shift(1))
        self.df['turnover_dollars'] = abs(self.df['delta_theta']).cumsum()
        return self.df['turnover_dollars']
    
    def get_turnover_unit(self):
        '''
        Get the turnover unit
        '''
        stock_hold = self.get_stock_hold()
        self.df['delta_stock_hold'] = stock_hold - stock_hold.shift(1)
        self.df['turnover_unit'] = abs(self.df['delta_stock_hold']).cumsum()
        return self.df['turnover_unit']
    
    def get_cumulative_cap_V(self):
        '''
        Get the cumulative capital money
        '''
        cap_V_total = [0]
        for i in range(1, len(self.get_cap_V())): 
            cap_V_total.append((cap_V_total[i-1] + self.get_cap_V()[i]) * (1 + self.df['Daily Rate'][i]/100))
        self.df['cumulative_cap_V'] = np.array(cap_V_total)
        return self.df['cumulative_cap_V']
    
    def get_delta_cap_V(self):
        '''
        Get the change in capital money
        '''
        self.df['delta_cap_V'] = self.get_cumulative_cap_V() - self.get_cumulative_cap_V().shift(1)
        return self.df['delta_cap_V']
    
