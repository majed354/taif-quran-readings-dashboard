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
import calendar # Needed for Arabic month names

# Import Github class safely
try:
    from github import Github, UnknownObjectException
except ImportError:
    st.error("مكتبة PyGithub غير مثبتة. يرجى تثبيتها: pip install PyGithub")
    st.stop()


# -------------------------------------------------------------------------
# قائمة أسماء الأعضاء (List of Member Names)
# -------------------------------------------------------------------------
MEMBER_NAMES = [
    "— اختر اسم العضو —", # Placeholder option
    "عبد الله حماد حميد القرشي", "ناصر سعود حمود القثامي", "حاتم عابد عبد الله القرشي",
    "ماجد عبد العزيز الحارثي", "رجاء محمد هوساوي", "عبد الله عيدان الزهراني",
    "منال منصور محمد القرشي", "خلود شاكر فهيد العبدلي", "عبد العزيز عيضه حربي الحارثي",
    "عبد العزيز عواض الثبيتي", "تهاني فيصل علي الحربي", "آمنة جمعة سعيد أحمد قحاف",
    "غدير محمد سليم الشريف", "أسرار عايف سراج الخالدي", "سلوى أحمد محمد الحارثي",
    "هويدا أبو بكر سعيد الخطيب", "تغريد أبو بكر سعيد الخطيب", "مهدي عبد الله قاري",
    "مها عيفان نوار الخليدي", "سلمى معيوض زويد الجميعي", "أسماء محمد السلومي",
    "رائد محمد عوضه الغامدي", "ماجد إبراهيم باقي الجهني", "مرام طلعت محمد أمين ينكصار",
    "سعود سعد محمد الأنصاري", "عبد الرحمن محمد العبيسي", "ولاء حسن مسلم المذكوري",
    "إسراء عبد الغني سندي", "وسام حسن مسلم المذكوري", "سمر علي محمد الشهراني",
    "فاطمه أبكر داوود أبكر", "شيماء محمود صالح بركات", "عبد الله سعد عويض الثبيتي",
    "عايده مصلح صالح المالكي", "أفنان عبد الله محمد السليماني", "أفنان مستور علي السواط"
]

# -------------------------------------------------------------------------
# الفئات (Categories)
# -------------------------------------------------------------------------
CATEGORIES = {
    "CURR": "تطوير المناهج", "TEAC": "التعليم والتقويم", "QUAL": "الاعتماد والجودة",
    "RESR": "بحث علمي ونشر", "EVNT": "فعاليات وخدمة مجتمع", "STUD": "دعم وخدمات طلابية",
    "ADMN": "مهام إدارية", "PDVL": "تطوير مهني"
}

# -------------------------------------------------------------------------
# أسماء الشهور العربية (Arabic Month Names) & Mapping
# -------------------------------------------------------------------------
ARABIC_MONTHS = {
    1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل", 5: "مايو", 6: "يونيو",
    7: "يوليو", 8: "أغسطس", 9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
}
MONTH_OPTIONS = list(ARABIC_MONTHS.items())

# -------------------------------------------------------------------------
# تهيئة الواجهة (UI Initialization)
# -------------------------------------------------------------------------
st.set_page_config("تسجيل المهام المكتملة", layout="centered")

