# -*- coding: utf-8 -*-

# =========================================
# القسم 1: الاستيرادات وإعدادات الصفحة
# =========================================
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import dateutil.relativedelta
import os
import numpy as np
import io # Required for CSV export
import traceback # For detailed error logging

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="لوحة إنجاز المهام | قسم القراءات", # عنوان محدث
    page_icon="📊", # أيقونة محدثة
    layout="wide"
)

# =========================================
# القسم 2: تنسيقات CSS (مع تعديلات طفيفة)
# =========================================
responsive_menu_css = """
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
    /* --- إخفاء عناصر Streamlit الافتراضية --- */
    [data-testid="stToolbar"], #MainMenu, header, footer,
    [class^="viewerBadge_"], [id^="GithubIcon"],
    [data-testid="stThumbnailsChipContainer"], .stProgress,
    [data-testid="stBottomNavBar"], [data-testid*="bottomNav"],
    [aria-label*="community"], [aria-label*="profile"],
    [title*="community"], [title*="profile"],
    h1 > div > a, h2 > div > a, h3 > div > a,
    h4 > div > a, h5 > div > a, h6 > div > a { display: none !important; visibility: hidden !important; }
    [data-testid="stSidebar"], [data-testid="stSidebarNavToggler"], [data-testid="stSidebarCollapseButton"] { display: none !important; }

    /* --- تطبيق الخط العربي و RTL --- */
    * { font-family: 'Tajawal', sans-serif !important; }
    .stApp { direction: rtl; text-align: right; }

    /* --- تنسيق شريط التنقل العلوي (للسطح المكتب) --- */
    .top-navbar {
        background-color: #f8f9fa; padding: 0.4rem 1rem; border-bottom: 1px solid #e7e7e7;
        width: 100%; box-sizing: border-box; margin-bottom: 1rem; /* Add margin below navbar */
    }
    .top-navbar ul { list-style: none; padding: 0; margin: 0; display: flex; justify-content: flex-start; align-items: center; flex-wrap: wrap; }
    .top-navbar li { position: relative; margin-left: 1rem; margin-bottom: 0.2rem; }
    .top-navbar li:first-child { margin-right: 0; }
    .top-navbar a { text-decoration: none; color: #333; padding: 0.3rem 0.1rem; display: block; font-weight: 500; white-space: nowrap; font-size: 0.9rem; }
    .top-navbar a:hover { color: #1e88e5; }

    /* --- تنسيق زر وقائمة البرجر (للجوال) --- */
    .mobile-menu-trigger {
        display: none; position: fixed; top: 8px; right: 12px; z-index: 1001;
        cursor: pointer; background-color: #1e88e5; color: white;
        padding: 5px 9px; border-radius: 5px; font-size: 1.2rem; line-height: 1;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .mobile-menu-checkbox { display: none; }
    .mobile-menu {
        display: none; position: fixed; top: 0; right: 0;
        width: 230px; height: 100%; background-color: #f8f9fa;
        z-index: 1000; padding: 50px 15px 15px 15px;
        box-shadow: -2px 0 5px rgba(0,0,0,0.1);
        transition: transform 0.3s ease-in-out;
        transform: translateX(100%); overflow-y: auto;
    }
    .mobile-menu ul { list-style: none; padding: 0; margin: 0; }
    .mobile-menu li { margin-bottom: 0.3rem; }
    .mobile-menu a { text-decoration: none; color: #333; padding: 8px 5px; display: block; font-weight: 500; border-bottom: 1px solid #eee; font-size: 0.9rem; }
    .mobile-menu a:hover { color: #1e88e5; background-color: #eee; }

    /* --- إظهار قائمة البرجر عند تفعيل الـ checkbox --- */
    .mobile-menu-checkbox:checked ~ .mobile-menu { display: block; transform: translateX(0); }
    .mobile-menu-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.4); z-index: 999; }
    .mobile-menu-checkbox:checked ~ .mobile-menu-overlay { display: block; }

    /* --- تنسيقات عامة --- */
    h1,h2,h3, h4 { color: #1e88e5; font-weight: 600; }
    h1 { padding-bottom: 10px; border-bottom: 1px solid #1e88e5; margin-bottom: 20px; font-size: calc(1.1rem + 0.6vw); } /* Slightly smaller H1 */
    h2 { margin-top: 25px; margin-bottom: 15px; font-size: calc(1rem + 0.4vw); }
    h3 { margin-top: 20px; margin-bottom: 10px; font-size: calc(0.9rem + 0.2vw); }
    h4 { margin-top: 15px; margin-bottom: 8px; font-size: calc(0.9rem + 0.1vw); color: #333; } /* Sub-headers within tabs */

    .metric-card { background-color: white; border-radius: 8px; padding: 15px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08); text-align: center; margin-bottom: 15px; height: 100%; display: flex; flex-direction: column; justify-content: center; } /* Ensure cards have same height in a row */
    .chart-container { background-color: white; border-radius: 8px; padding: 15px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08); margin-bottom: 15px; width: 100%; overflow: hidden; }
    .stSelectbox label, .stMultiselect label, .stRadio label { font-weight: 500; font-size: 0.9rem; } /* Slightly smaller filter labels */
    .stButton>button { background-color: #1e88e5; color: white; border-radius: 5px; padding: 0.3rem 1rem;}
    .stButton>button:hover { background-color: #1565c0; color: white;}

    .back-to-top { position: fixed; bottom: 15px; left: 15px; width: 35px; height: 35px; background-color: #1e88e5; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; z-index: 998; cursor: pointer; box-shadow: 0 2px 5px rgba(0,0,0,0.2); opacity: 0; transition: opacity 0.3s, transform 0.3s; transform: scale(0); }
    .back-to-top.visible { opacity: 1; transform: scale(1); }
    .back-to-top span { font-size: 1rem; }

    /* خطوط المقاييس داخل البطاقات */
    [data-testid="stMetricValue"] { font-size: 1.8rem !important; font-weight: 600; color: #1e88e5; }
    [data-testid="stMetricLabel"] { font-size: 0.85rem !important; color: #555; }
    [data-testid="stMetricDelta"] { font-size: 0.8rem !important; } /* Style delta if used */

    /* تنسيق الجداول */
    .stDataFrame, .stDataEditor { width: 100%; }
    .stDataFrame table, .stDataEditor table { width: 100%; }

    /* تنسيق مستوى الإنجاز المرتبط بالفئة */
    .level-category-display .level-name {
        font-weight: bold;
        font-size: 1.1em; /* أكبر قليلاً */
    }
    .level-category-display .category-name {
        font-size: 0.9em;
        color: #555;
    }

    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background-color: #1e88e5; /* Blue progress bar */
    }

    /* Heatmap styling */
    .plotly-heatmap .colorbar { margin-left: 10px !important; } /* Add space for heatmap colorbar */

    /* --- قواعد Media Query للتبديل بين القائمتين وتحسين عرض الجوال --- */
    @media only screen and (max-width: 768px) {
        .top-navbar { display: none; }
        .mobile-menu-trigger { display: block; }
        .main .block-container { padding-right: 0.8rem !important; padding-left: 0.8rem !important; padding-top: 40px !important; }

        h1 { font-size: 1.4rem; }
        h2 { font-size: 1.2rem; }
        h3 { font-size: 1.1rem; }
        h4 { font-size: 1.0rem; }

        [data-testid="stMetricValue"] { font-size: 1.5rem !important; }
        [data-testid="stMetricLabel"] { font-size: 0.8rem !important; }
        .metric-card { padding: 10px; margin-bottom: 10px;}

        button[data-baseweb="tab"] {
            font-size: 0.8rem !important; /* Smaller tab font */
            padding: 6px 8px !important; /* Adjust padding */
        }
        .stSelectbox label, .stRadio label { font-size: 0.85rem !important; }
        .stTextInput label { font-size: 0.85rem !important; }

         /* Adjust table font size for mobile */
         .stDataFrame table, .stDataEditor table { font-size: 0.75rem; }
         th, td { padding: 4px 6px !important; } /* Reduce padding */
    }

    @media only screen and (min-width: 769px) {
        .top-navbar { display: block; }
        .mobile-menu-trigger, .mobile-menu, .mobile-menu-overlay, .mobile-menu-checkbox { display: none; }
    }

</style>
"""
# =========================================
# القسم 3: هيكل HTML للقائمة وزر العودة للأعلى
# =========================================
# (نفس الكود السابق)
responsive_menu_html = """
<nav class="top-navbar">
    <ul>
        <li><a href="/">🏠 الرئيسية</a></li>
        <li><a href="/هيئة_التدريس">👥 هيئة التدريس</a></li>
        <li><a href="/إنجاز_المهام">🏆 إنجاز المهام</a></li>
        <li><a href="/program1">📚 بكالوريوس القرآن وعلومه</a></li>
        <li><a href="/program2">📖 بكالوريوس القراءات</a></li>
        <li><a href="/program3">🎓 ماجستير الدراسات القرآنية</a></li>
        <li><a href="/program4">📜 ماجستير القراءات</a></li>
        <li><a href="/program5">🔍 دكتوراه علوم القرآن</a></li>
        <li><a href="/program6">📘 دكتوراه القراءات</a></li>
        </ul>
</nav>

<input type="checkbox" id="mobile-menu-toggle" class="mobile-menu-checkbox">
<label for="mobile-menu-toggle" class="mobile-menu-trigger">☰</label>
<label for="mobile-menu-toggle" class="mobile-menu-overlay"></label>
<div class="mobile-menu">
    <ul>
        <li><a href="/">🏠 الرئيسية</a></li>
        <li><a href="/هيئة_التدريس">👥 هيئة التدريس</a></li>
        <li><a href="/إنجاز_المهام">🏆 إنجاز المهام</a></li>
        <li><a href="/program1">📚 بكالوريوس القرآن وعلومه</a></li>
        <li><a href="/program2">📖 بكالوريوس القراءات</a></li>
        <li><a href="/program3">🎓 ماجستير الدراسات القرآنية</a></li>
        <li><a href="/program4">📜 ماجستير القراءات</a></li>
        <li><a href="/program5">🔍 دكتوراه علوم القرآن</a></li>
        <li><a href="/program6">📘 دكتوراه القراءات</a></li>
        </ul>
</div>

<div class="back-to-top" onclick="scrollToTop()">
    <span style="font-size: 1.2rem;">↑</span>
</div>
"""

