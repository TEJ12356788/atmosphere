import streamlit as st
import bcrypt
import json
import os
import time
from datetime import datetime
from PIL import Image
import random
import uuid

# ===== CSS STYLING SECTION =====
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
    for file, structure in DB_FILES.items():
        if not os.path.exists(file):
            with open(file, "w") as f:
                if file in ["users", "businesses", "circles", "notifications"]:
                    json.dump({}, f)
                else:
                    json.dump([], f)

def load_db(file_key):
    """Load database file"""
    try:
        with open(DB_FILES[file_key], "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        init_db()
        return load_db(file_key)

def save_db(file_key, data):
    """Save database file"""
    with open(DB_FILES[file_key], "w") as f:
        json.dump(data, f, indent=2)

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

# ===== AUTHENTICATION PAGES =====
def login_page():
    """Login page with form and welcome content"""
    st.title("🔑 Welcome Back to Atmosphere")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            login_btn = st.form_submit_button("Login")
            
            if login_btn:
                users = load_db("users")
                if username in users and verify_password(password, users[username]["password"]):
                    st.session_state["user"] = users[username]
                    st.session_state["logged_in"] = True
                    add_notification(users[username]["user_id"], "login", "Welcome back to Atmosphere!")
                    st.success("Login successful!")
                    time.sleep(1)
                    st.experimental_rerun()
                else:
                    st.error("Invalid username or password")

    with col2:
        st.image("https://images.unsplash.com/photo-1531058020387-3be344556be6", 
                use_container_width=True, 
                caption="Join our community")
        st.markdown("""
        <div style="padding:20px;">
            <h3>New to Atmosphere?</h3>
            <ul style="list-style-type:none; padding-left:0;">
                <li>🌍 Connect with like-minded people</li>
                <li>📸 Share your experiences</li>
                <li>🎉 Discover local events</li>
                <li>💼 Grow your business</li>
            </ul>
            <p>Don't have an account? <a href="#sign-up" onclick="window.location.hash='sign-up'">Sign up now</a></p>
        </div>
        """, unsafe_allow_html=True)

def signup_page():
    """Signup page with tabs for different account types"""
    st.title("🆕 Join Our Community")
    
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
                        st.experimental_rerun()

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
                        st.experimental_rerun()

# ===== MAIN APP PAGES =====
def home_page():
    """Home page with user dashboard"""
    hero_section(
        f"Welcome, {st.session_state['user']['full_name']}", 
        "What would you like to do today?",
        "https://images.unsplash.com/photo-1469474968028-56623f02e42e"
    )
    
    # User stats
    col1, col2, col3 = st.columns(3)
    with col1:
        card("Circles Joined", str(len(get_user_circles(st.session_state["user"]["user_id"]))))
    with col2:
        user_events = sum(len(get_circle_events(c["circle_id"])) for c in get_user_circles(st.session_state["user"]["user_id"]))
        card("Events Available", str(user_events))
    with col3:
        card("Media Shared", str(len(get_user_media(st.session_state["user"]["user_id"]))))
    
    # Activity feed
    st.subheader("📰 Your Activity Feed")
    tab1, tab2, tab3 = st.tabs(["Recent Activity", "Your Circles", "Upcoming Events"])
    
    with tab1:
        activities = [
            {"user": "JaneDoe", "action": "posted a photo in NYC Photographers", "time": "2h ago"},
            {"user": "MikeT", "action": "created an event: Central Park Picnic", "time": "5h ago"},
            {"user": "CoffeeShop", "action": "offered 20% off for photos", "time": "1d ago"}
        ]
        for activity in activities:
            activity_item(activity["user"], activity["action"], activity["time"])
    
    with tab2:
        circles = get_user_circles(st.session_state["user"]["user_id"])
        for circle in circles[:3]:  # Show first 3 circles
            card(
                circle["name"],
                f"Members: {len(circle['members'])}\nType: {circle['type'].capitalize()}",
                action_button="View Circle"
            )
    
    with tab3:
        events = []
        for circle in get_user_circles(st.session_state["user"]["user_id"]):
            events.extend(get_circle_events(circle["circle_id"]))
        
        for event in sorted(events, key=lambda x: x["date"])[:3]:  # Show next 3 events
            card(
                event["name"],
                f"📅 {event['date']} at {event['time']}\n📍 {event['location']['name']}",
                action_button="RSVP"
            )

def explore_page():
    """Explore page to discover content"""
    st.title("🔍 Explore Our Community")
    
    # Search functionality
    search_col, filter_col = st.columns([3, 1])
    with search_col:
        search_query = st.text_input("Search for circles, events, or locations")
    with filter_col:
        filter_type = st.selectbox("Filter", ["All", "Circles", "Events", "Locations"])
    
    # Map view
    st.subheader("📍 Nearby Locations")
    st.image("https://maps.googleapis.com/maps/api/staticmap?center=40.7128,-74.0060&zoom=12&size=800x300&markers=color:red%7C40.7128,-74.0060&key=YOUR_API_KEY", 
             use_container_width=True, 
             caption="Map of nearby locations with Atmosphere activity")
    
    # Popular circles
    st.subheader("👥 Popular Circles")
    circles = load_db("circles")
    for circle_id, circle in list(circles.items())[:3]:  # Show 3 sample circles
        card(
            circle["name"],
            circle["description"],
            action_button="Join Circle"
        )
    
    # Upcoming events
    st.subheader("📅 Upcoming Events")
    events = load_db("events")
    for event_id, event in list(events.items())[:3]:  # Show 3 sample events
        card(
            event["name"],
            f"📅 {event['date']} at {event['time']}\n📍 {event['location']['name']}",
            action_button="View Details"
        )

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
    "circle_id": next((c["circle_id"] for c in user_circles if c["name"] == selected_circle), None), # Added None as default, and closed the next() call
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
                            caption=f"{item['location']['name']} • {datetime.fromisoformat(item['timestamp']).strftime('%b %d, %Y')}"
                        )
                        st.write(f"Tags: {', '.join(item['tags'])}")
                    except:
                        st.warning("Could not load this media file")

