import os

default_colors = ["#5f99e3", "#8ac87b", "#edc65f", "#e07a75", "#b26dda", "#878e96", "#91c1f2", "#b1e4a9", "#f8e088", "#e9afad", "#d0a2eb", "#8b7dec",
            "#3962a0", "#58854e", "#d89348", "#ca6839", "#8d354d", "#733d91", "#5347b7", "#36393e"]


def default_layout(fig):
    fig.update_layout(template='plotly_white', margin=dict(
        l=80, r=80, b=5, t=60, pad=0), colorway=default_colors)

def createDashSelectorOptions(options):
    """Create dash objector for use in selector options"""
    dash_options = [
        {"label": str(option), "value": options.index(option)}
        for option in options
    ]
    return dash_options
    