# =========================================
# القسم 4: منطق JavaScript للقائمة وزر العودة للأعلى
# =========================================
# (نفس الكود السابق)
responsive_menu_js = """
<script>
    // منطق التمرير إلى الأعلى
    window.scrollToTop = function() {
        try { window.scrollTo({ top: 0, behavior: 'smooth' }); }
        catch(e){ console.error("Error scrolling to top:", e); }
    }
    try {
        window.addEventListener('scroll', function() {
            const backToTopButton = document.querySelector('.back-to-top');
            if(backToTopButton){
                if (window.scrollY > 300) { backToTopButton.classList.add('visible'); }
                else { backToTopButton.classList.remove('visible'); }
            }
        });
    } catch(e){ console.error("Error adding scroll listener:", e); }

    // إغلاق قائمة الجوال عند النقر على أحد الروابط
    try {
        document.querySelectorAll('.mobile-menu a').forEach(link => {
            link.addEventListener('click', () => {
                const checkbox = document.getElementById('mobile-menu-toggle');
                if (checkbox) {
                    checkbox.checked = false; // إلغاء تحديد المربع لإغلاق القائمة
                }
            });
        });
    } catch(e) { console.error("Error adding mobile link click listener:", e); }
</script>
"""

# تطبيق CSS و HTML و JS
st.markdown(responsive_menu_css, unsafe_allow_html=True)
st.markdown(responsive_menu_html, unsafe_allow_html=True)
st.markdown(responsive_menu_js, unsafe_allow_html=True)

# =========================================
# القسم 5: ثوابت وإعدادات البيانات
# =========================================

# تعريف مستويات الإنجاز حسب النقاط (Global definition for reference)
ACHIEVEMENT_LEVELS = [
    {"name": "ممارس", "min": 50, "max": 200, "color": "#AED6F1", "icon": "🔹"},  # Light Blue
    {"name": "متمكن", "min": 201, "max": 400, "color": "#5DADE2", "icon": "🔷"},  # Blue
    {"name": "متميز", "min": 401, "max": 600, "color": "#58D68D", "icon": "🌟"},  # Green
    {"name": "خبير", "min": 601, "max": 800, "color": "#F5B041", "icon": "✨"},   # Orange
    {"name": "رائد", "min": 801, "max": float('inf'), "color": "#EC7063", "icon": "🏆"}, # Red
]
# Add 'مبتدئ' for consistency
BEGINNER_LEVEL = {"name": "مبتدئ", "min": 0, "max": 49, "color": "#D5DBDB", "icon": "🔘"} # Grey

# إنشاء قاموس لسهولة الوصول للألوان والرموز
LEVEL_COLORS = {level["name"]: level["color"] for level in ACHIEVEMENT_LEVELS}
LEVEL_COLORS[BEGINNER_LEVEL["name"]] = BEGINNER_LEVEL["color"]
LEVEL_ICONS = {level["name"]: level["icon"] for level in ACHIEVEMENT_LEVELS}
LEVEL_ICONS[BEGINNER_LEVEL["name"]] = BEGINNER_LEVEL["icon"]
LEVEL_ORDER = {level["name"]: i for i, level in enumerate([BEGINNER_LEVEL] + ACHIEVEMENT_LEVELS)} # Order for sorting


# تعريف خيارات التصفية الزمنية للنظرة العامة (جديد)
OVERVIEW_TIME_FILTER_OPTIONS = {
    "آخر شهر": 1,
    "آخر 3 أشهر": 3,
    "آخر 6 أشهر": 6,
    "آخر سنة": 12,
    "كل الوقت": None # Use None to represent all time
}
OVERVIEW_TIME_FILTER_LABELS = list(OVERVIEW_TIME_FILTER_OPTIONS.keys())

