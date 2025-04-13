import streamlit as st
import bcrypt
import json
import os
import time
from datetime import datetime
from PIL import Image
import random
import uuid
from pathlib import Path

# ===== CONFIGURATION =====
APP_NAME = "Atmosphere"
VERSION = "1.0.0"
DATA_DIR = "data"
MEDIA_DIR = "media_gallery"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MEDIA_DIR, exist_ok=True)

# ===== STYLING =====
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
    
    /* Base Styles */
    body {{
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.6;
        color: var(--dark);
    }}
    
    /* Main Containers */
    .main-container {{
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }}
    
    /* Cards */
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
    
    /* Stats Cards */
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
    
    /* Buttons */
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
    
    /* Forms */
    .stTextInput>div>div>input, 
    .stTextArea>div>textarea {{
        border-radius: 8px;
        border: 1px solid #ced4da;
    }}
    .stSelectbox>div>div>div {{
        border-radius: 8px;
    }}
    
    /* Navigation */
    .sidebar .sidebar-content {{
        background-color: var(--light);
        padding: 15px;
    }}
    .sidebar .sidebar-content .block-container {{
        padding-top: 0;
    }}
    
    /* Hero Section */
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
    
    /* Activity Feed Items */
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
    
    /* Responsive Adjustments */
    @media (max-width: 768px) {{
        .hero-title {{
            font-size: 1.8rem;
        }}
        .card {{
            margin-bottom: 15px;
        }}
        .sidebar .sidebar-content {{
            padding: 10px;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)

# ===== DATABASE CONFIGURATION =====
DB_FILES = {
    "users": os.path.join(DATA_DIR, "users.json"),
    "businesses": os.path.join(DATA_DIR, "businesses.json"),
    "media": os.path.join(DATA_DIR, "media.json"),
    "circles": os.path.join(DATA_DIR, "circles.json"),
    "events": os.path.join(DATA_DIR, "events.json"),
    "promotions": os.path.join(DATA_DIR, "promotions.json"),
    "notifications": os.path.join(DATA_DIR, "notifications.json"),
    "reports": os.path.join(DATA_DIR, "reports.json")
}

def init_db():
    """Initialize database files with empty structures"""
    for file_key, file_path in DB_FILES.items():
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                if file_key in ["users", "businesses", "circles", "events", "promotions", "notifications"]:
                    json.dump({}, f)
                else:
                    json.dump([], f)

def load_db(file_key):
    """Load database file with error handling"""
    file_path = DB_FILES[file_key]
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            # Ensure the structure matches expected format
            if file_key in ["users", "businesses", "circles", "events", "promotions", "notifications"] and not isinstance(data, dict):
                return {}
            elif file_key in ["media", "reports"] and not isinstance(data, list):
                return []
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        # If file is corrupted or doesn't exist, reinitialize it
        init_db()
        return load_db(file_key)

def save_db(file_key, data):
    """Save database file with atomic write"""
    file_path = DB_FILES[file_key]
    temp_path = f"{file_path}.tmp"
    
    with open(temp_path, "w") as f:
        json.dump(data, f, indent=2)
    
    # Atomic operation - replace old file only if new file was successfully written
    if os.path.exists(temp_path):
        os.replace(temp_path, file_path)

# ===== HELPER FUNCTIONS =====
def generate_id(prefix):
    """Generate unique ID"""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, hashed):
    """Verify password against hashed version"""
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False

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
    
    # Keep only the 50 most recent notifications
    notifications[user_id] = notifications[user_id][-50:]
    
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
            "date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
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

# ===== COMPONENTS =====
def card(title, content, image=None, action_button=None, action_key=None):
    """Reusable card component with optional image and action button"""
    img_html = f'<img src="{image}" style="width:100%; border-radius:8px; margin-bottom:15px;">' if image else ''
    button_html = f"""
    <div style="margin-top: 15px;">
        <button class="card-button" id="{action_key}">{action_button}</button>
    </div>
    """ if action_button and action_key else ''
    
    st.markdown(f"""
    <div class="card">
        <div class="card-title">{title}</div>
        {img_html}
        <div class="card-content">{content}</div>
        {button_html}
    </div>
    """, unsafe_allow_html=True)
    
    if action_button and action_key:
        return st.button(action_button, key=action_key)
    return None

def hero_section(title, subtitle, image_url):
    """Hero banner component with title and subtitle"""
    st.markdown(f"""
    <div class="hero-container">
        <img src="{image_url}" style="width:100%; border-radius:8px; max-height: 300px; object-fit: cover;">
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
    """Stats card component"""
    st.markdown(f"""
    <div class="stats-card">
        <h3>{title}</h3>
        <div class="value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

# ===== AUTHENTICATION PAGES =====
def login_page():
    """Login page with welcome message"""
    st.markdown(f"""
        <h1 class='hero-title'>Welcome to {APP_NAME}</h1>
        <p class='hero-subtitle'>
            Your digital space to connect with like-minded individuals, explore engaging events, 
            and share your stories within interest-based circles.
        </p>
    """, unsafe_allow_html=True)

    st.image("https://images.unsplash.com/photo-1469474968028-56623f02e42e", 
             use_container_width=True, 
             caption="Capture the vibe with Atmosphere")
    st.markdown("---")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("🔐 Log In to Your Account")
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            login_btn = st.form_submit_button("Login")
            
            if login_btn:
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    users = load_db("users")
                    if username in users and verify_password(password, users[username]["password"]):
                        st.session_state["user"] = users[username]
                        st.session_state["logged_in"] = True
                        st.session_state["current_page"] = "Home"
                        
                        # Add welcome back notification
                        add_notification(
                            users[username]["user_id"], 
                            "login", 
                            "Welcome back to Atmosphere!"
                        )
                        
                        st.success("Login successful! Redirecting...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
    
    with col2:
        st.markdown("""
            <div class="card">
                <h3 class="card-title" style="color: #212529;">🌞 New to Atmosphere?</h3>
                <ul style="list-style-type: none; padding-left: 0; font-size: 0.95rem; color: #212529;">
                    <li>✅ Discover local events & activities</li>
                    <li>🎨 Join interest-based circles</li>
                    <li>📷 Share your experiences & moments</li>
                    <li>🚀 Promote your business locally</li>
                </ul>
                <p style="margin-top: 10px; color: #212529;">Don't have an account?</p>
                <a href="#sign-up" onclick="window.location.hash='sign-up'" style="color: #4361ee; font-weight: bold;">Sign up now →</a>
            </div>
        """, unsafe_allow_html=True)

def signup_page():
    """Signup page with tabs for different account types"""
    st.title("🆕 Join Our Community")
    
    tab1, tab2 = st.tabs(["👤 General User", "💼 Business Account"])
    
    with tab1:
        with st.form("general_signup"):
            st.subheader("Create Personal Account")
            full_name = st.text_input("Full Name", placeholder="John Doe")
            username = st.text_input("Username", placeholder="johndoe123")
            email = st.text_input("Email", placeholder="john@example.com")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            location = st.text_input("Your Location (City)", placeholder="New York")
            interests = st.multiselect("Your Interests", ["Art", "Music", "Sports", "Food", "Tech", "Nature"])
            
            signup_btn = st.form_submit_button("Create Account")
            
            if signup_btn:
                if not all([full_name, username, email, password, confirm_password]):
                    st.error("Please fill in all required fields")
                elif password != confirm_password:
                    st.error("Passwords don't match!")
                else:
                    users = load_db("users")
                    if username in users:
                        st.error("Username already exists!")
                    elif any(u["email"] == email for u in users.values()):
                        st.error("Email already registered!")
                    else:
                        user_id = generate_id("usr")
                        users[username] = {
                            "user_id": user_id,
                            "full_name": full_name,
                            "email": email,
                            "password": hash_password(password),
                            "account_type": "general",
                            "verified": False,
                            "joined_date": datetime.now().strftime("%Y-%m-%d"),
                            "interests": interests,
                            "location": {"city": location},
                            "profile_pic": f"https://randomuser.me/api/portraits/{random.choice(['men','women'])}/{random.randint(1,100)}.jpg"
                        }
                        save_db("users", users)
                        
                        # Set session state and redirect
                        st.session_state["user"] = users[username]
                        st.session_state["logged_in"] = True
                        st.session_state["current_page"] = "Home"
                        
                        # Add welcome notification
                        add_notification(
                            user_id, 
                            "welcome", 
                            "Welcome to Atmosphere! Get started by joining a circle."
                        )
                        
                        st.success("Account created successfully! Redirecting...")
                        time.sleep(1)
                        st.rerun()

    with tab2:
        with st.form("business_signup"):
            st.subheader("Register Your Business")
            business_name = st.text_input("Business Name", placeholder="Cool Cafe")
            owner_name = st.text_input("Owner/Representative Name", placeholder="John Doe")
            username = st.text_input("Username", placeholder="coolcafe")
            email = st.text_input("Business Email", placeholder="contact@coolcafe.com")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            category = st.selectbox("Business Category", ["Food & Drink", "Retail", "Services", "Entertainment", "Other"])
            address = st.text_input("Business Address", placeholder="123 Main St, New York")
            
            signup_btn = st.form_submit_button("Register Business")
            
            if signup_btn:
                if not all([business_name, owner_name, username, email, password, confirm_password, address]):
                    st.error("Please fill in all required fields")
                elif password != confirm_password:
                    st.error("Passwords don't match!")
                else:
                    users = load_db("users")
                    businesses = load_db("businesses")
                    
                    if username in users:
                        st.error("Username already exists!")
                    elif any(u["email"] == email for u in users.values()):
                        st.error("Email already registered!")
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
                            "joined_date": datetime.now().strftime("%Y-%m-%d"),
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
                        
                        # Set session state and redirect
                        st.session_state["user"] = users[username]
                        st.session_state["business"] = businesses[business_id]
                        st.session_state["logged_in"] = True
                        st.session_state["current_page"] = "Home"
                        
                        # Add welcome notification
                        add_notification(
                            user_id, 
                            "welcome", 
                            "Your business account has been created! Verification pending."
                        )
                        
                        st.success("Business account created! Verification pending. Redirecting...")
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
            for notif in notifications[-3:][::-1]:  # Show 3 most recent
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
                card(
                    circle["name"],
                    f"{len(circle['members'])} members • {circle['type'].capitalize()}",
                    action_button="View Circle",
                    action_key=f"view_circle_{circle['circle_id']}"
                )
    
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
                card(
                    event["name"],
                    f"{event['date']} at {event['time']}\n{event['location']['name']}",
                    action_button="View Event",
                    action_key=f"view_event_{event['event_id']}"
                )

def explore_page():
    """Explore page to discover content"""
    generate_sample_data()
    st.title("🔍 Explore Our Community")
    
    # Search functionality
    search_col, filter_col = st.columns([3, 1])
    with search_col:
        search_query = st.text_input("Search for circles, events, or locations", placeholder="e.g. photography, food, etc.")
    with filter_col:
        filter_type = st.selectbox("Filter", ["All", "Circles", "Events", "Locations"])
    
    # Map view with location selector
    st.subheader("📍 Nearby Locations")
    location = st.selectbox(
        "Select Location",
        ["New York", "Dubai", "London", "Tokyo"],
        index=1  # Default to Dubai
    )
    
    # Sample map placeholder
    st.image("https://maps.googleapis.com/maps/api/staticmap?center=25.2048,55.2708&zoom=12&size=800x300&markers=color:red%7C25.2048,55.2708&key=YOUR_API_KEY",
             use_container_width=True,
             caption=f"Map of {location} with popular locations")
    
    # Popular circles section
    st.subheader("👥 Popular Circles")
    circles = load_db("circles")
    
    for circle in list(circles.values())[:3]:
        btn = card(
            circle["name"],
            f"{circle['description']}\n\n👥 {len(circle['members'])} members | 🔓 {circle['type'].capitalize()}",
            action_button="Join Circle",
            action_key=f"join_{circle['circle_id']}"
        )
        
        if btn:
            if st.session_state["user"]["user_id"] not in circle["members"]:
                circle["members"].append(st.session_state["user"]["user_id"])
                save_db("circles", circles)
                st.success(f"You joined {circle['name']}!")
                st.rerun()
            else:
                st.warning("You're already a member of this circle")

def media_page():
    """Media upload and gallery page"""
    st.title("📸 Capture & Share Your Moments")
    
    tab1, tab2 = st.tabs(["📤 Upload Media", "🖼️ Your Gallery"])
    
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
            # Ensure media directory exists
            os.makedirs(MEDIA_DIR, exist_ok=True)
            
            # Save media
            media_id = generate_id("med")
            filename = f"{st.session_state['user']['user_id']}_{media_id}.jpg"
            filepath = os.path.join(MEDIA_DIR, filename)
            
            try:
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
                
                st.rerun()
            except Exception as e:
                st.error(f"Failed to save image: {str(e)}")
    
    with tab2:
        st.subheader("Your Shared Memories")
        user_media = get_user_media(st.session_state["user"]["user_id"])
        
        if not user_media:
            st.info("You haven't uploaded any media yet. Capture your first moment!")
        else:
            # Display media in a grid
            cols = st.columns(3)
            for i, item in enumerate(user_media):
                with cols[i % 3]:
                    try:
                        if os.path.exists(item["file_path"]):
                            st.image(
                                item["file_path"], 
                                use_container_width=True,
                                caption=f"{item['location']['name']} • {datetime.fromisoformat(item['timestamp']).strftime('%b %d, %Y')}"
                            )
                            st.write(f"Tags: {', '.join(item['tags'])}")
                        else:
                            st.warning("Media file not found")
                    except Exception as e:
                        st.error(f"Error loading image: {str(e)}")

def business_page():
    """Business dashboard page"""
    if st.session_state["user"]["account_type"] != "business":
        st.warning("This page is only available for business accounts")
        return
    
    st.title("💼 Business Dashboard")
    
    tab1, tab2, tab3 = st.tabs(["Overview", "Promotions", "Analytics"])
    
    with tab1:
        st.subheader("Business Overview")
        
        # Get business info
        businesses = load_db("businesses")
        business = next(
            (b for b in businesses.values() 
             if b["owner_id"] == st.session_state["user"]["user_id"]),
            None
        )
        
        if not business:
            st.error("Business profile not found")
            return
        
        col1, col2 = st.columns(2)
        with col1:
            card(
                "Business Profile",
                f"""Name: {business['business_name']}
                Category: {business['category']}
                Status: {"✅ Verified" if business.get('verified', False) else "⏳ Pending"}""",
                action_button="Edit Profile",
                action_key="edit_business_profile"
            )
        
        with col2:
            card(
                "Locations",
                "\n".join([loc["address"] for loc in business["locations"]]),
                action_button="Add Location",
                action_key="add_business_location"
            )
        
        st.subheader("Recent Activity")
        st.info("Business activity feed would appear here")
    
    with tab2:
        st.subheader("Create Promotion")
        with st.form("create_promotion"):
            offer = st.text_input("Offer (e.g., '20% off')", placeholder="20% off all items")
            description = st.text_area("Promotion Details", placeholder="Describe your promotion in detail")
            requirements = st.text_input("Requirements (e.g., 'Post 3 photos with #OurBusiness')", 
                                       placeholder="Follow us and post with #OurBusiness")
            start_date = st.date_input("Start Date", min_value=datetime.today())
            end_date = st.date_input("End Date", min_value=datetime.today())
            tags = st.multiselect("Relevant Tags", ["Food", "Drink", "Retail", "Service", "Discount", "Event"])
            
            if st.form_submit_button("Launch Promotion"):
                if not all([offer, description, requirements]):
                    st.error("Please fill in all required fields")
                elif end_date <= start_date:
                    st.error("End date must be after start date")
                else:
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
                    st.rerun()

# ===== MAIN APP FUNCTION =====
def main():
    """Main application function"""
    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Home"
    
    # Initialize database
    init_db()
    
    # Load CSS
    load_css()
    
    # Sidebar navigation
    if st.session_state["logged_in"]:
        with st.sidebar:
            st.image("https://via.placeholder.com/150x50?text=Atmosphere", width=150)
            st.markdown(f"**Welcome, {st.session_state['user']['full_name'].split()[0]}!**")
            
            # Navigation menu
            menu_options = {
                "Home": "🏠",
                "Explore": "🔍",
                "Media": "📸",
                "Circles": "👥",
                "Events": "📅",
                "Business": "💼" if st.session_state["user"]["account_type"] == "business" else None
            }
            
            # Filter out None values (like Business for non-business accounts)
            menu_options = {k: v for k, v in menu_options.items() if v is not None}
            
            for page, icon in menu_options.items():
                if st.button(f"{icon} {page}"):
                    st.session_state["current_page"] = page
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
