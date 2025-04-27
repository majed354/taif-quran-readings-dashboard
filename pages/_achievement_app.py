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

INITIAL_CATEGORIES = [
    "— بدون فئة —", # Default/Placeholder
    "تطوير المناهج", "التعليم والتقويم", "الاعتماد والجودة", "بحث علمي ونشر",
    "فعاليات وخدمة مجتمع", "دعم وخدمات طلابية", "مهام إدارية", "تطوير مهني",
    # "➕ إضافة فئة أخرى..." # Option to add later if needed
]

PROGRAM_OPTIONS = [
    "— اختر البرنامج —", # Placeholder
    "بكالوريوس القراءات",
    "بكالوريوس القرآن وعلومه",
    "ماجستير الدراسات القرآنية المعاصرة",
    "ماجستير القراءات",
    "دكتوراه علوم القرآن",
    "دكتوراه القراءات",
    "غير مرتبط ببرنامج",
    "جميع البرامج"
]


ARABIC_MONTHS = {
    1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل", 5: "مايو", 6: "يونيو",
    7: "يوليو", 8: "أغسطس", 9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
}

# Single CSV file paths
MAIN_TASKS_PATH = "data/main_tasks.csv"
ALL_ACHIEVEMENTS_PATH = "data/all_achievements.csv"

# Expected columns
EXPECTED_MAIN_TASK_COLS = ["id", "title", "descr"]
EXPECTED_ACHIEVEMENT_COLS = ["العضو", "عنوان_المهمة", "المهمة", "التاريخ", "نطاق_الساعات_المقدرة", "الفئة", "البرنامج", "main_id"]

PREDEFINED_MAIN_TASKS = [
    {"id": "predef001", "title": "توصيف مقررات", "descr": "إعداد أو تحديث توصيف المقررات الدراسية"},
    {"id": "predef002", "title": "توصيف برنامج", "descr": "إعداد أو تحديث توصيف البرامج الأكاديمية"},
    {"id": "predef003", "title": "الاعتماد الأكاديمي", "descr": "المشاركة في أعمال لجان ومتطلبات الاعتماد الأكاديمي"},
    {"id": "predef004", "title": "مبادرة التحول", "descr": "المشاركة في المبادرات المتعلقة بالتحول الرقمي أو المؤسسي"},
    {"id": "predef005", "title": "المراجعة الشاملة", "descr": "المشاركة في أعمال المراجعة الشاملة للبرامج أو القسم"},
    {"id": "predef006", "title": "مراقبة سير الاختبارات", "descr": "المشاركة في مراقبة وتنظيم سير الاختبارات"},
]