# مسار الجدول الفعلي
ACHIEVEMENTS_DATA_PATH = "data/department/achievements.csv"

# تعريف الأعمدة المتوقعة وأساسية
EXPECTED_ACHIEVEMENT_COLS = [
    "عنوان المهمة", "وصف مختصر", "اسم العضو", "تاريخ الإنجاز",
    "عدد الساعات", "عدد النقاط", "مستوى التعقيد", "الفئة",
    "المهمة الرئيسية", "البرنامج"
]
REQUIRED_COLS = ["اسم العضو", "تاريخ الإنجاز", "عدد النقاط", "الفئة", "البرنامج", "عنوان المهمة"] # الأعمدة الأساسية المطلوبة

# بيانات افتراضية لخطط البرامج (يمكن استبدالها ببيانات حقيقية)
# المفتاح هو اسم البرنامج، القيمة هي النقاط المستهدفة
PROGRAM_PLANS = {
    "بكالوريوس القراءات": 5000,
    "بكالوريوس القرآن وعلومه": 6000,
    "ماجستير الدراسات القرآنية المعاصرة": 3000,
    "ماجستير القراءات": 2500,
    "دكتوراه علوم القرآن": 4000,
    "دكتوراه القراءات": 3500,
    "غير مرتبط ببرنامج": 1000, # خطة افتراضية للمهام غير المرتبطة
    "جميع البرامج": 25000 # مجموع افتراضي
}

# =========================================
# القسم 6: الدوال المساعدة (مع تحديثات)
# =========================================
def is_mobile():
    """التحقق من كون العرض الحالي محتملاً أن يكون جهاز محمول (افتراضي حاليًا)"""
    return False

def prepare_chart_layout(fig, title, is_mobile=False, chart_type="bar", show_legend=True, height=None):
    """تطبيق تنسيق موحد على مخططات Plotly مع الاستجابة للجوال"""
    try:
        if not isinstance(fig, (go.Figure, px.scatter, px.line, px.bar, px.pie)):
             st.warning(f"Invalid object passed to prepare_chart_layout for title '{title}'. Expected Plotly figure.")
             return fig

        fig.update_layout(dragmode=False)
        if hasattr(fig.layout, 'xaxis'): fig.update_xaxes(fixedrange=True)
        if hasattr(fig.layout, 'yaxis'): fig.update_yaxes(fixedrange=True)
        if hasattr(fig.layout, 'polar'):
             if hasattr(fig.layout.polar, 'angularaxis'): fig.update_polars(angularaxis_fixedrange=True)
             if hasattr(fig.layout.polar, 'radialaxis'): fig.update_polars(radialaxis_fixedrange=True)

        # تحديد الارتفاع
        default_height_desktop = 400 if chart_type not in ["heatmap", "radar"] else 380
        default_height_mobile = 300 if chart_type not in ["heatmap", "radar"] else 320
        chart_height = height if height else (default_height_mobile if is_mobile else default_height_desktop)

        # إعدادات التخطيط المشتركة
        layout_settings = {
            "title": {"text": title, "x": 0.5, "xanchor": "center", "font": {"size": 14 if not is_mobile else 11}},
            "font": {"family": "Tajawal", "size": 10 if not is_mobile else 8},
            "plot_bgcolor": "rgba(245, 245, 245, 0.8)", # Lighter plot background
            "paper_bgcolor": "white",
            "showlegend": show_legend,
            "legend": {
                "orientation": "h", "yanchor": "bottom", "y": -0.2,
                "xanchor": "center", "x": 0.5, "font": {"size": 9 if not is_mobile else 7}
            },
            "height": chart_height,
            "margin": {"t": 50, "b": 80 if show_legend else 40, "l": 40, "r": 40, "pad": 4} if not is_mobile else \
                      {"t": 40, "b": 60 if show_legend else 30, "l": 5, "r": 5, "pad": 0}
        }

        fig.update_layout(**layout_settings)

        # تعديلات خاصة بنوع المخطط (بعد تطبيق الإعدادات العامة)
        if chart_type == "pie" or chart_type == "donut":
            fig.update_traces(textposition='outside', textinfo='percent+label', hole=(0.4 if chart_type == "donut" else 0))
            fig.update_layout(legend={"y": -0.1}) # Adjust legend slightly for pie/donut
        elif chart_type == "bar":
            if hasattr(fig.layout, 'xaxis'): fig.update_xaxes(tickangle=-45 if is_mobile else 0)
        elif chart_type == "radar":
             fig.update_layout(polar=dict(angularaxis=dict(tickfont=dict(size=9 if not is_mobile else 7)),
                                          radialaxis=dict(tickfont=dict(size=9 if not is_mobile else 7))),
                               margin=dict(l=60, r=60)) # Radar needs more margin

    except Exception as e:
        st.warning(f"تعذر تطبيق إعدادات التخطيط للرسم '{title}': {e}")
        # st.error(traceback.format_exc()) # Uncomment for detailed debugging

    return fig

def get_achievement_level(points):
    """تحديد مستوى الإنجاز بناءً على عدد النقاط"""
    try: points = float(points)
    except (ValueError, TypeError): points = 0

    if points < ACHIEVEMENT_LEVELS[0]["min"]:
        return BEGINNER_LEVEL
    for level in ACHIEVEMENT_LEVELS:
        if level["min"] <= points <= level["max"]:
            return level
    return ACHIEVEMENT_LEVELS[-1] # Should be 'رائد'

def calculate_member_levels_by_category(df, member_name):
    """حساب مستوى العضو في كل فئة بناءً على مجموع نقاطه التاريخي في تلك الفئة"""
    if df is None or df.empty or "اسم العضو" not in df.columns or "الفئة" not in df.columns or "عدد النقاط" not in df.columns:
        return pd.DataFrame()

    member_data = df[df["اسم العضو"] == member_name]
    if member_data.empty:
        return pd.DataFrame()

    # Group by category and sum points historically for this member
    category_points = member_data.groupby("الفئة")["عدد النقاط"].sum().reset_index()

    # Get level for each category based on the summed points
    category_points["مستوى_الإنجاز"] = category_points["عدد النقاط"].apply(get_achievement_level)
    category_points["مستوى"] = category_points["مستوى_الإنجاز"].apply(lambda x: x["name"])
    category_points["لون_المستوى"] = category_points["مستوى_الإنجاز"].apply(lambda x: x["color"])
    category_points["أيقونة_المستوى"] = category_points["مستوى_الإنجاز"].apply(lambda x: x["icon"])

    return category_points[["الفئة", "عدد النقاط", "مستوى", "لون_المستوى", "أيقونة_المستوى"]]


# =========================================
# القسم 7: تحميل ومعالجة البيانات
# =========================================

