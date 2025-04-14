import streamlit as st
import bcrypt
import json
import os
import time
from datetime import datetime
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

# ===== HTML COMPONENTS SECTION =====
def card(title, content, image=None, action_button=None):
    """Reusable card component with optional image and action button"""
    img_html = f'<img src="{image}" style="width:100%; border-radius:8px; margin-bottom:15px;">' if image else ''
    button_html = f'<button class="card-button">{action_button}</button>' if action_button else ''
    
    st.markdown(f"""
    <div class="card">
        <div class="card-title">{title}</div>
        {img_html}
        <div class="card-content">{content}</div>
        {button_html}
    </div>
    """, unsafe_allow_html=True)

def hero_section(title, subtitle, image_url):
    """Hero banner component with title and subtitle"""
    st.markdown(f"""
    <div class="hero-container">
        <img src="{image_url}" style="width:100%; border-radius:8px;">
        <div class="hero-text">
            <h1 class="hero-title">{title}</h1>
            <p>{subtitle}</p>
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
DB_STRUCTURE = {
    "users": {
        "sample_user": {
            "user_id": "usr_123",
            "full_name": "John Doe",
            "email": "john@example.com",
            "password": "<hashed_password>",
            "account_type": "general",
            "verified": True,
            "joined_date": "2023-01-01",
            "interests": ["music", "tech"],
            "location": {"city": "New York", "lat": 40.7128, "lng": -74.0060},
            "profile_pic": "https://randomuser.me/api/portraits/men/1.jpg"
        }
    },
    "businesses": {
        "sample_business": {
            "business_id": "biz_123",
            "owner_id": "usr_123",
            "business_name": "Cool Cafe",
            "category": "Food & Drink",
            "verified": False,
            "locations": [
                {"address": "123 Main St", "lat": 40.7128, "lng": -74.0060}
            ]
        }
    },
    "media": [
        {
            "media_id": "med_123",
            "user_id": "usr_123",
            "file_path": "media_gallery/usr_123_photo1.jpg",
            "location": {"name": "Central Park", "lat": 40.7829, "lng": -73.9654},
            "timestamp": "2023-01-01T12:00:00",
            "circle_id": "cir_123",
            "tags": ["nature", "park"],
            "reports": []
        }
    ],
    "circles": {
        "cir_123": {
            "circle_id": "cir_123",
            "name": "NYC Photographers",
            "description": "For photography enthusiasts in NYC",
            "type": "public",
            "location": {"city": "New York", "lat": 40.7128, "lng": -74.0060},
            "members": ["usr_123"],
            "events": ["evt_123"],
            "business_owned": False,
            "created_at": "2023-01-01T10:00:00"
        }
    },
    "events": {
        "evt_123": {
            "event_id": "evt_123",
            "circle_id": "cir_123",
            "name": "Sunset Photography Meetup",
            "description": "Let's capture the sunset together!",
            "location": {"name": "Brooklyn Bridge", "lat": 40.7061, "lng": -73.9969},
            "date": "2023-06-15",
            "time": "18:00",
            "organizer": "usr_123",
            "attendees": ["usr_123"],
            "capacity": 20,
            "tags": ["photography", "outdoors"],
            "created_at": "2023-05-01T09:00:00"
        }
    },
    "promotions": {
        "promo_123": {
            "promo_id": "promo_123",
            "business_id": "biz_123",
            "offer": "20% off coffee",
            "requirements": "Post 3 photos with #CoolCafe",
            "start_date": "2023-01-01",
            "end_date": "2023-01-31",
            "claimed_by": ["usr_123"],
            "created_at": "2022-12-15T10:00:00"
        }
    },
    "notifications": {
        "usr_123": [
            {
                "notification_id": "notif_123",
                "type": "event_reminder",
                "content": "Sunset Photography Meetup starts in 2 hours!",
                "timestamp": "2023-06-15T16:00:00",
                "read": False,
                "related_id": "evt_123"
            }
        ]
    },
    "reports": [
        {
            "report_id": "rep_123",
            "reporter_id": "usr_123",
            "content_id": "med_123",
            "content_type": "media",
            "reason": "Inappropriate content",
            "status": "pending",
            "timestamp": "2023-01-01T12:30:00"
        }
    ]
}

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

# ===== HELPER FUNCTIONS =====
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
        # Ensure the file exists first
        if not os.path.exists(DB_FILES[file_key]):
            if retry_count >= max_retries:
                return {} if file_key in ["users", "businesses", "circles", "events", "promotions", "notifications"] else []
            init_db()
            
        with open(DB_FILES[file_key], "r") as f:
            data = json.load(f)
            # Ensure the structure matches expected format
            if file_key in ["users", "businesses", "circles", "events", "promotions", "notifications"] and not isinstance(data, dict):
                return {}
            elif file_key in ["media", "reports"] and not isinstance(data, list):
                return []
            return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        if retry_count >= max_retries:
            st.error(f"Database error: Unable to load {file_key}. Error: {str(e)}")
            return {} if file_key in ["users", "businesses", "circles", "events", "promotions", "notifications"] else []
        time.sleep(0.1)  # Add small delay between retries
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
        save_db("users", users)
    
    circles = load_db("circles")
    if not circles:
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
        save_db("circles", circles)
    
    events = load_db("events")
    if not events:
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
        save_db("events", events)
    
    # Ensure sample user has notifications
    notifications = load_db("notifications")
    if "usr_123" not in notifications:
        notifications["usr_123"] = [{
            "notification_id": "notif_123",
            "type": "welcome",
            "content": "Welcome to Atmosphere! Get started by joining a circle.",
            "timestamp": datetime.now().isoformat(),
            "read": False
        }]
        save_db("notifications", notifications)

# ===== AUTHENTICATION PAGES =====
def login_page():
    st.markdown("""
        <h1 class='hero-title'>Welcome to Atmosphere</h1>
        <p class='hero-subtitle'>
            Your digital space to connect with like-minded individuals, explore engaging events, 
            and share your stories within interest-based circles. Dive in and discover a vibrant, interactive community.
        </p>
    """, unsafe_allow_html=True)

    st.image("https://images.unsplash.com/photo-1469474968028-56623f02e42e", use_container_width=True, caption="Capture the vibe with Atmosphere")
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
        # Custom card layout using columns to position the button inside
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

            # Use an empty container with negative margin to "push" the button inside the card visually
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

# ===== MAIN APP PAGES =====
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
    
    # Search functionality
    search_col, filter_col = st.columns([3, 1])
    with search_col:
        search_query = st.text_input("Search for circles, events, or locations")
    with filter_col:
        filter_type = st.selectbox("Filter", ["All", "Circles", "Events", "Locations"])
    
    # Map view with location selector
    st.subheader("📍 Nearby Locations")
    location = st.selectbox(
        "Select Location",
        ["New York", "Dubai", "London", "Tokyo"],
        index=1  # Default to Dubai
    )
    
    # Sample map images
    map_images = {
        "New York": "https://maps.googleapis.com/maps/api/staticmap?center=40.7128,-74.0060&zoom=12&size=800x300&markers=color:red%7C40.7128,-74.0060&key=YOUR_API_KEY",
        "Dubai": "https://www.mapquest.com/dubai/dubai-282704697",
        "London": "https://maps.googleapis.com/maps/api/staticmap?center=51.5074,-0.1278&zoom=12&size=800x300&markers=color:red%7C51.5074,-0.1278&key=YOUR_API_KEY",
        "Tokyo": "https://maps.googleapis.com/maps/api/staticmap?center=35.6762,139.6503&zoom=12&size=800x300&markers=color:red%7C35.6762,139.6503&key=YOUR_API_KEY"
    }
    
    st.image(map_images[location], 
            use_container_width=True, 
            caption=f"Map of {location} with popular locations")
    
    # Popular circles section with sample data
    st.subheader("👥 Popular Circles")
    
    circles_data = [
        {
            "name": "NYC Photographers",
            "description": "For photography enthusiasts in NYC. Weekly photo walks and editing workshops.",
            "members": 327,
            "type": "public",
            "image": "https://images.unsplash.com/photo-1496568816309-51d7c20e3b21?w=500"
        },
        {
            "name": "Dubai Food Lovers",
            "description": "Discover hidden culinary gems across Dubai. Restaurant reviews and food tours.",
            "members": 215,
            "type": "public",
            "image": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=500"
        },
        {
            "name": "Tech Entrepreneurs UAE",
            "description": "Network with startup founders and tech professionals in the UAE.",
            "members": 183,
            "type": "private",
            "image": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=500"
        }
    ]
    
    for circle in circles_data:
        card(
            circle["name"],
            f"{circle['description']}\n\n👥 {circle['members']} members | 🔓 {circle['type'].capitalize()}",
            image=circle["image"],
            action_button="Join Circle"
        )
    
    # Upcoming events section with sample data
    st.subheader("📅 Upcoming Events")
    
    events_data = [
        {
            "name": "Sunset Photography at Burj Khalifa",
            "date": "2025-04-15",
            "time": "17:30",
            "location": "Burj Khalifa, Dubai",
            "description": "Capture stunning sunset views from the world's tallest building. Tripods recommended.",
            "image": "https://images.unsplash.com/photo-1518684079-3c830dcef090?w=500"
        },
        {
            "name": "Dubai Marina Food Tour",
            "date": "2025-04-18",
            "time": "19:00",
            "location": "Dubai Marina Walk",
            "description": "Sample cuisine from 5 different restaurants along the marina.",
            "image": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=500"
        },
        {
            "name": "Startup Pitch Night",
            "date": "2025-04-22",
            "time": "18:30",
            "location": "DIFC Innovation Hub",
            "description": "Watch 10 emerging startups pitch to investors. Networking drinks included.",
            "image": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=500"
        }
    ]
    
    for event in events_data:
        card(
            event["name"],
            f"""📅 {event['date']} at {event['time']}
            📍 {event['location']}
            
            {event['description']}""",
            image=event["image"],
            action_button="RSVP"
        )

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
    
    with tab2:
        st.subheader("Your Shared Memories")
        user_media = get_user_media(st.session_state["user"]["user_id"])
        st.subheader("Your Shared Memories")
        user_media = get_user_media(st.session_state["user"]["user_id"])
        
        if not user_media:
            st.info("You haven't uploaded any media yet. Capture your first moment!")
        else:
            cols = st.columns(3)
            for i, item in enumerate(user_media):
                with cols[i % 3]:
                    try:
                        st.image(
                            item["file_path"], 
                            use_container_width=True,
                            caption=f"{item['location']['name']} â¢ {datetime.fromisoformat(item['timestamp']).strftime('%b %d, %Y')}"
                        )
                        st.write(f"Tags: {', '.join(item['tags'])}")
                    except:
                        st.warning("Could not load this media file")

def circles_page():
    """Circles management page"""
    generate_sample_data()
    st.title("ð¥ Your Circles")
    
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
                card(
                    circle["name"],
                    f"{circle['description']}\n\nMembers: {len(circle['members'])} â¢ Type: {circle['type'].capitalize()}",
                    action_button="Join Circle"
                )
    
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
    st.title("ð Events")
    
    tab1, tab2, tab3 = st.tabs(["Upcoming", "Your Events", "Create"])
    
    with tab1:
        st.subheader("Upcoming Events")
        
        # Sample upcoming events data
        upcoming_events = [
            {
                "name": "Sunset Photography Meetup",
                "date": "2025-04-15",
                "time": "18:00",
                "location": "Brooklyn Bridge, New York",
                "attendees": 12,
                "capacity": 20,
                "organizer": "Jane Doe",
                "description": "Capture stunning sunset views from Brooklyn Bridge. All skill levels welcome!",
                "image": "https://images.unsplash.com/photo-1496568816309-51d7c20e3b21?w=500"
            },
            {
                "name": "Downtown Food Tour",
                "date": "2025-04-18",
                "time": "19:00",
                "location": "Lower Manhattan",
                "attendees": 8,
                "capacity": 15,
                "organizer": "Mike Chen",
                "description": "Explore hidden culinary gems in downtown NYC",
                "image": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=500"
            },
            {
                "name": "Tech Startup Mixer",
                "date": "2025-04-20",
                "time": "19:30",
                "location": "WeWork Soho",
                "attendees": 25,
                "capacity": 50,
                "organizer": "Alex Johnson",
                "description": "Network with fellow tech entrepreneurs and investors",
                "image": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=500"
            }
        ]
        
        if not upcoming_events:
            st.info("No upcoming events at the moment. Check back later!")
        else:
            for event in upcoming_events:
                card(
                    event["name"],
                    f"""ð {event['date']} at {event['time']}
                    ð {event['location']}
                    ð¥ {event['attendees']}/{event['capacity']} attending
                    ð« Organized by: {event['organizer']}
                    
                    {event['description']}""",
                    image=event["image"],
                    action_button="RSVP"
                )
    
    with tab2:
        st.subheader("Your Events")
        
        # Sample events you're attending
        your_events = [
            {
                "name": "Sunset Photography Meetup",
                "date": "2025-04-15",
                "time": "18:00",
                "status": "Confirmed",
                "organizer": "Jane Doe"
            },
            {
                "name": "Central Park Picnic",
                "date": "2025-04-10",
                "time": "12:00",
                "status": "Completed",
                "organizer": "Sarah Williams"
            }
        ]
        
        if not your_events:
            st.info("You're not attending any events yet. Explore upcoming events!")
        else:
            for event in your_events:
                card(
                    event["name"],
                    f"""ð {event['date']} at {event['time']}
                    ð« Organized by: {event['organizer']}
                    ð¢ Status: {event['status']}""",
                    action_button="View Details"
                )
    
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
                        st.success(f"Event '{name}' created successfully!")
                        time.sleep(1)
                        st.rerun()
def business_page():
    """Business dashboard page"""
    if st.session_state["user"]["account_type"] != "business":
        st.warning("This page is only available for business accounts")
        return
    
    st.title("ð¼ Business Dashboard")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Promotions", "Analytics", "Verification"])
    
    with tab1:
        st.subheader("Business Overview")
        
        # Business info
        businesses = load_db("businesses")
        business = next(
            b for b in businesses.values() 
            if b["owner_id"] == st.session_state["user"]["user_id"]
        )
        
        col1, col2 = st.columns(2)
        with col1:
            card(
                "Business Profile",
                f"""Name: {business['business_name']}
                Category: {business['category']}
                Status: {"â Verified" if business.get('verified', False) else "â³ Pending"}""",
                action_button="Edit Profile"
            )
        
        with col2:
            card(
                "Locations",
                "\n".join([loc["address"] for loc in business["locations"]]),
                action_button="Add Location"
            )
        
        st.subheader("Recent Activity")
        # Show business-related activity
        st.info("Business activity feed would appear here")
    
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
# ===== MAIN APP FUNCTION =====
def main():
    """Main application function"""
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
            st.image("https://via.placeholder.com/150x50?text=Atmosphere", width=150)
            st.markdown(f"**Welcome, {st.session_state['user']['full_name'].split()[0]}!**")
            
            # Navigation menu
            menu_options = {
                "Home": "ð ",
                "Explore": "ð",
                "Media": "ð¸",
                "Circles": "ð¥",
                "Events": "ð",
                "Business": "ð¼" if st.session_state["user"]["account_type"] == "business" else None
            }
            
            # Filter out None values (like Business for non-business accounts)
            menu_options = {k: v for k, v in menu_options.items() if v is not None}
            
            for page, icon in menu_options.items():
                if st.button(f"{icon} {page}"):
                    st.session_state["current_page"] = page
            
            st.markdown("---")
            if st.button("ðª Logout"):
                st.session_state["logged_in"] = False
                st.session_state["user"] = None
                st.session_state["current_page"] = "Home"
                st.rerun()
            
            # User profile
            st.markdown("---")
            st.image(st.session_state["user"].get("profile_pic", "https://via.placeholder.com/150"), width=60)
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
