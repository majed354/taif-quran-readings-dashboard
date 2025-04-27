import streamlit as st
import pandas as pd
import requests
import base64
import io
import uuid
from datetime import datetime
import traceback
import time
import json
import os
# Import Github class safely
try:
    from github import Github
except ImportError:
    st.error("مكتبة PyGithub غير مثبتة. يرجى تثبيتها: pip install PyGithub")
    st.stop()


# -------------------------------------------------------------------------
# قائمة أسماء الأعضاء (List of Member Names)
# -------------------------------------------------------------------------
# تم استخلاص الأسماء من البيانات المقدمة
MEMBER_NAMES = [
    "— اختر اسم العضو —", # Placeholder option
    "عبد الله حماد حميد القرشي",
    "ناصر سعود حمود القثامي",
    "حاتم عابد عبد الله القرشي",
    "ماجد عبد العزيز الحارثي",
    "رجاء محمد هوساوي",
    "عبد الله عيدان الزهراني",
    "منال منصور محمد القرشي",
    "خلود شاكر فهيد العبدلي",
    "عبد العزيز عيضه حربي الحارثي",
    "عبد العزيز عواض الثبيتي",
    "تهاني فيصل علي الحربي",
    "آمنة جمعة سعيد أحمد قحاف",
    "غدير محمد سليم الشريف",
    "أسرار عايف سراج الخالدي",
    "سلوى أحمد محمد الحارثي",
    "هويدا أبو بكر سعيد الخطيب",
    "تغريد أبو بكر سعيد الخطيب",
    "مهدي عبد الله قاري",
    "مها عيفان نوار الخليدي",
    "سلمى معيوض زويد الجميعي",
    "أسماء محمد السلومي",
    "رائد محمد عوضه الغامدي",
    "ماجد إبراهيم باقي الجهني",
    "مرام طلعت محمد أمين ينكصار",
    "سعود سعد محمد الأنصاري",
    "عبد الرحمن محمد العبيسي",
    "ولاء حسن مسلم المذكوري",
    "إسراء عبد الغني سندي",
    "وسام حسن مسلم المذكوري",
    "سمر علي محمد الشهراني",
    "فاطمه أبكر داوود أبكر",
    "شيماء محمود صالح بركات",
    "عبد الله سعد عويض الثبيتي",
    "عايده مصلح صالح المالكي",
    "أفنان عبد الله محمد السليماني",
    "أفنان مستور علي السواط"
]

# -------------------------------------------------------------------------
# الفئات (Categories)
# -------------------------------------------------------------------------
CATEGORIES = {
    "CURR": "تطوير المناهج",
    "TEAC": "التعليم والتقويم",
    "QUAL": "الاعتماد والجودة",
    "RESR": "بحث علمي ونشر",
    "EVNT": "فعاليات وخدمة مجتمع",
    "STUD": "دعم وخدمات طلابية",
    "ADMN": "مهام إدارية",
    "PDVL": "تطوير مهني"
}

# -------------------------------------------------------------------------
# تهيئة الواجهة (UI Initialization)
# -------------------------------------------------------------------------
# تم تغيير العنوان هنا
st.set_page_config("تسجيل المهام المكتملة", layout="centered")

