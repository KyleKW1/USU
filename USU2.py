import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Page config
st.set_page_config(
    page_title="UTech Students' Union Council Retreat Assessment",
    page_icon="🎓",
    layout="wide"
)

# ============ GOOGLE SHEETS SETUP ============
# Toggle Google Sheets integration
USE_GOOGLE_SHEETS = st.secrets.get("use_google_sheets", False)

def get_sheets_service():
    """Create Google Sheets API service"""
    try:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        service = build('sheets', 'v4', credentials=credentials)
        return service
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        return None

def save_to_sheets(response_data):
    """Save response to Google Sheets"""
    if not USE_GOOGLE_SHEETS:
        return False
    
    try:
        service = get_sheets_service()
        if not service:
            return False
        
        spreadsheet_id = st.secrets["spreadsheet_id"]
        
        # Convert response to row format
        row = [
            response_data.get("timestamp", ""),
            response_data.get("name", ""),
            response_data.get("email", ""),
            response_data.get("position", ""),
            response_data.get("tenure", ""),
            str(response_data.get("satisfaction", "")),
            response_data.get("role_dislikes", ""),
            response_data.get("executive_concerns", ""),
            response_data.get("council_dynamics", ""),
            response_data.get("student_body_challenges", ""),
            response_data.get("achievements", ""),
            response_data.get("weaknesses", ""),
            response_data.get("skills_needed", ""),
            response_data.get("constitution_knowledge", ""),
            ", ".join(response_data.get("support_gaps", [])),
            response_data.get("support_details", ""),
            response_data.get("code_of_conduct", ""),
            response_data.get("financial_challenges", ""),
            ", ".join(response_data.get("financial_impact", [])),
            response_data.get("financial_details", ""),
            response_data.get("academic_challenges", ""),
            ", ".join(response_data.get("academic_impact", [])),
            response_data.get("academic_details", ""),
            ", ".join(response_data.get("support_needs", [])),
            response_data.get("retreat_goals", ""),
            response_data.get("training_topics", ""),
            ", ".join(response_data.get("retreat_priorities", [])),
            response_data.get("previous_retreats", ""),
            response_data.get("additional_comments", "")
        ]
        
        body = {'values': [row]}
        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range='Responses!A:AC',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        return True
    except Exception as e:
        st.error(f"Error saving to Google Sheets: {e}")
        return False

def load_from_sheets():
    """Load all responses from Google Sheets"""
    if not USE_GOOGLE_SHEETS:
        return []
    
    try:
        service = get_sheets_service()
        if not service:
            return []
        
        spreadsheet_id = st.secrets["spreadsheet_id"]
        
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='Responses!A2:AC'
        ).execute()
        
        values = result.get('values', [])
        if not values:
            return []
        
        # Convert to list of dicts
        responses = []
        for row in values:
            # Pad row to ensure it has all columns
            while len(row) < 29:
                row.append("")
            
            response = {
                "timestamp": row[0],
                "name": row[1],
                "email": row[2],
                "position": row[3],
                "tenure": row[4],
                "satisfaction": int(row[5]) if row[5] else 3,
                "role_dislikes": row[6],
                "executive_concerns": row[7],
                "council_dynamics": row[8],
                "student_body_challenges": row[9],
                "achievements": row[10],
                "weaknesses": row[11],
                "skills_needed": row[12],
                "constitution_knowledge": row[13],
                "support_gaps": row[14].split(", ") if row[14] else [],
                "support_details": row[15],
                "code_of_conduct": row[16],
                "financial_challenges": row[17],
                "financial_impact": row[18].split(", ") if row[18] else [],
                "financial_details": row[19],
                "academic_challenges": row[20],
                "academic_impact": row[21].split(", ") if row[21] else [],
                "academic_details": row[22],
                "support_needs": row[23].split(", ") if row[23] else [],
                "retreat_goals": row[24],
                "training_topics": row[25],
                "retreat_priorities": row[26].split(", ") if row[26] else [],
                "previous_retreats": row[27],
                "additional_comments": row[28]
            }
            responses.append(response)
        
        return responses
    except Exception as e:
        st.error(f"Error loading from Google Sheets: {e}")
        return []

