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

# Simple test element added here
st.title("صفحة اختبار")
st.write("إذا رأيت هذه الرسالة، فإن التطبيق يعمل بشكل أساسي.")

# -------------------------------------------------------------------------
# الفئات
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
# تهيئة الواجهة -----------------------------------------------------------
# Note: st.set_page_config must be the first Streamlit command.
# Moved the test title after set_page_config.
st.set_page_config("لوحة الإنجازات", layout="centered")

# Re-add the test elements after set_page_config
st.title("صفحة اختبار")
st.write("إذا رأيت هذه الرسالة، فإن التطبيق يعمل بشكل أساسي.")


# CSS للواجهة العربية
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
    button, input, select, textarea {
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
    }
    .stButton>button:hover {
        background-color: #1565c0;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# معالجة الأخطاء ---------------------------------------------------------
def show_error(error_msg, details=None):
    st.error(f"حدث خطأ: {error_msg}")
    if details:
        with st.expander("تفاصيل الخطأ (للمطورين)"):
            st.code(details)

# -------------------------------------------------------------------------
# التحقق من المتغيرات المطلوبة --------------------------------------------
def check_environment():
    try:
        # تحقق من وجود المتغيرات الضرورية
        required_vars = ["GITHUB_TOKEN", "REPO_NAME", "MASTER_PASS", "DEESEEK_KEY"]
        missing_vars = []

        for var in required_vars:
            # Check if secrets are loaded and the variable exists
            if not hasattr(st, 'secrets') or var not in st.secrets:
                 missing_vars.append(var)

        if missing_vars:
            show_error(
                f"بعض المتغيرات المطلوبة غير موجودة في ملف الأسرار: {', '.join(missing_vars)}",
                "يجب إضافة هذه المتغيرات إلى ملف .streamlit/secrets.toml أو تكوينها كأسرار في بيئة النشر."
            )
            return False
        return True
    except Exception as e:
        show_error("خطأ في التحقق من المتغيرات البيئية", traceback.format_exc()) # Use traceback for more details
        return False

# -------------------------------------------------------------------------
# أدوات GitHub ------------------------------------------------------------
@st.cache_resource(ttl=3600) # Cache the GitHub connection for an hour
def get_github_instance():
    """Initializes and returns the GitHub instance."""
    try:
        from github import Github, Auth
        # Use Auth.Token for explicit token authentication
        auth = Auth.Token(st.secrets["GITHUB_TOKEN"])
        return Github(auth=auth)
    except ImportError:
        st.error("مكتبة PyGithub غير مثبتة. يرجى تثبيتها: pip install PyGithub")
        return None
    except Exception as e:
        show_error("خطأ في تهيئة اتصال GitHub", traceback.format_exc())
        return None

@st.cache_data(ttl=600) # Cache repository object for 10 minutes
def gh_repo(_gh_instance):
    """Gets the repository object using a cached GitHub instance."""
    if not _gh_instance:
        return None
    try:
        return _gh_instance.get_repo(st.secrets["REPO_NAME"])
    except Exception as e:
        # Reset specific caches if repo access fails
        st.cache_data.clear()
        show_error("خطأ في الوصول إلى مستودع GitHub المحدد", traceback.format_exc())
        return None

# Pass the GitHub instance to functions that need it
def load_csv(path: str, _repo):
    """Loads a CSV file from the GitHub repository."""
    if not _repo:
        return pd.DataFrame(), None
    try:
        file = _repo.get_contents(path)
        # Ensure content is treated as bytes before decoding
        content_bytes = base64.b64decode(file.content)
        data = content_bytes.decode("utf-8-sig") # Use utf-8-sig to handle BOM
        return pd.read_csv(io.StringIO(data)), file.sha
    except Exception as e: # Catch specific GithubException for 'Not Found'
        from github import UnknownObjectException
        if isinstance(e, UnknownObjectException):
             st.warning(f"لم يتم العثور على الملف: {path} - سيتم إنشاؤه عند الحفظ.")
             return pd.DataFrame(), None # Return empty DataFrame and None sha
        else:
             show_error(f"خطأ في تحميل الملف: {path}", traceback.format_exc())
             # Clear cache on error to force reload next time
             st.cache_data.clear()
             return pd.DataFrame(), None


def save_csv(path: str, df: pd.DataFrame, sha: str | None, msg: str, _repo):
    """Saves a DataFrame to a CSV file in the GitHub repository."""
    if not _repo:
        return False
    try:
        # Ensure line terminator is \n for consistency
        content = df.to_csv(index=False, line_terminator="\n", encoding="utf-8-sig") # Use utf-8-sig

        # Check if the file exists before trying to update
        file_exists = True
        try:
            # If sha is not provided, try to get the current file to check existence and get sha
            if not sha:
                current_file = _repo.get_contents(path)
                sha = current_file.sha
        except Exception: # Specifically catch UnknownObjectException if possible
             from github import UnknownObjectException
             # If getting contents fails, assume file doesn't exist
             file_exists = False
             sha = None # Ensure sha is None if file doesn't exist


        if file_exists and sha:
             _repo.update_file(path, msg, content, sha)
             st.success(f"تم تحديث الملف: {path}")
        else:
             # Create the file if it doesn't exist
             _repo.create_file(path, msg, content)
             st.success(f"تم إنشاء الملف: {path}")

        # Clear relevant caches after successful save
        st.cache_data.clear()
        # Optionally clear resource cache if repo structure might change significantly
        # st.cache_resource.clear()
        return True

    except Exception as e:
        show_error(f"خطأ في حفظ الملف: {path}", traceback.format_exc())
        return False


def year_path(y:int):         # مسار ملف الإنجازات للسنة
    # Use os.path.join for cross-platform compatibility, though GitHub uses forward slashes
    return f"data/department/{y}/achievements_{y}.csv"

# -------------------------------------------------------------------------
# تصنيف المهام (وظيفة احتياطية في حالة فشل DeepSeek) ----------------------
def fallback_classification(text:str)->dict:
    # تصنيف بسيط بناءً على الكلمات المفتاحية
    text_lower = text.lower() # Convert to lowercase for case-insensitive matching
    category_code = "PDVL" # Default category

    # Define keywords for each category
    keywords = {
        "RESR": ["بحث", "نشر", "مقالة", "مؤتمر", "مجلة", "دراسة", "علمي"],
        "CURR": ["مقرر", "منهج", "تطوير", "مادة", "خطة دراسية", "وصف مقرر"],
        "TEAC": ["تعليم", "تدريس", "محاضر", "تقويم", "اختبار", "ورشة عمل تدريسية"],
        "QUAL": ["جودة", "اعتماد", "تقييم", "مراجعة", "معايير", "تحسين"],
        "EVNT": ["خدمة", "مجتمع", "فعالية", "نشاط", "مبادرة", "تطوع", "مشاركة مجتمعية"],
        "STUD": ["طلاب", "طالب", "إرشاد", "دعم طلابي", "أنشطة طلابية"],
        "ADMN": ["إدارة", "لجنة", "اجتماع", "تنظيم", "تنسيق", "تقرير إداري"]
    }

    # Find the best matching category
    for code, words in keywords.items():
        if any(word in text_lower for word in words):
            category_code = code
            break # Stop after finding the first match

    # تقدير النقاط والساعات
    word_count = len(text.split())
    # Simple estimation: 1 hour per 10 words, capped between 2 and 40 hours
    virtual_hours = max(2, min(40, word_count // 10 + 1))
    # Simple points: 2 points per hour
    points = virtual_hours * 2

    return {
        "points": points,
        "virtual_hours": virtual_hours,
        "category_code": category_code,
        "category_label": CATEGORIES.get(category_code, "غير مصنف") # Use .get for safety
    }

# -------------------------------------------------------------------------
# DeepSeek (التصنيف + النقاط) --------------------------------------------
@st.cache_data(ttl=3600) # Cache DeepSeek results for an hour
def deepseek_eval(text:str)->dict:
    """Evaluates achievement text using DeepSeek API or fallback."""
    try:
        # Ensure DEESEEK_KEY is available
        if "DEESEEK_KEY" not in st.secrets:
            st.warning("مفتاح DeepSeek API غير موجود. استخدام التصنيف الاحتياطي.")
            return fallback_classification(text)

        api_key = st.secrets['DEESEEK_KEY']
        api_url = "https://api.deepseek.com/v1/chat/completions"

        # Construct the prompt with clear instructions and categories
        system_prompt = (
            "أنت مساعد خبير في تقييم الإنجازات الأكاديمية ضمن سياق جامعي سعودي. مهمتك هي قراءة وصف الإنجاز وتحديد الفئة الأكثر ملاءمة له من القائمة المحددة، وتقدير عدد النقاط والساعات الافتراضية التي يستحقها هذا الإنجاز بناءً على أهميته والجهد المبذول فيه.\n\n"
            "الفئات المتاحة مع رموزها:\n"
            + "\n".join([f"- {code}: {label}" for code, label in CATEGORIES.items()]) + "\n\n"
            "أعد دائماً استجابة بصيغة JSON تحتوي بالضبط على الحقول التالية:\n"
            "- points (integer): تقدير لعدد النقاط (مثلاً: بين 5 و 100 نقطة حسب الأهمية).\n"
            "- virtual_hours (integer): تقدير لعدد الساعات الافتراضية (مثلاً: بين 2 و 60 ساعة حسب الجهد).\n"
            "- category_code (string): رمز الفئة المختارة من القائمة أعلاه.\n"
            "- category_label (string): اسم الفئة المختارة المقابل للرمز.\n\n"
            "مثال على الاستجابة المطلوبة: {\"points\": 25, \"virtual_hours\": 15, \"category_code\": \"RESR\", \"category_label\": \"بحث علمي ونشر\"}"
        )

        payload = {
            "model": "deepseek-chat", # Use the appropriate model
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"يرجى تقييم الإنجاز التالي:\n\n{text}"}
            ],
            "temperature": 0.5, # Adjust temperature for more deterministic results if needed
            "max_tokens": 200, # Set a reasonable max token limit for the response
            "response_format": {"type": "json_object"} # Request JSON output directly if supported
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Make the API call with a timeout
        r = requests.post(api_url, headers=headers, json=payload, timeout=30) # Increased timeout
        r.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        response_data = r.json()

        # Extract the JSON content from the response
        if response_data.get("choices") and response_data["choices"][0].get("message"):
             content = response_data["choices"][0]["message"].get("content")
             if content:
                 try:
                     # Parse the JSON string from the content
                     result = json.loads(content)
                     # Validate the result structure
                     if all(k in result for k in ["points", "virtual_hours", "category_code", "category_label"]):
                          # Ensure the category code is valid
                          if result["category_code"] in CATEGORIES:
                              # Re-assign label from our definition for consistency
                              result["category_label"] = CATEGORIES[result["category_code"]]
                              return result
                          else:
                              st.warning(f"DeepSeek أعاد رمز فئة غير صالح: {result['category_code']}. استخدام التصنيف الاحتياطي.")
                              return fallback_classification(text)
                     else:
                          st.warning("استجابة DeepSeek JSON غير مكتملة. استخدام التصنيف الاحتياطي.")
                          return fallback_classification(text)
                 except json.JSONDecodeError:
                      st.warning("فشل في تحليل استجابة JSON من DeepSeek. استخدام التصنيف الاحتياطي.")
                      return fallback_classification(text)
             else:
                  st.warning("لم يتم العثور على محتوى في استجابة DeepSeek. استخدام التصنيف الاحتياطي.")
                  return fallback_classification(text)
        else:
             st.warning("استجابة DeepSeek غير متوقعة. استخدام التصنيف الاحتياطي.")
             return fallback_classification(text)

    except requests.exceptions.Timeout:
        st.warning("انتهت مهلة استدعاء DeepSeek API. استخدام التصنيف الاحتياطي.")
        return fallback_classification(text)
    except requests.exceptions.RequestException as e:
        st.warning(f"خطأ في الاتصال بـ DeepSeek API: {e}. استخدام التصنيف الاحتياطي.")
        return fallback_classification(text)
    except Exception as e:
        st.warning(f"حدث خطأ غير متوقع أثناء معالجة DeepSeek: {e}. استخدام التصنيف الاحتياطي.")
        # Log the full traceback for debugging if needed
        # show_error("خطأ غير متوقع في DeepSeek", traceback.format_exc())
        return fallback_classification(text)


# -------------------------------------------------------------------------
# الصفحة الرئيسية ---------------------------------------------------------

# Initialize session state keys if they don't exist
if "auth" not in st.session_state:
    st.session_state.auth = False
if "member_name" not in st.session_state:
    st.session_state.member_name = ""
if "selected_year" not in st.session_state:
    st.session_state.selected_year = datetime.now().year
if "main_task_choice" not in st.session_state:
     st.session_state.main_task_choice = "— اختر المهمة الرئيسية —" # Initial default


# --- Authentication ---
if not st.session_state.auth:
    st.header("🔒 تسجيل الدخول") # Use header for better structure
    # Check environment variables needed for login first
    env_ok = True
    if "MASTER_PASS" not in st.secrets:
         st.error("متغير كلمة المرور الرئيسية (MASTER_PASS) غير موجود في الأسرار.")
         env_ok = False

    if env_ok:
         pw = st.text_input("كلمة المرور العامة", type="password", key="login_pw")
         if st.button("دخول", key="login_button"):
             if pw == st.secrets.get("MASTER_PASS"): # Use .get for safety
                 st.session_state.auth = True
                 st.success("تم تسجيل الدخول بنجاح!")
                 time.sleep(1)
                 st.rerun() # Use st.rerun instead of experimental_rerun
             else:
                 st.error("كلمة المرور غير صحيحة!")
    else:
         st.warning("يرجى تكوين متغيرات البيئة المطلوبة لتسجيل الدخول.")
    st.stop() # Stop execution if not authenticated

# --- Main Application Logic (runs only if authenticated) ---

# Initialize GitHub connection (cached)
gh_instance = get_github_instance()
if not gh_instance:
     st.error("فشل الاتصال بـ GitHub. لا يمكن المتابعة.")
     st.stop()

repo = gh_repo(gh_instance) # Get repo object (cached)
if not repo:
     st.error("فشل الوصول إلى المستودع. تحقق من اسم المستودع والصلاحيات.")
     st.stop()


# --- Sidebar for User Info ---
with st.sidebar:
    st.header("👤 بيانات المستخدم")
    # Use session state to preserve name and year across reruns
    st.session_state.member_name = st.text_input(
        "الاسم الثلاثي",
        value=st.session_state.member_name,
        key="member_name_input"
    )
    st.session_state.selected_year = st.number_input(
        "السنة",
        min_value=2010,
        max_value=datetime.now().year + 1, # Allow next year
        value=st.session_state.selected_year,
        step=1,
        key="year_input"
    )

    st.markdown("---") # Separator
    if st.button("تسجيل الخروج", key="logout_button"):
        # Clear relevant session state on logout
        st.session_state.auth = False
        st.session_state.member_name = ""
        # Optionally reset other state if needed
        # st.session_state.main_task_choice = "— اختر المهمة الرئيسية —"
        st.cache_data.clear() # Clear data cache on logout
        st.cache_resource.clear() # Clear resource cache (like GitHub connection)
        st.rerun()

# Check if member name is entered
if not st.session_state.member_name.strip():
    st.info("👈 الرجاء إدخال اسمك الثلاثي في القائمة الجانبية للمتابعة.")
    st.stop()

# Assign state values to local variables for easier use
member = st.session_state.member_name
year = st.session_state.selected_year


# --- Main Task Selection ---
st.header("🎯 المهمة الرئيسية")
try:
    main_tasks_path = "data/main_tasks.csv"
    main_df, main_sha = load_csv(main_tasks_path, repo)

    # Initialize DataFrame if it's empty or doesn't exist
    if main_df.empty:
        main_df = pd.DataFrame(columns=["id", "title", "descr"])
        main_sha = None # Ensure sha is None if file was just created in memory

    # Ensure required columns exist
    if "title" not in main_df.columns: main_df["title"] = ""
    if "id" not in main_df.columns: main_df["id"] = ""
    if "descr" not in main_df.columns: main_df["descr"] = ""


    titles = main_df["title"].tolist()
    options = ["— اختر المهمة الرئيسية —"] + sorted([t for t in titles if t]) + ["➕ إضافة مهمة رئيسية…"] # Sort titles

    # Use session state for the selectbox choice
    st.session_state.main_task_choice = st.selectbox(
         "اختر أو أضف مهمة رئيسية",
         options,
         index=options.index(st.session_state.main_task_choice) if st.session_state.main_task_choice in options else 0,
         key="main_task_selectbox"
     )
    choice = st.session_state.main_task_choice


    main_id = None # Initialize main_id

    if choice == "➕ إضافة مهمة رئيسية…":
        st.subheader("➕ إضافة مهمة رئيسية جديدة")
        with st.form("add_main_task_form"):
            new_title = st.text_input("عنوان المهمة")
            new_descr = st.text_area("وصف مختصر (اختياري)")
            submitted = st.form_submit_button("💾 حفظ المهمة الرئيسية")

            if submitted:
                if not new_title.strip():
                    st.warning("عنوان المهمة مطلوب.")
                elif new_title in titles:
                     st.warning("هذه المهمة الرئيسية موجودة بالفعل.")
                else:
                    new_id = str(uuid.uuid4())[:8]
                    # Use pd.concat instead of .loc for adding rows
                    new_row = pd.DataFrame([{"id": new_id, "title": new_title, "descr": new_descr}])
                    main_df = pd.concat([main_df, new_row], ignore_index=True)

                    if save_csv(main_tasks_path, main_df, main_sha, f"Add main task: {new_title}", repo):
                        st.success(f"تمت إضافة المهمة الرئيسية: {new_title}")
                        # Update state and rerun
                        st.session_state.main_task_choice = new_title # Select the newly added task
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("حدث خطأ أثناء حفظ المهمة الرئيسية.")
                        # Revert DataFrame if save failed
                        main_df = main_df[:-1]


    elif choice.startswith("—"):
        st.warning("يرجى اختيار مهمة رئيسية من القائمة أعلاه أو إضافة واحدة جديدة.")
        st.stop()
    else:
        # Find the ID for the selected task
        task_row = main_df[main_df["title"] == choice]
        if not task_row.empty:
             main_id = task_row["id"].iloc[0]
             # Display description if available
             description = task_row["descr"].iloc[0]
             if pd.notna(description) and description.strip():
                  st.caption(f"وصف المهمة: {description}")
        else:
             st.error("لم يتم العثور على معرف المهمة المحددة. الرجاء إعادة المحاولة.")
             st.stop()


except Exception as e:
    show_error("خطأ في تحميل أو إدارة المهام الرئيسية", traceback.format_exc())
    st.stop()

# Stop if no valid main task is selected
if not main_id:
     st.warning("لم يتم تحديد مهمة رئيسية صالحة.")
     st.stop()


# --- Load/Display Member's Achievements for the Year ---
st.header(f"✍️ إنجازاتك لعام {year}")
achievement_file_path = year_path(year)
df, sha = load_csv(achievement_file_path, repo)

# Define expected columns
expected_cols = ["العضو", "الإنجاز", "التاريخ", "النقاط", "الفئة", "الساعات الافتراضية", "main_id"]

# Initialize DataFrame if empty or file not found
if df.empty:
    df = pd.DataFrame(columns=expected_cols)
    sha = None # Ensure sha is None if df is newly created

# Ensure all expected columns exist, add if missing
for col in expected_cols:
     if col not in df.columns:
          df[col] = pd.NA # Add missing column with NA values


# Filter tasks for the current member and selected main task
my_tasks = df[(df["العضو"] == member) & (df["main_id"] == main_id)].copy() # Filter and create a copy
my_tasks = my_tasks.sort_values(by="التاريخ", ascending=False).reset_index(drop=True) # Sort by date


if my_tasks.empty:
    st.caption(f"لا توجد إنجازات مسجلة لهذه المهمة الرئيسية ({choice}) في عام {year}.")
else:
    st.write(f"الإنجازات المسجلة للمهمة الرئيسية: **{choice}**")
    # Display tasks with delete buttons
    for i in my_tasks.index:
        task_col, date_col, points_col, delete_col = st.columns([5, 2, 1, 1]) # Adjust column ratios

        with task_col:
            achievement = my_tasks.loc[i, 'الإنجاز']
            st.markdown(f"**{achievement}**")

        with date_col:
             task_date = my_tasks.loc[i, 'التاريخ']
             st.caption(f"التاريخ: {task_date}")


        with points_col:
            points = my_tasks.loc[i, 'النقاط']
            hours = my_tasks.loc[i, 'الساعات الافتراضية']
            category = my_tasks.loc[i, 'الفئة']
            st.caption(f"{points} نقطة | {hours} س | {category}")


        with delete_col:
            # Use the original DataFrame index for deletion
            original_index = df[(df["العضو"] == member) &
                                (df["main_id"] == main_id) &
                                (df["الإنجاز"] == achievement) & # Add more conditions if needed for uniqueness
                                (df["التاريخ"] == task_date)].index

            if not original_index.empty:
                 # Generate a unique key for the button based on the original index
                 delete_key = f"del-{original_index[0]}"
                 if st.button("🗑️ حذف", key=delete_key, help="حذف هذا الإنجاز"):
                     # Get the latest sha before deleting
                     _, current_sha = load_csv(achievement_file_path, repo)
                     if current_sha: # Proceed only if sha is available
                          df_to_save = df.drop(original_index[0]).reset_index(drop=True)
                          if save_csv(achievement_file_path, df_to_save, current_sha, f"Delete achievement by {member}", repo):
                              st.success("تم حذف الإنجاز بنجاح.")
                              time.sleep(1)
                              st.rerun()
                          else:
                              st.error("حدث خطأ أثناء حذف الإنجاز.")
                     else:
                          st.error("لم يتم العثور على الملف أو حدث خطأ أثناء الحصول على SHA. لا يمكن الحذف.")

            else:
                 st.error("خطأ: لم يتم العثور على الفهرس الأصلي للمهمة.")


# --- Add New Achievement Form ---
st.markdown("---")
st.header("➕ إضافة إنجاز جديد")
st.write(f"المهمة الرئيسية المحددة: **{choice}**")


with st.form("add_achievement_form", clear_on_submit=True):
    # Default to today's date, ensure it's within the selected year
    today = datetime.now().date()
    default_date = today if today.year == year else datetime(year, 1, 1).date()
    min_date = datetime(year, 1, 1).date()
    max_date = datetime(year, 12, 31).date()

    date = st.date_input("تاريخ الإنجاز", value=default_date, min_value=min_date, max_value=max_date)
    desc = st.text_area("وصف الإنجاز/المهمة المنجزة", height=150, placeholder="اكتب وصفاً تفصيلياً للإنجاز هنا...")
    submitted = st.form_submit_button("💾 حفظ الإنجاز")

if submitted:
    if not desc.strip():
        st.error("وصف الإنجاز مطلوب.")
    elif not date:
         st.error("تاريخ الإنجاز مطلوب.")
    elif date.year != year:
         st.error(f"يجب أن يكون تاريخ الإنجاز ضمن السنة المحددة ({year}).")
    else:
        with st.spinner("⏳ جاري تقييم وحفظ الإنجاز..."):
            try:
                # Evaluate the achievement
                eva = deepseek_eval(desc) # This function now handles errors and fallback

                # Get the latest data and sha before appending
                df_current, current_sha = load_csv(achievement_file_path, repo)
                # Re-initialize if df_current is empty
                if df_current.empty:
                     df_current = pd.DataFrame(columns=expected_cols)
                     current_sha = None # SHA is None for a new file

                 # Ensure all columns exist in df_current
                for col in expected_cols:
                     if col not in df_current.columns:
                          df_current[col] = pd.NA


                # Create a new row as a DataFrame
                new_row_df = pd.DataFrame([{
                    "العضو": member,
                    "الإنجاز": desc,
                    "التاريخ": date.isoformat(), # Store date as ISO string
                    "النقاط": eva.get("points", 0), # Use .get with default
                    "الفئة": eva.get("category_label", "غير مصنف"),
                    "الساعات الافتراضية": eva.get("virtual_hours", 0),
                    "main_id": main_id
                }])

                # Concatenate the new row
                df_updated = pd.concat([df_current, new_row_df], ignore_index=True)

                # Save the updated DataFrame
                if save_csv(achievement_file_path, df_updated, current_sha, f"Add achievement by {member} ({date}) for task {main_id}", repo):
                    st.success(
                        f"✅ تم حفظ الإنجاز بنجاح!\n"
                        f"📊 التقييم: {eva.get('points', 'N/A')} نقطة، "
                        f"{eva.get('virtual_hours', 'N/A')} ساعة، "
                        f"الفئة: {eva.get('category_label', 'N/A')}"
                    )
                    time.sleep(2) # Slightly longer pause for success message
                    st.rerun()
                else:
                    st.error("❌ فشل حفظ الإنجاز. يرجى المحاولة مرة أخرى.")

            except Exception as e:
                show_error("خطأ غير متوقع أثناء إضافة الإنجاز", traceback.format_exc())

```

لقد أضفت `st.title("صفحة اختبار")` و `st.write(...)` مباشرة بعد `st.set_page_config`. جرب تشغيل هذا الكود الآن. إذا رأيت هذا العنوان والنص، فهذا يؤكد أن بيئة Streamlit تعمل والرابط صحيح. إذا لم تظهر، فقد تكون هناك مشكلة في إعداد بيئة Streamlit نفسها أو في كيفية تشغيل التطب