@st.cache_data(ttl=3600)
def load_and_prepare_data(file_path):
    """تحميل بيانات الإنجازات، معالجتها، والتحقق من الأعمدة الأساسية"""
    try:
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            st.warning(f"ملف بيانات الإنجازات غير موجود أو فارغ: {file_path}")
            return None # Return None to indicate failure

        df = pd.read_csv(file_path)

        # التحقق من وجود الأعمدة الأساسية المطلوبة
        missing_cols = [col for col in REQUIRED_COLS if col not in df.columns]
        if missing_cols:
            st.error(f"الأعمدة التالية مفقودة في الملف وهي أساسية: {', '.join(missing_cols)}")
            return None

        # ضمان وجود جميع الأعمدة المتوقعة الأخرى
        for col in EXPECTED_ACHIEVEMENT_COLS:
            if col not in df.columns:
                if col in ["عدد الساعات", "عدد النقاط"]: df[col] = 0
                else: df[col] = ""

        # --- المعالجة الأساسية ---
        # 1. تحويل التاريخ والتحقق منه
        df["التاريخ"] = pd.to_datetime(df["تاريخ الإنجاز"], errors='coerce')
        initial_rows = len(df)
        df.dropna(subset=["التاريخ"], inplace=True)
        if len(df) < initial_rows:
            st.warning(f"تم حذف {initial_rows - len(df)} سجل بسبب مشاكل في تنسيق التاريخ.")
        if df.empty:
            st.error("لا توجد سجلات بتاريخ صالح بعد المعالجة.")
            return None

        # 2. تحويل الأعمدة الرقمية والتأكد من أنها رقمية
        numeric_cols = ["عدد الساعات", "عدد النقاط"]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(float) # Use float for points/hours

        # 3. تنظيف الأعمدة النصية
        string_cols = ["عنوان المهمة", "وصف مختصر", "اسم العضو", "مستوى التعقيد", "الفئة", "المهمة الرئيسية", "البرنامج"]
        for col in string_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().fillna("غير محدد")
                df[col] = df[col].replace(['', 'nan'], 'غير محدد') # Handle empty strings and 'nan'

        # 4. معالجة خاصة للفئة والبرنامج
        df["الفئة"] = df["الفئة"].replace(["غير محدد"], "— بدون فئة —")
        df["البرنامج"] = df["البرنامج"].replace(["غير محدد"], "غير مرتبط ببرنامج")

        # 5. التأكد من أن اسم العضو صالح
        df = df[df["اسم العضو"].notna() & (df["اسم العضو"] != "غير محدد") & (df["اسم العضو"] != "")]
        if df.empty:
            st.error("لا توجد سجلات بأسماء أعضاء صالحة بعد المعالجة.")
            return None

        # 6. إضافة أعمدة مساعدة للزمن
        df['Year'] = df['التاريخ'].dt.year
        df['Month'] = df['التاريخ'].dt.to_period('M').astype(str) # YYYY-MM format
        df['Week'] = df['التاريخ'].dt.to_period('W').astype(str) # YYYY-MM-DD/YYYY-MM-DD format
        df['DateOnly'] = df['التاريخ'].dt.date # For heatmap grouping

        # 7. حساب مستوى الإنجاز لكل مهمة (قد لا نحتاجه مباشرة لكن جيد توفره)
        df['مستوى_المهمة'] = df['عدد النقاط'].apply(get_achievement_level)

        # 8. ترتيب البيانات افتراضيًا حسب التاريخ الأحدث
        df = df.sort_values(by="التاريخ", ascending=False).reset_index(drop=True)

        return df

    except Exception as e:
        st.error(f"خطأ فادح في تحميل أو معالجة بيانات الإنجازات: {e}")
        st.error(traceback.format_exc()) # Log detailed error
        return None

# =========================================
# القسم 8: تحميل البيانات واستخراج القوائم
# =========================================
# تحميل البيانات
all_data = load_and_prepare_data(ACHIEVEMENTS_DATA_PATH)

# استخراج القوائم للاستخدام في الفلاتر (فقط إذا تم تحميل البيانات بنجاح)
if all_data is not None:
    members_list = sorted(all_data["اسم العضو"].unique())
    category_list = sorted([cat for cat in all_data["الفئة"].unique() if cat != "— بدون فئة —"])
    program_list = sorted([prog for prog in all_data["البرنامج"].unique() if prog != "غير مرتبط ببرنامج"])
    # يمكنك إضافة قوائم أخرى هنا إذا لزم الأمر (مثل مستوى التعقيد)
else:
    # حالة فشل تحميل البيانات
    members_list = []
    category_list = []
    program_list = []
    st.stop() # إيقاف تنفيذ التطبيق إذا لم يتم تحميل البيانات الأساسية

# =========================================
# القسم 9: إعدادات الجلسة والفلاتر الرئيسية
# =========================================
# تهيئة متغيرات الجلسة للفلاتر
if "time_filter" not in st.session_state:
    st.session_state.time_filter = OVERVIEW_TIME_FILTER_LABELS[-1] # Default to "كل الوقت"
if "program_filter" not in st.session_state:
    st.session_state.program_filter = "الكل"
if "category_filter" not in st.session_state:
    st.session_state.category_filter = "الكل"

# --- عرض الفلاتر الرئيسية في الأعلى ---
st.markdown("#### فلترة البيانات")
filter_cols = st.columns([1, 1, 1])

with filter_cols[0]:
    st.session_state.time_filter = st.selectbox(
        "الفترة الزمنية:",
        options=OVERVIEW_TIME_FILTER_LABELS,
        index=OVERVIEW_TIME_FILTER_LABELS.index(st.session_state.time_filter),
        key="time_filter_selector_main"
    )
with filter_cols[1]:
    program_options = ["الكل"] + program_list + ["غير مرتبط ببرنامج"]
    st.session_state.program_filter = st.selectbox(
        "البرنامج:",
        options=program_options,
        index=program_options.index(st.session_state.program_filter) if st.session_state.program_filter in program_options else 0,
        key="program_filter_selector_main"
    )
with filter_cols[2]:
    category_options = ["الكل"] + category_list + ["— بدون فئة —"]
    st.session_state.category_filter = st.selectbox(
        "الفئة:",
        options=category_options,
        index=category_options.index(st.session_state.category_filter) if st.session_state.category_filter in category_options else 0,
        key="category_filter_selector_main"
    )

# =========================================
# القسم 10: تطبيق الفلاتر على البيانات
# =========================================
filtered_data = all_data.copy()

# 1. تطبيق فلتر الفترة الزمنية
months_to_subtract = OVERVIEW_TIME_FILTER_OPTIONS.get(st.session_state.time_filter)
if months_to_subtract is not None:
    current_date = pd.Timestamp.now().normalize()
    start_date = current_date - dateutil.relativedelta.relativedelta(months=months_to_subtract)
    filtered_data = filtered_data[(filtered_data["التاريخ"] >= start_date) & (filtered_data["التاريخ"] <= current_date)]

# 2. تطبيق فلتر البرنامج
if st.session_state.program_filter != "الكل":
    filtered_data = filtered_data[filtered_data["البرنامج"] == st.session_state.program_filter]

# 3. تطبيق فلتر الفئة
if st.session_state.category_filter != "الكل":
    filtered_data = filtered_data[filtered_data["الفئة"] == st.session_state.category_filter]