# Initialize session state
if 'responses' not in st.session_state:
    if USE_GOOGLE_SHEETS:
        st.session_state.responses = load_from_sheets()
    else:
        st.session_state.responses = []

if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

# Admin password
ADMIN_PASSWORD = st.secrets.get("admin_password", "UTechAdmin2024")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #667eea;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Show connection status
if USE_GOOGLE_SHEETS:
    st.sidebar.success("✅ Connected to Google Sheets")
else:
    st.sidebar.info("📥 Using local storage (download data)")

# Sidebar for navigation
page = st.sidebar.selectbox(
    "Navigation",
    ["📝 Assessment Form", "📊 Analysis Dashboard", "🔐 Admin"]
)

# ============ ASSESSMENT FORM PAGE ============
if page == "📝 Assessment Form":
    st.markdown('<div class="main-header">UTech Students\' Union Council Pre-Retreat Assessment</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Your responses will help us create a meaningful retreat experience</div>', unsafe_allow_html=True)
    
    st.info("**Confidential:** All responses are anonymous and used solely for planning purposes aligned with Article X, Section 16 of the Students' Union Constitution.")
    
    with st.form("assessment_form"):
        # Council Member Information
        st.subheader("Council Member Information")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name (Optional)")
            email = st.text_input("Email (Optional)")
        with col2:
            position = st.selectbox("Council Position (Optional)", [
                "",
                "President",
                "1st Vice President Academic Affairs",
                "Vice President, Finance",
                "Vice President, Student Services",
                "Vice President, Public Relations",
                "Executive Secretary",
                "Faculty of Science and Sport Rep",
                "College of Health Sciences Rep",
                "Faculty of Education and Liberal Studies Rep",
                "School of Engineering Rep",
                "School of Computing and IT Rep",
                "School of Business Administration/JDSEEL Rep",
                "School of Building and Land Management Rep",
                "Caribbean School of Architecture Rep",
                "Faculty of Law Rep",
                "Western Campus Rep",
                "Resident Students' Rep",
                "Graduate Students' Rep",
                "International Students' Rep",
                "Joint Colleges of Medicine, Oral Health, and Veterinary Sciences Rep",
                "Director of Elections and Regulatory Affairs",
                "Director of Community Service",
                "Director of Health and Safety",
                "Director of Entertainment and Cultural Activities",
                "Director of Sport",
                "Director of Spiritual Development",
                "Director of Special Projects",
                "Editor in Chief",
                "Advisor to the President",
                "Advisor to the 1st Vice President",
                "Executive Assistant",
                "Special Advisor to VP Student Services",
                "President's Assistant"
            ])
            tenure = st.selectbox("Time on Council", [
                "First year on Council",
                "Second year on Council",
                "Third year or more on Council"
            ])
        
        # Council Experience
        st.subheader("Council Experience & Effectiveness")
        satisfaction = st.select_slider(
            "Overall satisfaction with your Council experience",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: ["Very Dissatisfied", "Dissatisfied", "Neutral", "Satisfied", "Very Satisfied"][x-1]
        )
        
        role_dislikes = st.text_area(
            "What aspects of your Council role do you find most challenging or frustrating?",
            placeholder="Consider: portfolio responsibilities, time management, resource constraints, communication barriers, etc."
        )
        
        executive_concerns = st.text_area(
            "Are there concerns about the Executive Board or Council leadership you'd like to address?",
            placeholder="This may include decision-making processes, transparency, communication, or guidance received"
        )
        
        council_dynamics = st.text_area(
            "Describe any challenges in Council dynamics or relationships with fellow Council members",
            placeholder="Consider: Board interactions, collaboration between portfolios, conflicts, communication issues, etc."
        )
        
        student_body_challenges = st.text_area(
            "What challenges do you face in representing or serving the student body?",
            placeholder="Consider: student engagement, feedback mechanisms, addressing student concerns, etc."
        )
        
        # Leadership Development
        st.subheader("Leadership Development & Portfolio Performance")
        achievements = st.text_area(
            "What are your top 3 achievements in your Council role this year?",
            placeholder="Consider: programs implemented, initiatives led, student impact, collaboration successes, etc."
        )
        
        weaknesses = st.text_area(
            "What leadership or portfolio-specific areas do you feel you need to improve?",
            placeholder="Be honest - this helps us plan targeted training and support"
        )
        
        skills_needed = st.text_area(
            "What skills, training, or resources would help you serve more effectively?",
            placeholder="Examples: public speaking, conflict resolution, project management, budgeting, event planning, social media, etc."
        )
        
        constitution_knowledge = st.selectbox(
            "How well do you understand the Students' Union Constitution and your role's responsibilities?",
            ["Very limited understanding", "Basic understanding", "Moderate understanding", 
             "Strong understanding", "Expert understanding"]
        )
        
        # Support and Resources
        st.subheader("Support, Resources & Council Operations")
        support_gaps = st.multiselect(
            "Select areas where you feel you lack adequate support",
            ["Executive Board guidance and mentorship",
             "Fellow Council members collaboration",
             "University Administration support",
             "Financial resources for portfolio activities",
             "Students' Union Office resources and facilities",
             "Training and professional development",
             "Time management and workload balance",
             "Communication channels and information flow"]
        )
        
        support_details = st.text_area(
            "Please elaborate on any areas where you lack support and suggest improvements",
            placeholder="Be specific about what would help you succeed in your role"
        )
        
        code_of_conduct = st.text_area(
            "Have you experienced challenges related to the Council's Code of Conduct or accountability?",
            placeholder="This includes attendance expectations, report submissions, Council event participation, etc."
        )
        
        # Financial & Academic Well-being
        st.subheader("Financial & Academic Well-being")
        col1, col2 = st.columns(2)
        
        financial_impact = []
        financial_details = ""
        academic_impact = []
        academic_details = ""
        
        with col1:
            financial_challenges = st.radio("Are you facing financial challenges?", ["Yes", "No"])
            if financial_challenges == "Yes":
                financial_impact = st.multiselect(
                    "These financial challenges affect:",
                    ["My personal life and well-being",
                     "My ability to fulfill my Council role",
                     "My ability to maintain my academics"]
                )
                financial_details = st.text_area(
                    "Please elaborate (Optional)",
                    placeholder="Examples: transportation costs, meals during long Council days, tuition challenges, etc.",
                    key="fin_details"
                )
        
        with col2:
            academic_challenges = st.radio("Are you experiencing academic difficulties?", ["Yes", "No"])
            if academic_challenges == "Yes":
                academic_impact = st.multiselect(
                    "These academic difficulties affect:",
                    ["My personal stress and well-being",
                     "My ability to fulfill my Council role",
                     "My GPA and academic standing"]
                )
                academic_details = st.text_area(
                    "Please elaborate (Optional)",
                    placeholder="Examples: balancing coursework with Council duties, risk of academic probation, etc.",
                    key="acad_details"
                )
        
        support_needs = st.multiselect(
            "Would any of these benefit you?",
            ["Time management and study skills workshop",
             "Financial literacy and budgeting resources",
             "Academic or leadership mentorship",
             "Access to counseling or wellness services",
             "More flexible Council meeting schedules"]
        )
        
        # Retreat Expectations
        st.subheader("Retreat Expectations & Suggestions")
        retreat_goals = st.text_area(
            "What do you hope to gain from this mandatory Council retreat?",
            placeholder="Reference: Constitution Article X, Section 16 - designed for planning, leadership training, and team building"
        )
        
        training_topics = st.text_area(
            "What specific training topics would benefit you and the Council?",
            placeholder="Examples: parliamentary procedure, financial management, event planning, conflict resolution, public speaking, etc."
        )
        
        retreat_priorities = st.multiselect(
            "Which areas should the retreat prioritize? (Select up to 3)",
            ["Team building and Council unity",
             "Strategic planning for the year",
             "Skills training and workshops",
             "Addressing conflicts and improving communication",
             "Constitution review and governance",
             "Improving student engagement strategies",
             "Council member wellness and self-care"]
        )
        
        previous_retreats = st.text_area(
            "If you attended previous retreats, what worked well and what needs improvement?",
            placeholder="Your feedback helps us make this retreat the best yet"
        )
        
        additional_comments = st.text_area(
            "Any additional comments, concerns, or suggestions?",
            placeholder="This is your opportunity to share anything else on your mind"
        )
        
        # Submit button
        submitted = st.form_submit_button("Submit Assessment")
        
        if submitted:
            response_data = {
                "timestamp": datetime.now().isoformat(),
                "name": name,
                "email": email,
                "position": position,
                "tenure": tenure,
                "satisfaction": satisfaction,
                "role_dislikes": role_dislikes,
                "executive_concerns": executive_concerns,
                "council_dynamics": council_dynamics,
                "student_body_challenges": student_body_challenges,
                "achievements": achievements,
                "weaknesses": weaknesses,
                "skills_needed": skills_needed,
                "constitution_knowledge": constitution_knowledge,
                "support_gaps": support_gaps,
                "support_details": support_details,
                "code_of_conduct": code_of_conduct,
                "financial_challenges": financial_challenges,
                "financial_impact": financial_impact,
                "financial_details": financial_details,
                "academic_challenges": academic_challenges,
                "academic_impact": academic_impact,
                "academic_details": academic_details,
                "support_needs": support_needs,
                "retreat_goals": retreat_goals,
                "training_topics": training_topics,
                "retreat_priorities": retreat_priorities,
                "previous_retreats": previous_retreats,
                "additional_comments": additional_comments
            }
            
            # Save to Google Sheets if enabled
            if USE_GOOGLE_SHEETS:
                if save_to_sheets(response_data):
                    st.success("✅ Thank you! Your response has been saved to Google Sheets.")
                else:
                    st.warning("⚠️ Saved locally, but couldn't save to Google Sheets.")
            
            # Always save to session state as backup
            st.session_state.responses.append(response_data)
            st.success("✅ Thank you for completing the assessment! Your responses have been recorded.")
            st.balloons()