# CSS للواجهة العربية (CSS for Arabic UI)
st.markdown("""
<style>
    /* --- General Styles --- */
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif !important; }
    body, .stApp { direction: rtl; text-align: right; }
    h1, h2, h3, h4, h5, h6 { text-align: right; }

    /* --- Form Elements --- */
    button, input, select, textarea,
    .stTextInput>div>div>input, .stTextArea>div>textarea, .stSelectbox>div>div>select,
    .stDateInput>div>div>input {
        text-align: right !important; direction: rtl !important;
    }
    .stSelectbox [data-baseweb="select"] > div { text-align: right; } /* Selectbox text */
    div[data-baseweb="select"] > div:nth-child(1) { text-align: right; } /* Streamlit > 1.25 selectbox alignment */
    div[data-baseweb="input"] input::placeholder,
    div[data-baseweb="textarea"] textarea::placeholder { text-align: right !important; }

    /* --- Buttons --- */
    .stButton>button {
        background-color: #1e88e5; color: white; border-radius: 6px;
        padding: 8px 16px; font-weight: 600; border: none;
    }
    .stButton>button:hover { background-color: #1565c0; }
    .stButton>button[kind="secondary"] { /* Style for secondary buttons like logout */
        background-color: #f0f2f6; color: #31333F; border: 1px solid #d3d3d3;
    }
     .stButton>button[kind="secondary"]:hover { background-color: #e6e8eb; }
    .stButton>button[help="حذف هذا الإنجاز"] { /* Delete button */
        display: flex; justify-content: center; align-items: center;
        padding: 4px; line-height: 1; background-color: #f44336; /* Red background */
    }
    .stButton>button[help="حذف هذا الإنجاز"]:hover { background-color: #d32f2f; } /* Darker red on hover */


    /* --- Specific Layouts --- */
    .stTabs [data-baseweb="tab-list"] { direction: rtl; }
    .approx-date-header { font-weight: bold; margin-bottom: 5px; text-align: center; }
    .achievement-display { border: 1px solid #e0e0e0; border-radius: 5px; padding: 10px; margin-bottom: 10px; }
    .achievement-display .caption { color: #555; font-size: 0.9em; }

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# معالجة الأخطاء (Error Handling)
# -------------------------------------------------------------------------
def show_error(error_msg, details=None):
    st.error(f"حدث خطأ: {error_msg}")
    if details:
        with st.expander("تفاصيل الخطأ (للمطورين)"):
            st.code(details)

# -------------------------------------------------------------------------
# التحقق من المتغيرات المطلوبة (Check Required Environment Variables)
# -------------------------------------------------------------------------
def check_environment():
    try:
        required_vars = ["GITHUB_TOKEN", "REPO_NAME", "MASTER_PASS", "DEESEEK_KEY"]
        missing_vars = [var for var in required_vars if var not in st.secrets]
        if missing_vars:
            show_error(f"متغيرات مطلوبة غير موجودة: {', '.join(missing_vars)}", "أضفها إلى ملف .streamlit/secrets.toml.")
            return False
        for var in required_vars:
             if not st.secrets[var]:
                 show_error(f"المتغير '{var}' فارغ.", f"أضف قيمة للمتغير '{var}' في secrets.toml.")
                 return False
        return True
    except Exception as e:
        show_error("خطأ في التحقق من المتغيرات البيئية", traceback.format_exc())
        return False

# -------------------------------------------------------------------------
# أدوات GitHub (GitHub Utilities)
# -------------------------------------------------------------------------
@st.cache_resource(ttl=300)
def get_gh_repo():
    try:
        if not all(k in st.secrets for k in ["GITHUB_TOKEN", "REPO_NAME"]): return None
        if not st.secrets["GITHUB_TOKEN"] or not st.secrets["REPO_NAME"]: return None
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo(st.secrets["REPO_NAME"])
        return repo
    except UnknownObjectException:
         show_error(f"خطأ 404: المستودع '{st.secrets.get('REPO_NAME', 'غير محدد')}' غير موجود.", "تأكد من صحة 'REPO_NAME' وصلاحيات 'GITHUB_TOKEN'.")
         return None
    except Exception as e:
        show_error(f"خطأ في الاتصال بـ GitHub: {e}", traceback.format_exc())
        return None

def clear_repo_cache(): st.cache_resource.clear()

def load_csv(path: str):
    repo = get_gh_repo()
    if not repo: return pd.DataFrame(), None
    try:
        file_content = repo.get_contents(path)
        content_decoded = base64.b64decode(file_content.content).decode("utf-8-sig")
        # Handle potential empty data after decoding
        if not content_decoded.strip():
             st.warning(f"الملف '{path}' فارغ أو يحتوي فقط على مسافات بيضاء.")
             return pd.DataFrame(), file_content.sha # Return empty df but keep sha for potential update
        df = pd.read_csv(io.StringIO(content_decoded))
        # Fill NaN values resulting from empty strings in CSV with None or empty string
        df = df.fillna('') # Replace NaN with empty strings for consistency
        return df, file_content.sha
    except UnknownObjectException:
        st.warning(f"الملف '{path}' غير موجود، سيتم إنشاؤه عند الحفظ.")
        return pd.DataFrame(), None
    except pd.errors.EmptyDataError:
         st.warning(f"الملف '{path}' موجود ولكنه فارغ تمامًا (لا يحتوي حتى على رؤوس أعمدة).")
         # Try to get sha even if empty for update purposes
         try:
             file_content = repo.get_contents(path)
             return pd.DataFrame(), file_content.sha
         except Exception:
              return pd.DataFrame(), None # Fallback if getting sha fails too
    except Exception as e:
        show_error(f"خطأ في تحميل أو قراءة الملف '{path}': {e}", traceback.format_exc())
        return pd.DataFrame(), None

def save_csv(path: str, df: pd.DataFrame, sha: str | None, msg: str):
    repo = get_gh_repo()
    if not repo: return False
    try:
        # Before saving, replace any potential Python None with empty strings for CSV consistency
        df_to_save = df.fillna('')
        content = df_to_save.to_csv(index=False, line_terminator="\n", encoding="utf-8-sig")
        try:
            existing_file = repo.get_contents(path)
            # Use existing sha if provided sha is None or doesn't match
            current_sha = existing_file.sha if sha is None or sha != existing_file.sha else sha
            # Check if content actually changed before updating
            # Decode existing content to compare
            existing_content_decoded = base64.b64decode(existing_file.content).decode("utf-8-sig")
            if content == existing_content_decoded:
                 st.info(f"لا توجد تغييرات لحفظها في الملف '{path}'.")
                 return True # Indicate success as no action needed

            repo.update_file(path, msg, content, current_sha)
            st.toast(f"✅ تم تحديث '{os.path.basename(path)}'") # Use toast for less intrusive message
            clear_repo_cache()
            return True
        except UnknownObjectException:
            repo.create_file(path, msg, content)
            st.toast(f"✅ تم إنشاء '{os.path.basename(path)}'")
            clear_repo_cache()
            return True
        except Exception as update_create_e:
             show_error(f"فشل تحديث/إنشاء '{path}': {update_create_e}", traceback.format_exc())
             return False
    except Exception as e:
        show_error(f"خطأ عام أثناء حفظ '{path}': {e}", traceback.format_exc())
        return False

def year_path(y: int): return f"data/department/{y}/achievements_{y}.csv"

# -------------------------------------------------------------------------
# تصنيف المهام (Fallback Classification)
# -------------------------------------------------------------------------
def fallback_classification(text: str) -> dict:
    text_lower = text.lower(); category_code = "PDVL"
    keywords = {
        "RESR": ["بحث", "نشر", "مقالة", "مؤتمر", "مجلة"], "CURR": ["مقرر", "منهج", "تطوير", "مادة"],
        "TEAC": ["تعليم", "تدريس", "محاضر", "تقويم"], "QUAL": ["جودة", "اعتماد", "تقييم"],
        "EVNT": ["خدمة", "مجتمع", "فعالية", "نشاط", "ورشة"], "STUD": ["طلاب", "طالب", "إرشاد"],
        "ADMN": ["إدارة", "لجنة", "اجتماع"] }
    for code, words in keywords.items():
        if any(word in text_lower for word in words): category_code = code; break
    word_count = len(text.split())
    virtual_hours = max(1, min(30, word_count // 10 if word_count > 10 else 1))
    points = virtual_hours * 2
    return {"points": points, "virtual_hours": virtual_hours, "category_code": category_code,
            "category_label": CATEGORIES.get(category_code, "غير مصنف")}

# -------------------------------------------------------------------------
# DeepSeek (Classification + Points)
# -------------------------------------------------------------------------
def deepseek_eval(text: str) -> dict:
    if not st.secrets.get("DEESEEK_KEY"):
        st.warning("مفتاح DeepSeek API غير موجود. استخدام التصنيف الاحتياطي.")
        return fallback_classification(text)
    try:
        system_prompt = ("أنت مساعد تقييم إنجازات أكاديمية. قدر النقاط (1-100)، الساعات (1-50)، واختر الفئة الأنسب. "
                         "الفئات: " + ", ".join([f"{k}:{v}" for k, v in CATEGORIES.items()]) + ". "
                         "أعد JSON بـ: points, virtual_hours, category_code, category_label.")
        prompt_data = {
            "model": "deepseek-chat", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": text}],
            "tool_choice": {"type": "function", "function": {"name": "score_achievement"}},
            "tools": [{"type": "function", "function": {
                "name": "score_achievement", "description": "تحديد النقاط والساعات والفئة",
                "parameters": {"type": "object", "properties": {
                    "points": {"type": "integer"}, "virtual_hours": {"type": "integer"},
                    "category_code": {"type": "string", "enum": list(CATEGORIES.keys())},
                    "category_label": {"type": "string"}},
                    "required": ["points", "virtual_hours", "category_code", "category_label"]}}}]}
        response = requests.post("https://api.deepseek.com/v1/chat/completions",
                                 headers={"Authorization": f"Bearer {st.secrets['DEESEEK_KEY']}", "Content-Type": "application/json"},
                                 json=prompt_data, timeout=30)
        response.raise_for_status()
        result_json = response.json()
        # --- Simplified Response Handling ---
        try:
            tool_call = result_json["choices"][0]["message"]["tool_calls"][0]
            if tool_call["function"]["name"] == "score_achievement":
                arguments = json.loads(tool_call["function"]["arguments"])
                if arguments.get("category_code") in CATEGORIES:
                    arguments["category_label"] = CATEGORIES[arguments["category_code"]]
                    arguments["points"] = max(1, min(100, arguments.get("points", 1)))
                    arguments["virtual_hours"] = max(1, min(50, arguments.get("virtual_hours", 1)))
                    return arguments
        except (KeyError, IndexError, TypeError, json.JSONDecodeError):
             # Attempt to parse content if tool call failed or was missing
             try:
                 content = result_json["choices"][0]["message"]["content"]
                 arguments = json.loads(content)
                 if all(k in arguments for k in ["points", "virtual_hours", "category_code", "category_label"]) and arguments.get("category_code") in CATEGORIES:
                      arguments["category_label"] = CATEGORIES[arguments["category_code"]]
                      arguments["points"] = max(1, min(100, arguments.get("points", 1)))
                      arguments["virtual_hours"] = max(1, min(50, arguments.get("virtual_hours", 1)))
                      st.info("تم تحليل المحتوى النصي من DeepSeek.")
                      return arguments
             except (KeyError, IndexError, TypeError, json.JSONDecodeError):
                 st.warning("فشل تحليل استجابة DeepSeek. استخدام التصنيف الاحتياطي.")
                 st.write("DeepSeek Response:", result_json) # Log for debugging
                 return fallback_classification(text)

        # If parsing failed at any point above, fallback
        st.warning("استجابة DeepSeek غير متوقعة. استخدام التصنيف الاحتياطي.")
        return fallback_classification(text)

    except requests.exceptions.RequestException as e:
        st.warning(f"فشل استدعاء DeepSeek API: {e}. استخدام التصنيف الاحتياطي.")
        return fallback_classification(text)
    except Exception as e:
        st.warning(f"خطأ غير متوقع في DeepSeek: {e}. استخدام التصنيف الاحتياطي.")
        print(traceback.format_exc())
        return fallback_classification(text)

# -------------------------------------------------------------------------
# الصفحة الرئيسية (Main Page Logic)
# -------------------------------------------------------------------------

# --- Session State Initialization ---
current_year = datetime.now().year
current_month = datetime.now().month
if "auth" not in st.session_state: st.session_state.auth = False
if "selected_member" not in st.session_state: st.session_state.selected_member = MEMBER_NAMES[0]
if "selected_year" not in st.session_state: st.session_state.selected_year = current_year
if "selected_month" not in st.session_state: st.session_state.selected_month = current_month
# Add state for optional main task selection for the form
if "form_main_task_id" not in st.session_state: st.session_state.form_main_task_id = None
if "form_main_task_title" not in st.session_state: st.session_state.form_main_task_title = "— بدون مهمة رئيسية —"


# --- Environment Check ---
if not check_environment():
    st.warning("يرجى إصلاح مشكلات الإعداد قبل المتابعة.")
    if st.button("محاولة مسح ذاكرة التخزين المؤقت للمستودع"): clear_repo_cache(); st.rerun()
    st.stop()

# --- Login Form ---
if not st.session_state.auth:
    st.title("تسجيل الدخول")
    with st.form("login_form"):
        entered_pass = st.text_input("كلمة المرور العامة", type="password", key="password_input")
        login_button = st.form_submit_button("دخول")
        if login_button:
            master_pass = st.secrets.get("MASTER_PASS", "")
            if entered_pass == master_pass:
                st.session_state.auth = True; st.success("تم تسجيل الدخول!"); time.sleep(1); st.rerun()
            elif not master_pass: st.error("خطأ إعداد: كلمة المرور الرئيسية غير معرفة.")
            else: st.error("كلمة المرور غير صحيحة!")
    st.stop()

# --- Main Application ---
st.title("تسجيل المهام المكتملة")

# --- User & Date Selection ---
st.selectbox("اختر اسم العضو", options=MEMBER_NAMES, key="selected_member")
st.markdown("<div class='approx-date-header'>التاريخ التقريبي للإنجازات</div>", unsafe_allow_html=True)
col_month, col_year = st.columns(2)
with col_month: st.selectbox("الشهر", options=list(ARABIC_MONTHS.keys()), format_func=lambda m: ARABIC_MONTHS[m], key="selected_month")
with col_year: st.number_input("السنة", min_value=2010, max_value=current_year + 1, key="selected_year", step=1)

# --- Sidebar ---
with st.sidebar:
    st.header("الإجراءات")
    if st.button("تسجيل الخروج", type="secondary"): # Use secondary style
        st.session_state.auth = False; st.session_state.selected_member = MEMBER_NAMES[0]
        st.session_state.selected_year = current_year; st.session_state.selected_month = current_month
        st.rerun()
    if st.button("مسح ذاكرة التخزين المؤقت", type="secondary"):
        clear_repo_cache(); st.info("تم مسح ذاكرة التخزين المؤقت."); time.sleep(1); st.rerun()

# --- Validate User Selection ---
member = st.session_state.selected_member
year = st.session_state.selected_year
month = st.session_state.selected_month
if member == MEMBER_NAMES[0]:
    st.info("👈 الرجاء اختيار اسم العضو للمتابعة.")
    st.stop()

# --- Load Main Tasks (Needed for the optional selection) ---
main_tasks_path = "data/main_tasks.csv"
main_df, main_sha = load_csv(main_tasks_path)
if main_df.empty and main_sha is None:
    main_df = pd.DataFrame(columns=["id", "title", "descr"])
main_task_titles = main_df["title"].tolist() if "title" in main_df.columns else []
# Options for the form's main task selection
main_task_options_for_form = { "— بدون مهمة رئيسية —": None } # Map title to ID (None for no task)
if "id" in main_df.columns and "title" in main_df.columns:
     for _, row in main_df.iterrows():
         main_task_options_for_form[row['title']] = row['id']


# --- Add New Achievement Form (Moved Up) ---
st.header("1. إضافة إنجاز جديد")
with st.form("add_achievement_form", clear_on_submit=True):
    try: default_date = datetime(year, month, 1)
    except ValueError: default_date = datetime(year, month, calendar.monthrange(year, month)[1])
    achievement_date = st.date_input("تاريخ الإنجاز الفعلي", value=default_date)
    achievement_desc = st.text_area("وصف الإنجاز بالتفصيل", height=150, key="achievement_desc_input")

    # Optional: Select Main Task to associate with this new achievement
    selected_form_main_task_title = st.selectbox(
        "ربط بمهمة رئيسية (اختياري)",
        options=list(main_task_options_for_form.keys()), # Use the prepared dictionary keys
        key="form_main_task_selector"
        # No default index needed, will default to first option
    )
    # Get the corresponding main_id based on the selected title
    form_main_id = main_task_options_for_form.get(selected_form_main_task_title) # Returns None if "— بدون مهمة رئيسية —" is selected

    submit_achievement = st.form_submit_button("➕ إضافة وحفظ الإنجاز")

    if submit_achievement:
        if not achievement_desc.strip(): st.error("وصف الإنجاز مطلوب.")
        else:
            with st.spinner("⏳ جاري تقييم وحفظ الإنجاز..."):
                try:
                    evaluation = deepseek_eval(achievement_desc)
                    new_achievement_row = pd.Series({
                        "العضو": member, "الإنجاز": achievement_desc.strip(), "التاريخ": achievement_date.isoformat(),
                        "النقاط": evaluation.get("points", 0), "الفئة": evaluation.get("category_label", "غير مصنف"),
                        "الساعات الافتراضية": evaluation.get("virtual_hours", 0),
                        "main_id": form_main_id # Use the id selected in the form (can be None)
                    })

                    current_year_path = year_path(year) # Define path here
                    expected_cols = ["العضو", "الإنجاز", "التاريخ", "النقاط", "الفئة", "الساعات الافتراضية", "main_id"]
                    achievements_df_reloaded, achievements_sha_reloaded = load_csv(current_year_path)

                    if achievements_df_reloaded.empty and achievements_sha_reloaded is None:
                         achievements_df_reloaded = pd.DataFrame(columns=expected_cols)
                    else:
                         for col in expected_cols:
                             if col not in achievements_df_reloaded.columns: achievements_df_reloaded[col] = '' # Use empty string for missing

                    # Ensure main_id column exists before concat, fillna just in case
                    if 'main_id' not in achievements_df_reloaded.columns: achievements_df_reloaded['main_id'] = ''
                    achievements_df_reloaded['main_id'] = achievements_df_reloaded['main_id'].fillna('')


                    achievements_df_updated = pd.concat([achievements_df_reloaded, pd.DataFrame([new_achievement_row])], ignore_index=True)

                    try: # Convert types robustly
                        achievements_df_updated['النقاط'] = pd.to_numeric(achievements_df_updated['النقاط'], errors='coerce').fillna(0).astype(int)
                        achievements_df_updated['الساعات الافتراضية'] = pd.to_numeric(achievements_df_updated['الساعات الافتراضية'], errors='coerce').fillna(0).astype(int)
                        # Ensure main_id remains string or None (read as empty string from CSV)
                        achievements_df_updated['main_id'] = achievements_df_updated['main_id'].astype(str).replace('nan', '').replace('None','')
                    except Exception as type_e: st.warning(f"تحذير تحويل النوع: {type_e}")

                    commit_message = f"إضافة إنجاز بواسطة {member} ({achievement_date.isoformat()}): {evaluation.get('category_label')}"
                    if save_csv(current_year_path, achievements_df_updated, achievements_sha_reloaded, commit_message):
                        st.success(f"✅ تمت إضافة الإنجاز بنجاح!")
                        st.toast(f"التقييم: {evaluation.get('points', 'N/A')} نقطة، {evaluation.get('virtual_hours', 'N/A')} ساعة، {evaluation.get('category_label', 'N/A')}")
                        time.sleep(1) # Shorter sleep with toast
                        st.rerun()
                    else: st.error("❌ حدث خطأ أثناء حفظ الإنجاز.")
                except Exception as e: show_error("خطأ في إضافة الإنجاز", traceback.format_exc())


# --- Display Existing Achievements (No longer filtered by main_id initially) ---
st.header(f"2. الإنجازات المسجلة ({member} - {ARABIC_MONTHS.get(month, month)} {year})")
current_year_path_display = year_path(year) # Use separate var for clarity
try:
    achievements_df_display, achievements_sha_display = load_csv(current_year_path_display)
    expected_cols_display = ["العضو", "الإنجاز", "التاريخ", "النقاط", "الفئة", "الساعات الافتراضية", "main_id"]

    if not achievements_df_display.empty:
        # Ensure columns exist
        for col in expected_cols_display:
             if col not in achievements_df_display.columns: achievements_df_display[col] = ''
        # Convert date and filter
        achievements_df_display['التاريخ_dt'] = pd.to_datetime(achievements_df_display['التاريخ'], errors='coerce')
        # Fill NaN main_id with empty string for consistent mapping
        achievements_df_display['main_id'] = achievements_df_display['main_id'].fillna('')

        # Create a mapping from main_id to main_title for display
        id_to_title_map = {None: "— بدون مهمة رئيسية —", '': "— بدون مهمة رئيسية —"}
        if "id" in main_df.columns and "title" in main_df.columns:
            id_to_title_map.update(main_df.set_index('id')['title'].to_dict())


        my_tasks_display_df = achievements_df_display[
            (achievements_df_display["العضو"] == member) &
            (achievements_df_display['التاريخ_dt'].notna()) &
            (achievements_df_display['التاريخ_dt'].dt.year == year) &
            (achievements_df_display['التاريخ_dt'].dt.month == month)
        ].copy()
        my_tasks_display_df = my_tasks_display_df.sort_values(by='التاريخ_dt', ascending=False).reset_index()

        if my_tasks_display_df.empty:
            st.caption("لا توجد إنجازات مسجلة لهذا العضو في هذا الشهر وهذه السنة.")
        else:
            for i in my_tasks_display_df.index:
                original_df_index = my_tasks_display_df.loc[i, 'index']
                with st.container(): # Use container for better visual separation
                     st.markdown("<div class='achievement-display'>", unsafe_allow_html=True) # Add CSS class
                     col1, col2 = st.columns([0.9, 0.1])
                     with col1:
                        achievement_desc = my_tasks_display_df.loc[i].get('الإنجاز', "لا يوجد وصف")
                        achievement_date_dt = my_tasks_display_df.loc[i].get('التاريخ_dt')
                        achievement_date_str = achievement_date_dt.strftime('%Y-%m-%d') if pd.notna(achievement_date_dt) else my_tasks_display_df.loc[i].get('التاريخ', "غير معروف")
                        points = my_tasks_display_df.loc[i].get('النقاط', 'N/A')
                        hours = my_tasks_display_df.loc[i].get('الساعات الافتراضية', 'N/A')
                        category = my_tasks_display_df.loc[i].get('الفئة', 'N/A')
                        task_main_id = my_tasks_display_df.loc[i].get('main_id', '')
                        # Map main_id to title for display, default if not found
                        main_task_title_display = id_to_title_map.get(task_main_id, f"مهمة غير معروفة ({task_main_id})")


                        st.markdown(f"**{achievement_desc}**")
                        st.markdown(f"<span class='caption'>التاريخ: {achievement_date_str} | الفئة: {category} | النقاط: {points} | الساعات: {hours}<br>المهمة الرئيسية: {main_task_title_display}</span>", unsafe_allow_html=True)


                     with col2:
                        delete_key = f"del-{original_df_index}"
                        if st.button("🗑️", key=delete_key, help="حذف هذا الإنجاز"):
                            if original_df_index in achievements_df_display.index:
                                achievement_to_delete = achievements_df_display.loc[original_df_index, 'الإنجاز']
                                # Use the main df loaded for display for dropping
                                achievements_df_updated_del = achievements_df_display.drop(index=original_df_index).reset_index(drop=True)
                                if 'التاريخ_dt' in achievements_df_updated_del.columns:
                                     achievements_df_updated_del = achievements_df_updated_del.drop(columns=['التاريخ_dt'])

                                if save_csv(current_year_path_display, achievements_df_updated_del, achievements_sha_display, f"حذف إنجاز '{achievement_to_delete}' بواسطة {member}"):
                                    st.success("تم حذف الإنجاز بنجاح.")
                                    time.sleep(1); st.rerun()
                                else: st.error("حدث خطأ أثناء حذف الإنجاز.")
                            else: st.error("لم يتم العثور على الإنجاز المراد حذفه.")
                     st.markdown("</div>", unsafe_allow_html=True) # Close CSS class div
    else:
         st.caption("لم يتم تحميل بيانات الإنجازات أو أن الملف فارغ.")

except Exception as e:
    show_error("خطأ في تحميل أو عرض الإنجازات", traceback.format_exc())


# --- Optional: Section to Add/Manage Main Tasks (Can be kept at the end) ---
with st.expander("إدارة المهام الرئيسية (إضافة/تعديل)"):
    st.subheader("إضافة مهمة رئيسية جديدة")
    with st.form("add_main_task_form_expander"):
        new_title_exp = st.text_input("عنوان المهمة الرئيسية الجديدة", key="new_title_exp")
        new_descr_exp = st.text_area("وصف مختصر للمهمة (اختياري)", key="new_descr_exp")
        submitted_exp = st.form_submit_button("حفظ المهمة الرئيسية")
        if submitted_exp:
            if not new_title_exp.strip(): st.error("عنوان المهمة مطلوب.")
            elif new_title_exp in main_task_titles: st.error("المهمة موجودة بالفعل.")
            else:
                new_id_exp = str(uuid.uuid4())[:8]
                new_row_exp = pd.DataFrame([{"id": new_id_exp, "title": new_title_exp, "descr": new_descr_exp}])
                if main_df.empty: main_df_exp = pd.DataFrame(columns=["id", "title", "descr"])
                else: main_df_exp = main_df.copy() # Work on a copy
                main_df_updated_exp = pd.concat([main_df_exp, new_row_exp], ignore_index=True)
                if save_csv(main_tasks_path, main_df_updated_exp, main_sha, f"إضافة مهمة رئيسية: {new_title_exp}"):
                    st.success(f"تمت إضافة المهمة '{new_title_exp}'.")
                    time.sleep(1); st.rerun()
                else: st.error("خطأ في حفظ المهمة الرئيسية.")
    # Display existing main tasks (optional)
    st.subheader("المهام الرئيسية الحالية")
    if not main_df.empty and "title" in main_df.columns:
         st.dataframe(main_df[["title", "descr"]].rename(columns={"title": "العنوان", "descr": "الوصف"}), use_container_width=True)
    else:
         st.caption("لا توجد مهام رئيسية معرفة حتى الآن.")

