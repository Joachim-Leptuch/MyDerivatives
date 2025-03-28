import streamlit as st
from matplotlib import pyplot as plt
import yfinance as yf
import pandas as pd
import datetime
import lxml

from modules import BSM
from data import tickers
from utils import utils_pricing as utils

# Initilize application
days_year = 365
performed_pricing = False
today_date = datetime.datetime.today().date()

paramValuesDict = {
    'Spot': 'S', 'Strike':'K', 'Vol': 'sigma', 'Maturity': 'T', 'Rate': 'r', 'Div': 'q', 'Type': 'option_type',
    'Style':'option_style'
}

targetValuesDict = {
    "Option Price": "price", "Delta": "delta", "Gamma": "gamma", "Vega": "vega", "Theta": "theta", "Rho": "rho",
    "Vanna": "vanna", "Volga": "volga"
}

# Initialize underlyings
underlyings = {
    'SP500': tickers.sp500_tickers
}

# Correspondances ticker broker

# PRICER
st.title('Options Pricer')

body = "The underlying price, dividend, and interest rate variables are automatically updated."
st.caption(body, unsafe_allow_html=False)

characteristics, parameters_col = st.columns(2)

# Charasteristics
index = characteristics.selectbox('Select an index',
                     list(underlyings.keys()))

stock = characteristics.selectbox('Select stock',
                     underlyings[index])

option_type = characteristics.selectbox("What is the option type?",
                             ('Call', 'Put'))

exercise_style = characteristics.selectbox("What should be the exercise style?",
                             ('European'))

# Get target stock yahoo price
ticker = underlyings['SP500'][stock]
ticker_tf = yf.Ticker(ticker)

price = ticker_tf.history(period='1d')['Close'].iloc[0]
try:
    div_yield = ticker_tf.info.get('dividendYield') * 100
except:
    div_yield = 0.00

risk_free = yf.Ticker('^TNX').history(period='1d')['Close'].iloc[0]

# Parameters
parameters = {
    'Spot': parameters_col.number_input('Underlying price', value=price, step=0.01),
    'Strike': parameters_col.number_input('Strike price', step=0.01),
    'Maturity': characteristics.date_input('Maturity date', value=None, min_value=today_date),
    'Rate': parameters_col.number_input('Interest rate (%)', value=risk_free, step=0.01),
    'Div': parameters_col.number_input('Dividend yield (%)', value=div_yield, step=0.01),
    'Vol': parameters_col.number_input('Volatility (%)', step=0.01),
    'Type': option_type,
    'Style': exercise_style
}

# Format figures
parameters['Maturity'] = (parameters['Maturity'] - today_date).days / days_year if parameters['Maturity'] is not None else 0
parameters['Rate'] /= 100; parameters['Vol'] /= 100; parameters['Div'] /= 100

# Run pricing algorithm
option_price = 0

@st.cache_data
def price_option(parameters, option_type, exercise_style):
    option_price = None

    if exercise_style == 'European':
        option_price = BSM.BlackScholesOption(parameters['Spot'], parameters['Strike'], parameters['Maturity'],
                                                        parameters['Rate'], parameters['Div'], parameters['Vol'],
                                                        option_type, exercise_style).price

    return option_price

if not st.button("Price"):
    pass
else:
    if not all(parameters):
        st.write("Please input all required parameters to price the option.")
        st.write("Missing/Invalid Parameters:", [p for p in parameters if not p])
    elif parameters['Spot'] == 0 or parameters['Strike'] == 0 or parameters['Maturity'] == 0 :
        st.write("The specified maturity, sport or strike is 0. Input higher value.")
    else:

        option_price = price_option(parameters, option_type, exercise_style)
        st.write(f"The price for the {exercise_style} {option_type} on {stock} is {round(option_price, 3)} $.")

        performed_pricing = True

# Sensitivities modelling
st.title('Greeks Modelling')

risks, primary_factors, secondary_factors = st.columns(3)

risk = risks.selectbox("Choose the modelling target",
                             ('Option Price', 'Delta', 'Gamma', 'Vega', 'Theta', 'Rho', 'Vanna', 'Volga'))

primary_factor = primary_factors.selectbox("Choose the first factor",
                                           ('Spot', 'Maturity', 'Vol', 'Rate', 'Div'))