# =========================================
# القسم 11: عرض النظرة العامة (Overview)
# =========================================
st.markdown("---") # خط فاصل
st.header("نظرة عامة على الإنجازات")

if filtered_data.empty:
    st.warning(f"لا توجد بيانات تطابق الفلاتر المحددة للفترة: {st.session_state.time_filter}, البرنامج: {st.session_state.program_filter}, الفئة: {st.session_state.category_filter}")
else:
    # --- KPIs ---
    st.markdown("#### المؤشرات الرئيسية")
    kpi_cols = st.columns(5)
    total_tasks = len(filtered_data)
    total_hours = filtered_data["عدد الساعات"].sum()
    total_points = filtered_data["عدد النقاط"].sum()
    active_members = filtered_data["اسم العضو"].nunique()

    # حساب أعلى مستوى تم بلوغه في الفترة
    # (يعتمد على مجموع نقاط كل عضو في كل فئة *خلال الفترة*)
    highest_level_name = "مبتدئ"
    if not filtered_data.empty:
        member_category_points_period = filtered_data.groupby(['اسم العضو', 'الفئة'])['عدد النقاط'].sum().reset_index()
        if not member_category_points_period.empty:
             member_category_points_period['level_info'] = member_category_points_period['عدد النقاط'].apply(get_achievement_level)
             member_category_points_period['level_order'] = member_category_points_period['level_info'].apply(lambda x: LEVEL_ORDER.get(x['name'], -1))
             highest_level_order = member_category_points_period['level_order'].max()
             highest_level_name = next((name for name, order in LEVEL_ORDER.items() if order == highest_level_order), "مبتدئ")


    with kpi_cols[0]: st.metric("مجموع المهام", f"{total_tasks:,}")
    with kpi_cols[1]: st.metric("إجمالي الساعات", f"{total_hours:,.1f}")
    with kpi_cols[2]: st.metric("إجمالي النقاط", f"{total_points:,.0f}")
    with kpi_cols[3]: st.metric("الأعضاء النشطين", f"{active_members:,}")
    with kpi_cols[4]:
         st.metric("أعلى مستوى (الفترة)", highest_level_name,
                   help="أعلى مستوى تم بلوغه من قبل أي عضو في أي فئة بناءً على النقاط المكتسبة في الفترة المحددة.")


    st.markdown("---")
    overview_cols = st.columns([3, 2]) # قسم الرسوم البيانية

    with overview_cols[0]:
        # --- مخطط النقاط المكدس حسب الفئة والمستوى ---
        st.markdown("#### النقاط حسب الفئة والمستوى")
        category_points_levels = filtered_data[filtered_data['الفئة'] != '— بدون فئة —'].copy()
        if not category_points_levels.empty:
             # حساب المستوى لكل مهمة بناءً على نقاطها (للتلوين)
            category_points_levels['مستوى_المهمة_اسم'] = category_points_levels['مستوى_المهمة'].apply(lambda x: x['name'])
             # تجميع النقاط حسب الفئة والمستوى
            category_summary = category_points_levels.groupby(['الفئة', 'مستوى_المهمة_اسم'])['عدد النقاط'].sum().reset_index()

            if not category_summary.empty:
                 try:
                     fig_cat_stacked = px.bar(category_summary, x='الفئة', y='عدد النقاط',
                                              color='مستوى_المهمة_اسم',
                                              title="", # Remove title
                                              labels={'الفئة': 'الفئة', 'عدد النقاط': 'مجموع النقاط', 'مستوى_المهمة_اسم': 'المستوى'},
                                              category_orders={'مستوى_المهمة_اسم': list(LEVEL_ORDER.keys())}, # Ensure correct level order
                                              color_discrete_map=LEVEL_COLORS)
                     fig_cat_stacked = prepare_chart_layout(fig_cat_stacked, "النقاط حسب الفئة والمستوى", is_mobile, "bar")
                     st.plotly_chart(fig_cat_stacked, use_container_width=True, config={"displayModeBar": False})
                 except Exception as e:
                      st.error(f"خطأ في رسم مخطط الفئات المكدس: {e}")
            else:
                 st.info("لا توجد بيانات كافية لعرض مخطط النقاط حسب الفئة والمستوى.")
        else:
             st.info("لا توجد بيانات مصنفة حسب الفئات لعرضها.")


        # --- مخطط خطي تراكمي للمهام عبر الزمن (بالأسابيع) ---
        st.markdown("#### تطور عدد المهام التراكمي (أسبوعي)")
        if not filtered_data.empty and 'Week' in filtered_data.columns:
             try:
                 # Ensure 'التاريخ' is sorted for cumulative calculation if needed, though groupby handles it
                 tasks_per_week = filtered_data.sort_values('التاريخ').groupby('Week').size().reset_index(name='count')
                 # Ensure weeks are sorted chronologically
                 tasks_per_week['WeekStart'] = tasks_per_week['Week'].apply(lambda w: pd.to_datetime(w.split('/')[0]))
                 tasks_per_week = tasks_per_week.sort_values('WeekStart')
                 tasks_per_week['cumulative_tasks'] = tasks_per_week['count'].cumsum()

                 fig_area = px.area(tasks_per_week, x='WeekStart', y='cumulative_tasks',
                                    title="", # Remove title
                                    labels={'WeekStart': 'بداية الأسبوع', 'cumulative_tasks': 'إجمالي المهام التراكمي'},
                                    markers=True)
                 fig_area.update_xaxes(dtick="M1", tickformat="%Y-%m-%d") # Show monthly ticks approx
                 fig_area = prepare_chart_layout(fig_area, "تطور عدد المهام التراكمي (أسبوعي)", is_mobile, "line") # Use line type for area
                 st.plotly_chart(fig_area, use_container_width=True, config={"displayModeBar": False})
             except Exception as e:
                  st.error(f"خطأ في رسم المخطط الزمني التراكمي: {e}")
        else:
             st.info("لا توجد بيانات كافية لعرض المخطط الزمني التراكمي.")


    with overview_cols[1]:
        # --- تقدم البرامج (بيانات افتراضية) ---
        st.markdown("#### تقدم البرامج (مقابل الخطة)")
        program_summary = filtered_data.groupby("البرنامج")["عدد النقاط"].sum()
        for prog_name, target_points in PROGRAM_PLANS.items():
            if prog_name == "جميع البرامج": continue # Skip overall target here
            current_points = program_summary.get(prog_name, 0)
            progress = min(100, (current_points / target_points) * 100) if target_points > 0 else 0
            st.text(f"{prog_name}: ({int(current_points)} / {target_points} نقطة)")
            st.progress(int(progress) / 100) # st.progress takes 0.0 to 1.0

        # --- مخطط دائري لتوزيع المهام على البرامج ---
        st.markdown("#### توزيع المهام حسب البرنامج")
        program_tasks_dist = filtered_data['البرنامج'].value_counts().reset_index()
        program_tasks_dist.columns = ['البرنامج', 'عدد المهام']

        if not program_tasks_dist.empty:
             try:
                 fig_prog_donut = px.pie(program_tasks_dist, values='عدد المهام', names='البرنامج',
                                         title="", # Remove title
                                         hole=0.4, # Make it a donut chart
                                         color_discrete_sequence=px.colors.qualitative.Set3)
                 fig_prog_donut = prepare_chart_layout(fig_prog_donut, "توزيع المهام حسب البرنامج", is_mobile, "donut")
                 st.plotly_chart(fig_prog_donut, use_container_width=True, config={"displayModeBar": False})
             except Exception as e:
                  st.error(f"خطأ في رسم مخطط توزيع البرامج: {e}")
        else:
             st.info("لا توجد مهام لعرض توزيعها حسب البرامج.")


