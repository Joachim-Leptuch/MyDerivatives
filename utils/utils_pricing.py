import plotly.graph_objects as go
import numpy as np

# Function to calculate bounds and step for linear spaces
def calculate_bounds_and_step(factor, parameters, RISK_RANGE, RISK_GRANULARITY):
    """Helper function to calculate bounds and step size for the linear space."""
    if factor == 'Maturity':
        lower_bound = 0
        upper_bound = parameters[factor]
        step = upper_bound / RISK_GRANULARITY
    else:
        lower_bound = parameters[factor] * (1 - RISK_RANGE)
        upper_bound = parameters[factor] * (1 + RISK_RANGE)
        step = (upper_bound - lower_bound) / RISK_GRANULARITY
    return lower_bound, upper_bound, step

# Function to create linear spaces for risk factors
def create_linear_spaces_risk_factors(factor, parameters, risk_range, risk_granularity):

    # Calculate bounds and step size
    lbound, ubound, step = calculate_bounds_and_step(factor, parameters, risk_range, risk_granularity)

    # Create lin_space
    lin_space_risk_factor = np.arange(lbound, ubound, step)

    return lin_space_risk_factor

# Function to plot the surface
def plot_surface(data, x_label, y_label, z_label):

    # Create a meshgrid for plotting based on the DataFrame index and columns
    x = data.columns
    y = data.index
    z = data.values

    # Plotly surface plot
    fig = go.Figure(data=[go.Surface(z=z, x=x, y=y, colorscale='Plasma')])

    # Update layout for labels
    fig.update_layout(
        title=f"{z_label} as function of {x_label} and {y_label}",
        scene=dict(
            xaxis_title=x_label,
            yaxis_title=y_label,
            zaxis_title=z_label,
            camera = dict(
                eye=dict(x=1.3, y=1.3, z=1.3)  # Adjust x, y, z for zoom
            )
        ),
        margin = dict(l=10, r=10, t=40, b=10)  # Margin values

    )
    return fig