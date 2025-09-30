import streamlit as st
from agent.data_loader import FinanceDataLoader
from agent.tools import FinanceTools
from agent.planner import QueryPlanner
import plotly.graph_objects as go
import plotly.express as px
from agent.pdf_generator import PDFReportGenerator
import os
from datetime import datetime

st.set_page_config(page_title="CFO Copilot", page_icon="💼", layout="wide")

# Load data (caching it so it doesn't reload on every interaction)
@st.cache_data
def load_data():
    loader = FinanceDataLoader()
    return loader.load_all_data()


data = load_data()
tools = FinanceTools(data)
planner = QueryPlanner()


st.title("💼 CFO Copilot")
st.markdown("Ask questions about your financial performance")

col1, col2 = st.columns([6, 1])
with col2:
    if st.button("📄 Export PDF"):
        pdf_gen = PDFReportGenerator(tools)
        pdf_filename = f"cfo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_gen.generate_report(pdf_filename, month='2025-06')
        
        # Provide download button
        with open(pdf_filename, "rb") as pdf_file:
            st.download_button(
                label="⬇️ Download Report",
                data=pdf_file,
                file_name=pdf_filename,
                mime="application/pdf"
            )
        
        # Clean up
        if os.path.exists(pdf_filename):
            os.remove(pdf_filename)

# Chat interface
user_question = st.text_input("Ask a question:")

if user_question:
    # Parseing  the question
    parsed = planner.parse_query(user_question)
    
    st.markdown("---")
    

    if parsed['intent'] == 'revenue_vs_budget':
        if parsed['month']:
            result = tools.get_revenue_vs_budget(parsed['month'])
            
            # Displaying results
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Actual Revenue", f"${result['actual']:,.0f}")
            with col2:
                st.metric("Budget", f"${result['budget']:,.0f}")
            with col3:
                st.metric("Variance", f"${result['variance']:,.0f}", 
                         delta=f"{result['variance_pct']:.1f}%")
            
            # Creating  chart
            fig = go.Figure(data=[
                go.Bar(name='Actual', x=['Revenue'], y=[result['actual']], marker_color='#1f77b4'),
                go.Bar(name='Budget', x=['Revenue'], y=[result['budget']], marker_color='#ff7f0e')
            ])
            fig.update_layout(
                title=f"Revenue vs Budget - {parsed['month']}",
                yaxis_title="USD",
                barmode='group',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ Please specify a month (e.g., 'June 2025')")
    
    elif parsed['intent'] == 'gross_margin_trend':
        
        if parsed['date_range'] and parsed['date_range'][0] == 'LAST_N_MONTHS':
            num_months = parsed['date_range'][1]
        else:
            num_months = 3
        
     
        all_months = sorted(tools.actuals_usd['month'].unique(), reverse=True)
        end_month = all_months[0]
        start_month = all_months[num_months - 1]
        
        gm_trend = tools.get_gross_margin_trend(start_month, end_month)
        
        # Display summary
        avg_gm = gm_trend['gross_margin_pct'].mean()
        st.metric("Average Gross Margin", f"{avg_gm:.1f}%")
        
        # Creating  chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=gm_trend['month'], 
            y=gm_trend['gross_margin_pct'],
            mode='lines+markers',
            name='Gross Margin %',
            line=dict(color='#2ca02c', width=3),
            marker=dict(size=10)
        ))
        fig.update_layout(
            title="Gross Margin % Trend",
            xaxis_title="Month",
            yaxis_title="Gross Margin %",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
      
        st.dataframe(gm_trend, use_container_width=True)
    
    elif parsed['intent'] == 'opex_breakdown':
        month = parsed['month'] if parsed['month'] else '2025-06'  
        opex = tools.get_opex_breakdown(month)
        
   
        total_opex = opex['amount'].sum()
        st.metric("Total Operating Expenses", f"${total_opex:,.0f}")
        
     
        fig = px.pie(opex, values='amount', names='category', 
                     title=f"Opex Breakdown - {month}")
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
        
  
        st.dataframe(opex, use_container_width=True)
    
    elif parsed['intent'] == 'ebitda':
        month = parsed['month'] if parsed['month'] else '2025-06'
        ebitda = tools.get_ebitda(month)
     
        col1, col2 = st.columns(2)
        with col1:
            st.metric("EBITDA", f"${ebitda['ebitda']:,.0f}")
        with col2:
            st.metric("EBITDA Margin", f"{ebitda['ebitda_margin_pct']:.1f}%")

        fig = go.Figure(go.Waterfall(
            x=['Revenue', 'COGS', 'Opex', 'EBITDA'],
            y=[ebitda['revenue'], -ebitda['cogs'], -ebitda['opex'], ebitda['ebitda']],
            measure=['absolute', 'relative', 'relative', 'total'],
            text=[f"${ebitda['revenue']:,.0f}", f"-${ebitda['cogs']:,.0f}", 
                  f"-${ebitda['opex']:,.0f}", f"${ebitda['ebitda']:,.0f}"],
            textposition="outside"
        ))
        fig.update_layout(title=f"EBITDA Calculation - {month}", height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    elif parsed['intent'] == 'cash_runway':
        runway = tools.get_cash_runway()
        
  
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Cash", f"${runway['current_cash']:,.0f}")
        with col2:
            st.metric("Avg Monthly Burn", f"${runway['avg_monthly_burn']:,.0f}")
        with col3:
            if runway['runway_months'] == float('inf'):
                st.metric("Cash Runway", "∞ (Profitable!)", delta="Positive cash flow")
            else:
                st.metric("Cash Runway", f"{runway['runway_months']:.1f} months")
        
        st.info(f"📊 Based on cash balance as of {runway['latest_month']}")
    
    else:
        st.error("❌ I don't understand that question. Try asking about:\n"
                "- Revenue vs budget\n"
                "- Gross margin trends\n"
                "- Opex breakdown\n"
                "- EBITDA\n"
                "- Cash runway")