# =========================================
# القسم 12: التبويبات الفرعية
# =========================================
st.markdown("---")
st.header("التحليلات التفصيلية")

tab_titles = ["البرامج", "الأعضاء", "الفئات", "المهام التفصيلية"]
tabs = st.tabs(tab_titles)

# --- Tab 1: البرامج ---
with tabs[0]:
    st.subheader("تحليل البرامج")

    # Selector for program if "الكل" is selected in main filter
    program_to_show = st.session_state.program_filter
    if program_to_show == "الكل":
        program_options_tab = program_list + ["غير مرتبط ببرنامج"]
        program_to_show = st.selectbox("اختر برنامجًا لعرض تفاصيله:", program_options_tab, key="program_tab_selector")

    # Filter data for the selected program
    program_data = filtered_data[filtered_data["البرنامج"] == program_to_show]

    if program_data.empty:
        st.warning(f"لا توجد بيانات للبرنامج المحدد '{program_to_show}' ضمن الفلاتر الحالية.")
    else:
        st.markdown(f"#### تفاصيل برنامج: {program_to_show}")
        prog_cols = st.columns(2)
        with prog_cols[0]:
            # KPIs for the program
            prog_total_tasks = len(program_data)
            prog_total_points = program_data["عدد النقاط"].sum()
            prog_total_hours = program_data["عدد الساعات"].sum()
            prog_active_members = program_data["اسم العضو"].nunique()
            st.metric("مجموع المهام (البرنامج)", f"{prog_total_tasks:,}")
            st.metric("مجموع النقاط (البرنامج)", f"{prog_total_points:,.0f}")

        with prog_cols[1]:
             st.metric("مجموع الساعات (البرنامج)", f"{prog_total_hours:,.1f}")
             st.metric("الأعضاء النشطين (البرنامج)", f"{prog_active_members:,}")

        # Progress bar vs Plan
        st.markdown("##### التقدم مقابل الخطة")
        prog_target = PROGRAM_PLANS.get(program_to_show, 0)
        prog_progress = min(100, (prog_total_points / prog_target) * 100) if prog_target > 0 else 0
        st.text(f"الخطة: {prog_target} نقطة | المحقق: {int(prog_total_points)} نقطة")
        st.progress(int(prog_progress) / 100)

        # Stacked bar: Points by Category within the program
        st.markdown("##### النقاط حسب الفئة داخل البرنامج")
        prog_cat_points = program_data[program_data['الفئة'] != '— بدون فئة —'].copy()
        if not prog_cat_points.empty:
             prog_cat_points['مستوى_المهمة_اسم'] = prog_cat_points['مستوى_المهمة'].apply(lambda x: x['name'])
             prog_cat_summary = prog_cat_points.groupby(['الفئة', 'مستوى_المهمة_اسم'])['عدد النقاط'].sum().reset_index()

             if not prog_cat_summary.empty:
                  try:
                      fig_prog_cat_stacked = px.bar(prog_cat_summary, x='الفئة', y='عدد النقاط',
                                                    color='مستوى_المهمة_اسم', title="",
                                                    labels={'الفئة': 'الفئة', 'عدد النقاط': 'مجموع النقاط', 'مستوى_المهمة_اسم': 'المستوى'},
                                                    category_orders={'مستوى_المهمة_اسم': list(LEVEL_ORDER.keys())},
                                                    color_discrete_map=LEVEL_COLORS)
                      fig_prog_cat_stacked = prepare_chart_layout(fig_prog_cat_stacked, f"النقاط حسب الفئة ({program_to_show})", is_mobile, "bar")
                      st.plotly_chart(fig_prog_cat_stacked, use_container_width=True, config={"displayModeBar": False})
                  except Exception as e:
                       st.error(f"خطأ في رسم مخطط الفئات المكدس للبرنامج: {e}")
             else:
                  st.info("لا توجد بيانات كافية لعرض مخطط النقاط حسب الفئة داخل البرنامج.")
        else:
             st.info("لا توجد مهام بفئات لعرضها لهذا البرنامج.")


        # Simple table for recent tasks
        st.markdown("##### أحدث المهام في البرنامج")
        recent_tasks_prog = program_data.head(5)[["تاريخ الإنجاز", "عنوان المهمة", "اسم العضو", "عدد النقاط"]]
        st.dataframe(recent_tasks_prog, use_container_width=True, hide_index=True)


