import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page Config
st.set_page_config(page_title="☕ Super Cool Cafe Breakeven Tracker", layout="wide")

# CSS for Styling (Optional)
st.markdown("""
    <style>
        * {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .main-header {
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
        }
        .metric-box {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 15px;
            border-radius: 15px;
            text-align: center;
            font-weight: bold;
            font-size: 18px;
            margin: 10px 0;
        }
        .profit-positive {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            padding: 15px;
            border-radius: 15px;
            text-align: center;
            font-weight: bold;
            font-size: 18px;
        }
        .profit-negative {
            background: linear-gradient(45deg, #f44336, #d32f2f);
            color: white;
            padding: 15px;
            border-radius: 15px;
            text-align: center;
            font-weight: bold;
            font-size: 18px;
        }
        .chart-container {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Cafe Parameters
items = {
    "Latte": {"price": 150, "variable_cost": 50, "color": "#8B4513"},
    "Americano": {"price": 120, "variable_cost": 40, "color": "#654321"},
    "Cappuccino": {"price": 180, "variable_cost": 60, "color": "#D2691E"}
}
fixed_costs = 50000  # Rent, salaries, etc.

# Session State Initialization
if "state" not in st.session_state:
    st.session_state.state = {"Latte": 0, "Americano": 0, "Cappuccino": 0}

if "sales_history" not in st.session_state:
    st.session_state.sales_history = []

# Helper Functions
def update_sales(item, action):
    state = st.session_state.state
    sales_history = st.session_state.sales_history

    if action == "add":
        state[item] += 1
    elif action == "remove" and state[item] > 0:
        state[item] -= 1

    total_units = sum(state.values())
    revenue = sum(state[item] * items[item]["price"] for item in state)
    variable_cost = sum(state[item] * items[item]["variable_cost"] for item in state)
    contribution = revenue - variable_cost
    profit = contribution - fixed_costs

    sales_history.append({
        'total_units': total_units,
        'revenue': revenue,
        'variable_cost': variable_cost,
        'contribution': contribution,
        'profit': profit,
        'state': state.copy()
    })

    st.session_state.sales_history = sales_history


def create_charts():
    """Create comprehensive analytics charts"""
    sales_history = st.session_state.sales_history  # Fixed: Use session state
    state = st.session_state.state  # Also ensure state is accessed from session

    if not sales_history:
        fig = go.Figure()
        fig.add_annotation(
            text="Start selling items to see analytics!<br>📊📈",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            font=dict(size=20, color="gray")
        )
        fig.update_layout(
            showlegend=False,
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        return fig

    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('📊 Sales by Item', '💰 Revenue Breakdown', '📈 Cumulative Profit', '🎯 Breakeven Progress'),
        specs=[[{"type": "pie"}, {"type": "bar"}],
               [{"type": "xy"}, {"type": "indicator"}]],
        horizontal_spacing=0.15,
        vertical_spacing=0.3
    )

    # Pie Chart - Sales Distribution
    sales_data = [state[item] for item in items.keys()]
    colors = [items[item]["color"] for item in items.keys()]
    if sum(sales_data) > 0:
        fig.add_trace(go.Pie(labels=list(items.keys()), values=sales_data,
                             marker_colors=colors, hole=0.4,
                             textinfo='label+percent+value'), row=1, col=1)

    # Bar Chart - Revenue Breakdown
    revenues = [state[item] * items[item]["price"] for item in items.keys()]
    fig.add_trace(go.Bar(x=list(items.keys()), y=revenues,
                         marker_color=colors,
                         text=[f"₹{rev}" for rev in revenues],
                         textposition='auto'), row=1, col=2)

    # Line Chart - Cumulative Profit
    cumulative_profits = [entry['profit'] for entry in sales_history]
    fig.add_trace(go.Scatter(y=cumulative_profits, mode='lines+markers',
                             line=dict(color='#4CAF50', width=3),
                             marker=dict(size=8, color='#4CAF50'),
                             fill='tozeroy' if any(p >= 0 for p in cumulative_profits) else None),
                  row=2, col=1)

    # ✅ Add Breakeven Line
    fig.add_hline(y=0, line_dash="dash", line_color="red",
                  annotation_text="Breakeven Line", row=2, col=1)

    # Indicator - Breakeven Progress
    current_profit = cumulative_profits[-1] if cumulative_profits else -fixed_costs
    breakeven_percentage = max(0, min(100, ((current_profit + fixed_costs) / fixed_costs) * 100))
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=breakeven_percentage,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Breakeven %"},
        delta={'reference': 100},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "#4CAF50" if breakeven_percentage >= 100 else "#ff6b6b"},
            'steps': [{'range': [0, 50], 'color': "lightgray"},
                      {'range': [50, 100], 'color': "gray"}],
            'threshold': {'line': {'color': "red", 'width': 4}, 'value': 100}
        }
    ), row=2, col=2)

    fig.update_layout(
        height=700,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        title_font_size=16,
        margin=dict(l=50, r=50, t=80, b=50)
    )

    fig.update_yaxes(title_text="Cumulative Profit (₹)", row=2, col=1)

    return fig

def reset_all():
    st.session_state.state = {"Latte": 0, "Americano": 0, "Cappuccino": 0}
    st.session_state.sales_history = []


# UI Layout
st.markdown('<h1 class="main-header">☕ SUPER COOL CAFE BREAKEVEN TRACKER 📊</h1>', unsafe_allow_html=True)

with st.container():
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("🎛️ CONTROL PANEL")
        for item in items:
            with st.expander(f"☕ {item}", expanded=True):
                price = st.slider(f"Set {item} Price (₹)", 50, 300, step=5,
                                  value=items[item]["price"], key=f"{item}_price")
                items[item]["price"] = price
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button(f"🛒 Sell {item}", key=f"sell_{item}"):
                        update_sales(item, "add")
                        st.rerun()
                with col_btn2:
                    if st.button(f"❌ Remove {item}", key=f"remove_{item}"):
                        update_sales(item, "remove")
                        st.rerun()

        if st.button("🔄 RESET ALL", use_container_width=True):
            reset_all()
            st.rerun()

    with col2:
        st.subheader("📊 REAL-TIME ANALYTICS")

        state = st.session_state.state
        total_units = sum(state.values())
        revenue = sum(state[item] * items[item]["price"] for item in state)
        variable_cost = sum(state[item] * items[item]["variable_cost"] for item in state)
        contribution = revenue - variable_cost
        profit = contribution - fixed_costs

        col_stats1, col_stats2 = st.columns(2)
        with col_stats1:
            st.markdown(f'<div class="metric-box">📦 Units Sold: <br>'
                        f'{"".join([f"<br>☕ {item}: {count}" for item, count in state.items()])}</div>',
                        unsafe_allow_html=True)
            st.markdown(f'<div class="metric-box">💰 Total Revenue: ₹{revenue:,}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-box">📦 Variable Cost: ₹{variable_cost:,}</div>', unsafe_allow_html=True)
        with col_stats2:
            st.markdown(f'<div class="metric-box">📈 Contribution Margin: ₹{contribution:,}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-box">🏢 Fixed Costs: ₹{fixed_costs:,}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-box">💵 Net Profit: ₹{profit:,}</div>', unsafe_allow_html=True)

        if profit >= 0:
            st.markdown(f'<div class="profit-positive">🎉 BREAKEVEN ACHIEVED! Profit: ₹{profit:,}</div>', unsafe_allow_html=True)
        else:
            needed = abs(profit)
            st.markdown(f'<div class="profit-negative">📈 Need ₹{needed:,} more to breakeven</div>', unsafe_allow_html=True)

        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.plotly_chart(create_charts(), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
