import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pickle

# Set page config for dashboard quality
st.set_page_config(page_title="Hedge Fund Risk Dashboard", layout="wide")

def load_backtest_results():
    """Correctly deserializes backtest results for visualization."""
    try:
        with open('results.pkl', 'rb') as f:
            # FIX: Use pickle.load(f) instead of pickle.read(f)
            return pickle.load(f)
    except FileNotFoundError:
        st.error("No backtest results found. Please run main.py first.")
        return None
    except Exception as e:
        st.error(f"Error loading results: {e}")
        return None

def run_dashboard():
    st.title("📊 Hedge Fund Risk Modeling & Trading System")
    st.markdown("### Performance Insights and Risk Assessment")
    
    results = load_backtest_results()
    if not results: return

    # --- Metrics Row: Issue 12, 13, 18 ---
    col1, col2, col3, col4 = st.columns(4)
    metrics = results['risk_metrics']
    col1.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
    col2.metric("Annualized Alpha", f"{metrics['alpha']:.2%}")
    col3.metric("Portfolio Beta", f"{metrics['beta']:.2f}")
    col4.metric("Max Drawdown", f"{results['max_drawdown']:.2%}")

    # --- Performance Trajectory: Issue 18 ---
    st.subheader("Cumulative Portfolio Returns")
    fig_returns = px.line(results['equity_curve'], title="Portfolio Value Over Time")
    st.plotly_chart(fig_returns, use_container_width=True)

    # --- Explainable Strategy Logs: Issue 14 & 18 ---
    st.subheader("📜 Explainable Trade Logs")
    trade_df = pd.DataFrame(results['trade_logs'])
    st.dataframe(trade_df, use_container_width=True)

    # --- Risk Exposure: Issue 6 & 18 ---
    st.subheader("Value at Risk (VaR) Analysis")
    st.write(f"The 95% Confidence 1-Day VaR is: **{results['var_95']:.2%}**")

if __name__ == "__main__":
    run_dashboard()