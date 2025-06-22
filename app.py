import streamlit as st
import plotly.graph_objects as go

# Page Config
st.set_page_config(page_title="☕ My Café", layout="wide")

# CSS for Styling with Watermark
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
        .watermark {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-45deg);
            font-size: 2rem;
            color: rgba(0, 0, 0, 0.1);
            pointer-events: none;
            z-index: 0;
            font-weight: bold;
            text-align: center;
        }
        .footer-watermark {
            position: fixed;
            bottom: 10px;
            left: 0;
            width: 100%;
            text-align: center;
            font-size: 0.9rem;
            color: rgba(0, 0, 0, 0.5);
            pointer-events: none;
            z-index: 1000;
        }
    </style>
    <div class="watermark">Powered by BITSoM AI Center</div>
    <div class="footer-watermark">© 2025 BITSoM AI Center. All rights reserved.</div>
""", unsafe_allow_html=True)

# Cafe Parameters
items = {
    "Latte": {"price": 100, "variable_cost": 50, "color": "#8B4513"},  # Set default price
    "Americano": {"price": 90, "variable_cost": 40, "color": "#654321"},
    "Cappuccino": {"price": 120, "variable_cost": 60, "color": "#D2691E"}
}
fixed_costs = 10000  # Rent, salaries, etc.

# Session State Initialization
if "state" not in st.session_state:
    st.session_state.state = {"Latte": 0, "Americano": 0, "Cappuccino": 0}

# Helper Functions
def update_sales(item):
    quantity = st.session_state[f"quantity_{item}"]
    st.session_state.state[item] = max(0, quantity)  # Ensure quantity is non-negative

def create_breakeven_chart():
    """Create simple breakeven bar chart"""
    state = st.session_state.state
    
    # Calculate contribution for each product
    contributions = {}
    for item in items:
        contribution_per_unit = items[item]["price"] - items[item]["variable_cost"]
        contributions[item] = state[item] * contribution_per_unit
    
    total_contribution = sum(contributions.values())
    
    # Create the chart
    fig = go.Figure()
    
    # Add stacked bars for contributions from each product
    bottom = 0
    for item, contribution in contributions.items():
        # Show all items, even with zero contribution, for visibility
        fig.add_trace(go.Bar(
            x=['Total Contribution'],
            y=[max(0, contribution)],  # Use max to avoid negative bars
            name=f'{item} Contribution',
            marker_color=items[item]["color"],
            base=bottom,
            text=f'₹{contribution:,}' if contribution != 0 else '₹0',
            textposition='inside' if contribution > 10000 else 'outside',
            textfont=dict(color='white' if contribution > 10000 else 'black')
        ))
        if contribution > 0:
            bottom += contribution
    
    # Add fixed costs bar
    fig.add_trace(go.Bar(
        x=['Fixed Costs'],
        y=[fixed_costs],
        name='Fixed Costs',
        marker_color='#ff4444',
        text=f'₹{fixed_costs:,}',
        textposition='inside',
        textfont=dict(color='white')
    ))
    
    # Add breakeven line
    if total_contribution > 0:
        max_height = max(total_contribution, fixed_costs)
        fig.add_hline(
            y=fixed_costs, 
            line_dash="dash", 
            line_color="red", 
            line_width=3,
            annotation_text="Breakeven Line",
            annotation_position="top right"
        )
    
    # Update layout
    fig.update_layout(
        title={
            'text': '🎯 Breakeven Analysis - Contribution vs Fixed Costs',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#333'}
        },
        yaxis_title="Amount (₹)",
        xaxis_title="",
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=14),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Add annotations for better understanding
    if total_contribution >= fixed_costs:
        profit = total_contribution - fixed_costs
        fig.add_annotation(
            x=0,
            y=total_contribution + 2000,
            text=f"🎉 BREAKEVEN ACHIEVED!<br>Profit: ₹{profit:,}",
            showarrow=True,
            arrowhead=2,
            arrowcolor="green",
            bgcolor="lightgreen",
            bordercolor="green"
        )
    else:
        shortfall = fixed_costs - total_contribution
        fig.add_annotation(
            x=0,
            y=total_contribution + 2000,
            text=f"📈 Need ₹{shortfall:,} more<br>to reach breakeven",
            showarrow=True,
            arrowhead=2,
            arrowcolor="orange",
            bgcolor="lightyellow",
            bordercolor="orange"
        )
    
    return fig

def reset_all():
    st.session_state.state = {"Latte": 0, "Americano": 0, "Cappuccino": 0}

# UI Layout
st.markdown('<h1 class="main-header">☕ My Café 📊</h1>', unsafe_allow_html=True)

with st.container():
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("🎛️ CONTROL PANEL")
        for item in items:
            with st.expander(f"☕ {item}", expanded=True):
                price = st.slider(f"Set {item} Price (₹)", 50, 300, step=5,
                                  value=items[item]["price"], key=f"{item}_price")
                items[item]["price"] = price
                
                # Show variable cost info
                st.info(f"📊 Variable Cost: ₹{items[item]['variable_cost']}")
                
                # Quantity slider
                st.slider(
                    f"Set {item} Quantity",
                    min_value=0,
                    max_value=100,
                    value=st.session_state.state[item],
                    step=1,
                    key=f"quantity_{item}",
                    on_change=update_sales,
                    args=(item,)
                )

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
                        f'{"".join([f"<br>☕ {item}: {count} × ₹{items[item]['price']} = ₹{count * items[item]['price']}" for item, count in state.items()])}</div>',
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
        st.plotly_chart(create_breakeven_chart(), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