# ============ ANALYSIS DASHBOARD PAGE ============
elif page == "📊 Analysis Dashboard":
    st.markdown('<div class="main-header">Analysis Dashboard</div>', unsafe_allow_html=True)
    
    # Refresh data button for Google Sheets
    if USE_GOOGLE_SHEETS:
        if st.button("🔄 Refresh Data from Google Sheets"):
            st.session_state.responses = load_from_sheets()
            st.success("Data refreshed!")
            st.rerun()
    
    if len(st.session_state.responses) == 0:
        st.warning("No responses yet. Please submit assessments first.")
        st.info("You can also upload a JSON file with responses collected previously.")
        
        uploaded_file = st.file_uploader("Upload responses JSON file", type=['json'])
        if uploaded_file is not None:
            try:
                data = json.load(uploaded_file)
                st.session_state.responses = data if isinstance(data, list) else [data]
                st.success(f"Loaded {len(st.session_state.responses)} responses!")
                st.rerun()
            except Exception as e:
                st.error(f"Error loading file: {e}")
    else:
        df = pd.DataFrame(st.session_state.responses)
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Responses", len(df))
        with col2:
            avg_sat = df['satisfaction'].mean()
            st.metric("Avg Satisfaction", f"{avg_sat:.2f}/5")
        with col3:
            financial_yes = len(df[df['financial_challenges'] == 'Yes'])
            st.metric("Financial Challenges", financial_yes)
        with col4:
            academic_yes = len(df[df['academic_challenges'] == 'Yes'])
            st.metric("Academic Challenges", academic_yes)
        
        st.divider()
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Satisfaction Distribution
            st.subheader("Overall Satisfaction Distribution")
            sat_counts = df['satisfaction'].value_counts().sort_index()
            sat_labels = {1: "Very Dissatisfied", 2: "Dissatisfied", 3: "Neutral", 
                         4: "Satisfied", 5: "Very Satisfied"}
            fig = px.bar(x=[sat_labels[i] for i in sat_counts.index], 
                        y=sat_counts.values,
                        labels={'x': 'Satisfaction Level', 'y': 'Count'},
                        color=sat_counts.values,
                        color_continuous_scale='Blues')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Financial Challenges
            st.subheader("Financial Challenges")
            fin_counts = df['financial_challenges'].value_counts()
            fig = px.pie(values=fin_counts.values, names=fin_counts.index,
                        color_discrete_sequence=['#ef4444', '#10b981'])
            st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Academic Challenges
            st.subheader("Academic Challenges")
            acad_counts = df['academic_challenges'].value_counts()
            fig = px.pie(values=acad_counts.values, names=acad_counts.index,
                        color_discrete_sequence=['#f59e0b', '#10b981'])
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Support Gaps
            st.subheader("Top Support Gaps")
            all_gaps = []
            for gaps in df['support_gaps']:
                if isinstance(gaps, list):
                    all_gaps.extend(gaps)
            if all_gaps:
                gap_counts = pd.Series(all_gaps).value_counts().head(8)
                fig = px.bar(x=gap_counts.values, y=gap_counts.index, orientation='h',
                           labels={'x': 'Count', 'y': 'Support Area'},
                           color=gap_counts.values,
                           color_continuous_scale='Purples')
                fig.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig, use_container_width=True)
        
        # Retreat Priorities
        st.subheader("Retreat Priorities")
        all_priorities = []
        for priorities in df['retreat_priorities']:
            if isinstance(priorities, list):
                all_priorities.extend(priorities)
        if all_priorities:
            priority_counts = pd.Series(all_priorities).value_counts()
            fig = px.bar(x=priority_counts.values, y=priority_counts.index, orientation='h',
                       labels={'x': 'Count', 'y': 'Priority'},
                       color=priority_counts.values,
                       color_continuous_scale='Teal')
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        
        # Key Insights
        st.divider()
        st.subheader("🎯 Key Insights & Recommendations")
        
        if avg_sat < 3:
            st.error("**Low Satisfaction Alert:** Average satisfaction is below 3. Consider prioritizing team morale and addressing concerns in the retreat.")
        
        if financial_yes > len(df) * 0.3:
            st.warning("**Financial Support Needed:** Over 30% of Council members report financial challenges. Consider discussing stipends, transportation support, or flexible scheduling.")
        
        if academic_yes > len(df) * 0.3:
            st.warning("**Academic Balance Concerns:** Significant academic challenges reported. Include time management training and consider lighter Council commitments during exam periods.")
        
        if all_priorities:
            top_3 = priority_counts.head(3)
            st.info(f"**Retreat Focus Areas:** Most requested priorities are: {', '.join(top_3.index)}. Plan retreat sessions accordingly.")

