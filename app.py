import streamlit as st
import asyncio
from main import standard_coupon_agent, creative_coupon_agent, Deps, ModelRequest, ModelResponse, UserPromptPart, TextPart, messages
from pathlib import Path
import time

# Set up the Streamlit app
st.set_page_config(
    page_title="Clink - Restaurant KPI Analyzer", 
    page_icon="🍽️",
    layout="wide"
)

st.title("🍽️ Clink - Restaurant KPI Analysis & Coupon Generator")
st.markdown("*Data-driven coupon strategies for Indian restaurants*")

# Sidebar for quick actions and info
with st.sidebar:
    st.header("📊 Quick Actions")
    
    if st.button("🔍 Explore KPI Structure", use_container_width=True):
        st.session_state.auto_query = "Show me the complete KPI folder structure"
    
    if st.button("📈 Customer Analysis", use_container_width=True):
        st.session_state.auto_query = "List all files in customer_analysis and give me a brief overview"
    
    if st.button("🛒 Order Analysis", use_container_width=True):
        st.session_state.auto_query = "List all files in order_analysis and show key insights"
    
    if st.button("🍕 Product Analysis", use_container_width=True):
        st.session_state.auto_query = "Show me product_analysis structure and recent performance data"

    if st.button("📚 Generate Standard Coupon", use_container_width=True):
        st.session_state.auto_query = "Generate standard coupons to increase footfall"
        st.session_state.selected_agent = "standard"

    if st.button("🎲 Generate Creative Coupon", use_container_width=True):
        st.session_state.auto_query = "Generate creative coupon strategies for footfall increase"
        st.session_state.selected_agent = "creative"
    
    st.divider()
    
    st.header("💡 Sample Queries")
    st.markdown("""
    **Quick starts:**
    - "Generate coupons for weekend footfall"
    - "Analyze customer retention patterns"
    - "What are our peak and off-peak hours?"
    - "Show me top performing products"
    - "Create loyalty program recommendations"
    """)

    st.divider()
    
    st.header("⚙️ System Info")
    kpi_path = Path("./results")
    if kpi_path.exists():
        csv_files = list(kpi_path.rglob("*.csv"))
        st.success(f"✅ {len(csv_files)} KPI files detected")
    else:
        st.error("❌ KPI folder not found")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "auto_query" not in st.session_state:
    st.session_state.auto_query = None

if "selected_agent" not in st.session_state:
    st.session_state.selected_agent = "standard"

# Welcome message
if not st.session_state.messages:
    welcome_msg = {
        "role": "assistant", 
        "content": "👋 **Welcome to Clink!**"}
    st.session_state.messages.append(welcome_msg)

def display_messages():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                content = message["content"]
                if "**Coupon Recommendations**" in content or "coupons:" in content.lower():
                    st.markdown("### 🎟️ Coupon Strategy Generated")
                    st.markdown(content)
                    if st.button("📥 Download Strategy", key=f"download_{hash(content)}"):
                        st.download_button(
                            label="Save as Text File",
                            data=content,
                            file_name=f"coupon_strategy_{int(time.time())}.txt",
                            mime="text/plain"
                        )
                else:
                    st.markdown(content)
            else:
                st.write(message["content"])

async def get_bot_response(user_input: str):
    try:
        with st.spinner("🤖 Clink is analyzing your data..."):
            active_agent = (
                standard_coupon_agent 
                if st.session_state.selected_agent == "standard" 
                else creative_coupon_agent
            )

            response = await active_agent.run(
                user_prompt=user_input,
                deps=Deps(kpi_base_folder="./results")
            )

            if st.session_state.selected_agent == "standard":
                formatted_response = f"""
                    ### 🎁 **Joining Bonus Coupon**

                    {response.output.joining_bonus_coupon}

                    **Why:** {response.output.joining_bonus_coupon_reasoning}

                    **Cost Impact:** {response.output.joining_bonus_coupon_cost_analysis}

                    
                    ### 🧾 **Stamp Card Coupon**
                    
                    {response.output.stamp_card_coupon}

                    **Why:** {response.output.stamp_card_coupon_reasoning}

                    **Cost Impact:** {response.output.stamp_card_coupon_cost_analysis}

                    
                    ### 💌 **Miss You Coupon**

                    {response.output.miss_you_coupon}

                    **Why:** {response.output.miss_you_coupon_reasoning}

                    **Cost Impact:** {response.output.miss_you_coupon_cost_analysis}

                    
                    ### 💰 **Combined Cost Analysis**

                    {response.output.combined_cost_analysis}
                    """
            else:
                formatted_response = f"""
                    ### 🎟️ **Coupon Recommendations**
                    {response.output.coupons}

                    ### 🧠 **Strategic Reasoning**
                    {response.output.reasoning}

                    ### 💰 **Cost & Impact Analysis**
                    {response.output.cost}

                    ### 💬 **Chat Response**
                    {response.output.conversation}
                    """

            messages.append(ModelResponse(parts=[TextPart(content=formatted_response)]))
            return formatted_response

    except Exception as e:
        return f"❌ **Error:** {str(e)}\n\nPlease try again or check your data."

# Main chat interface
col1, col2 = st.columns([3, 1])

with col1:
    display_messages()

with col2:
    if st.session_state.messages:
        st.markdown("### 📊 Chat Stats")
        user_msgs = [m for m in st.session_state.messages if m["role"] == "user"]
        st.metric("Queries Made", len(user_msgs))

# Handle auto-query from sidebar
if st.session_state.auto_query:
    user_input = st.session_state.auto_query
    st.session_state.auto_query = None

    st.session_state.messages.append({"role": "user", "content": user_input})
    bot_response = asyncio.run(get_bot_response(user_input))
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    messages.append(ModelRequest(parts=[UserPromptPart(content=user_input)]))
    messages.append(ModelResponse(parts=[TextPart(content=bot_response)]))
    st.rerun()

# Handle direct user input
user_input = st.chat_input("Ask Clink about your restaurant data...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    bot_response = asyncio.run(get_bot_response(user_input))
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    with st.chat_message("assistant"):
        if "**Coupon Recommendations**" in bot_response:
            st.markdown("### 🎟️ Coupon Strategy Generated")
        st.markdown(bot_response)
    messages.append(ModelRequest(parts=[UserPromptPart(content=user_input)]))
    messages.append(ModelResponse(parts=[TextPart(content=bot_response)]))
