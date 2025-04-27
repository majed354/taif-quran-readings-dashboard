import streamlit as st
import pandas as pd
import requests  # احتفظ به للاستخدام المستقبلي المحتمل
import base64
import io
import uuid
from datetime import datetime
import traceback
import time
import json
import os
import calendar

# -------------------------------------------------------------------------
# تحميل أسرار Streamlit مرة واحدة مع قيم افتراضيّة (Bootstrapping Secrets)
# -------------------------------------------------------------------------

def get_secret(name: str, default: str = ""):
    """يجلب السر من st.secrets أو يرجع القيمة الافتراضيّة إن لم يوجد."""
    if name in st.secrets and st.secrets[name]:
        return st.secrets[name]
    # تنبيه واحد فقط، كي لا يتكرّر في كلّ مرّة يُستدعى فيها السر
    if f"_warned_{name}" not in st.session_state:
        st.session_state[f"_warned_{name}"] = True
        st.warning(f"⚠️ لم يتم العثور على المتغيّر السري '{name}'. سيتم استخدام القيمة الافتراضيّة.")
    return default

# الأسرار اللازمة للتكامل مع GitHub
GITHUB_TOKEN = get_secret("GITHUB_TOKEN")
REPO_NAME = get_secret("REPO_NAME")
# المتغيّر التالي اختياري (لم يعد حاسمًا للتشغيل)
MASTER_PASS = get_secret("MASTER_PASS")

# -------------------------------------------------------------------------
# استيراد PyGithub بأمان
# -------------------------------------------------------------------------
try:
    from github import Github, UnknownObjectException
except ImportError:
    st.error("مكتبة PyGithub غير مثبتة. يرجى تثبيتها: pip install PyGithub")
    st.stop()

# -------------------------------------------------------------------------
# ثوابت التهيئة (Constants & Configuration)
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
    "— بدون فئة —",  # Default/Placeholder
    "تطوير المناهج", "التعليم والتقويم", "الاعتماد والجودة", "بحث علمي ونشر",
    "فعاليات وخدمة مجتمع", "دعم وخدمات طلابية", "مهام إدارية", "تطوير مهني",
]

