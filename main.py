import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go


def calculate_compounding(
    interest_rate: float, initial_investment: int, yearly_contributions: int, n_years: int
) -> pd.DataFrame:
    future_values = np.zeros(n_years + 1)
    future_values[0] = initial_investment
    for i in range(1, n_years + 1):
        future_values[i] = future_values[i - 1] * (1 + interest_rate) + yearly_contributions
    future_values = future_values[1:]
    total_contributions = np.cumsum(np.repeat(yearly_contributions, n_years))
    accrued_interest = future_values - total_contributions
    data_result = pd.DataFrame(
        {
            "Year": np.arange(1, n_years + 1),
            "Total Contributions": total_contributions,
            "Accrued Interest": accrued_interest,
            "Total Value": future_values,
        }
    )
    return data_result


def make_chart_1(data_frame: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    # Adding bars for A
    fig.add_trace(
        go.Bar(
            x=data_frame["Year"],
            y=data_frame["Total Contributions"],
            name="Total Contributions",
            marker_color="rgb(55, 83, 109)",
        )
    )

    # Adding bars for B
    fig.add_trace(
        go.Bar(
            x=data_frame["Year"],
            y=data_frame["Accrued Interest"],
            name="Accrued Interest",
            marker_color="rgb(26, 118, 255)",
        )
    )

    # Adding line for C
    fig.add_trace(
        go.Scatter(
            x=data_frame["Year"],
            y=data_frame["Total Value"],
            name="Total Value",
            mode="lines+markers",
            marker=dict(color="rgb(0, 204, 150)", size=10),
            line=dict(color="rgb(0, 204, 150)", width=2),
        )
    )

    # Update layout
    fig.update_layout(
        barmode="stack",
        xaxis=dict(title="Year"),
        yaxis=dict(title="Values"),
        # title="Stacked Bar Plot with Line Plot",
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    )

    return fig


if __name__ == "__main__":
    st.title("Investment Calculator for the 3a pillar")

    interest_rate = st.number_input(
        "Market Return (yearly %)", min_value=0.0, max_value=100.0, value=8.0
    )
    interest_rate /= 100

    fees_stock = st.number_input(
        "Fees on your Broker app + ETF TER (yearly %)", min_value=0.0, max_value=100.0, value=0.2
    )
    fees_stock /= 100

    fees_3a = st.number_input(
        "3a Pillar Fees (yearly %)", min_value=0.0, max_value=100.0, value=0.5
    )
    fees_3a /= 100

    tax_rate = st.number_input(
        "Tax Rate After 3a pillar (yearly %)", min_value=0.0, max_value=100.0, value=20.0
    )
    tax_rate /= 100

    st.subheader("Option 1: investing yourself in the stock market")
    st.write(
        """
        Here we assume to invest all 7056 chf in the stock market every year.
        In this case the return is simply the market return minus the fees on your
        stock investements.
        """
    )

    rate_stocks = interest_rate - fees_stock
    data_result = calculate_compounding(
        rate_stocks, initial_investment=0, yearly_contributions=7056, n_years=40
    )

    fig = make_chart_1(data_result)
    st.plotly_chart(fig)
    st.dataframe(data_result, hide_index=True, use_container_width=True)

    st.subheader("Option 2: investing in the 3a pillar")
    st.write(
        """
        Here we assume that we invest 7056 chf in the 3a pillar every year,
        as well as the tax benfit we get from it in the stock market as above.
        For example, for a tax rate of 25%, we get 7056 * 0.25 = 1764 chf tax
        benefit that are invested in the stock market as above.
        At the end of the 40 years period, we have to pay taxes on the 3a pillar,
        so we show in the last row (41) the total value after taxes.
        """
    )

    rate_3a = interest_rate - fees_3a
    data_result_3a = calculate_compounding(
        rate_3a, initial_investment=0, yearly_contributions=7056, n_years=40
    )
    fig_3a = make_chart_1(data_result_3a)
    fig_3a.update_layout(title="3a Pillar Investment")
    st.plotly_chart(fig_3a)
    st.dataframe(data_result_3a, hide_index=True, use_container_width=True)

    data_result_tax_benefit = calculate_compounding(
        rate_stocks, initial_investment=0, yearly_contributions=7056 * tax_rate, n_years=40
    )
    fig_tax_benefit = make_chart_1(data_result_tax_benefit)
    fig_tax_benefit.update_layout(title="Tax Benefit Investment")
    st.plotly_chart(fig_tax_benefit)
    st.dataframe(data_result_tax_benefit, hide_index=True, use_container_width=True)

    # merge the two dataframes by summing the values
    total_3a_result = data_result_3a.copy()
    total_3a_result["Total Value"] += data_result_tax_benefit["Total Value"]
    total_3a_result["Total Contributions"] += data_result_tax_benefit["Total Contributions"]
    total_3a_result["Accrued Interest"] += data_result_tax_benefit["Accrued Interest"]

    # Taxes at the end
    gain = total_3a_result["Total Value"].iloc[-1] - total_3a_result["Total Contributions"].iloc[-1]
    tax = gain * tax_rate  # TODO: apparently this tax rate is lower than the normal one
    total_3a_result = pd.concat(
        [
            total_3a_result,
            pd.DataFrame(
                {
                    "Year": [41],
                    "Total Contributions": [None],
                    "Accrued Interest": [None],
                    "Total Value": [total_3a_result["Total Value"].iloc[-1] - tax],
                }
            ),
        ],
        ignore_index=True,
    )

    fig_3a_total = make_chart_1(total_3a_result)
    fig_3a_total.update_layout(title="Total Investment (3a + Tax Benefit)")
    st.plotly_chart(fig_3a_total)
    st.dataframe(total_3a_result, hide_index=True, use_container_width=True)

    st.subheader("Conclusion")
    st.write(
        "Option 1 total value after 40 years: ", f'{int(data_result["Total Value"].iloc[-1]):,}'
    )
    st.write(
        "Option 2 total value after 40 years and after final taxes: ",
        f'{int(total_3a_result["Total Value"].iloc[-1]):,}',
    )