# CSS للواجهة العربية (CSS for Arabic UI)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');

    * {
        font-family: 'Tajawal', sans-serif !important;
    }
    body, .stApp {
        direction: rtl;
        text-align: right;
    }
    /* Ensure input fields and buttons also align text to the right */
    button, input, select, textarea, .stTextInput>div>div>input, .stTextArea>div>textarea, .stSelectbox>div>div>select {
        text-align: right !important;
        direction: rtl !important;
    }
    /* Ensure selectbox options are right-aligned */
     .stSelectbox [data-baseweb="select"] > div {
         text-align: right;
     }
    .stTabs [data-baseweb="tab-list"] {
        direction: rtl;
    }
    h1, h2, h3, h4, h5, h6 {
        text-align: right;
    }
    .stButton>button {
        background-color: #1e88e5;
        color: white;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 600;
        border: none; /* Remove default border */
    }
    .stButton>button:hover {
        background-color: #1565c0;
    }
    /* Fix for Streamlit > 1.25 selectbox alignment */
    div[data-baseweb="select"] > div:nth-child(1) {
        text-align: right;
    }
    /* Ensure placeholder text is also right-aligned */
     div[data-baseweb="input"] input::placeholder, div[data-baseweb="textarea"] textarea::placeholder {
        text-align: right !important;
    }
    /* Ensure delete button icon is centered */
    .stButton>button[help="حذف هذا الإنجاز"] {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 4px; /* Adjust padding if needed */
        line-height: 1; /* Ensure icon is vertically centered */
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# معالجة الأخطاء (Error Handling)
# -------------------------------------------------------------------------
def show_error(error_msg, details=None):
    """Displays an error message and optional details."""
    st.error(f"حدث خطأ: {error_msg}")
    if details:
        with st.expander("تفاصيل الخطأ (للمطورين)"):
            st.code(details)

# -------------------------------------------------------------------------
# التحقق من المتغيرات المطلوبة (Check Required Environment Variables)
# -------------------------------------------------------------------------
def check_environment():
    """Checks if necessary secrets are set."""
    try:
        required_vars = ["GITHUB_TOKEN", "REPO_NAME", "MASTER_PASS", "DEESEEK_KEY"]
        missing_vars = [var for var in required_vars if var not in st.secrets]

        if missing_vars:
            show_error(
                f"بعض المتغيرات المطلوبة غير موجودة في ملف الأسرار: {', '.join(missing_vars)}",
                "يجب إضافة هذه المتغيرات إلى ملف .streamlit/secrets.toml"
            )
            return False
        return True
    except Exception as e:
        show_error("خطأ في التحقق من المتغيرات البيئية", traceback.format_exc())
        return False

# -------------------------------------------------------------------------
# أدوات GitHub (GitHub Utilities)
# -------------------------------------------------------------------------
@st.cache_resource(ttl=3600) # Cache the repo object for an hour
def get_gh_repo():
    """Connects to the GitHub repository specified in secrets."""
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        return g.get_repo(st.secrets["REPO_NAME"])
    except Exception as e:
        show_error("خطأ في الاتصال بمستودع GitHub", traceback.format_exc())
        return None

def load_csv(path: str):
    """Loads a CSV file from the GitHub repo."""
    repo = get_gh_repo()
    if not repo:
        return pd.DataFrame(), None  # Return empty DataFrame if repo connection failed

    try:
        file_content = repo.get_contents(path)
        content_decoded = base64.b64decode(file_content.content).decode("utf-8-sig")
        # Use StringIO to read the string data as a file
        df = pd.read_csv(io.StringIO(content_decoded))
        return df, file_content.sha
    except Exception as e:
        # Differentiate between file not found and other errors
        if "Not Found" in str(e):
             st.warning(f"لم يتم العثور على الملف: {path} - سيتم إنشاؤه عند الحفظ.")
        else:
            show_error(f"خطأ في تحميل الملف: {path}", traceback.format_exc())
        return pd.DataFrame(), None # Return empty DataFrame if file not found or error

def save_csv(path: str, df: pd.DataFrame, sha: str | None, msg: str):
    """Saves a DataFrame to a CSV file in the GitHub repo."""
    repo = get_gh_repo()
    if not repo:
        return False

    try:
        # Convert DataFrame to CSV string
        content = df.to_csv(index=False, line_terminator="\n", encoding="utf-8-sig")

        # Check if the file exists to decide between update and create
        try:
            # Try to get the file to check existence and get current SHA if not provided
            existing_file = repo.get_contents(path)
            current_sha = existing_file.sha if sha is None else sha
            # Update the file
            repo.update_file(path, msg, content, current_sha)
            st.cache_resource.clear() # Clear resource cache after update
            return True
        except Exception as e: # Primarily github.UnknownObjectException if not found
             if "Not Found" in str(e) or sha is None:
                # File doesn't exist or SHA wasn't provided (implying creation)
                # Ensure parent directory exists (optional, GitHub usually handles this)
                folder_path = os.path.dirname(path)
                if folder_path: # Check if there's actually a folder path
                    # This part is complex and might fail with nested non-existent folders.
                    # Consider simplifying or ensuring folders are pre-created.
                    # A simpler approach is to just try creating the file.
                    pass # Let create_file handle it, might need manual folder creation if deep

                # Create the file
                repo.create_file(path, msg, content)
                st.cache_resource.clear() # Clear resource cache after creation
                return True
             else:
                 # Another error occurred during get_contents or update_file
                 raise e # Re-raise the exception to be caught by the outer try-except

    except Exception as e:
        show_error(f"خطأ في حفظ الملف: {path}", traceback.format_exc())
        return False


def year_path(y: int):
    """Generates the file path for a given year's achievements."""
    return f"data/department/{y}/achievements_{y}.csv"

# -------------------------------------------------------------------------
# تصنيف المهام (Fallback Classification)
# -------------------------------------------------------------------------
def fallback_classification(text: str) -> dict:
    """Simple keyword-based classification if DeepSeek fails."""
    text_lower = text.lower() # Convert to lowercase for case-insensitive matching
    category_code = "PDVL" # Default: Professional Development

    # Define keywords for each category
    keywords = {
        "RESR": ["بحث", "نشر", "مقالة", "مؤتمر", "مجلة", "research", "publish", "paper", "conference", "journal"],
        "CURR": ["مقرر", "منهج", "تطوير", "مادة", "course", "curriculum", "develop", "material"],
        "TEAC": ["تعليم", "تدريس", "محاضر", "تقويم", "teach", "lecture", "assessment", "grading"],
        "QUAL": ["جودة", "اعتماد", "تقييم", "quality", "accreditation", "evaluation"],
        "EVNT": ["خدمة", "مجتمع", "فعالية", "نشاط", "ورشة", "service", "community", "event", "activity", "workshop"],
        "STUD": ["طلاب", "طالب", "إرشاد", "student", "guidance", "advising"],
        "ADMN": ["إدارة", "لجنة", "اجتماع", "admin", "committee", "meeting"]
    }

    # Find the best matching category
    for code, words in keywords.items():
        if any(word in text_lower for word in words):
            category_code = code
            break # Stop after first match

    # Estimate points and hours based on text length
    word_count = len(text.split())
    # Simple estimation: 1 hour per 10 words, capped between 1 and 30
    virtual_hours = max(1, min(30, word_count // 10 if word_count > 10 else 1)) # Ensure at least 1 hour
    points = virtual_hours * 2 # Points are roughly double the hours

    return {
        "points": points,
        "virtual_hours": virtual_hours,
        "category_code": category_code,
        "category_label": CATEGORIES.get(category_code, "غير مصنف") # Use .get for safety
    }

# -------------------------------------------------------------------------
# DeepSeek (Classification + Points)
# -------------------------------------------------------------------------
def deepseek_eval(text: str) -> dict:
    """Evaluates achievement text using DeepSeek API."""
    # Check if DEESEEK_KEY exists and is not empty
    if not st.secrets.get("DEESEEK_KEY"):
        st.warning("مفتاح DeepSeek API غير موجود أو فارغ في الأسرار. استخدام التصنيف الاحتياطي.")
        return fallback_classification(text)

    try:
        # Construct the prompt for DeepSeek API
        system_prompt = (
            "أنت مساعد يقيّم إنجازات أكاديمية لعضو هيئة تدريس جامعي. "
            "بناءً على وصف الإنجاز المقدم، قم بـ:\n"
            "1. تقدير عدد 'النقاط' المستحقة (بين 1 و 100) بناءً على أهمية وتعقيد الإنجاز.\n"
            "2. تقدير عدد 'الساعات الافتراضية' المستغرقة (بين 1 و 50) بناءً على الجهد المتوقع.\n"
            "3. اختر 'رمز الفئة' (category_code) الأنسب من القائمة.\n"
            "4. أعد 'اسم الفئة' (category_label) المقابل للرمز.\n"
            "قائمة الفئات المتاحة:\n"
            + "\n".join([f"- {k}: {v}" for k, v in CATEGORIES.items()]) + "\n"
            "أعد النتيجة فقط بصيغة JSON تحتوي على الحقول الأربعة المطلوبة: "
            "points (integer), virtual_hours (integer), category_code (string), category_label (string)."
        )

        prompt_data = {
            "model": "deepseek-chat", # Use the appropriate model
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"وصف الإنجاز: {text}"}
            ],
             # Use function calling for structured output
            "tool_choice": {"type": "function", "function": {"name": "score_achievement"}},
            "tools": [{
                "type": "function",
                "function": {
                    "name": "score_achievement",
                    "description": "تحديد النقاط والساعات والفئة للإنجاز الأكاديمي",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "points": {"type": "integer", "description": "النقاط المقدرة (1-100)"},
                            "virtual_hours": {"type": "integer", "description": "الساعات الافتراضية المقدرة (1-50)"},
                            "category_code": {"type": "string", "enum": list(CATEGORIES.keys()), "description": "رمز الفئة من القائمة"},
                            "category_label": {"type": "string", "description": "اسم الفئة المقابل للرمز"}
                        },
                        "required": ["points", "virtual_hours", "category_code", "category_label"]
                    }
                }
            }]
        }

        # Make the API request
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {st.secrets['DEESEEK_KEY']}",
                "Content-Type": "application/json"
            },
            json=prompt_data,
            timeout=30 # Increased timeout
        )
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        result_json = response.json()

        # Extract function call arguments
        if result_json.get("choices") and result_json["choices"][0].get("message", {}).get("tool_calls"):
            tool_call = result_json["choices"][0]["message"]["tool_calls"][0]
            if tool_call["function"]["name"] == "score_achievement":
                arguments = json.loads(tool_call["function"]["arguments"])
                # Validate category code and label
                if arguments.get("category_code") in CATEGORIES:
                    arguments["category_label"] = CATEGORIES[arguments["category_code"]] # Ensure label matches code
                    # Ensure points and hours are within reasonable bounds
                    arguments["points"] = max(1, min(100, arguments.get("points", 1)))
                    arguments["virtual_hours"] = max(1, min(50, arguments.get("virtual_hours", 1)))
                    return arguments
                else:
                    st.warning(f"DeepSeek أعاد رمز فئة غير صالح: {arguments.get('category_code')}. استخدام التصنيف الاحتياطي.")
                    return fallback_classification(text) # Fallback if category is wrong
            else:
                 st.warning("DeepSeek لم يستدعِ الدالة المطلوبة. استخدام التصنيف الاحتياطي.")
                 return fallback_classification(text)
        else:
            st.warning("لم يتم العثور على استدعاء الدالة في استجابة DeepSeek. استخدام التصنيف الاحتياطي.")
            # Log the actual response for debugging
            st.write("DeepSeek Response:", result_json)
            return fallback_classification(text)

    except requests.exceptions.RequestException as e:
        st.warning(f"فشل في استدعاء DeepSeek API (خطأ شبكة/طلب): {e}. استخدام التصنيف الاحتياطي.")
        return fallback_classification(text)
    except (json.JSONDecodeError, KeyError, IndexError, Exception) as e:
        st.warning(f"خطأ في معالجة استجابة DeepSeek أو خطأ غير متوقع: {e}. استخدام التصنيف الاحتياطي.")
        # Log details if possible
        try:
            st.write("DeepSeek Response on Error:", response.text)
        except NameError: # If response object doesn't exist
            pass
        print(traceback.format_exc()) # Print traceback to console/logs
        return fallback_classification(text)

