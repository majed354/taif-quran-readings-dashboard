import streamlit as st
import pandas as pd
import requests # Keep for potential future use
import base64
import io
import uuid
from datetime import datetime
import traceback
import time
import json
import os
import calendar

# Import Github class safely
try:
    from github import Github, UnknownObjectException
except ImportError:
    st.error("مكتبة PyGithub غير مثبتة. يرجى تثبيتها: pip install PyGithub")
    st.stop()


# -------------------------------------------------------------------------
# Constants and Configuration
# -------------------------------------------------------------------------
MEMBER_NAMES = [
    "— اختر اسم العضو —",
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

HOUR_RANGES = [
    "— اختر نطاق الساعات —", "1 ساعة أو أقل", "1-2 ساعات", "2-4 ساعات", "4-6 ساعات",
    "6-8 ساعات", "8-10 ساعات", "10-15 ساعة", "15-20 ساعة", "20-30 ساعة",
    "30-50 ساعة", "50-100 ساعة", "أكثر من 100 ساعة"
]

# Initial list of categories - تمت الإضافة
INITIAL_CATEGORIES = [
    "— بدون فئة —", # Default/Placeholder
    "تطوير المناهج", "التعليم والتقويم", "الاعتماد والجودة", "بحث علمي ونشر",
    "فعاليات وخدمة مجتمع", "دعم وخدمات طلابية", "مهام إدارية", "تطوير مهني",
    # "➕ إضافة فئة أخرى..." # Option to add later if needed
]

ARABIC_MONTHS = {
    1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل", 5: "مايو", 6: "يونيو",
    7: "يوليو", 8: "أغسطس", 9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
}

# Single CSV file paths - تم التغيير
MAIN_TASKS_PATH = "data/main_tasks.csv"
ALL_ACHIEVEMENTS_PATH = "data/all_achievements.csv" # Path for the single achievements file

# Expected columns - تم التحديث
EXPECTED_MAIN_TASK_COLS = ["id", "title", "descr"]
EXPECTED_ACHIEVEMENT_COLS = ["العضو", "الإنجاز", "التاريخ", "نطاق_الساعات_المقدرة", "الفئة", "main_id"]

# -------------------------------------------------------------------------
# تهيئة الواجهة (UI Initialization)
# -------------------------------------------------------------------------
st.set_page_config("تسجيل المهام المكتملة", layout="centered")
st.markdown("""
<style>
    /* CSS remains largely the same, ensure it covers new elements if needed */
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    * { font-family: 'Tajawal', sans-serif !important; }
    body, .stApp { direction: rtl; text-align: right; }
    h1, h2, h3, h4, h5, h6 { text-align: right; }
    button, input, select, textarea,
    .stTextInput>div>div>input, .stTextArea>div>textarea, .stSelectbox>div>div>select,
    .stDateInput>div>div>input { text-align: right !important; direction: rtl !important; }
    .stSelectbox [data-baseweb="select"] > div { text-align: right; }
    div[data-baseweb="select"] > div:nth-child(1) { text-align: right; }
    div[data-baseweb="input"] input::placeholder, div[data-baseweb="textarea"] textarea::placeholder { text-align: right !important; }
    .stButton>button { background-color: #1e88e5; color: white; border-radius: 6px; padding: 8px 16px; font-weight: 600; border: none; }
    .stButton>button:hover { background-color: #1565c0; }
    .stButton>button[kind="secondary"] { background-color: #f0f2f6; color: #31333F; border: 1px solid #d3d3d3; }
    .stButton>button[kind="secondary"]:hover { background-color: #e6e8eb; }
    .stButton>button[help="حذف هذا الإنجاز"] { display: flex; justify-content: center; align-items: center; padding: 4px; line-height: 1; background-color: #f44336; }
    .stButton>button[help="حذف هذا الإنجاز"]:hover { background-color: #d32f2f; }
    .stTabs [data-baseweb="tab-list"] { direction: rtl; }
    .approx-date-header { font-weight: bold; margin-bottom: 5px; text-align: center; }
    .achievement-display { border: 1px solid #e0e0e0; border-radius: 5px; padding: 10px; margin-bottom: 10px; background-color: #fafafa; }
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
        required_vars = ["GITHUB_TOKEN", "REPO_NAME", "MASTER_PASS"] # DEESEEK_KEY no longer needed
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
        # Check for necessary secrets first
        if not all(k in st.secrets for k in ["GITHUB_TOKEN", "REPO_NAME"]):
             show_error("GITHUB_TOKEN أو REPO_NAME غير موجود في الأسرار.")
             return None
        if not st.secrets["GITHUB_TOKEN"] or not st.secrets["REPO_NAME"]:
             show_error("GITHUB_TOKEN أو REPO_NAME فارغ في الأسرار.")
             return None
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

# Updated load_csv to handle single file and ensure columns
def load_csv(path: str, expected_cols: list):
    """Loads the single CSV file from GitHub, ensuring expected columns exist."""
    repo = get_gh_repo()
    if not repo: return pd.DataFrame(columns=expected_cols), None

    df = pd.DataFrame(columns=expected_cols)
    sha = None

    try:
        file_content = repo.get_contents(path)
        sha = file_content.sha
        content_decoded = base64.b64decode(file_content.content).decode("utf-8-sig")

        if content_decoded.strip():
            try:
                # Specify dtype as object to prevent pandas from guessing numeric types incorrectly
                df_read = pd.read_csv(io.StringIO(content_decoded), dtype=object)
                # Ensure all expected columns are present
                for col in expected_cols:
                    if col not in df_read.columns:
                        df_read[col] = '' # Add missing columns
                df = df_read[expected_cols] # Select only expected columns
            except Exception as read_err:
                 show_error(f"خطأ عند قراءة CSV '{path}': {read_err}", traceback.format_exc())
                 return pd.DataFrame(columns=expected_cols), sha
        else:
             st.warning(f"الملف '{path}' فارغ أو يحتوي فقط على مسافات بيضاء.")

        df = df.fillna('') # Replace NaN with empty strings
        return df, sha

    except UnknownObjectException:
        st.warning(f"الملف '{path}' غير موجود، سيتم إنشاؤه عند الحفظ.")
        return pd.DataFrame(columns=expected_cols), None
    except Exception as e:
        show_error(f"خطأ في تحميل الملف '{path}': {e}", traceback.format_exc())
        return pd.DataFrame(columns=expected_cols), sha

# Updated save_csv to handle single file and correct argument name
def save_csv(path: str, df: pd.DataFrame, sha: str | None, msg: str, expected_cols: list):
    """Saves the DataFrame to the single CSV file."""
    repo = get_gh_repo()
    if not repo: return False

    try:
        # Ensure only expected columns and fill NA before saving
        df_to_save = df[expected_cols].copy()
        df_to_save = df_to_save.fillna('')
        # Corrected argument: lineterminator (lowercase)
        content = df_to_save.to_csv(index=False, lineterminator="\n", encoding="utf-8-sig")

        try:
            existing_file = repo.get_contents(path)
            current_sha = existing_file.sha
            # Only update if sha matches or if provided sha is None
            if sha is None or sha == current_sha:
                existing_content_decoded = base64.b64decode(existing_file.content).decode("utf-8-sig")
                if content == existing_content_decoded:
                     st.toast(f"لا تغييرات لحفظها في '{os.path.basename(path)}'.")
                     return True
                repo.update_file(path, msg, content, current_sha)
                st.toast(f"✅ تم تحديث '{os.path.basename(path)}'")
                clear_repo_cache()
                return True
            else:
                 show_error(f"فشل الحفظ: تم تعديل الملف '{path}' على GitHub.", "تم تحميل أحدث نسخة. أعد المحاولة.")
                 clear_repo_cache(); st.rerun(); return False
        except UnknownObjectException:
            # Create the file (and potentially the 'data' directory)
            folder_path = os.path.dirname(path)
            if folder_path and folder_path != '.':
                 # Basic check, create_file handles nested creation
                 pass
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

# --- Removed year_path function ---

# -------------------------------------------------------------------------
# الصفحة الرئيسية (Main Page Logic)
# -------------------------------------------------------------------------

# --- Session State Initialization ---
# Default year set to 2025
default_year = 2025
current_month = datetime.now().month
if "auth" not in st.session_state: st.session_state.auth = False
if "selected_member" not in st.session_state: st.session_state.selected_member = MEMBER_NAMES[0]
if "selected_year" not in st.session_state: st.session_state.selected_year = default_year # Default to 2025
if "selected_month" not in st.session_state: st.session_state.selected_month = current_month
if "form_main_task_id" not in st.session_state: st.session_state.form_main_task_id = None
if "form_main_task_title" not in st.session_state: st.session_state.form_main_task_title = "— بدون مهمة رئيسية —"
if "selected_category" not in st.session_state: st.session_state.selected_category = INITIAL_CATEGORIES[0] # Default category


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
# Year input defaults to session state (which is 2025)
with col_year: st.number_input("السنة", min_value=2010, max_value=default_year + 5, key="selected_year", step=1) # Allow few years ahead

# --- Sidebar ---
with st.sidebar:
    st.header("الإجراءات")
    if st.button("تسجيل الخروج", type="secondary"):
        st.session_state.auth = False; st.session_state.selected_member = MEMBER_NAMES[0]
        st.session_state.selected_year = default_year; st.session_state.selected_month = current_month
        st.session_state.selected_category = INITIAL_CATEGORIES[0] # Reset category on logout
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

# --- Load Main Tasks ---
main_df, main_sha = load_csv(MAIN_TASKS_PATH, expected_cols=EXPECTED_MAIN_TASK_COLS)
main_task_options_for_form = { "— بدون مهمة رئيسية —": None }
if not main_df.empty:
     main_df_filled = main_df.fillna('')
     # Create {title: id} mapping
     id_to_title_map_form = main_df_filled.set_index('id')['title'].to_dict()
     id_to_title_map_form = {k: v for k, v in id_to_title_map_form.items() if k and v}
     main_task_options_for_form.update({v: k for k, v in id_to_title_map_form.items()})


# --- Add New Achievement Form ---
st.header("1. إضافة إنجاز جديد")
with st.form("add_achievement_form", clear_on_submit=True):
    try: default_date_val = datetime(year, month, 1)
    except ValueError: default_date_val = datetime(year, month, calendar.monthrange(year, month)[1])
    achievement_date = st.date_input("تاريخ الإنجاز الفعلي", value=default_date_val)
    achievement_desc = st.text_area("وصف الإنجاز بالتفصيل", height=100, key="achievement_desc_input") # Reduced height slightly

    # Select Estimated Hour Range
    selected_hour_range = st.selectbox( "نطاق الساعات المقدرة", options=HOUR_RANGES, key="hour_range_selector")

    # Select Category (Optional) - تمت الإضافة
    selected_category = st.selectbox(
        "تحديد فئة المهمة (اختياري)",
        options=INITIAL_CATEGORIES, # Use the initial list
        key="selected_category" # Bind to session state
    )

    # Optional: Select Main Task - تم تعديل العنوان والافتراضي
    selected_form_main_task_title = st.selectbox(
        "هل تنتمي هذه المهمة الجزئية إلى مهمة رئيسية؟", # Changed label
        options=list(main_task_options_for_form.keys()),
        index=0, # Default to "— بدون مهمة رئيسية —"
        key="form_main_task_selector"
    )
    form_main_id = main_task_options_for_form.get(selected_form_main_task_title)

    submit_achievement = st.form_submit_button("➕ إضافة وحفظ الإنجاز")

    if submit_achievement:
        if not achievement_desc.strip(): st.error("وصف الإنجاز مطلوب.")
        elif selected_hour_range == HOUR_RANGES[0]: st.error("الرجاء اختيار نطاق الساعات المقدرة.")
        else:
            with st.spinner("⏳ جاري حفظ الإنجاز..."):
                try:
                    # Prepare data row including the selected category
                    category_to_save = selected_category if selected_category != INITIAL_CATEGORIES[0] else '' # Save empty string if default selected

                    new_achievement_row = pd.Series({
                        "العضو": member,
                        "الإنجاز": achievement_desc.strip(),
                        "التاريخ": achievement_date.isoformat(),
                        "نطاق_الساعات_المقدرة": selected_hour_range,
                        "الفئة": category_to_save, # Save selected category
                        "main_id": form_main_id if form_main_id else ''
                    })

                    # Load the single achievements file
                    achievements_df_reloaded, achievements_sha_reloaded = load_csv(ALL_ACHIEVEMENTS_PATH, expected_cols=EXPECTED_ACHIEVEMENT_COLS)

                    # Ensure columns before concat
                    for col in EXPECTED_ACHIEVEMENT_COLS:
                         if col not in achievements_df_reloaded.columns: achievements_df_reloaded[col] = ''
                    achievements_df_reloaded['main_id'] = achievements_df_reloaded['main_id'].fillna('')

                    achievements_df_updated = pd.concat([achievements_df_reloaded, pd.DataFrame([new_achievement_row])], ignore_index=True)
                    # Ensure correct types before saving
                    achievements_df_updated['main_id'] = achievements_df_updated['main_id'].astype(str).replace('nan', '').replace('None','')
                    achievements_df_updated['الفئة'] = achievements_df_updated['الفئة'].astype(str).fillna('') # Ensure category is string

                    commit_message = f"إضافة إنجاز بواسطة {member} ({achievement_date.isoformat()})"
                    # Save to the single file
                    if save_csv(ALL_ACHIEVEMENTS_PATH, achievements_df_updated, achievements_sha_reloaded, commit_message, expected_cols=EXPECTED_ACHIEVEMENT_COLS):
                        st.success(f"✅ تم حفظ الإنجاز بنجاح!")
                        time.sleep(1); st.rerun()
                    else: st.error("❌ حدث خطأ أثناء حفظ الإنجاز.")
                except Exception as e: show_error("خطأ في إضافة الإنجاز", traceback.format_exc())


# --- Display Existing Achievements (from Single File) ---
st.header(f"2. الإنجازات المسجلة ({member} - {ARABIC_MONTHS.get(month, month)} {year})")
try:
    # Load the single achievements file
    achievements_df_display, achievements_sha_display = load_csv(ALL_ACHIEVEMENTS_PATH, expected_cols=EXPECTED_ACHIEVEMENT_COLS)

    if not achievements_df_display.empty:
        # Convert date and fill NAs
        achievements_df_display['التاريخ_dt'] = pd.to_datetime(achievements_df_display['التاريخ'], errors='coerce')
        achievements_df_display['main_id'] = achievements_df_display['main_id'].fillna('')
        achievements_df_display['الفئة'] = achievements_df_display['الفئة'].fillna('') # Fill NA for category too

        # Create id-to-title map (using the already loaded main_df)
        id_to_title_map = {None: "— بدون مهمة رئيسية —", '': "— بدون مهمة رئيسية —"}
        if not main_df.empty: id_to_title_map.update(main_df.fillna('').set_index('id')['title'].to_dict())

        # Filter the single DataFrame by member, year, and month
        my_tasks_display_df = achievements_df_display[
            (achievements_df_display["العضو"] == member) &
            (achievements_df_display['التاريخ_dt'].notna()) &
            (achievements_df_display['التاريخ_dt'].dt.year == year) &
            (achievements_df_display['التاريخ_dt'].dt.month == month)
        ].copy()
        # Get the original index from the main DataFrame before sorting
        my_tasks_display_df['original_index'] = my_tasks_display_df.index
        my_tasks_display_df = my_tasks_display_df.sort_values(by='التاريخ_dt', ascending=False) # Sort but keep original index

        if my_tasks_display_df.empty:
            st.caption("لا توجد إنجازات مسجلة لهذا العضو في هذا الشهر وهذه السنة.")
        else:
            st.write(f"إجمالي الإنجازات المعروضة: {len(my_tasks_display_df)}")
            # Iterate using the index of the filtered dataframe
            for i in my_tasks_display_df.index:
                original_df_index = my_tasks_display_df.loc[i, 'original_index'] # Get original index for deletion
                with st.container():
                     st.markdown("<div class='achievement-display'>", unsafe_allow_html=True)
                     col1, col2 = st.columns([0.9, 0.1])
                     with col1:
                        achievement_desc = my_tasks_display_df.loc[i].get('الإنجاز', "")
                        achievement_date_dt = my_tasks_display_df.loc[i].get('التاريخ_dt')
                        achievement_date_str = achievement_date_dt.strftime('%Y-%m-%d') if pd.notna(achievement_date_dt) else my_tasks_display_df.loc[i].get('التاريخ', "غير معروف")
                        hour_range_display = my_tasks_display_df.loc[i].get('نطاق_الساعات_المقدرة', 'غير محدد')
                        category_display = my_tasks_display_df.loc[i].get('الفئة', 'غير محدد') # Get category
                        task_main_id = my_tasks_display_df.loc[i].get('main_id', '')
                        main_task_title_display = id_to_title_map.get(task_main_id, f"({task_main_id})") if task_main_id else "— بدون مهمة رئيسية —"


                        st.markdown(f"**{achievement_desc}**")
                        # Updated caption to include Category
                        st.markdown(f"<span class='caption'>التاريخ: {achievement_date_str} | الساعات المقدرة: {hour_range_display} | الفئة: {category_display or 'غير محدد'}<br>المهمة الرئيسية: {main_task_title_display}</span>", unsafe_allow_html=True)

                     with col2:
                        # Use the original index for the key and deletion logic
                        delete_key = f"del-{original_df_index}"
                        if st.button("🗑️", key=delete_key, help="حذف هذا الإنجاز"):
                            # Use the main achievements_df_display for dropping
                            if original_df_index in achievements_df_display.index:
                                achievement_to_delete = achievements_df_display.loc[original_df_index, 'الإنجاز']
                                # Drop using the original index from the main loaded df
                                achievements_df_updated_del = achievements_df_display.drop(index=original_df_index)
                                # Drop the temporary datetime column before saving
                                if 'التاريخ_dt' in achievements_df_updated_del.columns:
                                     achievements_df_updated_del = achievements_df_updated_del.drop(columns=['التاريخ_dt'])

                                # Save the updated single file
                                if save_csv(ALL_ACHIEVEMENTS_PATH, achievements_df_updated_del, achievements_sha_display, f"حذف إنجاز '{achievement_to_delete}' بواسطة {member}", expected_cols=EXPECTED_ACHIEVEMENT_COLS):
                                    st.success("تم حذف الإنجاز بنجاح.")
                                    time.sleep(1); st.rerun()
                                else: st.error("حدث خطأ أثناء حذف الإنجاز.")
                            else: st.error("لم يتم العثور على الإنجاز المراد حذفه (قد يكون تم حذفه بالفعل).")
                     st.markdown("</div>", unsafe_allow_html=True)
    else:
         # Handle case where the single CSV file exists but is empty
         if achievements_sha_display is not None: # Check if sha exists (meaning file was found but empty)
              st.caption("ملف الإنجازات فارغ.")
         # Otherwise, load_csv already showed a warning if the file wasn't found

except Exception as e:
    show_error("خطأ في تحميل أو عرض الإنجازات", traceback.format_exc())


# --- Optional: Section to Add/Manage Main Tasks ---
with st.expander("إدارة المهام الرئيسية (إضافة/تعديل)"):
    st.subheader("إضافة مهمة رئيسية جديدة")
    with st.form("add_main_task_form_expander"):
        new_title_exp = st.text_input("عنوان المهمة الرئيسية الجديدة", key="new_title_exp")
        new_descr_exp = st.text_area("وصف مختصر للمهمة (اختياري)", key="new_descr_exp")
        submitted_exp = st.form_submit_button("حفظ المهمة الرئيسية")
        if submitted_exp:
            main_df_reloaded, main_sha_reloaded = load_csv(MAIN_TASKS_PATH, expected_cols=EXPECTED_MAIN_TASK_COLS)
            main_task_titles_reloaded = main_df_reloaded["title"].tolist() if "title" in main_df_reloaded.columns else []

            if not new_title_exp.strip(): st.error("عنوان المهمة مطلوب.")
            elif new_title_exp in main_task_titles_reloaded: st.error("المهمة موجودة بالفعل.")
            else:
                new_id_exp = str(uuid.uuid4())[:8]
                new_row_exp = pd.DataFrame([{"id": new_id_exp, "title": new_title_exp, "descr": new_descr_exp}])
                if main_df_reloaded.empty: main_df_exp_updated = new_row_exp
                else: main_df_exp_updated = pd.concat([main_df_reloaded, new_row_exp], ignore_index=True)

                if save_csv(MAIN_TASKS_PATH, main_df_exp_updated, main_sha_reloaded, f"إضافة مهمة رئيسية: {new_title_exp}", expected_cols=EXPECTED_MAIN_TASK_COLS):
                    st.success(f"تمت إضافة المهمة '{new_title_exp}'.")
                    time.sleep(1); st.rerun()
                else: st.error("خطأ في حفظ المهمة الرئيسية.")

    st.subheader("المهام الرئيسية الحالية")
    if not main_df.empty:
         st.dataframe(main_df.fillna('')[["title", "descr"]].rename(columns={"title": "العنوان", "descr": "الوصف"}), use_container_width=True)
    else:
         st.caption("لا توجد مهام رئيسية معرفة حتى الآن.")