def circles_page():
    """Circles management page"""
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
                            st.experimental_rerun()
                    with col2:
                        if st.button("Leave Circle", key=f"leave_{circle['circle_id']}"):
                            circles = load_db("circles")
                            circles[circle["circle_id"]]["members"].remove(st.session_state["user"]["user_id"])
                            save_db("circles", circles)
                            st.success(f"You left {circle['name']}")
                            st.experimental_rerun()
    
    with tab2:
        st.subheader("Discover New Circles")
        all_circles = load_db("circles")
        user_circles = get_user_circles(st.session_state["user"]["user_id"])
        user_circle_ids = [c["circle_id"] for c in user_circles]
        
        discover_circles = [c for c in all_circles.values() if c["circle_id"] not in user_circle_ids]
        
        if not discover_circles:
            st.info("No new circles to discover at the moment. Check back later!")
        else:
            for circle in discover_circles[:5]:  # Show up to 5 circles
                card(
                    circle["name"],
                    f"{circle['description']}\n\nMembers: {len(circle['members'])} • Type: {circle['type'].capitalize()}",
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
                    st.experimental_rerun()

def events_page():
    """Events management page"""
    st.title("📅 Events")
    
    tab1, tab2, tab3 = st.tabs(["Upcoming", "Your Events", "Create"])
    
    with tab1:
        st.subheader("Upcoming Events")
        all_events = load_db("events")
        upcoming_events = sorted(
            [e for e in all_events.values() if e["date"] >= datetime.now().strftime("%Y-%m-%d")],
            key=lambda x: x["date"]
        )
        
        if not upcoming_events:
            st.info("No upcoming events at the moment. Check back later!")
        else:
            for event in upcoming_events[:5]:  # Show up to 5 events
                card(
                    event["name"],
                    f"""📅 {event['date']} at {event['time']}
                    📍 {event['location']['name']}
                    👥 {len(event['attendees'])} attending
                    Organized by: {event['organizer']}""",
                    action_button="RSVP"
                )
    
    with tab2:
        st.subheader("Events You're Attending")
        user_events = []
        all_events = load_db("events")
        for event in all_events.values():
            if st.session_state["user"]["user_id"] in event["attendees"]:
                user_events.append(event)
        
        if not user_events:
            st.info("You're not attending any events yet. Explore upcoming events!")
        else:
            for event in user_events:
                card(
                    event["name"],
                    f"""📅 {event['date']} at {event['time']}
                    Status: {"Confirmed" if event['date'] >= datetime.now().strftime("%Y-%m-%d") else "Past Event"}""",
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
                        event_id = generate_id("evt")
                        events = load_db("events")
                        circle_id = next(c["circle_id"] for c in user_circles if c["name"] == circle)
                        
                        events[event_id] = {
                            "event_id": event_id,
                            "name": name,
                            "description": description,
                            "date": date.strftime("%Y-%m-%d"),
                            "time": str(time),
                            "location": {"name": location},
                            "organizer": st.session_state["user"]["user_id"],
                            "circle_id": circle_id,
                            "capacity": capacity,
                            "attendees": [st.session_state["user"]["user_id"]],
                            "tags": [],
                            "created_at": datetime.now().isoformat()
                        }
                        save_db("events", events)
                        
                        # Add to circle's events list
                        circles = load_db("circles")
                        circles[circle_id]["events"].append(event_id)
                        save_db("circles", circles)
                        
                        st.success(f"Event '{name}' created successfully!")
                        
                        # Notify circle members
                        for member in circles[circle_id]["members"]:
                            if member != st.session_state["user"]["user_id"]:
                                add_notification(
                                    member,
                                    "event",
                                    f"New event in {circle}: {name}",
                                    event_id
                                )
                        
                        time.sleep(1)
                        st.experimental_rerun()

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
                Status: {"✅ Verified" if business.get('verified', False) else "⏳ Pending"}""",
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
            
            st.markdown("---")
            if st.button("🚪 Logout"):
                st.session_state["logged_in"] = False
                st.session_state["user"] = None
                st.session_state["current_page"] = "Home"
                st.experimental_rerun()
            
            # User profile
            st.markdown("---")
            st.image(st.session_state["user"].get("profile_pic", "https://via.placeholder.com/150"), width=60)
            st.caption(st.session_state["user"]["full_name"])
    
    # Page routing
    if not st.session_state["logged_in"]:
        # Authentication pages
        st.sidebar.title("Atmosphere")
        auth_tab = st.sidebar.radio("Navigation", ["Login", "Sign Up"])
        
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
