import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="QueueLess", layout="wide", page_icon="🎫")

# ─── Session State Initialization ──────────────────────────────────────────────
BUSINESSES = ["🏦 Bank", "🏥 Clinic", "🍽️ Restaurant", "💇 Salon", "🏛️ Government Office"]
WAIT_PER_PERSON = 5  # minutes

if "queues" not in st.session_state:
    st.session_state.queues = {b: [] for b in BUSINESSES}

if "served_today" not in st.session_state:
    st.session_state.served_today = {b: 0 for b in BUSINESSES}

if "token_counter" not in st.session_state:
    st.session_state.token_counter = {b: 100 for b in BUSINESSES}

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎫 QueueLess")
    st.markdown("*Skip the wait. Join virtually.*")
    st.divider()
    mode = st.radio("Select Mode", ["👤 User Mode", "📊 Business Dashboard"])
    st.divider()
    st.caption(f"🕐 {datetime.now().strftime('%I:%M %p')}")

# ═══════════════════════════════════════════════════════════════════════════════
# USER MODE
# ═══════════════════════════════════════════════════════════════════════════════
if mode == "👤 User Mode":
    st.title("🎫 Join a Virtual Queue")
    st.markdown("Select a location, join the queue, and arrive just in time — no waiting around!")
    st.divider()

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📍 Select Location")
        selected_biz = st.selectbox("Choose a business", BUSINESSES)
        user_name = st.text_input("Your Name", placeholder="e.g. Ravi Kumar")

        if st.button("🟢 Join Queue", use_container_width=True):
            if not user_name.strip():
                st.warning("Please enter your name to join the queue.")
            else:
                # Assign token
                st.session_state.token_counter[selected_biz] += 1
                token = st.session_state.token_counter[selected_biz]
                st.session_state.queues[selected_biz].append({
                    "token": token,
                    "name": user_name.strip(),
                    "joined_at": datetime.now().strftime("%I:%M %p")
                })
                st.success(f"✅ You've joined the queue at **{selected_biz}**!")
                st.balloons()

    with col2:
        st.subheader("📋 Your Queue Status")
        queue = st.session_state.queues[selected_biz]

        if not queue:
            st.info("No one is in the queue right now. You'd be first!")
        else:
            # Show last joined person's info (simulate current user)
            position = len(queue)
            wait_time = position * WAIT_PER_PERSON

            m1, m2, m3 = st.columns(3)
            m1.metric("Your Position", f"#{position}")
            m2.metric("Est. Wait", f"{wait_time} mins")
            m3.metric("People Ahead", position - 1)

            if position == 1:
                st.success("🔔 It's almost your turn! Please proceed to the counter.")
            elif position <= 3:
                st.warning("⏳ You're almost up — make your way there soon!")
            else:
                st.info("😌 Relax — you have some time before your turn.")

            st.divider()
            st.markdown("**Current Queue:**")
            df = pd.DataFrame(queue)
            df.index = df.index + 1
            df.columns = ["Token #", "Name", "Joined At"]
            st.dataframe(df, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# BUSINESS DASHBOARD MODE
# ═══════════════════════════════════════════════════════════════════════════════
else:
    st.title("📊 Business Dashboard")
    st.markdown("Manage your queue, track customers, and monitor performance.")
    st.divider()

    selected_biz = st.selectbox("Select Your Business", BUSINESSES)
    queue = st.session_state.queues[selected_biz]

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader(f"Queue for {selected_biz}")

        m1, m2, m3 = st.columns(3)
        m1.metric("In Queue", len(queue))
        m2.metric("Served Today", st.session_state.served_today[selected_biz])
        m3.metric("Est. Clear Time", f"{len(queue) * WAIT_PER_PERSON} mins")

        st.divider()

        if queue:
            next_customer = queue[0]
            st.info(f"🔔 **Next:** Token #{next_customer['token']} — {next_customer['name']}")

            if st.button("✅ Call Next Customer", use_container_width=True):
                st.session_state.queues[selected_biz].pop(0)
                st.session_state.served_today[selected_biz] += 1
                st.success(f"Called {next_customer['name']} (Token #{next_customer['token']})")
                st.rerun()
        else:
            st.success("🎉 Queue is empty — no waiting customers!")

        if st.button("🗑️ Clear Entire Queue", use_container_width=True):
            st.session_state.queues[selected_biz] = []
            st.rerun()

        if queue:
            st.divider()
            st.markdown("**Full Queue List:**")
            df = pd.DataFrame(queue)
            df.index = df.index + 1
            df.columns = ["Token #", "Name", "Joined At"]
            st.dataframe(df, use_container_width=True)

    with col2:
        st.subheader("📈 Queue Analytics")

        # Bar chart: queue lengths per business
        chart_data = {
            "Business": list(st.session_state.queues.keys()),
            "In Queue": [len(q) for q in st.session_state.queues.values()],
            "Served Today": list(st.session_state.served_today.values())
        }
        df_chart = pd.DataFrame(chart_data)

        fig = px.bar(
            df_chart,
            x="Business",
            y=["In Queue", "Served Today"],
            barmode="group",
            title="Queue Status Across All Businesses",
            color_discrete_sequence=["#4F46E5", "#10B981"]
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#333",
            legend_title_text=""
        )
        st.plotly_chart(fig, use_container_width=True)

        # Summary table
        st.markdown("**Summary Table:**")
        st.dataframe(df_chart.set_index("Business"), use_container_width=True)