# --- Tab 2: الأعضاء ---
with tabs[1]:
    st.subheader("تحليل الأعضاء")

    if filtered_data.empty:
         st.warning("لا توجد بيانات لعرض تحليل الأعضاء بناءً على الفلاتر الحالية.")
    else:
        # Leaderboard (based on filtered data)
        st.markdown("#### لوحة الشرف (حسب الفلاتر)")
        member_summary_filtered = filtered_data.groupby("اسم العضو").agg(
            عدد_النقاط_فترة=("عدد النقاط", "sum"),
            عدد_الساعات_فترة=("عدد الساعات", "sum"),
            عدد_المهام_فترة=("عنوان المهمة", "count")
        ).reset_index().sort_values("عدد_النقاط_فترة", ascending=False)

        if not member_summary_filtered.empty:
            # Add overall historical level for context
            historical_points = all_data.groupby('اسم العضو')['عدد النقاط'].sum()
            member_summary_filtered["المستوى_الإجمالي"] = member_summary_filtered["اسم العضو"].apply(
                lambda name: get_achievement_level(historical_points.get(name, 0))['name']
            )
            member_summary_filtered["لون_المستوى_الإجمالي"] = member_summary_filtered["المستوى_الإجمالي"].map(LEVEL_COLORS)

            try:
                fig_leaderboard_filt = px.bar(member_summary_filtered.head(15), # Show top 15
                                             y="اسم العضو", x="عدد_النقاط_فترة",
                                             orientation='h',
                                             color="المستوى_الإجمالي",
                                             color_discrete_map=LEVEL_COLORS,
                                             labels={"عدد_النقاط_فترة": "النقاط (الفترة)", "اسم العضو": "العضو", "المستوى_الإجمالي": "المستوى التاريخي"},
                                             text="عدد_النقاط_فترة")
                fig_leaderboard_filt.update_layout(yaxis={'categoryorder':'total ascending'})
                fig_leaderboard_filt = prepare_chart_layout(fig_leaderboard_filt, "لوحة الشرف (حسب الفلاتر)", is_mobile, "bar", show_legend=False)
                st.plotly_chart(fig_leaderboard_filt, use_container_width=True, config={"displayModeBar": False})
            except Exception as e:
                 st.error(f"خطأ في رسم لوحة الشرف: {e}")

            # Member Details Section
            st.markdown("---")
            st.markdown("#### تفاصيل العضو ومستوياته")
            selected_member_tab = st.selectbox("اختر عضوًا لعرض تفاصيله:", ["اختر..."] + members_list, key="member_tab_selector")

            if selected_member_tab != "اختر...":
                 member_data_filtered = filtered_data[filtered_data["اسم العضو"] == selected_member_tab]
                 member_data_all = all_data[all_data["اسم العضو"] == selected_member_tab] # For historical context

                 if not member_data_filtered.empty:
                     m_cols = st.columns(3)
                     m_points_filt = member_data_filtered["عدد النقاط"].sum()
                     m_hours_filt = member_data_filtered["عدد الساعات"].sum()
                     m_tasks_filt = len(member_data_filtered)
                     m_points_hist = member_data_all["عدد النقاط"].sum()
                     m_level_hist_info = get_achievement_level(m_points_hist)
                     m_level_hist_name = m_level_hist_info['name']
                     m_level_hist_icon = m_level_hist_info['icon']
                     m_level_hist_color = m_level_hist_info['color']

                     with m_cols[0]: st.metric("النقاط (الفترة)", f"{m_points_filt:,.0f}")
                     with m_cols[1]: st.metric("الساعات (الفترة)", f"{m_hours_filt:,.1f}")
                     with m_cols[2]: st.metric("المهام (الفترة)", f"{m_tasks_filt:,}")

                     st.markdown(f"**المستوى التاريخي الإجمالي:** <span style='color:{m_level_hist_color}; font-weight:bold;'>{m_level_hist_icon} {m_level_hist_name}</span> ({int(m_points_hist)} نقطة)", unsafe_allow_html=True)

                     # Levels per Category (Historical)
                     st.markdown("##### مستويات العضو حسب الفئة (التاريخي)")
                     member_levels_cat = calculate_member_levels_by_category(all_data, selected_member_tab)
                     if not member_levels_cat.empty:
                          # Display as styled text or small table
                          cat_level_html = "<div style='display: flex; flex-wrap: wrap; gap: 15px;'>"
                          for _, row in member_levels_cat.iterrows():
                               cat_level_html += f"""
                               <div style='text-align: center; padding: 5px; border: 1px solid {row['لون_المستوى']}; border-radius: 5px; background-color: {row['لون_المستوى']}15;'>
                                   <span style='font-size: 0.8em; color: #555;'>{row['الفئة']}</span><br>
                                   <span style='font-size: 1.2em; color: {row['لون_المستوى']}; font-weight: bold;'>{row['أيقونة_المستوى']} {row['مستوى']}</span><br>
                                   <span style='font-size: 0.75em;'>({int(row['عدد النقاط'])} نقطة)</span>
                               </div>"""
                          cat_level_html += "</div>"
                          st.markdown(cat_level_html, unsafe_allow_html=True)
                     else:
                          st.info("لا توجد بيانات مستويات حسب الفئة لهذا العضو.")

                     # Activity Heatmap (based on filtered data)
                     st.markdown("##### خريطة النشاط الحرارية (حسب الفلاتر)")
                     if not member_data_filtered.empty and 'DateOnly' in member_data_filtered.columns:
                          try:
                              activity_counts = member_data_filtered.groupby('DateOnly').size().reset_index(name='tasks')
                              activity_counts['DateOnly'] = pd.to_datetime(activity_counts['DateOnly'])

                              # Create a full date range for the filtered period
                              if not filtered_data.empty:
                                   min_date_filt = filtered_data['التاريخ'].min().normalize()
                                   max_date_filt = filtered_data['التاريخ'].max().normalize()
                                   all_days = pd.date_range(start=min_date_filt, end=max_date_filt, freq='D')
                                   activity_full_range = pd.DataFrame(all_days, columns=['DateOnly'])
                                   # Merge to get counts, fill missing days with 0
                                   activity_merged = pd.merge(activity_full_range, activity_counts, on='DateOnly', how='left').fillna(0)

                                   # Prepare data for heatmap
                                   activity_merged['Year'] = activity_merged['DateOnly'].dt.year
                                   activity_merged['MonthInt'] = activity_merged['DateOnly'].dt.month
                                   activity_merged['DayOfMonth'] = activity_merged['DateOnly'].dt.day
                                   activity_merged['Weekday'] = activity_merged['DateOnly'].dt.dayofweek # Monday=0, Sunday=6
                                   activity_merged['WeekOfYear'] = activity_merged['DateOnly'].dt.isocalendar().week

                                   # Pivot for heatmap (example: tasks per day of week vs week number)
                                   # This requires more complex handling for a calendar view like GitHub's
                                   # Let's do a simpler heatmap: Day vs Month
                                   activity_pivot = activity_merged.pivot_table(index='MonthInt', columns='DayOfMonth', values='tasks', fill_value=0)

                                   fig_heatmap = px.imshow(activity_pivot,
                                                           labels=dict(x="يوم الشهر", y="الشهر", color="عدد المهام"),
                                                           x=activity_pivot.columns,
                                                           y=activity_pivot.index,
                                                           aspect="auto",
                                                           color_continuous_scale="Greens") # Green color scale
                                   fig_heatmap = prepare_chart_layout(fig_heatmap, f"خريطة نشاط {selected_member_tab} (المهام اليومية)", is_mobile, "heatmap", height=250)
                                   fig_heatmap.update_yaxes(tickmode='array', tickvals=list(range(1, 13)), ticktext=[f'{m:02d}' for m in range(1, 13)]) # Format month ticks
                                   st.plotly_chart(fig_heatmap, use_container_width=True, config={"displayModeBar": False})

                              else:
                                   st.info("لا يمكن تحديد نطاق زمني للحرائط الحرارية.")

                          except Exception as e:
                               st.error(f"خطأ في رسم الخريطة الحرارية: {e}")
                     else:
                          st.info("لا توجد بيانات كافية لرسم الخريطة الحرارية للعضو المحدد.")


                 else:
                     st.info(f"لا توجد بيانات للعضو '{selected_member_tab}' ضمن الفلاتر الحالية.")


        else: # If member summary is empty
             st.info("لا توجد بيانات أعضاء لعرضها بناءً على الفلاتر الحالية.")


