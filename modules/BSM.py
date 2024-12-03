import math
from scipy.stats import norm


class BlackScholesOption:
    """
    Black & Scholes option object for european style options.
    """

    def __init__(self, S: float, K: float, T: float, r: float, q: float, sigma: float, option_type: str,
                 option_style: str):

        assert sigma >= 0, "Volatility can't be less than zero"
        assert S >= 0, "Initial stock value can't be less than zero"
        assert K >= 0, "Strike price can't be less than zero"
        assert T >= 0, "Time to maturity can't be less than zero"
        assert option_type in ['Call', 'Put'], "Option type must be either Call or Put"
        assert option_style == 'European', "Option style must be European"
        assert q >= 0, "Dividend yield cannot be less than zero"

        # Parameters
        self.type = str(option_type)
        self.style = str(option_style)
        self.S = float(S)
        self.K = float(K)
        self.r = float(r)
        self.sigma = float(sigma)
        self.T = float(T)
        self.q = float(q)

        # Calculations
        self.d1 = self.d1()
        self.d2 = self.d2()

        self.price = self.optionPrice()

        self.delta = self.optionDelta()
        self.gamma = self.optionGamma()
        self.vega = self.optionVega()
        self.theta = self.optionTheta()
        self.rho = self.optionRho()

        self.vanna = self.optionVanna()
        self.volga = self.optionVolga()
        self.charm = self.optionCharm()
        self.color = self.optionColor()
        self.speed = self.optionSpeed()

        self.gearing = self.optionLambda()
        self.epsilon = self.optionEpsilon()

    def N(self, x):
        """
        Cumulative distribution function of a normal distribution.
        """
        return norm.cdf(x, 0, 1)

    def n(self, x):
        """
        Probability density function of a normal distribution.
        """
        return norm.pdf(x, 0, 1)

    def d1(self):
        d1 = (math.log(self.S / self.K) + (self.r + self.sigma ** 2 / 2) * self.T) / \
             (self.sigma * math.sqrt(self.T))

        return d1

    def d2(self):
        d2 = self.d1 - self.sigma * math.sqrt(self.T)

        return d2

    def optionPrice(self) -> float:
        if self.type == 'Put':
            price = self.K * math.exp(-self.r * self.T) * self.N(-self.d2) - self.S * math.exp(
                -self.q * self.T) * self.N(-self.d1)
        elif self.type == 'Call':
            price = self.S * math.exp(-self.q * self.T) * self.N(self.d1) - self.K * math.exp(
                -self.r * self.T) * self.N(self.d2)

        return price

    def optionDelta(self) -> float:
        """
        Rate of change of the theoretical option value with respect to changes in the underlying price.
        """
        if self.type == 'Put':
            delta = -math.exp(-self.q * self.T) * self.N(-self.d1)
        elif self.type == 'Call':
            delta = math.exp(-self.q * self.T) * self.N(self.d1)

        return delta

    def optionGamma(self) -> float:
        """
        Rate of change in the delta with respect to changes in the underlying price.
        """
        gamma = (self.n(self.d1) * math.exp(-self.q * self.T)) / (self.S * self.sigma * math.sqrt(self.T))

        return gamma

    def optionVega(self) -> float:
        """
        Sensivity of the option theoretical value with respect to changes in the volatility.
        """
        vega = self.S * math.exp(-self.q * self.T) * self.n(self.d1) * math.sqrt(self.T)

        return vega * 0.01

    def optionTheta(self) -> float:
        """
        Sensivity of the option theoretical value over the passage of time.
        """
        if self.type == 'Put':
            theta = -math.exp(-self.q * self.T) * (self.S * self.n(self.d1) * self.sigma) / (
                        2 * math.sqrt(self.T)) + self.r * \
                    self.K * math.exp(-self.r * self.T) * self.N(-self.d2) - self.q * self.S * math.exp(
                -self.q * self.T) * self.N(-self.d1)
        elif self.type == 'Call':
            theta = - math.exp(-self.q * self.T) * (self.S * self.n(self.d1) * self.sigma) / (
                        2 * math.sqrt(self.T)) - self.r * \
                    self.K * math.exp(-self.r * self.T) * self.N(self.d2) + self.q * self.S * math.exp(
                -self.q * self.T) * self.N(self.d1)

        return theta / 365

    def optionRho(self) -> float:
        """
        Sensivity of the option price to changes in interest rates.
        """
        if self.type == 'Put':
            rho = -self.K * self.T * math.exp(-self.r * self.T) * self.N(-self.d2)
        elif self.type == 'Call':
            rho = self.K * self.T * math.exp(-self.r * self.T) * self.N(self.d2)
        return rho * 0.01

    def optionLambda(self) -> float:
        """
        Lambda, omega or elasticity. Called gearing.
        Represents the percentage change in option value per percentage change in the underlying price.
        """

        gearing = self.delta * (self.S / self.price)

        return gearing

    def optionEpsilon(self) -> float:
        """
        Epsilon. Called psi.
        Represents the percentage change in option value per percentage change in the underlying dividend yield.
        """
        if self.type == 'Put':
            epsilon = self.S * self.r * math.exp(-self.q * self.T) * self.N(-self.d1)
        elif self.type == 'Call':
            epsilon = - self.S * self.r * math.exp(-self.q * self.T) * self.N(self.d1)

        return epsilon

    def optionVanna(self) -> float:
        """
        Sensitivity of the option delta with respect to change in volatility or,
        alternatively, the partial of vega with respect to the underlying instrument's price.
        """
        vanna = - math.exp(-self.q * self.T) * self.n(self.d1) * (self.d2 / self.sigma)

        return vanna * 0.01

    def optionVolga(self) -> float:
        """
        Vomma or Volga measures the rate of change to vega as volatility changes.
        It is the second order price sensivity to volatility.
        """
        volga = self.S * math.exp(-self.q * self.T) * self.n(self.d1) * math.sqrt(self.T) * (
                    self.d1 * self.d2 / self.sigma)

        return volga * 0.0001

    def optionCharm(self) -> float:
        """
        Charm is a second-order derivative of the option value, once to price and once to the passage of time.
        It is also then the derivative of theta with respect to the underlying's price.
        """
        if self.type == 'Put':
            charm = -self.q * math.exp(-self.q * self.T) * self.N(-self.d1) - math.exp(-self.q * self.T) * self.n(
                self.d1) * \
                    (2 * (self.r - self.q) * self.T - self.d2 * self.sigma * math.sqrt(self.T)) / (
                                2 * self.T * self.sigma * math.sqrt(self.T))
        elif self.type == 'Call':
            charm = self.q * math.exp(-self.q * self.T) * self.N(self.d1) - math.exp(-self.q * self.T) * self.n(
                self.d1) * \
                    (2 * (self.r - self.q) * self.T - self.d2 * self.sigma * math.sqrt(self.T)) / (
                                2 * self.T * self.sigma * math.sqrt(self.T))

        return charm / 365

    def optionColor(self) -> float:
        """
        Rate of change in the gamma over the passage of time.
        """
        color = -math.exp(-self.q * self.T) * (
                    self.n(self.d1) / (2 * self.S * self.T * self.sigma * math.sqrt(self.T))) * \
                (2 * self.q * self.T + 1 + (
                            (2 * (self.r - self.q) * self.T - self.d2 * self.sigma * math.sqrt(self.T)) / (
                                self.sigma * math.sqrt(self.T))) * self.d1)

        return color / 365

    def optionSpeed(self) -> float:
        """
        Rate of change in the gamma with respect to changes in the underlying price.
        """
        speed = -math.exp(-self.q * self.T) * (self.n(self.d1) / (self.S ** 2 * self.sigma * math.sqrt(self.T))) * \
                ((self.d1 / (self.sigma * math.sqrt(self.T))) + 1)

        return speed

    def impliedVolatility(self, marketPrice, tolerance=0.00001):
        """
        Derives the implied volatility of an European Option with Newton-Raphson Algorithm
        """
        S = self.S
        K = self.K
        T = self.T * 365
        r = self.r * 100
        q = self.q * 100
        oldVolatility = self.sigma * 100

        maxIterations = 500

        for k in range(maxIterations):

            newInstance = BlackScholesOption(S, K, T, r, q, oldVolatility, self.type, self.style)
            theoPrice = newInstance.price
            optionPremium = newInstance.vega * 100
            OptionPrice = theoPrice - marketPrice
            newVolatility = oldVolatility - OptionPrice / optionPremium

            if newVolatility < 0:
                continue

            newTheoPrice = BlackScholesOption(S, K, T, r, q, newVolatility, self.type, self.style).price

            if (abs(oldVolatility - newVolatility) < tolerance or abs(newTheoPrice - marketPrice) < tolerance):
                break
            oldVolatility = newVolatility

        impliedVolatility = oldVolatility

        return impliedVolatility

    def optionPayoff(self, St):

        if self.type == 'Call':

            payoff = max(St - self.K, 0)

        elif self.type == 'Put':

            payoff = max(self.K - St, 0)

        return payoff