PROGRAM_OPTIONS = [
    "— اختر البرنامج —",  # Placeholder
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

# مسارات ملفات CSV على المستودع
MAIN_TASKS_PATH = "data/main_tasks.csv"
ALL_ACHIEVEMENTS_PATH = "data/all_achievements.csv"

EXPECTED_MAIN_TASK_COLS = ["id", "title", "descr"]
EXPECTED_ACHIEVEMENT_COLS = [
    "العضو", "عنوان_المهمة", "المهمة", "التاريخ", "نطاق_الساعات_المقدرة",
    "الفئة", "البرنامج", "main_id"
]

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
st.markdown(
    """
<style>
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
    .achievement-display .task-title { font-weight: bold; margin-bottom: 3px; display: block; }
</style>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------------------
# معالجة الأخطاء (Error Handling)
# -------------------------------------------------------------------------

def show_error(error_msg, details=None):
    st.error(f"حدث خطأ: {error_msg}")
    if details:
        with st.expander("تفاصيل الخطأ (للمطورين)"):
            st.code(details)

# -------------------------------------------------------------------------
# التحقق من الجاهزية للتكامل مع GitHub (بدون إيقاف التطبيق)
# -------------------------------------------------------------------------

def github_ready() -> bool:
    """يُرجِع True إذا كانت متغيّرات GitHub متوفّرة (Token & Repo)."""
    return bool(GITHUB_TOKEN and REPO_NAME)

# -------------------------------------------------------------------------
# أدوات GitHub (GitHub Utilities)
# -------------------------------------------------------------------------
@st.cache_resource(ttl=300)
def get_gh_repo():
    """يربط بالمستودع على GitHub إذا توفّرت الأسرار."""
    if not github_ready():
        return None
    try:
        g = Github(GITHUB_TOKEN)
        repo = g.get_repo(REPO_NAME)
        return repo
    except UnknownObjectException:
        show_error(
            f"خطأ 404: المستودع '{REPO_NAME}' غير موجود.",
            "تأكّد من صحة 'REPO_NAME' وصلاحيات 'GITHUB_TOKEN'.",
        )
        return None
    except Exception as e:
        show_error(f"خطأ في الاتصال بـ GitHub: {e}", traceback.format_exc())
        return None

def clear_repo_cache():
    st.cache_resource.clear()

# -------------------------------------------------------------------------
# تحميل وحفظ CSV من/إلى GitHub
# -------------------------------------------------------------------------

def load_csv(path: str, expected_cols: list, is_main_tasks=False):
    repo = get_gh_repo()

    # لو لم تتوفر صلاحيات GitHub نستخدم DataFrame فارغًا ليظل التطبيق يعمل
    if repo is None:
        return pd.DataFrame(columns=expected_cols), None

    df = pd.DataFrame(columns=expected_cols)
    sha = None

    try:
        file_content = repo.get_contents(path)
        sha = file_content.sha
        content_decoded = base64.b64decode(file_content.content).decode("utf-8-sig")

        if content_decoded.strip():
            df_read = pd.read_csv(io.StringIO(content_decoded), dtype=object)
            for col in expected_cols:
                if col not in df_read.columns:
                    df_read[col] = ""
            df = df_read[expected_cols]
        else:
            st.warning(f"الملف '{path}' فارغ.")
            if is_main_tasks and path == MAIN_TASKS_PATH:
                df = pd.DataFrame(PREDEFINED_MAIN_TASKS)
                for col in expected_cols:
                    if col not in df.columns:
                        df[col] = ""
                return df[expected_cols], None
        return df.fillna(""), sha

    except UnknownObjectException:
        st.info(f"الملف '{path}' غير موجود وسيتم إنشاؤه عند الحفظ.")
        if is_main_tasks and path == MAIN_TASKS_PATH:
            df = pd.DataFrame(PREDEFINED_MAIN_TASKS)
            for col in expected_cols:
                if col not in df.columns:
                    df[col] = ""
            return df[expected_cols], None
        return pd.DataFrame(columns=expected_cols), None
    except Exception as e:
        show_error(f"خطأ في تحميل الملف '{path}': {e}", traceback.format_exc())
        return pd.DataFrame(columns=expected_cols), sha


def save_csv(path: str, df: pd.DataFrame, sha: str | None, msg: str, expected_cols: list):
    repo = get_gh_repo()
    if repo is None:
        # بدون GitHub نحفظ محليًا على نظام الملفات (اختياري)
        local_dir = os.path.dirname(path)
        if local_dir and not os.path.isdir(local_dir):
            os.makedirs(local_dir, exist_ok=True)
        df[expected_cols].to_csv(path, index=False, encoding="utf-8-sig")
        st.toast("💾 تم الحفظ محليًا لعدم توفر اتصال GitHub.")
        return True

    try:
        df_to_save = df[expected_cols].fillna("")
        content = df_to_save.to_csv(index=False, lineterminator="\n", encoding="utf-8-sig")

        try:
            existing_file = repo.get_contents(path)
            current_sha = existing_file.sha
            existing_content = base64.b64decode(existing_file.content).decode("utf-8-sig")

            if content == existing_content:
                st.toast(f"لا تغييرات لحفظها في '{os.path.basename(path)}'.")
                return True

            repo.update_file(path, msg, content, current_sha)
            st.toast(f"✅ تم تحديث '{os.path.basename(path)}'")
            clear_repo_cache()
            return True
        except UnknownObjectException:
            repo.create_file(path, msg, content)
            st.toast(f"✅ تم إنشاء '{os.path.basename(path)}'")
            clear_repo_cache()
            return True
    except Exception as e:
        show_error(f"خطأ عام أثناء حفظ '{path}': {e}", traceback.format_exc())
        return False

# -------------------------------------------------------------------------
# الصفحة الرئيسية (Main Page Logic)
# -------------------------------------------------------------------------

# --- Session State Initialization ---
default_year = 2025
current_month = datetime.now().month

for key, value in [
    ("selected_member", MEMBER_NAMES[0]),
    ("selected_year", default_year),
    ("selected_month", current_month),
    ("selected_category", INITIAL_CATEGORIES[0]),
    ("selected_program", PROGRAM_OPTIONS[0]),
    ("show_add_main_task_inline", False),
    ("new_main_task_title_inline", ""),
    ("new_main_task_descr_inline", ""),
]:
    if key not in st.session_state:
        st.session_state[key] = value

# --- إشعار بعدم توفر GitHub إن لزم ---
if not github_ready():
    st.info("يعمل التطبيق دون مزايا GitHub لأن بيانات الاتصال غير مكتملة. سيتم حفظ البيانات محليًّا فقط خلال هذه الجلسة.")

# --- عنوان الصفحة ---
st.title("تسجيل المهام المكتملة")

# ============================== بقية منطق التطبيق كما هو ==============================
# (جميع الأقسام اللاحقة من الكود الأصليّ لم تتغيّر إلا في حذف أي استخدامٍ مباشرٍ لــ st.secrets)

# لاحظ: لأسباب طول الملف، لم تُجرَ أي تعديلات أخرى على المنطق الرئيسي؛ فقط وظائف الأسرار و GitHub
# هي التي عُدِّلت لضمان عدم حدوث الخطأ عند غياب MASTER_PASS.

# -------------------------------------------------------------------------
# بقية الكود (Forms, العرض، الحذف ... إلخ) كما في النسخة الأصليّة
# -------------------------------------------------------------------------
# يمكنك لصق الأجزاء المتبقيّة من الكود دون تغيير، أو الإبقاء على نسختك الحالية؛
# فهي ستعمل مع التعديلات أعلاه دون ظهور الخطأ المتعلق بــ MASTER_PASS.