# --- Tab 3: الفئات ---
with tabs[2]:
    st.subheader("تحليل الفئات")
    category_to_show = st.session_state.category_filter
    if category_to_show == "الكل" or category_to_show == "— بدون فئة —":
        category_to_show = st.selectbox("اختر فئة لعرض تفاصيلها:", category_list, key="category_tab_selector")

    # Filter data for the selected category (using the globally filtered data)
    category_data = filtered_data[filtered_data["الفئة"] == category_to_show]

    if category_data.empty:
        st.warning(f"لا توجد بيانات للفئة المحددة '{category_to_show}' ضمن الفلاتر الحالية.")
    else:
        st.markdown(f"#### تحليل فئة: {category_to_show}")

        # Distribution of members across levels within the category
        st.markdown("##### توزيع الأعضاء حسب المستوى داخل الفئة (النقاط في الفترة)")
        # Calculate points per member *within this category* based on *filtered data*
        cat_member_points = category_data.groupby("اسم العضو")["عدد النقاط"].sum().reset_index()
        if not cat_member_points.empty:
            cat_member_points["level_info"] = cat_member_points["عدد النقاط"].apply(get_achievement_level)
            cat_member_points["level_name"] = cat_member_points["level_info"].apply(lambda x: x['name'])

            level_distribution = cat_member_points["level_name"].value_counts().reset_index()
            level_distribution.columns = ['المستوى', 'عدد الأعضاء']

            # Ensure correct order and colors
            level_distribution['order'] = level_distribution['المستوى'].map(LEVEL_ORDER)
            level_distribution = level_distribution.sort_values('order')

            try:
                fig_level_dist = px.bar(level_distribution, x='المستوى', y='عدد الأعضاء',
                                        color='المستوى',
                                        color_discrete_map=LEVEL_COLORS,
                                        labels={'المستوى': 'المستوى', 'عدد الأعضاء': 'عدد الأعضاء'})
                # Use categoryorderarray for specific order if needed, though mapping and sorting should work
                # fig_level_dist.update_xaxes(categoryorder='array', categoryarray=list(LEVEL_ORDER.keys()))
                fig_level_dist = prepare_chart_layout(fig_level_dist, f"توزيع مستويات الأعضاء في فئة '{category_to_show}'", is_mobile, "bar", show_legend=False)
                st.plotly_chart(fig_level_dist, use_container_width=True, config={"displayModeBar": False})

                # Optional: 100% Stacked Bar (might be less clear with many levels)
                # try:
                #     fig_level_dist_100 = px.bar(level_distribution, x=['الفئة'], y='عدد الأعضاء', # Need a dummy x if only one category
                #                             color='المستوى', barnorm='percent',
                #                             color_discrete_map=LEVEL_COLORS,
                #                             labels={'المستوى': 'المستوى', 'value': 'النسبة المئوية للأعضاء'})
                #     fig_level_dist_100 = prepare_chart_layout(fig_level_dist_100, f"نسبة مستويات الأعضاء في فئة '{category_to_show}' (%)", is_mobile, "bar", show_legend=True)
                #     st.plotly_chart(fig_level_dist_100, use_container_width=True, config={"displayModeBar": False})
                # except Exception as e:
                #      st.error(f"خطأ في رسم مخطط المستويات النسبي: {e}")

            except Exception as e:
                 st.error(f"خطأ في رسم مخطط توزيع المستويات: {e}")

        else:
            st.info("لا يوجد أعضاء لديهم نقاط في هذه الفئة ضمن الفلاتر الحالية.")

        # Time to promote: Skipped due to data complexity


# --- Tab 4: المهام التفصيلية ---
with tabs[3]:
    st.subheader("قائمة المهام التفصيلية")
    st.markdown("يعرض هذا الجدول المهام التي تطابق الفلاتر المحددة في أعلى الصفحة.")

    if filtered_data.empty:
        st.warning("لا توجد مهام تطابق الفلاتر الحالية.")
    else:
        # Select and rename columns for display
        display_cols = {
            "تاريخ الإنجاز": "التاريخ",
            "اسم العضو": "العضو",
            "عنوان المهمة": "المهمة",
            "الفئة": "الفئة",
            "البرنامج": "البرنامج",
            "عدد النقاط": "النقاط",
            "عدد الساعات": "الساعات",
            "مستوى التعقيد": "التعقيد",
            "المهمة الرئيسية": "المهمة الرئيسية",
            # Add "وصف مختصر" if needed, but might make table too wide
        }
        tasks_display_df = filtered_data[list(display_cols.keys())].rename(columns=display_cols)

        # Display the interactive dataframe
        st.dataframe(tasks_display_df, use_container_width=True, hide_index=True)

        # --- Export Button ---
        st.markdown("---")
        st.markdown("#### تصدير البيانات")

        # Function to convert DF to CSV
        @st.cache_data # Cache the conversion result
        def convert_df_to_csv(df):
            output = io.StringIO()
            df.to_csv(output, index=False, encoding='utf-8-sig') # utf-8-sig for Excel compatibility
            return output.getvalue()

        csv_data = convert_df_to_csv(tasks_display_df)

        # Get current filters for filename
        time_f = st.session_state.time_filter.replace(" ", "_")
        prog_f = st.session_state.program_filter.replace(" ", "_")
        cat_f = st.session_state.category_filter.replace(" ", "_")
        export_filename = f"tasks_{time_f}_{prog_f}_{cat_f}_{datetime.now().strftime('%Y%m%d')}.csv"

        st.download_button(
            label="📥 تحميل الجدول الحالي (CSV)",
            data=csv_data,
            file_name=export_filename,
            mime='text/csv',
        )
        st.caption("سيتم تحميل البيانات المعروضة في الجدول أعلاه بناءً على الفلاتر المطبقة.")


# =========================================
# القسم 13: نصائح الاستخدام وتذييل الصفحة
# =========================================
with st.expander("💡 نصائح للاستخدام", expanded=False):
    st.markdown("""
    - **الفلاتر العلوية:** استخدم القوائم المنسدلة في الأعلى لتصفية البيانات المعروضة في *جميع* أقسام اللوحة (النظرة العامة والتبويبات).
    - **النظرة العامة:** تعطيك ملخصًا سريعًا ومؤشرات أداء رئيسية بناءً على الفلاتر المحددة.
    - **تبويب البرامج:** يعرض تفاصيل برنامج واحد في كل مرة. إذا اخترت "الكل" في الفلتر العلوي، استخدم القائمة المنسدلة داخل التبويب لاختيار البرنامج.
    - **تبويب الأعضاء:** يعرض لوحة شرف للأعضاء الأكثر نقاطًا (حسب الفلاتر). اختر عضوًا من القائمة المنسدلة لرؤية تفاصيله التاريخية ومستوياته حسب الفئة وخريطة نشاطه.
    - **تبويب الفئات:** اختر فئة من القائمة المنسدلة (إذا كان الفلتر العلوي "الكل") لتحليل توزيع مستويات الأعضاء داخلها.
    - **تبويب المهام التفصيلية:** يعرض جدولاً بجميع المهام المطابقة للفلاتر، مع إمكانية تحميل البيانات كملف CSV.
    - **الرسوم البيانية تفاعلية:** مرر الفأرة فوقها لرؤية التفاصيل.
    - **للعودة إلى أعلى الصفحة:** انقر على زر السهم ↑ في أسفل يسار الشاشة.
    """, unsafe_allow_html=True)

# --- إضافة نص تذييل الصفحة ---
st.markdown("""
<div style="margin-top: 50px; text-align: center; color: #888; font-size: 0.75em;">
    © قسم القراءات - جامعة الطائف {0}
</div>
""".format(datetime.now().year), unsafe_allow_html=True)