# -------------------------------------------------------------------------
# تهيئة الواجهة (UI Initialization)
# -------------------------------------------------------------------------
st.set_page_config("تسجيل المهام المكتملة", layout="centered")
st.markdown("""
<style>
    /* CSS remains largely the same */
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
    .stButton>button[help="حذف هذه المهمة"] { display: flex; justify-content: center; align-items: center; padding: 4px; line-height: 1; background-color: #f44336; }
    .stButton>button[help="حذف هذه المهمة"]:hover { background-color: #d32f2f; }
    .stTabs [data-baseweb="tab-list"] { direction: rtl; }
    .approx-date-header { font-weight: bold; margin-bottom: 5px; text-align: center; }
    .achievement-display { border: 1px solid #e0e0e0; border-radius: 5px; padding: 10px; margin-bottom: 10px; background-color: #fafafa; }
    .achievement-display .caption { color: #555; font-size: 0.9em; }
    .achievement-display .task-title { font-weight: bold; margin-bottom: 3px; display: block; } /* Style for task title */
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
# التحقق من المتغيرات المطلوبة (Check Required Environment Variables) - تم التحديث
# -------------------------------------------------------------------------
def check_environment():
    """Checks if necessary GitHub secrets are set."""
    try:
        # Only check for GitHub related secrets now
        required_vars = ["GITHUB_TOKEN", "REPO_NAME"]
        missing_vars = [var for var in required_vars if var not in st.secrets]
        if missing_vars:
            show_error(f"متغيرات GitHub المطلوبة غير موجودة: {', '.join(missing_vars)}", "أضفها إلى ملف .streamlit/secrets.toml.")
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
    """Connects to the GitHub repository."""
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

def load_csv(path: str, expected_cols: list, is_main_tasks=False):
    """Loads a CSV file from GitHub, ensuring expected columns exist."""
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
                df_read = pd.read_csv(io.StringIO(content_decoded), dtype=object)
                cols_added_warning = False
                for col in expected_cols:
                    if col not in df_read.columns:
                        df_read[col] = ''
                        cols_added_warning = True
                if cols_added_warning:
                     st.warning(f"تمت إضافة أعمدة مفقودة إلى DataFrame عند تحميل '{path}'. قد تحتاج لمراجعة الملف على GitHub.")
                df = df_read[expected_cols]
            except Exception as read_err:
                 show_error(f"خطأ عند قراءة CSV '{path}': {read_err}", traceback.format_exc())
                 return pd.DataFrame(columns=expected_cols), sha
        else:
             # Keep warning, but handle predefined tasks only if file is truly empty on load
             st.warning(f"الملف '{path}' فارغ أو يحتوي فقط على مسافات بيضاء.")
             if is_main_tasks and path == MAIN_TASKS_PATH:
                 st.info("ملف المهام الرئيسية فارغ. سيتم إضافة مهام أولية.")
                 df = pd.DataFrame(PREDEFINED_MAIN_TASKS)
                 # Make sure the predefined df has the expected columns
                 for col in expected_cols:
                     if col not in df.columns: df[col] = ''
                 return df[expected_cols], None # Return df with predefined tasks, sha=None to force save

        df = df.fillna('')
        return df, sha

    except UnknownObjectException:
        st.warning(f"الملف '{path}' غير موجود، سيتم إنشاؤه.")
        if is_main_tasks and path == MAIN_TASKS_PATH:
            st.info("ملف المهام الرئيسية غير موجود. سيتم إنشاؤه بمهام أولية.")
            df = pd.DataFrame(PREDEFINED_MAIN_TASKS)
            # Make sure the predefined df has the expected columns
            for col in expected_cols:
                if col not in df.columns: df[col] = ''
            return df[expected_cols], None
        else:
            return pd.DataFrame(columns=expected_cols), None
    except Exception as e:
        show_error(f"خطأ في تحميل الملف '{path}': {e}", traceback.format_exc())
        return pd.DataFrame(columns=expected_cols), sha

def save_csv(path: str, df: pd.DataFrame, sha: str | None, msg: str, expected_cols: list):
    """Saves the DataFrame to the CSV file, ensuring only expected columns."""
    repo = get_gh_repo()
    if not repo: return False

    try:
        df_to_save = df[expected_cols].copy()
        df_to_save = df_to_save.fillna('')
        content = df_to_save.to_csv(index=False, lineterminator="\n", encoding="utf-8-sig")

        try:
            existing_file = repo.get_contents(path)
            current_sha = existing_file.sha
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
            folder_path = os.path.dirname(path)
            if folder_path and folder_path != '.': pass
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

# -------------------------------------------------------------------------
# الصفحة الرئيسية (Main Page Logic)
# -------------------------------------------------------------------------

# --- Session State Initialization ---
default_year = 2025
current_month = datetime.now().month
# Removed auth state
if "selected_member" not in st.session_state: st.session_state.selected_member = MEMBER_NAMES[0]
if "selected_year" not in st.session_state: st.session_state.selected_year = default_year
if "selected_month" not in st.session_state: st.session_state.selected_month = current_month
if "selected_category" not in st.session_state: st.session_state.selected_category = INITIAL_CATEGORIES[0]
if "selected_program" not in st.session_state: st.session_state.selected_program = PROGRAM_OPTIONS[0]
if "show_add_main_task_inline" not in st.session_state: st.session_state.show_add_main_task_inline = False
if "new_main_task_title_inline" not in st.session_state: st.session_state.new_main_task_title_inline = ""
if "new_main_task_descr_inline" not in st.session_state: st.session_state.new_main_task_descr_inline = ""


# --- Environment Check ---
if not check_environment():
    st.warning("يرجى إصلاح مشكلات الإعداد قبل المتابعة.")
    if st.button("محاولة مسح ذاكرة التخزين المؤقت للمستودع"): clear_repo_cache(); st.rerun()
    st.stop()

# --- Login Form Removed ---

# --- Main Application ---
st.title("تسجيل المهام المكتملة")

# --- Instructions Expander ---
with st.expander("تعليمات هامة لأعضاء هيئة التدريس بقسم القراءات", expanded=False):
    st.markdown("""
    **أهلاً بكم في نظام تسجيل المهام المكتملة،،**

    يهدف هذا النظام إلى توثيق جهودكم القيمة ومتابعة إنجاز المهام المختلفة. لضمان دقة البيانات والاستفادة القصوى من النظام، يرجى اتباع التعليمات التالية عند تعبئة النموذج:

    1.  **اختيار العضو والتاريخ:** تأكد من اختيار اسمك الصحيح من القائمة، ثم حدد الشهر والسنة التقريبية التي تمت فيها المهمة (السنة الافتراضية هي 2025).
    2.  **عنوان المهمة:** أدخل عنوانًا مختصرًا وواضحًا للمهمة (مثال: "تطوير مقرر 101"، "الإشراف على طالب الماجستير").
    3.  **وصف المهمة:** قدم وصفًا تفصيليًا ودقيقًا للمهمة التي قمت بها. كلما كان الوصف أوضح، كان التقييم أدق.
    4.  **الساعات المقدرة:** اختر أقرب نطاق زمني يعكس الجهد المبذول في إنجاز المهمة.
    5.  **الفئة والبرنامج (اختياري):** يمكنك تصنيف المهمة ضمن فئة محددة أو ربطها ببرنامج أكاديمي معين إذا كان ذلك مناسبًا.
    6.  **المهمة الرئيسية (اختياري):** إذا كانت هذه المهمة جزءًا من مهمة أكبر أو مشروع مستمر (مثل "الاعتماد الأكاديمي")، يمكنك ربطها بالمهمة الرئيسية المقابلة من القائمة. يمكنك أيضًا إضافة مهمة رئيسية جديدة إذا لم تكن موجودة باختيار "➕ إضافة مهمة رئيسية…".

    **ملاحظة هامة:** سيتم مستقبلًا الاعتماد على التصنيف بالذكاء الآلي للمهام المدخلة لتحديد النقاط المستحقة لكل مهمة بناءً على الوصف ونطاق الساعات والفئة. لذا، فإن دقة البيانات المدخلة أساسية لضمان تقييم عادل ومنصف لجهودكم.

    **شكرًا لتعاونكم.**
    """)


# --- User & Date Selection ---
st.selectbox("اختر اسم العضو", options=MEMBER_NAMES, key="selected_member")
st.markdown("<div class='approx-date-header'>التاريخ التقريبي للمهام</div>", unsafe_allow_html=True)
col_month, col_year = st.columns(2)
with col_month: st.selectbox("الشهر", options=list(ARABIC_MONTHS.keys()), format_func=lambda m: ARABIC_MONTHS[m], key="selected_month")
with col_year: st.number_input("السنة", min_value=2010, max_value=default_year + 5, value=st.session_state.selected_year, key="selected_year", step=1)

# --- Sidebar ---
# Removed Logout button
with st.sidebar:
    st.header("الإجراءات")
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
main_df, main_sha = load_csv(MAIN_TASKS_PATH, expected_cols=EXPECTED_MAIN_TASK_COLS, is_main_tasks=True)
if main_sha is None and not main_df.empty:
     if save_csv(MAIN_TASKS_PATH, main_df, None, "إضافة المهام الرئيسية الأولية", expected_cols=EXPECTED_MAIN_TASK_COLS):
         st.success("تم حفظ المهام الرئيسية الأولية بنجاح.")
         main_df, main_sha = load_csv(MAIN_TASKS_PATH, expected_cols=EXPECTED_MAIN_TASK_COLS, is_main_tasks=True)
     else: st.error("فشل حفظ المهام الرئيسية الأولية.")

# Prepare options for main task dropdowns
main_task_options_for_form = { "— بدون مهمة رئيسية —": None }
add_new_main_task_option = "➕ إضافة مهمة رئيسية…"
if not main_df.empty:
     main_df_filled = main_df.fillna('')
     id_to_title_map = main_df_filled.set_index('id')['title'].to_dict()
     id_to_title_map = {k: v for k, v in id_to_title_map.items() if k and v}
     title_to_id_map = {v: k for k, v in id_to_title_map.items()}
     sorted_titles = sorted(title_to_id_map.keys())
     for title in sorted_titles:
         main_task_options_for_form[title] = title_to_id_map[title]
main_task_options_list = list(main_task_options_for_form.keys()) + [add_new_main_task_option]


# --- Add New Task Form ---
st.header("1. إضافة مهمة جديدة")
inline_form_placeholder = st.empty()

with st.form("add_task_form", clear_on_submit=False):
    task_title = st.text_input("عنوان مختصر للمهمة", key="task_title_input")
    try: default_date_val = datetime(year, month, 1)
    except ValueError: default_date_val = datetime(year, month, calendar.monthrange(year, month)[1])
    achievement_date = st.date_input("تاريخ المهمة الفعلي", value=default_date_val)
    achievement_desc = st.text_area("وصف المهمة بالتفصيل", height=100, key="achievement_desc_input")

    selected_hour_range = st.selectbox( "نطاق الساعات المقدرة", options=HOUR_RANGES, key="hour_range_selector")
    selected_category = st.selectbox("تحديد فئة المهمة (اختياري)", options=INITIAL_CATEGORIES, key="selected_category")
    selected_program = st.selectbox("تحديد البرنامج (اختياري)", options=PROGRAM_OPTIONS, key="selected_program")

    selected_form_main_task_option = st.selectbox(
        "هل تنتمي هذه المهمة الجزئية إلى مهمة رئيسية؟",
        options=main_task_options_list,
        index=0,
        key="form_main_task_selector"
    )

    if selected_form_main_task_option == add_new_main_task_option:
        st.session_state.show_add_main_task_inline = True
    else:
         st.session_state.show_add_main_task_inline = False

    submit_task = st.form_submit_button("➕ إضافة وحفظ المهمة")

# --- Display Inline Add Main Task Form (if triggered) ---
if st.session_state.show_add_main_task_inline:
     with inline_form_placeholder.container():
         st.subheader("إضافة مهمة رئيسية جديدة")
         st.session_state.new_main_task_title_inline = st.text_input("عنوان المهمة الرئيسية الجديدة", key="new_main_title_inline_standalone")
         st.session_state.new_main_task_descr_inline = st.text_area("وصف مختصر (اختياري)", key="new_main_descr_inline_standalone")
         if st.button("حفظ المهمة الرئيسية الجديدة", key="save_inline_main_task"):
             new_title_inline = st.session_state.new_main_task_title_inline.strip()
             new_descr_inline = st.session_state.new_main_task_descr_inline.strip()
             main_df_reloaded_inline, main_sha_reloaded_inline = load_csv(MAIN_TASKS_PATH, expected_cols=EXPECTED_MAIN_TASK_COLS, is_main_tasks=True)
             main_titles_reloaded_inline = main_df_reloaded_inline["title"].tolist() if "title" in main_df_reloaded_inline.columns else []

             if not new_title_inline: st.error("عنوان المهمة الرئيسية مطلوب.")
             elif new_title_inline in main_titles_reloaded_inline: st.error("هذه المهمة الرئيسية موجودة بالفعل.")
             else:
                 new_id_inline = str(uuid.uuid4())[:8]
                 new_row_inline = pd.DataFrame([{"id": new_id_inline, "title": new_title_inline, "descr": new_descr_inline}])
                 main_df_updated_inline = pd.concat([main_df_reloaded_inline, new_row_inline], ignore_index=True)
                 if save_csv(MAIN_TASKS_PATH, main_df_updated_inline, main_sha_reloaded_inline, f"إضافة مهمة رئيسية: {new_title_inline}", expected_cols=EXPECTED_MAIN_TASK_COLS):
                     st.success(f"تمت إضافة المهمة الرئيسية '{new_title_inline}'. يمكنك الآن اختيارها من القائمة في النموذج أعلاه.")
                     st.session_state.show_add_main_task_inline = False
                     st.session_state.new_main_task_title_inline = ""
                     st.session_state.new_main_task_descr_inline = ""
                     time.sleep(1); st.rerun()
                 else: st.error("خطأ في حفظ المهمة الرئيسية الجديدة.")


# --- Process Main Form Submission ---
if submit_task:
    task_title_val = st.session_state.task_title_input
    achievement_desc_val = st.session_state.achievement_desc_input
    selected_hour_range_val = st.session_state.hour_range_selector
    selected_category_val = st.session_state.selected_category
    selected_program_val = st.session_state.selected_program
    selected_form_main_task_option_val = st.session_state.form_main_task_selector
    achievement_date_val = achievement_date

    if selected_form_main_task_option_val == add_new_main_task_option:
         st.warning("لقد اخترت 'إضافة مهمة رئيسية جديدة'. يرجى إدخال تفاصيل المهمة الجديدة وحفظها أولاً، أو اختيار مهمة أخرى.")
    elif not task_title_val.strip(): st.error("عنوان مختصر للمهمة مطلوب.")
    elif not achievement_desc_val.strip(): st.error("وصف المهمة مطلوب.")
    elif selected_hour_range_val == HOUR_RANGES[0]: st.error("الرجاء اختيار نطاق الساعات المقدرة.")
    else:
        with st.spinner("⏳ جاري حفظ المهمة..."):
            try:
                form_main_id = None
                if selected_form_main_task_option_val != add_new_main_task_option:
                     form_main_id = main_task_options_for_form.get(selected_form_main_task_option_val)

                category_to_save = selected_category_val if selected_category_val != INITIAL_CATEGORIES[0] else ''
                program_to_save = selected_program_val if selected_program_val != PROGRAM_OPTIONS[0] else ''

                new_task_row = pd.Series({
                    "العضو": member,
                    "عنوان_المهمة": task_title_val.strip(),
                    "المهمة": achievement_desc_val.strip(),
                    "التاريخ": achievement_date_val.isoformat(),
                    "نطاق_الساعات_المقدرة": selected_hour_range_val,
                    "الفئة": category_to_save,
                    "البرنامج": program_to_save,
                    "main_id": form_main_id if form_main_id else ''
                })

                achievements_df_reloaded, achievements_sha_reloaded = load_csv(ALL_ACHIEVEMENTS_PATH, expected_cols=EXPECTED_ACHIEVEMENT_COLS)

                for col in EXPECTED_ACHIEVEMENT_COLS:
                     if col not in achievements_df_reloaded.columns: achievements_df_reloaded[col] = ''
                achievements_df_reloaded['main_id'] = achievements_df_reloaded['main_id'].fillna('')

                achievements_df_updated = pd.concat([achievements_df_reloaded, pd.DataFrame([new_task_row])], ignore_index=True)
                achievements_df_updated = achievements_df_updated.fillna('')
                achievements_df_updated['main_id'] = achievements_df_updated['main_id'].astype(str).replace('nan', '').replace('None','')
                achievements_df_updated['الفئة'] = achievements_df_updated['الفئة'].astype(str)
                achievements_df_updated['البرنامج'] = achievements_df_updated['البرنامج'].astype(str)

                commit_message = f"إضافة مهمة '{task_title_val.strip()}' بواسطة {member} ({achievement_date_val.isoformat()})"
                if save_csv(ALL_ACHIEVEMENTS_PATH, achievements_df_updated, achievements_sha_reloaded, commit_message, expected_cols=EXPECTED_ACHIEVEMENT_COLS):
                    st.success(f"✅ تم حفظ المهمة بنجاح!")
                    st.session_state.task_title_input = ""
                    st.session_state.achievement_desc_input = ""
                    st.session_state.hour_range_selector = HOUR_RANGES[0]
                    st.session_state.selected_category = INITIAL_CATEGORIES[0]
                    st.session_state.selected_program = PROGRAM_OPTIONS[0]
                    st.session_state.form_main_task_selector = list(main_task_options_for_form.keys())[0]
                    time.sleep(1); st.rerun()
                else: st.error("❌ حدث خطأ أثناء حفظ المهمة.")
            except Exception as e: show_error("خطأ في إضافة المهمة", traceback.format_exc())


# --- Display Existing Tasks ---
st.header(f"2. المهام المسجلة ({member} - {ARABIC_MONTHS.get(month, month)} {year})")
try:
    achievements_df_display, achievements_sha_display = load_csv(ALL_ACHIEVEMENTS_PATH, expected_cols=EXPECTED_ACHIEVEMENT_COLS)

    if not achievements_df_display.empty:
        achievements_df_display['التاريخ_dt'] = pd.to_datetime(achievements_df_display['التاريخ'], errors='coerce')
        achievements_df_display = achievements_df_display.fillna('')

        id_to_title_map_display = {None: "— بدون مهمة رئيسية —", '': "— بدون مهمة رئيسية —"}
        if not main_df.empty: id_to_title_map_display.update(main_df.fillna('').set_index('id')['title'].to_dict())

        my_tasks_display_df = achievements_df_display[
            (achievements_df_display["العضو"] == member) &
            (achievements_df_display['التاريخ_dt'].notna()) &
            (achievements_df_display['التاريخ_dt'].dt.year == year) &
            (achievements_df_display['التاريخ_dt'].dt.month == month)
        ].copy()
        my_tasks_display_df['original_index'] = my_tasks_display_df.index
        my_tasks_display_df = my_tasks_display_df.sort_values(by='التاريخ_dt', ascending=False)

        if my_tasks_display_df.empty:
            st.caption("لا توجد مهام مسجلة لهذا العضو في هذا الشهر وهذه السنة.")
        else:
            st.write(f"إجمالي المهام المعروضة: {len(my_tasks_display_df)}")
            for i in my_tasks_display_df.index:
                original_df_index = my_tasks_display_df.loc[i, 'original_index']
                with st.container():
                     st.markdown("<div class='achievement-display'>", unsafe_allow_html=True)
                     col1, col2 = st.columns([0.9, 0.1])
                     with col1:
                        task_title_display = my_tasks_display_df.loc[i].get('عنوان_المهمة', '')
                        task_desc_display = my_tasks_display_df.loc[i].get('المهمة', "")
                        achievement_date_dt = my_tasks_display_df.loc[i].get('التاريخ_dt')
                        achievement_date_str = achievement_date_dt.strftime('%Y-%m-%d') if pd.notna(achievement_date_dt) else my_tasks_display_df.loc[i].get('التاريخ', "غير معروف")
                        hour_range_display = my_tasks_display_df.loc[i].get('نطاق_الساعات_المقدرة', 'غير محدد')
                        category_display = my_tasks_display_df.loc[i].get('الفئة', 'غير محدد')
                        program_display = my_tasks_display_df.loc[i].get('البرنامج', 'غير محدد')
                        task_main_id = my_tasks_display_df.loc[i].get('main_id', '')
                        main_task_title_display = id_to_title_map_display.get(task_main_id, f"({task_main_id})") if task_main_id else "— بدون مهمة رئيسية —"

                        display_title = task_title_display if task_title_display else f"{task_desc_display[:50]}..." if task_desc_display else "مهمة بدون عنوان"
                        st.markdown(f"<span class='task-title'>{display_title}</span>", unsafe_allow_html=True)
                        if task_desc_display and (task_desc_display != task_title_display or len(task_title_display) < 20):
                             st.markdown(f"{task_desc_display}")

                        st.markdown(f"<span class='caption'>التاريخ: {achievement_date_str} | الساعات: {hour_range_display} | الفئة: {category_display or 'غير محدد'} | البرنامج: {program_display or 'غير محدد'}<br>المهمة الرئيسية: {main_task_title_display}</span>", unsafe_allow_html=True)

                     with col2:
                        delete_key = f"del-{original_df_index}"
                        if st.button("🗑️", key=delete_key, help="حذف هذه المهمة"):
                            if original_df_index in achievements_df_display.index:
                                task_to_delete_title = achievements_df_display.loc[original_df_index, 'عنوان_المهمة'] or achievements_df_display.loc[original_df_index, 'المهمة'][:20]
                                achievements_df_updated_del = achievements_df_display.drop(index=original_df_index)
                                if 'التاريخ_dt' in achievements_df_updated_del.columns:
                                     achievements_df_updated_del = achievements_df_updated_del.drop(columns=['التاريخ_dt'])

                                if save_csv(ALL_ACHIEVEMENTS_PATH, achievements_df_updated_del, achievements_sha_display, f"حذف مهمة '{task_to_delete_title}' بواسطة {member}", expected_cols=EXPECTED_ACHIEVEMENT_COLS):
                                    st.success("تم حذف المهمة بنجاح.")
                                    time.sleep(1); st.rerun()
                                else: st.error("حدث خطأ أثناء حذف المهمة.")
                            else: st.error("لم يتم العثور على المهمة المراد حذفها.")
                     st.markdown("</div>", unsafe_allow_html=True)
    else:
         if achievements_sha_display is not None: st.caption("ملف المهام فارغ.")

except Exception as e:
    show_error("خطأ في تحميل أو عرض المهام", traceback.format_exc())


# --- Optional: Section to Add/Manage Main Tasks ---
with st.expander("إدارة المهام الرئيسية (إضافة/تعديل)"):
    st.subheader("إضافة مهمة رئيسية جديدة")
    with st.form("add_main_task_form_expander"):
        new_title_exp = st.text_input("عنوان المهمة الرئيسية الجديدة", key="new_title_exp")
        new_descr_exp = st.text_area("وصف مختصر للمهمة (اختياري)", key="new_descr_exp")
        submitted_exp = st.form_submit_button("حفظ المهمة الرئيسية")
        if submitted_exp:
            main_df_reloaded, main_sha_reloaded = load_csv(MAIN_TASKS_PATH, expected_cols=EXPECTED_MAIN_TASK_COLS, is_main_tasks=True)
            main_task_titles_reloaded = main_df_reloaded["title"].tolist() if "title" in main_df_reloaded.columns else []

            if not new_title_exp.strip(): st.error("عنوان المهمة مطلوب.")
            elif new_title_exp in main_task_titles_reloaded: st.error("المهمة موجودة بالفعل.")
            else:
                new_id_exp = str(uuid.uuid4())[:8]
                new_row_exp = pd.DataFrame([{"id": new_id_exp, "title": new_title_exp, "descr": new_descr_exp}])
                main_df_exp_updated = pd.concat([main_df_reloaded, new_row_exp], ignore_index=True)

                if save_csv(MAIN_TASKS_PATH, main_df_exp_updated, main_sha_reloaded, f"إضافة مهمة رئيسية: {new_title_exp}", expected_cols=EXPECTED_MAIN_TASK_COLS):
                    st.success(f"تمت إضافة المهمة '{new_title_exp}'.")
                    time.sleep(1); st.rerun()
                else: st.error("خطأ في حفظ المهمة الرئيسية.")

    st.subheader("المهام الرئيسية الحالية")
    if not main_df.empty:
         st.dataframe(main_df.fillna('')[["title", "descr"]].rename(columns={"title": "العنوان", "descr": "الوصف"}), use_container_width=True)
    else:
         st.caption("لا توجد مهام رئيسية معرفة حتى الآن.")