# -------------------------------------------------------------------------
# الصفحة الرئيسية (Main Page Logic)
# -------------------------------------------------------------------------

# Initialize session state for authentication and user selection
if "auth" not in st.session_state:
    st.session_state.auth = False
if "selected_member" not in st.session_state:
    st.session_state.selected_member = MEMBER_NAMES[0] # Default to placeholder
if "selected_year" not in st.session_state:
    st.session_state.selected_year = datetime.now().year

# --- Environment Check ---
if not check_environment():
    st.warning("يرجى إصلاح مشكلات الإعداد قبل المتابعة.")
    st.stop()

# --- Login Form ---
if not st.session_state.auth:
    st.title("تسجيل الدخول") # Changed Login Title
    with st.form("login_form"):
        entered_pass = st.text_input("كلمة المرور العامة", type="password", key="password_input")
        login_button = st.form_submit_button("دخول")

        if login_button:
            if entered_pass == st.secrets["MASTER_PASS"]:
                st.session_state.auth = True
                st.success("تم تسجيل الدخول بنجاح!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("كلمة المرور غير صحيحة!")
    st.stop() # Stop execution if not authenticated

# --- Main Application (After Login) ---
# تم تغيير العنوان الرئيسي هنا
st.title("تسجيل المهام المكتملة")

# --- User Data Input (Sidebar) ---
with st.sidebar:
    st.header("بيانات المستخدم والسنة")
    # Use session state to preserve selections across reruns
    # Replaced text_input with selectbox for member name
    st.session_state.selected_member = st.selectbox(
        "اختر اسم العضو",
        options=MEMBER_NAMES,
        index=MEMBER_NAMES.index(st.session_state.selected_member) if st.session_state.selected_member in MEMBER_NAMES else 0, # Keep selection
        key="member_name_selector"
    )
    st.session_state.selected_year = st.number_input(
        "اختر السنة",
        min_value=2010,
        max_value=datetime.now().year + 1, # Allow next year potentially
        value=st.session_state.selected_year,
        step=1,
        key="year_input"
    )

    if st.button("تسجيل الخروج"):
        # Clear sensitive session state on logout
        st.session_state.auth = False
        st.session_state.selected_member = MEMBER_NAMES[0] # Reset to placeholder
        # Optionally reset year or keep it
        st.rerun()

# --- Validate User Input ---
# Get selected member name, ensure it's not the placeholder
member = st.session_state.selected_member
year = st.session_state.selected_year

if member == MEMBER_NAMES[0]: # Check if placeholder is selected
    st.info("👈 الرجاء اختيار اسم العضو من القائمة المنسدلة في الشريط الجانبي للمتابعة.")
    st.stop()

# --- Load/Manage Main Tasks ---
st.header("1. اختيار المهمة الرئيسية")
try:
    main_tasks_path = "data/main_tasks.csv"
    main_df, main_sha = load_csv(main_tasks_path)

    # Initialize DataFrame if it's empty or doesn't exist yet
    if main_df.empty:
        main_df = pd.DataFrame(columns=["id", "title", "descr"])
        main_sha = None # Ensure SHA is None if creating the file

    # Get list of titles, ensure 'title' column exists
    titles = main_df["title"].tolist() if "title" in main_df.columns else []
    options = ["— اختر المهمة الرئيسية —"] + sorted(titles) + ["➕ إضافة مهمة رئيسية…"] # Sort titles

    # Use session state for the selectbox choice if needed, or a simple variable
    selected_main_task = st.selectbox(
        "المهمة الرئيسية",
        options,
        key="main_task_selector"
    )

    main_id = None # Initialize main_id

    if selected_main_task == "➕ إضافة مهمة رئيسية…":
        st.subheader("إضافة مهمة رئيسية جديدة")
        with st.form("add_main_task_form"):
            new_title = st.text_input("عنوان المهمة الرئيسية الجديدة")
            new_descr = st.text_area("وصف مختصر للمهمة (اختياري)")
            submitted = st.form_submit_button("حفظ المهمة الرئيسية")
            if submitted:
                if not new_title.strip():
                    st.error("عنوان المهمة الرئيسية مطلوب.")
                elif new_title in titles:
                     st.error("هذه المهمة الرئيسية موجودة بالفعل.")
                else:
                    new_id = str(uuid.uuid4())[:8] # Generate unique ID
                    # Append new task using pd.concat
                    new_row = pd.DataFrame([{"id": new_id, "title": new_title, "descr": new_descr}])
                    main_df = pd.concat([main_df, new_row], ignore_index=True)

                    if save_csv(main_tasks_path, main_df, main_sha, f"إضافة مهمة رئيسية: {new_title}"):
                        st.success(f"تمت إضافة المهمة الرئيسية '{new_title}' بنجاح.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("حدث خطأ أثناء حفظ المهمة الرئيسية.")
                        # Optionally revert dataframe change if save fails
                        main_df = main_df.iloc[:-1] # Use iloc for positional slicing

    elif selected_main_task.startswith("—"):
        st.warning("الرجاء اختيار مهمة رئيسية من القائمة أعلاه أو إضافة مهمة جديدة.")
        st.stop()
    else:
        # Find the ID of the selected task
        # Ensure 'id' and 'title' columns exist before accessing
        if "id" in main_df.columns and "title" in main_df.columns:
            task_row = main_df[main_df["title"] == selected_main_task]
            if not task_row.empty:
                main_id = task_row["id"].iloc[0]
            else:
                st.error("لم يتم العثور على معرف المهمة المحددة. حاول تحديث الصفحة.")
                st.stop()
        else:
             st.error("خطأ في هيكل ملف المهام الرئيسية (الأعمدة غير موجودة).")
             st.stop()

except Exception as e:
    show_error("خطأ في تحميل أو إدارة المهام الرئيسية", traceback.format_exc())
    st.stop() # Stop if main tasks cannot be loaded/managed

# --- Load and Display Member's Achievements for the Year ---
st.header(f"2. عرض وإضافة إنجازاتك لعام {year}")

# Only proceed if a main task has been selected
if main_id is None and selected_main_task != "➕ إضافة مهمة رئيسية…":
     st.warning("الرجاء اختيار مهمة رئيسية للمتابعة.")
     st.stop()
elif main_id is None: # Case where user is adding a main task
     st.info("أضف المهمة الرئيسية أولاً، ثم ستتمكن من إضافة إنجازات فرعية لها.")
     st.stop()


current_year_path = year_path(year)
try:
    achievements_df, achievements_sha = load_csv(current_year_path)

    # Define expected columns
    expected_cols = ["العضو", "الإنجاز", "التاريخ", "النقاط", "الفئة", "الساعات الافتراضية", "main_id"]

    # Initialize DataFrame if empty or doesn't exist, ensuring columns
    if achievements_df.empty:
        achievements_df = pd.DataFrame(columns=expected_cols)
        achievements_sha = None # Ensure SHA is None for creation
    else:
        # Ensure all expected columns exist, add if missing
        for col in expected_cols:
            if col not in achievements_df.columns:
                achievements_df[col] = None # Add missing column with None values
                st.warning(f"تمت إضافة العمود المفقود '{col}' إلى ملف الإنجازات.")
                achievements_sha = None # Force recreation/update if structure changed


    # Filter tasks for the current member and selected main task
    # Ensure 'العضو' and 'main_id' columns exist (checked above)
    my_tasks_df = achievements_df[
        (achievements_df["العضو"] == member) &
        (achievements_df["main_id"] == main_id)
    ].copy() # Use .copy() to avoid SettingWithCopyWarning

    # Convert 'التاريخ' to datetime for sorting, handle potential errors
    if 'التاريخ' in my_tasks_df.columns:
        my_tasks_df['التاريخ'] = pd.to_datetime(my_tasks_df['التاريخ'], errors='coerce')
        my_tasks_df = my_tasks_df.sort_values(by='التاريخ', ascending=False).reset_index() # Keep original index
    else:
        st.warning("عمود 'التاريخ' غير موجود، لا يمكن الفرز حسب التاريخ.")
        my_tasks_df = my_tasks_df.reset_index() # Keep original index


    st.subheader(f"الإنجازات المضافة تحت '{selected_main_task}' في {year}")
    if my_tasks_df.empty:
        st.caption("لا توجد إنجازات مضافة لهذه المهمة الرئيسية في هذه السنة حتى الآن.")
    else:
        # Display tasks with delete buttons
        for i in my_tasks_df.index: # Iterate using the new index (0, 1, 2...)
            original_df_index = my_tasks_df.loc[i, 'index'] # Get the original index from the reset_index operation

            col1, col2 = st.columns([0.9, 0.1]) # Adjust column ratio
            with col1:
                # Safely access columns using .get() with default values
                achievement_desc = my_tasks_df.loc[i].get('الإنجاز', "لا يوجد وصف")
                achievement_date_dt = my_tasks_df.loc[i].get('التاريخ')
                # Format date nicely if it's a valid datetime object
                achievement_date_str = achievement_date_dt.strftime('%Y-%m-%d') if pd.notna(achievement_date_dt) else "تاريخ غير معروف"

                points = my_tasks_df.loc[i].get('النقاط', 'N/A')
                hours = my_tasks_df.loc[i].get('الساعات الافتراضية', 'N/A')
                category = my_tasks_df.loc[i].get('الفئة', 'N/A')

                st.markdown(f"**{achievement_desc}**")
                st.caption(f"التاريخ: {achievement_date_str} | الفئة: {category} | النقاط: {points} | الساعات: {hours}")

            with col2:
                 # Use the original DataFrame index for the delete button key and logic
                delete_key = f"del-{original_df_index}" # Use original index in key
                if st.button("🗑️", key=delete_key, help="حذف هذا الإنجاز"):
                    # Verify the index still exists in the main DataFrame before dropping
                    if original_df_index in achievements_df.index:
                        achievement_to_delete = achievements_df.loc[original_df_index, 'الإنجاز'] # Get desc for message

                        # Drop the row from the main DataFrame using the original index
                        achievements_df_updated = achievements_df.drop(index=original_df_index).reset_index(drop=True)

                        if save_csv(current_year_path, achievements_df_updated, achievements_sha, f"حذف إنجاز '{achievement_to_delete}' بواسطة {member}"):
                            st.success("تم حذف الإنجاز بنجاح.")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("حدث خطأ أثناء حذف الإنجاز.")
                    else:
                        st.error("لم يتم العثور على الإنجاز المراد حذفه (قد يكون تم حذفه بالفعل). الرجاء تحديث الصفحة.")


except Exception as e:
    show_error("خطأ في تحميل أو عرض الإنجازات", traceback.format_exc())

# --- Form for Adding New Achievement ---
st.markdown("---")
st.subheader("3. إضافة إنجاز فرعي جديد") # Added step number

with st.form("add_achievement_form", clear_on_submit=True):
    achievement_date = st.date_input("تاريخ الإنجاز", value=datetime.now()) # Default to today
    achievement_desc = st.text_area("وصف الإنجاز بالتفصيل", height=150, key="achievement_desc_input")
    submit_achievement = st.form_submit_button("➕ إضافة وحفظ الإنجاز")

    if submit_achievement:
        if not achievement_desc.strip():
            st.error("وصف الإنجاز مطلوب.")
        elif main_id is None:
             st.error("خطأ: لم يتم تحديد المهمة الرئيسية. الرجاء اختيار واحدة أولاً.") # Should be caught earlier
        else:
            with st.spinner("⏳ جاري تقييم الإنجاز وحفظه..."):
                try:
                    # Evaluate using DeepSeek or fallback
                    evaluation = deepseek_eval(achievement_desc)

                    # Create the new row data
                    new_achievement_row = pd.Series({
                        "العضو": member,
                        "الإنجاز": achievement_desc.strip(),
                        "التاريخ": achievement_date.isoformat(), # Store as ISO string
                        "النقاط": evaluation.get("points", 0),
                        "الفئة": evaluation.get("category_label", "غير مصنف"),
                        "الساعات الافتراضية": evaluation.get("virtual_hours", 0),
                        "main_id": main_id
                    })

                    # Append the new row using pd.concat
                    # Ensure achievements_df has the correct columns before concat
                    for col in expected_cols:
                        if col not in achievements_df.columns:
                             achievements_df[col] = None # Add if missing

                    achievements_df_updated = pd.concat(
                        [achievements_df, pd.DataFrame([new_achievement_row])],
                        ignore_index=True
                    )
                    # Ensure dtypes are consistent if possible (optional, pandas might handle)
                    # achievements_df_updated = achievements_df_updated.astype(achievements_df.dtypes)


                    # Save the updated DataFrame
                    commit_message = f"إضافة إنجاز بواسطة {member} ({achievement_date.isoformat()}): {evaluation.get('category_label')}"
                    if save_csv(current_year_path, achievements_df_updated, achievements_sha, commit_message):
                        st.success(
                            f"✅ تمت إضافة الإنجاز بنجاح! "
                            f"(التقييم: {evaluation.get('points', 'N/A')} نقطة، "
                            f"{evaluation.get('virtual_hours', 'N/A')} ساعة، "
                            f"الفئة: {evaluation.get('category_label', 'N/A')})"
                        )
                        time.sleep(2) # Slightly longer sleep to read success message
                        st.rerun()
                    else:
                        st.error("❌ حدث خطأ أثناء حفظ الإنجاز.")

                except Exception as e:
                    show_error("خطأ في إضافة الإنجاز", traceback.format_exc())