secondary_factor = secondary_factors.selectbox("Choose the second factor",
                                               (None, 'Spot', 'Maturity', 'Vol', 'Rate', 'Div'))


risk_granularity = risks.number_input('Granularity.', value=30, step=1, max_value=100, min_value=1)

first_param_range = primary_factors.number_input('Parameter range.', value=0.90, step=0.01, max_value=0.99,
                                                 min_value=0.1, key="#P1R")
if secondary_factor and secondary_factor != 'Maturity':
    second_param_range = secondary_factors.number_input('Parameter range.', value=0.50, step=0.01, max_value=0.99,
                                                        min_value=0.1, key="#P2R")
else:
    second_param_range = 1

# Prepare params
params = {new_key: parameters[old_key] for old_key, new_key in paramValuesDict.items() if old_key in parameters}

params_check = True  # Assume all parameters are valid initially

for k, v in params.items():
    if v == 0 or v == "":
        if k == 'q':  # Allow 'Div' to be 0
            continue
        params_check = False
        break  # Stop checking further as one invalid parameter is enough

if params_check:

    # 2D Risk modelling
    if secondary_factor is None:

        # Create linear space for the first factor
        first_factor_lin_space = utils.create_linear_spaces_risk_factors(primary_factor, parameters, first_param_range, risk_granularity)

        # Replace first value with a small number if necessary
        if primary_factor == 'Maturity':
            first_factor_lin_space[0] = 1e-05

        # Compute target values
        target_values = [
            getattr(BSM.BlackScholesOption(**{**params, paramValuesDict[primary_factor]: firstParam}),
                    targetValuesDict[risk])
            for firstParam in first_factor_lin_space
        ]

        # Convert to series
        target_values = pd.DataFrame(target_values, index=first_factor_lin_space, columns=[risk])

    # 3D Risk modelling
    elif not secondary_factor is None:

        # Create linear spaces for risk factors
        first_factor_lin_space = utils.create_linear_spaces_risk_factors(primary_factor, parameters,
                                                                         first_param_range, risk_granularity)
        second_param_lin_space = utils.create_linear_spaces_risk_factors(secondary_factor, parameters,
                                                                         second_param_range, risk_granularity)

        if primary_factor == 'Maturity':
            first_factor_lin_space[0] = 1e-05

        if secondary_factor == 'Maturity':
            second_param_lin_space[0] = 1e-05

        # Set target values storage
        target_values = pd.DataFrame(columns=first_factor_lin_space, index=second_param_lin_space)

        for firstParam in first_factor_lin_space:
            for secondParam in second_param_lin_space:

                params[paramValuesDict[primary_factor]] = firstParam
                params[paramValuesDict[secondary_factor]] = secondParam

                # Get option instance
                option = BSM.BlackScholesOption(**params)

                # Create dataframe
                target_values.at[secondParam, firstParam] = getattr(option, targetValuesDict[risk])

    # Show results
    if secondary_factor is None and not target_values.empty: # 2D Graph

        if primary_factor == 'Maturity':
            first_factor_lin_space *= days_year

        st.subheader(f"{risk} as function of {primary_factor}")

        fig = plt.figure()
        plt.plot(target_values, label=f'{risk} as function of {primary_factor}')
        plt.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.5)
        plt.xlabel(f"{primary_factor}", fontsize=12)  # Fixed: Changed `ax.xlabel` to `ax.set_xlabel`
        plt.ylabel(f"{risk}", fontsize=12)  # Fixed: Changed `ax.ylabel` to `ax.set_ylabel`
        plt.legend()  # Add a legend for clarity
        plt.tight_layout()  # Fixed: Use `plt.tight_layout` at the figure level
        st.pyplot(fig)

        # st.line_chart(target_values)

    if secondary_factor is not None and not target_values.empty: # 3D Surface

        if primary_factor == 'Maturity':
            first_factor_lin_space *= days_year
        if secondary_factor == 'Maturity':
            second_param_lin_space *= days_year

        # Use the plotting function and display in Streamlit
        fig = utils.plot_surface(target_values, primary_factor, secondary_factor, risk)
        st.plotly_chart(fig, use_container_width=True)
else:
    st.write("Please input parameters and price the option first.")
