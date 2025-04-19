import streamlit as st
import bcrypt
import json
import os
import time
from datetime import datetime, timedelta
from PIL import Image
import random
import uuid

def load_css():
    """Define all CSS styling for the application"""
    st.markdown(f"""
    <style>
    /* Color Variables */
    :root {{
        --primary: #4361ee;
        --secondary: #3f37c9;
        --accent: #4895ef;
        --light: #f8f9fa;
        --dark: #212529;
        --success: #4cc9f0;
        --warning: #f72585;
        --danger: #7209b7;
    }}

    body {{
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
        color: var(--dark);
    }}

    /* Fix for recent activity font color */
    .activity-item {{
        color: #212529 !important;
    }}

    .activity-item div {{
        color: #212529 !important;
    }}

    .main-container {{
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }}

    .card {{
        border-radius: 12px;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.1);
        padding: 20px;
        margin-bottom: 25px;
        background-color: white;
        transition: transform 0.3s, box-shadow 0.3s;
        border: 1px solid #e9ecef;
    }}

    .card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 8px 16px 0 rgba(0,0,0,0.15);
    }}

    .card-title {{
        color: var(--primary);
        margin-bottom: 15px;
        font-size: 1.2rem;
    }}

    .stats-card {{
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        background-color: white;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
        text-align: center;
    }}

    .stats-card h3 {{
        color: #6c757d;
        font-size: 1rem;
        margin-bottom: 5px;
    }}

    .stats-card .value {{
        font-size: 2rem;
        font-weight: bold;
        color: #4361ee;
        margin: 10px 0;
    }}

    .stButton>button {{
        border-radius: 8px;
        padding: 8px 16px;
        background-color: var(--primary);
        color: white;
        border: none;
        transition: background-color 0.3s;
    }}

    .stButton>button:hover {{
        background-color: var(--secondary);
    }}

    .stTextInput>div>div>input, 
    .stTextArea>div>textarea {{
        border-radius: 8px;
        border: 1px solid #ced4da;
    }}

    .stSelectbox>div>div>div {{
        border-radius: 8px;
    }}

    .sidebar .sidebar-content {{
        background-color: var(--light);
        padding: 15px;
    }}

    .sidebar .sidebar-content .block-container {{
        padding-top: 0;
    }}

    .hero-container {{
        position: relative;
        text-align: center;
        margin-bottom: 30px;
    }}

    .hero-text {{
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }}

    .hero-title {{
        font-size: 2.5rem;
        margin-bottom: 10px;
    }}

    .activity-item {{
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 4px solid var(--accent);
    }}

    .activity-time {{
        color: #6c757d;
        font-size: 0.8rem;
    }}

    .activity-tab {{
        border-bottom: 1px solid #dee2e6;
        padding-bottom: 10px;
        margin-bottom: 15px;
    }}

    @media (max-width: 768px) {{
        .hero-title {{
            font-size: 1.8rem;
        }}
        .card {{
            margin-bottom: 15px;
        }}
    }}

    /* Make "Sign up now" look like a link */
    button[kind="secondary"][data-testid="baseButton-signup_now"] {{
        background: none;
        border: none;
        color: #4361ee;
        font-weight: bold;
        text-align: left;
        padding: 0;
        margin-top: -10px;
        cursor: pointer;
    }}
    </style>
    """, unsafe_allow_html=True)