# ============ ADMIN PAGE ============
elif page == "🔐 Admin":
    st.markdown('<div class="main-header">Admin Panel</div>', unsafe_allow_html=True)
    
    if not st.session_state.admin_logged_in:
        st.subheader("Admin Login")
        password = st.text_input("Enter admin password", type="password")
        if st.button("Login"):
            if password == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Incorrect password")
    else:
        st.success("✅ Logged in as Admin")
        
        # Refresh from Sheets if enabled
        if USE_GOOGLE_SHEETS:
            if st.button("🔄 Sync with Google Sheets"):
                st.session_state.responses = load_from_sheets()
                st.success("Synced with Google Sheets!")
                st.rerun()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Responses", len(st.session_state.responses))
        with col2:
            if st.session_state.responses:
                latest = datetime.fromisoformat(st.session_state.responses[-1]['timestamp'])
                st.metric("Latest Response", latest.strftime("%Y-%m-%d %H:%M"))
        with col3:
            if st.button("🚪 Logout"):
                st.session_state.admin_logged_in = False
                st.rerun()
        
        st.divider()
        
        # Download Data
        st.subheader("📥 Download Data")
        if st.session_state.responses:
            json_data = json.dumps(st.session_state.responses, indent=2)
            st.download_button(
                label="Download as JSON",
                data=json_data,
                file_name=f"retreat-responses-{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
            
            # Also offer CSV download
            df = pd.DataFrame(st.session_state.responses)
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name=f"retreat-responses-{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No responses to download yet.")
        
        st.divider()
        
        # View Responses
        st.subheader("📋 View Responses")
        if st.session_state.responses:
            df = pd.DataFrame(st.session_state.responses)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No responses yet.")
        
        st.divider()
        
        # Clear Data
        st.subheader("🗑️ Clear All Data")
        st.warning("⚠️ This action cannot be undone!")
        if st.button("Clear All Responses", type="primary"):
            if st.checkbox("I understand this will delete all data"):
                st.session_state.responses = []
                st.success("All responses cleared!")
                st.rerun()
