import streamlit as st
import asyncio
from main import agent, Deps, ModelRequest, ModelResponse, UserPromptPart, TextPart, messages
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
    
    # KPI Explorer section
    if st.button("🔍 Explore KPI Structure", use_container_width=True):
        st.session_state.auto_query = "Show me the complete KPI folder structure"
    
    if st.button("📈 Customer Analysis", use_container_width=True):
        st.session_state.auto_query = "List all files in customer_analysis and give me a brief overview"
    
    if st.button("🛒 Order Analysis", use_container_width=True):
        st.session_state.auto_query = "List all files in order_analysis and show key insights"
    
    if st.button("🍕 Product Analysis", use_container_width=True):
        st.session_state.auto_query = "Show me product_analysis structure and recent performance data"

    if st.button("Generate Miss You", use_container_width=True):

        with open("prompts/miss_you.txt", "r", encoding="utf-8") as f:
            
            st.session_state.auto_query = f.read()

    if st.button("Generate Stamp Card", use_container_width=True):

        with open("prompts/stamp_card.txt", "r", encoding="utf-8") as f:
            
            st.session_state.auto_query = f.read()
    
    if st.button("Generate Creative", use_container_width=True):

        with open("prompts/creative.txt", "r", encoding="utf-8") as f:
            
            st.session_state.auto_query = f.read()
    
    st.divider()
    
    # Sample queries
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
    
    # System status
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

# Welcome message for new users
if not st.session_state.messages:
    welcome_msg = {
        "role": "assistant", 
        "content": """👋 **Welcome to Clink!** 

I'm your restaurant data analyst specializing in coupon strategy for the Indian market. I can help you:

• 📊 Analyze your KPI data across customer, order, and product metrics
• 🎟️ Generate targeted coupon strategies to boost footfall
• 📈 Identify trends and opportunities in your restaurant data
• 💰 Calculate ROI and cost-benefit analysis for promotions

**Try asking:** "Show me the KPI structure" or use the quick actions in the sidebar!"""
    }
    st.session_state.messages.append(welcome_msg)

# Function to display chat messages with better formatting
def display_messages():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                # Better formatting for bot responses
                content = message["content"]
                
                # Check if it's a structured coupon response
                if "**Coupon Recommendations**" in content or "coupons:" in content.lower():
                    st.markdown("### 🎟️ Coupon Strategy Generated")
                    st.markdown(content)
                    
                    # Add download option for coupon strategies
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

# Function to handle user input and get bot response
async def get_bot_response(user_input: str):
    try:
        # Show loading indicator
        with st.spinner("🤖 Clink is analyzing your data..."):
            # Run the agent to get the bot's response
            response = await agent.run(user_prompt=user_input, deps=Deps(kpi_base_folder="./results"))
            
            # Format the response nicely
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
        error_msg = f"❌ **Error occurred:** {str(e)}\n\nPlease try rephrasing your question or check if the KPI files are accessible."
        return error_msg

# Main chat interface
col1, col2 = st.columns([3, 1])

with col1:
    # Display existing messages
    display_messages()

with col2:
    # Recent queries or stats could go here
    if st.session_state.messages:
        st.markdown("### 📊 Chat Stats")
        user_msgs = [m for m in st.session_state.messages if m["role"] == "user"]
        st.metric("Queries Made", len(user_msgs))

# Handle auto-queries from sidebar
if st.session_state.auto_query:
    user_input = st.session_state.auto_query
    st.session_state.auto_query = None  # Reset
    
    # Add to chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Get response
    bot_response = asyncio.run(get_bot_response(user_input))
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    
    # Update message history
    messages.append(ModelRequest(parts=[UserPromptPart(content=user_input)]))
    messages.append(ModelResponse(parts=[TextPart(content=bot_response)]))
    
    st.rerun()

# Get user input
user_input = st.chat_input("Ask Clink about your restaurant data...")

if user_input:
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message immediately
    with st.chat_message("user"):
        st.write(user_input)
    
    # Get bot response
    bot_response = asyncio.run(get_bot_response(user_input))
    
    # Add bot response to session state
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    
    # Display bot response
    with st.chat_message("assistant"):
        if "**Coupon Recommendations**" in bot_response:
            st.markdown("### 🎟️ Coupon Strategy Generated")
        st.markdown(bot_response)
    
    # Update message history
    messages.append(ModelRequest(parts=[UserPromptPart(content=user_input)]))
    messages.append(ModelResponse(parts=[TextPart(content=bot_response)]))

# Footer
# st.divider()
# st.markdown(body="""
# <small>
# 🚀 Clink - Powered by advanced AI to help Indian restaurants thrive in the competitive food delivery market.\n  
# 💡 *Tip: Be specific about what KPI data you want to analyze for better coupon recommendations.*
# </small>
# """, unsafe_allow_html=True)