def card(title, content, image=None, action_button=None, key=None):
    """Reusable card component with optional image and action button"""
    try:
        img_html = f'<img src="{image}" style="width:100%; border-radius:8px; margin-bottom:15px;">' if image else ''
    except:
        img_html = ''
    
    if key is None:
        key = f"card_{title}_{random.randint(0, 10000)}"
    
    st.markdown(f"""
    <div class="card">
        <div class="card-title">{title}</div>
        {img_html}
        <div class="card-content">{content}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if action_button:
        return st.button(action_button, key=key)
    return None

def hero_section(title, subtitle, image_url):
    """Hero banner component with title and subtitle"""
    try:
        # Check if image_url is accessible before using it
        st.markdown(f"""
        <div class="hero-container">
            <img src="{image_url}" style="width:100%; border-radius:8px;">
            <div class="hero-text">
                <h1 class="hero-title">{title}</h1>
                <p>{subtitle}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Could not load hero image: {str(e)}")
        st.markdown(f"""
        <div class="hero-container" style="background-color: #4361ee; padding: 50px; border-radius: 8px;">
            <div class="hero-text" style="position: static; transform: none;">
                <h1 class="hero-title" style="color: white;">{title}</h1>
                <p style="color: white;">{subtitle}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

def activity_item(user, action, time_ago):
    """Activity feed item component"""
    st.markdown(f"""
    <div class="activity-item">
        <strong>{user}</strong> {action}
        <div class="activity-time">{time_ago}</div>
    </div>
    """, unsafe_allow_html=True)

def stats_card(title, value):
    st.markdown(f"""
    <div class="stats-card">
        <h3>{title}</h3>
        <div class="value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

# ===== DATABASE CONFIGURATION =====
DB_FILES = {
    "users": "data/users.json",
    "businesses": "data/businesses.json",
    "media": "data/media.json",
    "circles": "data/circles.json",
    "events": "data/events.json",
    "promotions": "data/promotions.json",
    "notifications": "data/notifications.json",
    "reports": "data/reports.json"
}

MEDIA_DIR = "media_gallery"
os.makedirs("data", exist_ok=True)
os.makedirs(MEDIA_DIR, exist_ok=True)

def init_db():
    """Initialize database files with empty structures"""
    for file_key, file_path in DB_FILES.items():
        if not os.path.exists(file_path):
            try:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, "w") as f:
                    if file_key in ["users", "businesses", "circles", "events", "promotions", "notifications"]:
                        json.dump({}, f)
                    else:
                        json.dump([], f)
            except Exception as e:
                st.error(f"Failed to initialize database file {file_path}: {str(e)}")

def load_db(file_key, retry_count=0, max_retries=1):
    """Load database file"""
    try:
        if not os.path.exists(DB_FILES[file_key]):
            if retry_count >= max_retries:
                return {} if file_key in ["users", "businesses", "circles", "events", "promotions", "notifications"] else []
            init_db()
            
        with open(DB_FILES[file_key], "r") as f:
            data = json.load(f)
            if file_key in ["users", "businesses", "circles", "events", "promotions", "notifications"] and not isinstance(data, dict):
                return {}
            elif file_key in ["media", "reports"] and not isinstance(data, list):
                return []
            return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        if retry_count >= max_retries:
            st.error(f"Database error: Unable to load {file_key}. Error: {str(e)}")
            return {} if file_key in ["users", "businesses", "circles", "events", "promotions", "notifications"] else []
        time.sleep(0.1)
        init_db()
        return load_db(file_key, retry_count + 1)

def save_db(file_key, data):
    """Save database file"""
    try:
        with open(DB_FILES[file_key], "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        st.error(f"Failed to save database file {DB_FILES[file_key]}: {str(e)}")

def generate_id(prefix):
    """Generate unique ID"""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def add_notification(user_id, notification_type, content, related_id=None):
    """Add notification to user's feed"""
    notifications = load_db("notifications")
    if user_id not in notifications:
        notifications[user_id] = []
    
    notifications[user_id].append({
        "notification_id": generate_id("notif"),
        "type": notification_type,
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "read": False,
        "related_id": related_id
    })
    save_db("notifications", notifications)

def get_user_media(user_id):
    """Get all media for a specific user"""
    media = load_db("media")
    return [m for m in media if m["user_id"] == user_id]

def get_user_circles(user_id):
    """Get all circles a user belongs to"""
    circles = load_db("circles")
    return [c for c in circles.values() if user_id in c["members"]]

def get_circle_events(circle_id):
    """Get all events for a specific circle"""
    events = load_db("events")
    return [e for e in events.values() if e["circle_id"] == circle_id]

def generate_sample_data():
    """Generate sample data if databases are empty"""
    users = load_db("users")
    if not users:
        users["sample_user"] = {
            "user_id": "usr_123",
            "full_name": "John Doe",
            "email": "john@example.com",
            "password": hash_password("password123"),
            "account_type": "general",
            "verified": True,
            "joined_date": datetime.now().strftime("%Y-%m-%d"),
            "interests": ["music", "tech"],
            "location": {"city": "New York", "lat": 40.7128, "lng": -74.0060},
            "profile_pic": "https://randomuser.me/api/portraits/men/1.jpg"
        }
        
        # Add UAE sample user
        users["uae_user"] = {
            "user_id": "usr_124",
            "full_name": "Ahmed Al Maktoum",
            "email": "ahmed@example.com",
            "password": hash_password("password123"),
            "account_type": "general",
            "verified": True,
            "joined_date": datetime.now().strftime("%Y-%m-%d"),
            "interests": ["photography", "food"],
            "location": {"city": "Dubai", "lat": 25.2048, "lng": 55.2708},
            "profile_pic": "https://randomuser.me/api/portraits/men/30.jpg"
        }
        save_db("users", users)
    
    circles = load_db("circles")
    if not circles:
        # Original circle
        circles["cir_123"] = {
            "circle_id": "cir_123",
            "name": "NYC Photographers",
            "description": "For photography enthusiasts in NYC",
            "type": "public",
            "location": {"city": "New York", "lat": 40.7128, "lng": -74.0060},
            "members": ["usr_123"],
            "events": ["evt_123"],
            "business_owned": False,
            "created_at": datetime.now().isoformat()
        }
        
        # UAE circles
        circles["cir_124"] = {
            "circle_id": "cir_124",
            "name": "Dubai Photography Enthusiasts",
            "description": "For photography lovers in Dubai to share and learn",
            "type": "public",
            "location": {"city": "Dubai", "lat": 25.2048, "lng": 55.2708},
            "members": ["usr_124"],
            "events": ["evt_124"],
            "business_owned": False,
            "created_at": datetime.now().isoformat(),
            "tags": ["photography", "dubai"]
        }
        
        circles["cir_125"] = {
            "circle_id": "cir_125",
            "name": "Sharjah Foodies",
            "description": "Discover and share the best food spots in Sharjah",
            "type": "public",
            "location": {"city": "Sharjah", "lat": 25.3463, "lng": 55.4209},
            "members": [],
            "events": ["evt_125"],
            "business_owned": False,
            "created_at": datetime.now().isoformat(),
            "tags": ["food", "sharjah"]
        }
        
        circles["cir_126"] = {
            "circle_id": "cir_126",
            "name": "Sheikh Zayed Road Business Network",
            "description": "Professional networking for businesses along SZ Road",
            "type": "private",
            "location": {"city": "Dubai", "lat": 25.2048, "lng": 55.2708},
            "members": [],
            "events": [],
            "business_owned": True,
            "created_at": datetime.now().isoformat(),
            "tags": ["business", "networking"]
        }
        save_db("circles", circles)
    
    events = load_db("events")
    if not events:
        # Original event
        events["evt_123"] = {
            "event_id": "evt_123",
            "circle_id": "cir_123",
            "name": "Sunset Photography Meetup",
            "description": "Let's capture the sunset together!",
            "location": {"name": "Brooklyn Bridge", "lat": 40.7061, "lng": -73.9969},
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": "18:00",
            "organizer": "usr_123",
            "attendees": ["usr_123"],
            "capacity": 20,
            "tags": ["photography", "outdoors"],
            "created_at": datetime.now().isoformat()
        }
        
        # UAE events
        events["evt_124"] = {
            "event_id": "evt_124",
            "circle_id": "cir_124",
            "name": "Burj Khalifa Night Photography",
            "description": "Night photography session at Burj Khalifa",
            "location": {"name": "Burj Khalifa, Dubai", "lat": 25.1972, "lng": 55.2744},
            "date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "time": "19:00",
            "organizer": "usr_124",
            "attendees": ["usr_124"],
            "capacity": 15,
            "tags": ["photography", "dubai", "landmarks"],
            "created_at": datetime.now().isoformat()
        }
        
        events["evt_125"] = {
            "event_id": "evt_125",
            "circle_id": "cir_125",
            "name": "Sharjah Street Food Tour",
            "description": "Explore hidden street food gems in Sharjah",
            "location": {"name": "Al Qasba, Sharjah", "lat": 25.3471, "lng": 55.3913},
            "date": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d"),
            "time": "18:00",
            "organizer": "usr_124",
            "attendees": [],
            "capacity": 10,
            "tags": ["food", "sharjah", "tour"],
            "created_at": datetime.now().isoformat()
        }
        save_db("events", events)
    
    # Ensure sample users have notifications
    notifications = load_db("notifications")
    if "usr_123" not in notifications:
        notifications["usr_123"] = [{
            "notification_id": "notif_123",
            "type": "welcome",
            "content": "Welcome to Atmosphere! Get started by joining a circle.",
            "timestamp": datetime.now().isoformat(),
            "read": False
        }]
    
    if "usr_124" not in notifications:
        notifications["usr_124"] = [{
            "notification_id": "notif_124",
            "type": "welcome",
            "content": "Welcome to Atmosphere! Discover events in Dubai.",
            "timestamp": datetime.now().isoformat(),
            "read": False
        }]
    
    save_db("notifications", notifications)

def login_page():
    st.markdown("""
        <h1 class='hero-title'>Welcome to Atmosphere</h1>
        <p class='hero-subtitle'>
            Your digital space to connect with like-minded individuals, explore engaging events, 
            and share your stories within interest-based circles. Dive in and discover a vibrant, interactive community.
        </p>
    """, unsafe_allow_html=True)

    try:
        st.image("https://images.unsplash.com/photo-1469474968028-56623f02e42e", use_container_width=True, caption="Capture the vibe with Atmosphere")
    except Exception as e:
        st.warning(f"Could not load image: {str(e)}")
        st.markdown("### Capture the vibe with Atmosphere")
    
    st.markdown("---")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("🔐 Log In to Your Account")
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            login_btn = st.form_submit_button("Login")
            try:
                if login_btn:
                    users = load_db("users")
                    if not users:
                        st.error("User database not available. Please try again later.")
                    elif username in users and verify_password(password, users[username]["password"]):
                        st.session_state["user"] = users[username]
                        st.session_state["logged_in"] = True
                        add_notification(users[username]["user_id"], "login", "Welcome back to Atmosphere!")
                        st.success("Login successful!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
            except Exception as e:
                st.error(f"Something went wrong: {e}")
    with col2:
        with st.container():
            st.markdown("""
                <div class="card">
                    <h3 class="card-title" style="color: #212529;">🌐 New to Atmosphere?</h3>
                    <ul style="list-style-type: none; padding-left: 0; font-size: 0.95rem; color: #212529;">
                        <li>✔️ Discover local events & activities</li>
                        <li>🎯 Join interest-based circles</li>
                        <li>📷 Share your experiences & moments</li>
                        <li>🚀 Promote your business locally</li>
                    </ul>
                    <p style="margin-top: 10px; color: #212529;">Don't have an account?</p>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='margin-top: -40px;'>", unsafe_allow_html=True)
            if st.button("🔗 Sign up now →", key="signup_now"):
                st.session_state["auth_tab"] = "Sign Up"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

def signup_page():
    """Signup page with tabs for different account types"""
    st.title("👤 Join Our Community")
    
    tab1, tab2 = st.tabs(["👤 General User", "💼 Business Account"])
    
    with tab1:
        with st.form("general_signup"):
            st.subheader("Create Personal Account")
            full_name = st.text_input("Full Name")
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            location = st.text_input("Your Location (City)")
            interests = st.multiselect("Your Interests", ["Art", "Music", "Sports", "Food", "Tech", "Nature"])
            
            signup_btn = st.form_submit_button("Create Account")
            
            if signup_btn:
                if password != confirm_password:
                    st.error("Passwords don't match!")
                else:
                    users = load_db("users")
                    if username in users:
                        st.error("Username already exists!")
                    else:
                        user_id = generate_id("usr")
                        users[username] = {
                            "user_id": user_id,
                            "full_name": full_name,
                            "email": email,
                            "password": hash_password(password),
                            "account_type": "general",
                            "verified": False,
                            "joined_date": datetime.now().isoformat(),
                            "interests": interests,
                            "location": {"city": location},
                            "profile_pic": f"https://randomuser.me/api/portraits/{random.choice(['men','women'])}/{random.randint(1,100)}.jpg"
                        }
                        save_db("users", users)
                        st.session_state["user"] = users[username]
                        st.session_state["logged_in"] = True
                        st.success("Account created successfully!")
                        time.sleep(1)
                        st.rerun()

    with tab2:
        with st.form("business_signup"):
            st.subheader("Register Your Business")
            business_name = st.text_input("Business Name")
            owner_name = st.text_input("Owner/Representative Name")
            username = st.text_input("Username")
            email = st.text_input("Business Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            category = st.selectbox("Business Category", ["Food & Drink", "Retail", "Services", "Entertainment", "Other"])
            address = st.text_input("Business Address")
            
            signup_btn = st.form_submit_button("Register Business")
            
            if signup_btn:
                if password != confirm_password:
                    st.error("Passwords don't match!")
                else:
                    users = load_db("users")
                    businesses = load_db("businesses")
                    
                    if username in users:
                        st.error("Username already exists!")
                    else:
                        # Create user account
                        user_id = generate_id("usr")
                        users[username] = {
                            "user_id": user_id,
                            "full_name": owner_name,
                            "email": email,
                            "password": hash_password(password),
                            "account_type": "business",
                            "verified": False,
                            "joined_date": datetime.now().isoformat(),
                            "profile_pic": f"https://randomuser.me/api/portraits/{random.choice(['men','women'])}/{random.randint(1,100)}.jpg"
                        }
                        
                        # Create business profile
                        business_id = generate_id("biz")
                        businesses[business_id] = {
                            "business_id": business_id,
                            "owner_id": user_id,
                            "business_name": business_name,
                            "category": category,
                            "verified": False,
                            "locations": [{"address": address}],
                            "created_at": datetime.now().isoformat()
                        }
                        
                        save_db("users", users)
                        save_db("businesses", businesses)
                        st.session_state["user"] = users[username]
                        st.session_state["business"] = businesses[business_id]
                        st.session_state["logged_in"] = True
                        st.success("Business account created! Verification pending.")
                        time.sleep(1)
                        st.rerun()

def home_page():
    """Home page with user dashboard"""
    generate_sample_data()
    
    hero_section(
        f"Welcome, {st.session_state['user']['full_name']}", 
        "What would you like to do today?",
        "https://images.unsplash.com/photo-1469474968028-56623f02e42e"
    )
    
    # User stats
    user_circles = get_user_circles(st.session_state["user"]["user_id"])
    user_events = sum(len(get_circle_events(c["circle_id"])) for c in user_circles)
    user_media = len(get_user_media(st.session_state["user"]["user_id"]))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        stats_card("Circles Joined", str(len(user_circles)) or "0")
    with col2:
        stats_card("Events Available", str(user_events) or "0")
    with col3:
        stats_card("Media Shared", str(user_media) or "0")
    
    # Activity feed
    st.markdown("## 📰 Your Activity Feed")
    tab1, tab2, tab3 = st.tabs(["Recent Activity", "Your Circles", "Upcoming Events"])
    
    with tab1:
        st.markdown('<div class="activity-tab">Recent Activity</div>', unsafe_allow_html=True)
        notifications = load_db("notifications").get(st.session_state["user"]["user_id"], [])
        
        if not notifications:
            st.info("No recent activity")
        else:
            for notif in notifications[:3]:
                st.markdown(f"""
                <div class="activity-item">
                    <div>System: {notif['content']}</div>
                    <div class="activity-time">
                        {datetime.fromisoformat(notif['timestamp']).strftime('%b %d, %H:%M')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="activity-tab">Your Circles</div>', unsafe_allow_html=True)
        circles = user_circles[:3]
        if not circles:
            st.info("You haven't joined any circles yet")
        else:
            for circle in circles:
                st.markdown(f"""
                <div class="activity-item">
                    <div><strong>{circle['name']}</strong></div>
                    <div class="activity-time">
                        {len(circle['members'])} members • {circle['type'].capitalize()}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="activity-tab">Upcoming Events</div>', unsafe_allow_html=True)
        events = []
        for circle in user_circles:
            events.extend(get_circle_events(circle["circle_id"]))
        
        events = sorted(events, key=lambda x: x["date"])[:3]
        if not events:
            st.info("No upcoming events")
        else:
            for event in events:
                st.markdown(f"""
                <div class="activity-item">
                    <div><strong>{event['name']}</strong></div>
                    <div>{event['date']} at {event['time']}</div>
                    <div class="activity-time">
                        {event['location']['name']}
                    </div>


                    </div>
                """, unsafe_allow_html=True)

def explore_page():
    """Explore page to discover content"""
    generate_sample_data()
    st.title("🔍 Explore Our Community")
    
    # Sheikh Zayed Road Map Section
    st.subheader("📍 Sheikh Zayed Road - Dubai's Iconic Highway")
    
    # Use a try/except block to handle image loading issues
    try:
        if os.path.exists("Images/sheikhzayed.png"):
            st.image("Images/sheikhzayed.png", caption="Map of Sheikh Zayed Road with key landmarks")
        else:
            st.info("Map image not available. Sheikh Zayed Road is Dubai's main highway with numerous iconic landmarks.")
    except Exception as e:
        st.warning(f"Could not load image: {str(e)}")
        st.info("Sheikh Zayed Road is Dubai's main highway with numerous iconic landmarks.")
    
    # Museum of the Future section
    st.subheader("🏛️ Museum of the Future")
    col1, col2 = st.columns([1, 2])
    with col1:
        try:
            if os.path.exists("Images/museumoffuture.webp"):
                st.image("Images/museumoffuture.webp", caption="Museum of the Future - Dubai")
            else:
                st.info("Museum image not available.")
        except Exception as e:
            st.warning(f"Could not load image: {str(e)}")
    with col2:
        st.markdown("""
        <div style="padding:15px;">
            <h3>About the Museum</h3>
            <p>The Museum of the Future is an exhibition space for innovative and futuristic ideologies, 
            services, and products. Located in the Financial District of Dubai, UAE, the museum has 
            been described as the most beautiful building on earth.</p>
            <p><strong>Location:</strong> Sheikh Zayed Road, Trade Centre 2, Dubai</p>
            <p><strong>Opening Hours:</strong> 10AM - 6PM daily</p>
        </div>
        """, unsafe_allow_html=True)

    # Popular circles section
    st.subheader("👥 Popular Circles")
    circles = [
        {
            "name": "NYC Photographers",
            "image_path": "Images/nycphotography.jpg",
            "description": "For photography enthusiasts in NYC",
            "id": "circle_1"
        },
        {
            "name": "Dubai Photography Enthusiasts", 
            "image_path": "Images/photographygroup.jpg",
            "description": "For photography lovers in Dubai",
            "id": "circle_2"
        },
        {
            "name": "Sharjah Foodies",
            "image_path": "Images/foodies.jpg",
            "description": "Discover the best food spots in Sharjah",
            "id": "circle_3"
        },
        {
            "name": "Business Network",
            "image_path": "Images/businessnetworks.webp",
            "description": "Professional networking group",
            "id": "circle_4"
        }
    ]
    
    # Display circles in columns
    cols = st.columns(2)
    for i, circle in enumerate(circles):
        with cols[i % 2]:
            try:
                if os.path.exists(circle["image_path"]):
                    st.image(circle["image_path"], width=300)
                else:
                    st.info(f"Image for {circle['name']} not available.")
            except Exception as e:
                st.warning(f"Could not load image: {str(e)}")
            
            st.markdown(f"""
            <div class="card">
                <h3>{circle['name']}</h3>
                <p>{circle['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Join Circle", key=f"join_{circle['id']}"):
                st.success(f"You joined {circle['name']}!")
                
    # Events section
    st.subheader("📅 Upcoming Events")
    events = [
        {
            "name": "Burj Khalifa Sunset Photography",
            "image_path": "Images/buijkhalifasunset.jpg",
            "date": "2023-11-15 at 18:00",
            "location": "Burj Khalifa, Dubai",
            "id": "event_1"
        },
        {
            "name": "Museum of the Future Tour", 
            "image_path": "Images/buijkhalifa.avif",
            "date": "2023-11-20 at 14:00",
            "location": "Museum of the Future",
            "id": "event_2"
        }
    ]
    
    for event in events:
        try:
            if os.path.exists(event["image_path"]):
                st.image(event["image_path"], width=500)
            else:
                st.info(f"Image for {event['name']} not available.")
        except Exception as e:
            st.warning(f"Could not load image: {str(e)}")
            
        st.markdown(f"""
        <div class="event-card">
            <h3>{event['name']}</h3>
            <p>📅 {event['date']}</p>
            <p>📍 {event['location']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("RSVP", key=f"rsvp_{event['id']}"):
            st.success(f"RSVP confirmed for {event['name']}!")

def media_page():
    """Media upload and gallery page"""
    st.title("📸 Capture & Share Your Moments")
    
    tab1, tab2 = st.tabs(["📷 Upload Media", "🖼️ Your Gallery"])
    
    with tab1:
        st.subheader("Share Your Experience")
        
        # Camera capture
        captured_photo = st.camera_input("Take a photo or upload one below")
        
        # Location selection
        location = st.text_input("Location", "Central Park, NYC")
        
        # Circle selection
        user_circles = get_user_circles(st.session_state["user"]["user_id"])
        circle_options = [""] + [c["name"] for c in user_circles]
        selected_circle = st.selectbox("Share to Circle (optional)", circle_options)
        
        # Tags
        tags = st.multiselect("Tags", ["Nature", "Food", "Tech", "Art", "Sports", "Travel"])
        
        if st.button("Upload Media") and captured_photo:
            try:
                # Ensure media directory exists
                os.makedirs(MEDIA_DIR, exist_ok=True)
                
                # Save media
                media_id = generate_id("med")
                filename = f"{st.session_state['user']['user_id']}_{media_id}.jpg"
                filepath = os.path.join(MEDIA_DIR, filename)
                
                image = Image.open(captured_photo)
                image.save(filepath)
                
                # Add to database
                media = load_db("media")
                media.append({
                    "media_id": media_id,
                    "user_id": st.session_state["user"]["user_id"],
                    "file_path": filepath,
                    "location": {"name": location},
                    "timestamp": datetime.now().isoformat(),
                    "circle_id": next((c["circle_id"] for c in user_circles if c["name"] == selected_circle), None),
                    "tags": tags,
                    "reports": []
                })
                save_db("media", media)
                
                st.success("Media uploaded successfully!")
                
                # Check if this qualifies for any promotions
                promotions = load_db("promotions")
                for promo_id, promo in promotions.items():
                    if any(tag.lower() in [t.lower() for t in tags] for tag in promo.get("tags", [])):
                        add_notification(
                            st.session_state["user"]["user_id"], 
                            "promotion", 
                            f"Your photo qualifies for {promo['offer']} from {promo['business_id']}!"
                        )
            except Exception as e:
                st.error(f"Error uploading media: {str(e)}")
    
    with tab2:
        st.subheader("Your Shared Memories")
        user_media = get_user_media(st.session_state["user"]["user_id"])
        
        if not user_media:
            st.info("You haven't uploaded any media yet. Capture your first moment!")
        else:
            cols = st.columns(3)
            for i, item in enumerate(user_media):
                with cols[i % 3]:
                    try:
                        # Check if file exists
                        if os.path.exists(item["file_path"]):
                            st.image(
                                item["file_path"], 
                                use_container_width=True,
                                caption=f"{item['location']['name']} • {datetime.fromisoformat(item['timestamp']).strftime('%b %d, %Y')}"
                            )
                        else:
                            st.warning("Image file not found")
                        st.write(f"Tags: {', '.join(item['tags'])}")
                    except Exception as e:
                        st.warning(f"Could not load media: {str(e)}")

def circles_page():
    """Circles management page"""
    generate_sample_data()
    st.title("👥 Your Circles")
    
    tab1, tab2, tab3 = st.tabs(["Your Circles", "Discover", "Create"])
    
    with tab1:
        st.subheader("Your Communities")
        user_circles = get_user_circles(st.session_state["user"]["user_id"])
        
        if not user_circles:
            st.info("You haven't joined any circles yet. Explore some below!")
        else:
            for circle in user_circles:
                with st.expander(f"{circle['name']} ({len(circle['members'])} members)"):
                    st.write(circle["description"])
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("View Posts", key=f"posts_{circle['circle_id']}"):
                            st.session_state["current_circle"] = circle['circle_id']
                            st.rerun()
                    with col2:
                        if st.button("Leave Circle", key=f"leave_{circle['circle_id']}"):
                            circles = load_db("circles")
                            circles[circle["circle_id"]]["members"].remove(st.session_state["user"]["user_id"])
                            save_db("circles", circles)
                            st.success(f"You left {circle['name']}")
                            st.rerun()
    
    with tab2:
        st.subheader("Discover New Circles")
        all_circles = load_db("circles")
        user_circles = get_user_circles(st.session_state["user"]["user_id"])
        user_circle_ids = [c["circle_id"] for c in user_circles]
        
        discover_circles = [c for c in all_circles.values() if c["circle_id"] not in user_circle_ids]
        
        if not discover_circles:
            st.info("No new circles to discover at the moment. Check back later!")
        else:
            for circle in discover_circles[:5]:
                # Fixed: Using markdown for properly rendered content
                st.markdown(f"""
                <div class="card">
                    <div class="card-title">{circle['name']}</div>
                    <div class="card-content">
                        {circle['description']}
                        <p>Members: {len(circle['members'])} • Type: {circle['type'].capitalize()}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Join Circle", key=f"join_{circle['circle_id']}"):
                    # Add the user to the circle
                    circles = load_db("circles")
                    if st.session_state["user"]["user_id"] not in circles[circle["circle_id"]]["members"]:
                        circles[circle["circle_id"]]["members"].append(st.session_state["user"]["user_id"])
                        save_db("circles", circles)
                        st.success(f"You've joined {circle['name']}!")
                        time.sleep(1)
                        st.rerun()
    
    with tab3:
        st.subheader("Create a New Circle")
        with st.form("create_circle"):
            name = st.text_input("Circle Name")
            description = st.text_area("Description")
            circle_type = st.radio("Type", ["Public", "Private"])
            location = st.text_input("Primary Location (optional)")
            tags = st.multiselect("Tags", ["Art", "Music", "Sports", "Food", "Tech", "Nature", "Business"])
            
            if st.form_submit_button("Create Circle"):
                if name:
                    circle_id = generate_id("cir")
                    circles = load_db("circles")
                    circles[circle_id] = {
                        "circle_id": circle_id,
                        "name": name,
                        "description": description,
                        "type": circle_type.lower(),
                        "creator": st.session_state["user"]["user_id"],
                        "members": [st.session_state["user"]["user_id"]],
                        "location": {"name": location} if location else None,
                        "tags": tags,
                        "events": [],
                        "created_at": datetime.now().isoformat(),
                        "business_owned": st.session_state["user"]["account_type"] == "business"
                    }
                    save_db("circles", circles)
                    st.success(f"Circle '{name}' created successfully!")
                    add_notification(
                        st.session_state["user"]["user_id"], 
                        "circle", 
                        f"You created a new circle: {name}"
                    )
                    time.sleep(1)
                    st.rerun()

def events_page():
    """Events management page"""
    generate_sample_data()
    st.title("📅 Events")
    
    tab1, tab2, tab3 = st.tabs(["Upcoming", "Your Events", "Create"])
    
    with tab1:
        st.subheader("Upcoming Events")
        
        # Enhanced upcoming events with UAE focus
        upcoming_events = [
            {
                "name": "Sunset Photography at Burj Khalifa",
                "date": "2025-04-18",
                "time": "18:30",
                "location": "Burj Khalifa, Dubai",
                "attendees": 8,
                "capacity": 15,
                "organizer": "Ahmed Al Maktoum",
                "description": "Capture stunning sunset views from the world's tallest building. All skill levels welcome!",
                "image": "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=500",
                "details": """
                    <h3>Event Details</h3>
                    <p><strong>Date:</strong> April 18, 2025 at 6:30 PM</p>
                    <p><strong>Meeting Point:</strong> Burj Khalifa Observation Deck Entrance</p>
                    <p><strong>What to Bring:</strong> Camera (any type), tripod (optional), comfortable shoes</p>
                    <p><strong>Price:</strong> AED 150 (includes observation deck ticket)</p>
                    <img src="https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800" style="width:100%; border-radius:8px; margin:10px 0;">
                    <p>This workshop will guide you through the best techniques for capturing Dubai's famous sunsets from the world's tallest building. Our professional photographer will provide tips on composition, exposure, and post-processing.</p>
                """
            },
            {
                "name": "Museum of the Future Tech Tour",
                "date": "2025-04-20",
                "time": "14:00",
                "location": "Museum of the Future, Dubai",
                "attendees": 12,
                "capacity": 20,
                "organizer": "Tech Explorers UAE",
                "description": "Exclusive guided tour of Dubai's iconic Museum of the Future with tech experts",
                "image": "https://images.unsplash.com/photo-1643795788371-85c8f5e56767?w=500",
                "details": """
                    <h3>Event Details</h3>
                    <p><strong>Date:</strong> April 20, 2025 at 2:00 PM</p>
                    <p><strong>Meeting Point:</strong> Museum of the Future Main Entrance</p>
                    <p><strong>Duration:</strong> Approximately 2 hours</p>
                    <p><strong>Price:</strong> AED 200 (includes museum admission)</p>
                    <img src="https://images.unsplash.com/photo-1643795788371-85c8f5e56767?w=800" style="width:100%; border-radius:8px; margin:10px 0;">
                    <p>Join our expert-led tour of the Museum of the Future, where we'll explore the most innovative exhibits and discuss the future of technology. This is a unique opportunity to gain insights not available on regular tours.</p>
                """
            }
        ]
        
        if not upcoming_events:
            st.info("No upcoming events at the moment. Check back later!")
        else:        
            for event in upcoming_events:
                event_details = f"""
                <p style="color: #333333; margin: 5px 0;"><strong>📅 Date:</strong> {event['date']} at {event['time']}</p>
                <p style="color: #333333; margin: 5px 0;"><strong>📍 Location:</strong> {event['location']}</p>
                <p style="color: #333333; margin: 5px 0;"><strong>👥 Attendees:</strong> {event['attendees']}/{event['capacity']}</p>
                <p style="color: #333333; margin: 5px 0;"><strong>🎫 Organizer:</strong> {event['organizer']}</p>
                <p style="color: #333333; margin: 10px 0;">{event['description']}</p>
                """
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"""
                    <div class="card" style="background-color: #f8f9fa; border: 1px solid #dee2e6;">
                        <div class="card-title" style="color: #212529; font-weight: bold; font-size: 1.2rem; margin-bottom: 10px;">{event['name']}</div>
                        <div class="card-content" style="color: #333333;">{event_details}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    try:
                        if event.get('image'):
                            st.image(event['image'], use_container_width=True)
                    except Exception as e:
                        st.warning(f"Could not load image: {str(e)}")
                
                # View Details button with expanded details
                if st.button(f"View Details for {event['name']}", key=f"details_{event['name']}"):
                    st.markdown(event['details'].replace('<p>', '<p style="color: #333333;">'), unsafe_allow_html=True)
                
                # RSVP button
                if st.button("RSVP", key=f"rsvp_{event['name']}"):
                    st.success(f"You've RSVP'd to {event['name']}!")
                    time.sleep(1)
                    st.rerun()
                
                st.markdown("---")
    with tab2:
        st.subheader("Your Events")
        
        # Sample events you're attending
        your_events = [
            {
                "name": "Sunset Photography at Burj Khalifa",
                "date": "2025-04-18",
                "time": "18:30",
                "status": "Confirmed",
                "organizer": "Ahmed Al Maktoum"
            },
            {
                "name": "Museum of the Future Tech Tour",
                "date": "2025-04-20",
                "time": "14:00",
                "status": "Confirmed",
                "organizer": "Tech Explorers UAE"
            }
        ]
        
        if not your_events:
            st.info("You're not attending any events yet. Explore upcoming events!")
        else:
            for event in your_events:
                # Fixed: Using markdown for properly rendered content
                st.markdown(f"""
                <div class="card">
                    <div class="card-title">{event['name']}</div>
                    <div class="card-content">
                        <p>📅 {event['date']} at {event['time']}</p>
                        <p>🎫 Organized by: {event['organizer']}</p>
                        <p>🟢 Status: {event['status']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("View Details", key=f"details_{event['name']}_view"):
                    st.markdown(f"""
                    <div style="padding:15px; background-color:#f8f9fa; border-radius:8px; margin-top:10px;">
                        <h4>Event Details</h4>
                        <p><strong>Name:</strong> {event['name']}</p>
                        <p><strong>Date:</strong> {event['date']} at {event['time']}</p>
                        <p><strong>Organizer:</strong> {event['organizer']}</p>
                        <p><strong>Status:</strong> {event['status']}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    with tab3:
        st.subheader("Create New Event")
        user_circles = get_user_circles(st.session_state["user"]["user_id"])
        
        if not user_circles:
            st.warning("You need to join or create a circle before creating events")
        else:
            with st.form("create_event"):
                name = st.text_input("Event Name")
                description = st.text_area("Description")
                date = st.date_input("Date")
                time = st.time_input("Time")
                location = st.text_input("Location")
                circle = st.selectbox(
                    "Associated Circle",
                    [c["name"] for c in user_circles]
                )
                capacity = st.number_input("Capacity (0 for unlimited)", min_value=0)
                
                if st.form_submit_button("Create Event"):
                    if name:
                        event_id = generate_id("evt")
                        events = load_db("events")
                        
                        circle_id = next(c["circle_id"] for c in user_circles if c["name"] == circle)
                        
                        events[event_id] = {
                            "event_id": event_id,
                            "circle_id": circle_id,
                            "name": name,
                            "description": description,
                            "location": {"name": location},
                            "date": date.strftime("%Y-%m-%d"),
                            "time": time.strftime("%H:%M"),
                            "organizer": st.session_state["user"]["user_id"],
                            "attendees": [st.session_state["user"]["user_id"]],
                            "capacity": capacity,
                            "created_at": datetime.now().isoformat()
                        }
                        
                        # Add event to circle
                        circles = load_db("circles")
                        if "events" not in circles[circle_id]:
                            circles[circle_id]["events"] = []
                        circles[circle_id]["events"].append(event_id)
                        
                        save_db("events", events)
                        save_db("circles", circles)
                        
                        st.success(f"Event '{name}' created successfully!")
                        add_notification(
                            st.session_state["user"]["user_id"],
                            "event_created",
                            f"You created a new event: {name}"
                        )
                        time.sleep(1)
                        st.rerun()

def business_page():
    """Business dashboard page"""
    if st.session_state["user"]["account_type"] != "business":
        st.warning("This page is only available for business accounts")
        return
    
    st.title("💼 Business Dashboard")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Promotions", "Analytics", "Verification"])
    
    with tab1:
        st.subheader("Business Overview")
        
        # Business info
        businesses = load_db("businesses")
        try:
            business = next(
                b for b in businesses.values() 
                if b["owner_id"] == st.session_state["user"]["user_id"]
            )
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="card">
                    <div class="card-title">Business Profile</div>
                    <div class="card-content">
                        <p>Name: {business['business_name']}</p>
                        <p>Category: {business['category']}</p>
                        <p>Status: {"✅ Verified" if business.get('verified', False) else "⚠️ Pending"}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Edit Profile", key="edit_profile"):
                    st.info("Profile editing functionality will be added soon.")
            
            with col2:
                st.markdown(f"""
                <div class="card">
                    <div class="card-title">Locations</div>
                    <div class="card-content">
                        {"<br>".join([loc["address"] for loc in business["locations"]])}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Add Location", key="add_location"):
                    st.info("Location adding functionality will be added soon.")
            
            st.subheader("Recent Activity")
            st.info("Business activity feed would appear here")
        except StopIteration:
            st.error("Business profile not found. Please contact support.")
    
    with tab2:
        st.subheader("Create Promotion")
        with st.form("create_promotion"):
            offer = st.text_input("Offer (e.g., '20% off')")
            description = st.text_area("Promotion Details")
            requirements = st.text_input("Requirements (e.g., 'Post 3 photos with #OurBusiness')")
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
            tags = st.multiselect("Relevant Tags", ["Food", "Drink", "Retail", "Service", "Discount", "Event"])
            
            if st.form_submit_button("Launch Promotion"):
                try:
                    promo_id = generate_id("promo")
                    promotions = load_db("promotions")
                    
                    businesses = load_db("businesses")
                    business_id = next(
                        b["business_id"] for b in businesses.values() 
                        if b["owner_id"] == st.session_state["user"]["user_id"]
                    )
                    
                    promotions[promo_id] = {
                        "promo_id": promo_id,
                        "business_id": business_id,
                        "offer": offer,
                        "description": description,
                        "requirements": requirements,
                        "start_date": start_date.strftime("%Y-%m-%d"),
                        "end_date": end_date.strftime("%Y-%m-%d"),
                        "tags": tags,
                        "claimed_by": [],
                        "created_at": datetime.now().isoformat()
                    }
                    save_db("promotions", promotions)
                    st.success("Promotion launched successfully!")
                except StopIteration:
                    st.error("Business profile not found. Please contact support.")
                except Exception as e:
                    st.error(f"Error creating promotion: {str(e)}")

def main():
    """Main application function"""
    # Initialize database first
    init_db()
    generate_sample_data()
    
    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Home"
    
    # Load CSS
    load_css()
    
    # Sidebar navigation
    if st.session_state["logged_in"]:
        with st.sidebar:
            try:
                st.image("https://via.placeholder.com/150x50?text=Atmosphere", use_container_width=True)
            except Exception as e:
                st.markdown("# Atmosphere")
                
            st.markdown(f"**Welcome, {st.session_state['user']['full_name'].split()[0]}!**")
            
            # Navigation menu
            menu_options = {
                "Home": "🏠 Home",
                "Explore": "🔍 Explore",
                "Media": "📸 Media",
                "Circles": "👥 Circles",
                "Events": "📅 Events",
                "Business": "💼 Business" if st.session_state["user"]["account_type"] == "business" else None
            }
            
            for page, label in menu_options.items():
                if label is not None and st.button(label):
                    st.session_state["current_page"] = page
            
            st.markdown("---")
            if st.button("🚪 Logout"):
                st.session_state["logged_in"] = False
                st.session_state["user"] = None
                st.session_state["current_page"] = "Home"
                st.rerun()
            
            # User profile
            st.markdown("---")
            try:
                st.image(st.session_state["user"].get("profile_pic", "https://via.placeholder.com/150"), width=60)
            except Exception as e:
                st.info("Profile picture not available")
                
            st.caption(st.session_state["user"]["full_name"])
    
    # Page routing
    if not st.session_state["logged_in"]:
        # Authentication pages
        st.sidebar.title("Atmosphere")
        auth_tab = st.session_state.get("auth_tab", "Login")
        auth_tab = st.sidebar.radio("Navigation", ["Login", "Sign Up"], index=0 if auth_tab == "Login" else 1)
        st.session_state["auth_tab"] = auth_tab

        if auth_tab == "Login":
            login_page()
        else:
            signup_page()
    else:
        # Main app pages
        if st.session_state["current_page"] == "Home":
            home_page()
        elif st.session_state["current_page"] == "Explore":
            explore_page()
        elif st.session_state["current_page"] == "Media":
            media_page()
        elif st.session_state["current_page"] == "Circles":
            circles_page()
        elif st.session_state["current_page"] == "Events":
            events_page()
        elif st.session_state["current_page"] == "Business":
            business_page()

if __name__ == "__main__":
    main()
