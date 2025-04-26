# -*- coding: utf-8 -*-

# =========================================
# القسم 1: الاستيرادات وإعدادات الصفحة
# =========================================
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import hashlib
import os
import numpy as np

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="إنجاز المهام | قسم القراءات",
    page_icon="🏆",
    layout="wide"
)

# =========================================
# القسم 2: تنسيقات CSS للقائمة والصفحة
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
        width: 100%; box-sizing: border-box;
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
    h1,h2,h3 { color: #1e88e5; font-weight: 600; }
    h1 { padding-bottom: 10px; border-bottom: 1px solid #1e88e5; margin-bottom: 20px; font-size: calc(1rem + 0.6vw); }
    h2 { margin-top: 25px; margin-bottom: 15px; font-size: calc(0.9rem + 0.4vw); }
    h3 { margin-top: 25px; margin-bottom: 15px; font-size: calc(0.9rem + 0.1vw); }
    .metric-card { background-color: white; border-radius: 8px; padding: 12px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08); text-align: center; margin-bottom: 12px; }
    .chart-container { background-color: white; border-radius: 8px; padding: 8px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08); margin-bottom: 15px; width: 100%; overflow: hidden; }
    .stSelectbox label, .stMultiselect label { font-weight: 500; font-size: 0.95rem; }
    .back-to-top { position: fixed; bottom: 15px; left: 15px; width: 35px; height: 35px; background-color: #1e88e5; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; z-index: 998; cursor: pointer; box-shadow: 0 2px 5px rgba(0,0,0,0.2); opacity: 0; transition: opacity 0.3s, transform 0.3s; transform: scale(0); }
    .back-to-top.visible { opacity: 1; transform: scale(1); }
    .back-to-top span { font-size: 1rem; }

    /* تلوين البطاقات حسب قيمة المؤشر */
    .metric-card.positive { background-color: rgba(39, 174, 96, 0.1); }
    .metric-card.warning { background-color: rgba(241, 196, 15, 0.1); }
    .metric-card.negative { background-color: rgba(231, 76, 60, 0.1); }

    /* خطوط المقاييس داخل البطاقات */
    [data-testid="stMetricValue"] { font-size: 1.5rem !important; }
    [data-testid="stMetricLabel"] { font-size: 0.85rem !important; }

    /* --- تنسيقات خاصة بصفحة إنجاز المهام --- */
    .task-card {
        background-color: white;
        border-radius: 8px;
        border-right: 4px solid #1e88e5;
        padding: 15px;
        margin-bottom: 12px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08);
        display: flex;
        flex-direction: column;
    }
    .task-card.completed { border-right-color: #27AE60; }
    .task-card.in-progress { border-right-color: #F39C12; }
    .task-card.planned { border-right-color: #E74C3C; }
    
    .task-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 10px;
    }
    .task-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e88e5;
        margin-bottom: 3px;
    }
    .task-details {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 5px;
    }
    .task-detail-item {
        font-size: 0.8rem;
        background-color: #f0f2f6;
        padding: 3px 6px;
        border-radius: 4px;
        white-space: nowrap;
    }
    .task-metrics {
        display: flex;
        gap: 10px;
        margin-top: 8px;
    }
    .task-metric {
        text-align: center;
        flex-grow: 1;
        padding: 4px;
        border-radius: 5px;
        background-color: rgba(30, 136, 229, 0.05);
    }
    .task-metric-value {
        font-size: 1.1rem;
        font-weight: bold;
        color: #1e88e5;
    }
    .task-metric-label {
        font-size: 0.75rem;
        color: #666;
    }

    /* تنسيق قائمة المهام */
    .achievements-table {
        width: 100%;
        margin-top: 15px;
        border-collapse: collapse;
    }
    .achievements-table th {
        background-color: #f0f2f6;
        padding: 8px 12px;
        text-align: right;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .achievements-table td {
        padding: 8px 12px;
        border-bottom: 1px solid #eee;
        font-size: 0.85rem;
    }
    .achievements-table tr:hover {
        background-color: rgba(30, 136, 229, 0.05);
    }

    /* تنسيق الشارات */
    .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 10px;
        font-size: 0.75rem;
        font-weight: 500;
        margin-right: 4px;
    }
    .badge-blue { background-color: rgba(30, 136, 229, 0.1); color: #1e88e5; }
    .badge-green { background-color: rgba(39, 174, 96, 0.1); color: #27AE60; }
    .badge-orange { background-color: rgba(243, 156, 18, 0.1); color: #F39C12; }
    .badge-red { background-color: rgba(231, 76, 60, 0.1); color: #E74C3C; }

    /* تنسيق مخطط الإنجازات */
    .achievements-timeline {
        margin-top: 20px;
        padding: 15px;
        background-color: #f8f9fa;
        border-radius: 8px;
    }
    .timeline-item {
        display: flex;
        margin-bottom: 15px;
        position: relative;
    }
    .timeline-date {
        width: 100px;
        text-align: left;
        padding-left: 10px;
        font-size: 0.8rem;
        color: #666;
    }
    .timeline-content {
        flex-grow: 1;
        background-color: white;
        padding: 10px;
        border-radius: 5px;
        border-right: 3px solid #1e88e5;
        position: relative;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    .timeline-content.completed { border-right-color: #27AE60; }
    .timeline-content.in-progress { border-right-color: #F39C12; }
    .timeline-content.planned { border-right-color: #E74C3C; }
    
    .timeline-content h4 {
        margin: 0;
        font-size: 0.95rem;
        color: #1e88e5;
    }
    .timeline-content p {
        margin: 5px 0 0;
        font-size: 0.85rem;
        color: #666;
    }
    .timeline-meta {
        display: flex;
        justify-content: space-between;
        margin-top: 8px;
    }
    .timeline-meta-item {
        font-size: 0.75rem;
        color: #777;
    }

    /* تنسيق عرض الأعضاء المتميزين */
    .member-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #e3e6f0 100%);
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
    }
    .member-name {
        font-size: 0.95rem;
        font-weight: 600;
        color: #1e88e5;
        margin-bottom: 3px;
    }
    .member-stats {
        display: flex;
        justify-content: space-between;
        margin-top: 5px;
    }
    .member-stat {
        text-align: center;
        flex-grow: 1;
    }
    .member-stat-value {
        font-size: 1rem;
        font-weight: bold;
        color: #1e88e5;
    }
    .member-stat-label {
        font-size: 0.7rem;
        color: #666;
    }

    /* --- قواعد Media Query للتبديل بين القائمتين وتحسين عرض الجوال --- */
    @media only screen and (max-width: 768px) {
        .top-navbar { display: none; }
        .mobile-menu-trigger { display: block; }
        .main .block-container { padding-right: 0.8rem !important; padding-left: 0.8rem !important; padding-top: 40px !important; }

        /* تصغير الخطوط والهوامش للعناوين في الجوال */
        h1 { font-size: 1.3rem; margin-bottom: 15px; padding-bottom: 8px; }
        h2 { font-size: 1.1rem; margin-top: 20px; margin-bottom: 10px; }
        h3 { font-size: 1.0rem; margin-top: 18px; margin-bottom: 8px; }

        /* تصغير خطوط المقاييس في الجوال */
        [data-testid="stMetricValue"] { font-size: 1.3rem !important; }
        [data-testid="stMetricLabel"] { font-size: 0.8rem !important; }
        .metric-card { padding: 10px; margin-bottom: 10px;}

        /* تصغير خطوط بطاقات المهام في الجوال */
        .task-title { font-size: 1rem; }
        .task-detail-item { font-size: 0.75rem; padding: 2px 5px; }
        .task-metric-value { font-size: 1rem; }
        .task-metric-label { font-size: 0.7rem; }

        /* تصغير خطوط التبويبات */
        button[data-baseweb="tab"] {
            font-size: 0.85rem !important;
            padding-top: 8px !important;
            padding-bottom: 8px !important;
        }
        /* تصغير خط منتقي السنة والفلاتر الأخرى */
        .stSelectbox label { font-size: 0.9rem !important; }
        .stTextInput label { font-size: 0.9rem !important; }

        /* تعديل الجدول للشاشات الصغيرة */
        .achievements-table th { font-size: 0.8rem; padding: 6px 8px; }
        .achievements-table td { font-size: 0.75rem; padding: 6px 8px; }

        /* تعديل بطاقة العضو للشاشات الصغيرة */
        .member-name { font-size: 0.9rem; }
        .member-stat-value { font-size: 0.9rem; }
        .member-stat-label { font-size: 0.65rem; }

        /* تعديل مخطط الإنجازات للشاشات الصغيرة */
        .timeline-date { width: 80px; font-size: 0.75rem; }
        .timeline-content h4 { font-size: 0.85rem; }
        .timeline-content p { font-size: 0.8rem; }
        .timeline-meta-item { font-size: 0.7rem; }
    }

    @media only screen and (min-width: 769px) {
        .top-navbar { display: block; }
        .mobile-menu-trigger, .mobile-menu, .mobile-menu-overlay, .mobile-menu-checkbox { display: none; }
    }

    @media only screen and (min-width: 769px) and (max-width: 1024px) {
        h1 { font-size: 1.5rem; }
        h2, h3 { font-size: 1.1rem; }
        .top-navbar a { font-size: 0.85rem; }
    }
</style>
"""

# =========================================
# القسم 3: هيكل HTML للقائمة وزر العودة للأعلى
# =========================================
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

# --- العنوان الرئيسي للصفحة ---
st.markdown("<h1>🏆 إنجاز المهام</h1>", unsafe_allow_html=True)

# =========================================
# القسم 5: الدوال المساعدة
# =========================================
def is_mobile():
    """التحقق من كون العرض الحالي محتملاً أن يكون جهاز محمول"""
    # ملاحظة: هذه الدالة تحتاج إلى طريقة لتحديد عرض الشاشة بشكل فعلي.
    # يمكنك استخدام مكون مثل streamlit_js_eval أو اختبار العرض يدويًا بتغيير حجم المتصفح.
    # حاليًا، ستُرجع False دائمًا.
    return False # غير القيمة إلى True لاختبار تنسيقات الجوال

def prepare_chart_layout(fig, title, is_mobile=False, chart_type="bar"):
    """تطبيق تنسيق موحد على مخططات Plotly مع الاستجابة للجوال"""
    try:
        fig.update_layout(dragmode=False)
        fig.update_xaxes(fixedrange=True)
        fig.update_yaxes(fixedrange=True)

        # إعدادات التخطيط المشتركة
        layout_settings = {
            "title": title,
            "font": {"family": "Tajawal"},
            "plot_bgcolor": "rgba(240, 240, 240, 0.8)",
            "paper_bgcolor": "white",
            "legend": {
                "orientation": "h",
                "yanchor": "bottom",
                "xanchor": "center",
                "x": 0.5,
            }
        }

        # تعديلات خاصة بالجوال
        if is_mobile:
            mobile_settings = {
                "height": 260 if chart_type != "heatmap" else 300,
                "margin": {"t": 30, "b": 60, "l": 5, "r": 5, "pad": 0},
                "font": {"size": 8},
                "title": {"font": {"size": 10}},
                "legend": {"y": -0.3, "font": {"size": 7}}
            }
            layout_settings.update(mobile_settings)

            # تعديلات خاصة بنوع المخطط للجوال
            if chart_type == "pie":
                layout_settings["showlegend"] = False
                fig.update_traces(textfont_size=8)
            elif chart_type == "line":
                fig.update_traces(marker=dict(size=3))
            elif chart_type == "bar":
                fig.update_xaxes(tickangle=0, tickfont={"size": 6})
                fig.update_yaxes(tickfont={"size": 6})
            elif chart_type == "heatmap":
                 fig.update_traces(textfont={"size": 8})
                 fig.update_yaxes(tickfont=dict(size=7))
        else:
            # إعدادات سطح المكتب
            desktop_settings = {
                "height": 400 if chart_type != "heatmap" else 380,
                "margin": {"t": 40, "b": 80, "l": 25, "r": 25, "pad": 4},
                "legend": {"y": -0.2, "font": {"size": 9}},
                "title": {"font": {"size": 14}},
                "font": {"size": 10}
            }
            layout_settings.update(desktop_settings)
            if chart_type == "heatmap":
                 fig.update_traces(textfont={"size": 10})
                 fig.update_yaxes(tickfont=dict(size=9))

        fig.update_layout(**layout_settings)
    except Exception as e:
        st.warning(f"تعذر تطبيق إعدادات التخطيط للرسم '{title}': {e}")

    return fig

def get_status_badge(status):
    """تحديد فئة الشارة بناءً على حالة المهمة"""
    if status == "منجزة":
        return "badge-green"
    elif status == "قيد التنفيذ":
        return "badge-orange"
    elif status == "مخطط لها":
        return "badge-red"
    else:
        return "badge-blue"

def get_status_class(status):
    """تحديد فئة CSS بناءً على حالة المهمة"""
    if status == "منجزة":
        return "completed"
    elif status == "قيد التنفيذ":
        return "in-progress"
    elif status == "مخطط لها":
        return "planned"
    else:
        return ""

def format_date(date_str):
    """تنسيق التاريخ بالشكل المطلوب"""
    try:
        date_obj = pd.to_datetime(date_str)
        return date_obj.strftime("%Y/%m/%d")
    except:
        return date_str

# =========================================
# القسم 6: دوال تحميل البيانات
# =========================================

# --- تحديد قاموس رموز البرامج ---
PROGRAM_MAP = {
    "بكالوريوس في القرآن وعلومه": "bachelor_quran",
    "بكالوريوس القراءات": "bachelor_readings",
    "ماجستير الدراسات القرآنية المعاصرة": "master_contemporary",
    "ماجستير القراءات": "master_readings",
    "دكتوراه علوم القرآن": "phd_quran",
    "دكتوراه القراءات": "phd_readings"
}

# --- دالة لتحديد السنوات التي تتوفر لها بيانات فعلية ---
@st.cache_data(ttl=3600)
def get_available_years():
    """تحديد السنوات التي تتوفر لها بيانات فعلية في المجلدات"""
    available_years = []
    # نطاق السنوات المحتملة
    potential_years = list(range(2020, 2026))  # يمكن تعديل النطاق حسب الحاجة

    for year in potential_years:
        # فحص وجود ملف البيانات لهذه السنة
        has_data = False

        # بالنسبة لصفحة إنجاز المهام
        tasks_file_path = f"data/department/{year}/tasks_{year}.csv"
        achievements_path = f"data/department/{year}/achievements_{year}.csv"
        
        if (os.path.exists(tasks_file_path) and os.path.getsize(tasks_file_path) > 100) or \
           (os.path.exists(achievements_path) and os.path.getsize(achievements_path) > 100):
            has_data = True

        # إذا وجدنا أي بيانات لهذه السنة، نضيفها إلى القائمة
        if has_data:
            available_years.append(year)

    # إذا لم نجد أي سنوات، نستخدم العام الحالي كمثال
    if not available_years:
        current_year = datetime.now().year
        st.warning(f"لم يتم العثور على بيانات لأي سنة. يرجى إضافة ملفات البيانات في المجلدات المناسبة.")
        return [current_year]

    # ترتيب السنوات تنازليًا (الأحدث أولاً)
    return sorted(available_years, reverse=True)

def generate_sample_tasks_data(year):
    """توليد بيانات تجريبية للمهام عند عدم وجود ملف"""
    current_date = datetime.now()
    # تحديد تواريخ ضمن السنة المحددة
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)
    
    if current_date < end_date:
        end_date = current_date
    
    # تعريف أنواع المهام وفئاتها
    task_categories = ["تطوير المقررات", "أنشطة بحثية", "لجان علمية", "خدمة المجتمع", "تدريب وورش عمل"]
    member_names = [
        "د. محمد أحمد علي", "د. عائشة محمد سعيد", "د. عبدالله محمد خالد", 
        "د. فاطمة علي حسن", "د. خالد إبراهيم عمر", "د. نورا سعيد أحمد",
        "د. عبد الله حماد حميد القرشي", "د. ناصر سعود حمود القثامي"
    ]
    statuses = ["منجزة", "قيد التنفيذ", "مخطط لها"]
    
    def random_date(start, end):
        delta = end - start
        int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
        random_second = np.random.randint(0, int_delta)
        return start + timedelta(seconds=random_second)
    
    # توليد مهام تجريبية
    tasks = []
    num_tasks = 30  # عدد المهام التي سيتم توليدها
    
    for i in range(1, num_tasks + 1):
        task_date = random_date(start_date, end_date)
        status = np.random.choice(statuses, p=[0.6, 0.3, 0.1])  # توزيع الاحتمالات لكل حالة
        
        if status == "منجزة":
            completion_date = random_date(task_date, end_date)
            due_date = task_date + timedelta(days=np.random.randint(10, 30))
        elif status == "قيد التنفيذ":
            completion_date = None
            due_date = task_date + timedelta(days=np.random.randint(15, 45))
        else:  # مخطط لها
            completion_date = None
            due_date = task_date + timedelta(days=np.random.randint(20, 60))
        
        category = np.random.choice(task_categories)
        member = np.random.choice(member_names)
        virtual_hours = np.random.randint(5, 30)
        points = int(virtual_hours * np.random.uniform(1.5, 3.0))
        
        task_name = f"مهمة {category} رقم {i}"
        description = f"وصف تفصيلي للمهمة ضمن فئة {category}"
        
        task = {
            "رقم المهمة": i,
            "اسم المهمة": task_name,
            "الوصف": description,
            "العضو المسؤول": member,
            "الفئة": category,
            "تاريخ البدء": task_date.strftime("%Y-%m-%d"),
            "تاريخ الاستحقاق": due_date.strftime("%Y-%m-%d"),
            "تاريخ الإنجاز": completion_date.strftime("%Y-%m-%d") if completion_date else None,
            "الساعات الافتراضية": virtual_hours,
            "النقاط": points,
            "الحالة": status,
            "الأولوية": np.random.choice(["عالية", "متوسطة", "منخفضة"])
        }
        tasks.append(task)
    
    return pd.DataFrame(tasks)

@st.cache_data(ttl=3600)
def load_tasks_data(year=None):
    """تحميل بيانات المهام للسنة المحددة"""
    try:
        available_years = get_available_years()

        if year is None:
            year = max(available_years) if available_years else datetime.now().year

        # المسار بناءً على هيكل المستودع والسنة
        file_path = f"data/department/{year}/tasks_{year}.csv"

        # التحقق من وجود الملف، وإلا حاول تحميل الملف القديم
        if os.path.exists(file_path) and os.path.getsize(file_path) > 100:
            df = pd.read_csv(file_path)
            df["year"] = year # إضافة عمود السنة للتمييز لاحقاً
            return df
        else:
            # إذا لم يجد ملف السنة المحددة، ابحث عن أقرب سنة متاحة
            for y in sorted(available_years, reverse=True):
                alt_file_path = f"data/department/{y}/tasks_{y}.csv"
                if os.path.exists(alt_file_path) and os.path.getsize(alt_file_path) > 100:
                    st.warning(f"بيانات سنة {year} غير متوفرة. تم تحميل بيانات سنة {y} بدلاً عنها.")
                    df = pd.read_csv(alt_file_path)
                    df["year"] = y # إضافة عمود السنة الفعلية
                    return df

            # إذا لم يجد أي ملف، استخدم بيانات تجريبية
            st.warning(f"بيانات سنة {year} غير متوفرة. استخدام بيانات تجريبية.")
            return generate_sample_tasks_data(year)

    except Exception as e:
        st.error(f"خطأ في تحميل بيانات المهام: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_achievements_data(year=None):
    """تحميل بيانات الإنجازات للسنة المحددة"""
    try:
        available_years = get_available_years()

        if year is None:
            year = max(available_years) if available_years else datetime.now().year

        file_path = f"data/department/{year}/achievements_{year}.csv"
        
        if os.path.exists(file_path) and os.path.getsize(file_path) > 100:
            df = pd.read_csv(file_path)
            df["year"] = year
            return df
        else:
            # إذا لم يجد ملف السنة المحددة، ابحث عن أقرب سنة متاحة
            for y in sorted(available_years, reverse=True):
                alt_file_path = f"data/department/{y}/achievements_{y}.csv"
                if os.path.exists(alt_file_path) and os.path.getsize(alt_file_path) > 100:
                    st.warning(f"بيانات إنجازات سنة {year} غير متوفرة. تم تحميل بيانات سنة {y} بدلاً عنها.")
                    df = pd.read_csv(alt_file_path)
                    df["year"] = y
                    return df
                    
            # إذا لم يجد أي ملف، استخدم بيانات المهام لتوليد الإنجازات
            tasks_df = load_tasks_data(year)
            if not tasks_df.empty:
                # تحويل المهام المنجزة إلى إنجازات
                completed_tasks = tasks_df[tasks_df["الحالة"] == "منجزة"].copy()
                if not completed_tasks.empty:
                    achievements_data = []
                    for _, task in completed_tasks.iterrows():
                        achievement = {
                            "العضو": task["العضو المسؤول"],
                            "الإنجاز": task["اسم المهمة"],
                            "التاريخ": task["تاريخ الإنجاز"] if "تاريخ الإنجاز" in task else task["تاريخ الاستحقاق"],
                            "النقاط": task["النقاط"] if "النقاط" in task else 10,
                            "الفئة": task["الفئة"] if "الفئة" in task else "أخرى",
                            "الساعات الافتراضية": task["الساعات الافتراضية"] if "الساعات الافتراضية" in task else 5
                        }
                        achievements_data.append(achievement)
                    return pd.DataFrame(achievements_data)
                    
            # إذا لا توجد مهام منجزة، إنشاء بيانات تجريبية
            achievements = []
            member_names = [
                "د. محمد أحمد علي", "د. عائشة محمد سعيد", "د. عبدالله محمد خالد", 
                "د. فاطمة علي حسن", "د. خالد إبراهيم عمر", "د. نورا سعيد أحمد",
                "د. عبد الله حماد حميد القرشي", "د. ناصر سعود حمود القثامي"
            ]
            achievement_types = ["نشر بحث", "إعداد دورة", "تطوير مقرر", "مشاركة في مؤتمر", "إنجاز مشروع", "تقديم ورشة عمل"]
            categories = ["تطوير المقررات", "أنشطة بحثية", "لجان علمية", "خدمة المجتمع", "تدريب وورش عمل"]
            
            # إنشاء تواريخ ضمن السنة المحددة
            start_date = datetime(year, 1, 1)
            end_date = datetime(year, 12, 31)
            if datetime.now() < end_date:
                end_date = datetime.now()
                
            for i in range(20):  # إنشاء 20 إنجاز تجريبي
                random_date = start_date + timedelta(days=np.random.randint(0, (end_date - start_date).days))
                achievements.append({
                    "العضو": np.random.choice(member_names),
                    "الإنجاز": f"{np.random.choice(achievement_types)} - {i+1}",
                    "التاريخ": random_date.strftime("%Y-%m-%d"),
                    "النقاط": np.random.randint(10, 60),
                    "الفئة": np.random.choice(categories),
                    "الساعات الافتراضية": np.random.randint(5, 30)
                })
            
            return pd.DataFrame(achievements)
            
    except Exception as e:
        st.error(f"خطأ في تحميل بيانات الإنجازات: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_faculty_data(year=None):
    """تحميل بيانات أعضاء هيئة التدريس للسنة المحددة"""
    try:
        available_years = get_available_years()

        if year is None:
            year = max(available_years) if available_years else datetime.now().year

        # المسار بناءً على هيكل المستودع والسنة
        file_path = f"data/department/{year}/faculty_{year}.csv"

        if os.path.exists(file_path) and os.path.getsize(file_path) > 100:
            df = pd.read_csv(file_path)
            return df
        else:
            # بيانات تجريبية لأعضاء هيئة التدريس
            faculty_data = [
                {"الاسم": "د. محمد أحمد علي", "الرتبة": "أستاذ مشارك", "التخصص": "قراءات", "حالة الموظف": "رأس العمل", "الجنس": "ذكر", "الجنسية": "سعودي"},
                {"الاسم": "د. عائشة محمد سعيد", "الرتبة": "أستاذ", "التخصص": "علوم القرآن", "حالة الموظف": "رأس العمل", "الجنس": "أنثى", "الجنسية": "سعودية"},
                {"الاسم": "د. عبدالله محمد خالد", "الرتبة": "أستاذ مساعد", "التخصص": "قراءات", "حالة الموظف": "رأس العمل", "الجنس": "ذكر", "الجنسية": "سعودي"},
                {"الاسم": "د. فاطمة علي حسن", "الرتبة": "أستاذ مشارك", "التخصص": "الدراسات القرآنية", "حالة الموظف": "رأس العمل", "الجنس": "أنثى", "الجنسية": "سعودية"},
                {"الاسم": "د. خالد إبراهيم عمر", "الرتبة": "أستاذ", "التخصص": "قراءات", "حالة الموظف": "متعاون", "الجنس": "ذكر", "الجنسية": "مصري"},
                {"الاسم": "د. نورا سعيد أحمد", "الرتبة": "أستاذ مساعد", "التخصص": "علوم القرآن", "حالة الموظف": "رأس العمل", "الجنس": "أنثى", "الجنسية": "سعودية"},
                {"الاسم": "د. عبد الله حماد حميد القرشي", "الرتبة": "أستاذ", "التخصص": "قراءات", "حالة الموظف": "رأس العمل", "الجنس": "ذكر", "الجنسية": "سعودي"},
                {"الاسم": "د. ناصر سعود حمود القثامي", "الرتبة": "أستاذ مشارك", "التخصص": "علوم القرآن", "حالة الموظف": "رأس العمل", "الجنس": "ذكر", "الجنسية": "سعودي"}
            ]
            return pd.DataFrame(faculty_data)
    except Exception as e:
        st.error(f"خطأ في تحميل بيانات أعضاء هيئة التدريس: {e}")
        return pd.DataFrame()

# =========================================
# القسم 7: منتقي السنة وتحميل البيانات الأولية
# =========================================
mobile_view = is_mobile()
AVAILABLE_YEARS = get_available_years()

# تطبيق منتقي السنة المعدل
if len(AVAILABLE_YEARS) > 1:
    selected_year = st.selectbox("اختر السنة", AVAILABLE_YEARS)
else:
    # إذا كانت هناك سنة واحدة فقط، نستخدمها مباشرة دون عرض منتقي
    if AVAILABLE_YEARS:
        selected_year = AVAILABLE_YEARS[0]
        st.info(f"البيانات متوفرة لسنة {selected_year} فقط")
    else:
        # في حالة عدم وجود سنوات متاحة على الإطلاق (احتياطي)
        selected_year = datetime.now().year
        st.warning("لا توجد بيانات متاحة لأي سنة. سيتم استخدام بيانات تجريبية.")

# تحميل البيانات للسنة المختارة
tasks_data = load_tasks_data(selected_year)
achievements_data = load_achievements_data(selected_year)
faculty_data = load_faculty_data(selected_year)

# =========================================
# القسم 8: حساب المؤشرات الرئيسية
# =========================================
# حساب المؤشرات الرئيسية من البيانات المتاحة
total_tasks = len(tasks_data) if not tasks_data.empty else 0
completed_tasks = len(tasks_data[tasks_data["الحالة"] == "منجزة"]) if not tasks_data.empty and "الحالة" in tasks_data.columns else 0
in_progress_tasks = len(tasks_data[tasks_data["الحالة"] == "قيد التنفيذ"]) if not tasks_data.empty and "الحالة" in tasks_data.columns else 0
planned_tasks = len(tasks_data[tasks_data["الحالة"] == "مخطط لها"]) if not tasks_data.empty and "الحالة" in tasks_data.columns else 0

total_members = len(faculty_data) if not faculty_data.empty else 0
active_members = 0  # سيتم حسابها لاحقاً

total_points = achievements_data["النقاط"].sum() if not achievements_data.empty and "النقاط" in achievements_data.columns else 0
total_hours = achievements_data["الساعات الافتراضية"].sum() if not achievements_data.empty and "الساعات الافتراضية" in achievements_data.columns else 0

# حساب المؤشرات المتعلقة بالأعضاء
if not achievements_data.empty and "العضو" in achievements_data.columns:
    member_achievements = achievements_data.groupby("العضو").size().reset_index()
    member_achievements.columns = ["العضو", "عدد الإنجازات"]
    active_members = len(member_achievements[member_achievements["عدد الإنجازات"] > 0])
    
    # حساب مجموع النقاط لكل عضو
    if "النقاط" in achievements_data.columns:
        member_points = achievements_data.groupby("العضو")["النقاط"].sum().reset_index()
        member_points.columns = ["العضو", "مجموع النقاط"]
        member_achievements = pd.merge(member_achievements, member_points, on="العضو", how="left")
    
    # حساب مجموع الساعات لكل عضو
    if "الساعات الافتراضية" in achievements_data.columns:
        member_hours = achievements_data.groupby("العضو")["الساعات الافتراضية"].sum().reset_index()
        member_hours.columns = ["العضو", "مجموع الساعات"]
        member_achievements = pd.merge(member_achievements, member_hours, on="العضو", how="left")

# حساب نسبة الإنجاز
completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

# حساب الإنجازات في الشهر الحالي
current_month_achievements = 0
if not achievements_data.empty and "التاريخ" in achievements_data.columns:
    achievements_data["التاريخ"] = pd.to_datetime(achievements_data["التاريخ"], errors='coerce')
    current_date = datetime.now()
    first_day_of_month = datetime(current_date.year, current_date.month, 1)
    current_month_mask = (achievements_data["التاريخ"] >= first_day_of_month) & (achievements_data["التاريخ"] <= current_date)
    current_month_achievements = achievements_data[current_month_mask].shape[0]

# =========================================
# القسم 9: عرض المقاييس الإجمالية
# =========================================
st.subheader("نظرة عامة")

# عرض المقاييس في صف (أو 3x2 في الجوال)
if mobile_view:
    row1_cols = st.columns(2)
    row2_cols = st.columns(2)
    row3_cols = st.columns(2)
    metric_cols = [row1_cols[0], row1_cols[1], row2_cols[0], row2_cols[1], row3_cols[0], row3_cols[1]]
else:
    metric_cols = st.columns(6)

# عرض المقاييس
with metric_cols[0]: st.metric("إجمالي المهام", f"{total_tasks:,}")
with metric_cols[1]: st.metric("المهام المنجزة", f"{completed_tasks:,}")
with metric_cols[2]: st.metric("مجموع النقاط", f"{total_points:,}")
with metric_cols[3]: st.metric("مجموع الساعات", f"{total_hours:,}")
with metric_cols[4]: st.metric("الأعضاء النشطين", f"{active_members:,} من {total_members:,}")
with metric_cols[5]: st.metric("إنجازات الشهر", f"{current_month_achievements:,}")

# =========================================
# القسم 10: إعداد التبويبات الرئيسية
# =========================================
main_tabs = st.tabs(["لوحة المعلومات", "قائمة المهام", "إنجازات الأعضاء", "المهام الحالية والمخطط لها", "تحليل الإنجازات"])

# =========================================
# القسم 11: تبويب لوحة المعلومات
# =========================================
with main_tabs[0]:
    st.markdown("### لوحة معلومات الإنجازات")
    
    # 1. توزيع المهام حسب الحالة (منجزة، قيد التنفيذ، مخطط لها)
    task_status_data = pd.DataFrame({
        "الحالة": ["منجزة", "قيد التنفيذ", "مخطط لها"],
        "العدد": [completed_tasks, in_progress_tasks, planned_tasks]
    })
    
    if mobile_view:
        fig_status = px.pie(task_status_data, values="العدد", names="الحالة", title="توزيع المهام حسب الحالة",
                         color="الحالة", color_discrete_map={"منجزة": "#27AE60", "قيد التنفيذ": "#F39C12", "مخطط لها": "#E74C3C"})
        fig_status = prepare_chart_layout(fig_status, "توزيع المهام حسب الحالة", is_mobile=mobile_view, chart_type="pie")
        st.plotly_chart(fig_status, use_container_width=True, config={"displayModeBar": False})
        
        # توزيع المهام حسب الفئة
        if not tasks_data.empty and "الفئة" in tasks_data.columns:
            category_counts = tasks_data["الفئة"].value_counts().reset_index()
            category_counts.columns = ["الفئة", "العدد"]
            fig_category = px.bar(category_counts, x="الفئة", y="العدد", title="توزيع المهام حسب الفئة",
                                 color="العدد", color_continuous_scale="Blues")
            fig_category = prepare_chart_layout(fig_category, "توزيع المهام حسب الفئة", is_mobile=mobile_view, chart_type="bar")
            st.plotly_chart(fig_category, use_container_width=True, config={"displayModeBar": False})
    else:
        col1, col2 = st.columns([1, 1])
        with col1:
            fig_status = px.pie(task_status_data, values="العدد", names="الحالة", title="توزيع المهام حسب الحالة",
                            color="الحالة", color_discrete_map={"منجزة": "#27AE60", "قيد التنفيذ": "#F39C12", "مخطط لها": "#E74C3C"})
            fig_status = prepare_chart_layout(fig_status, "توزيع المهام حسب الحالة", is_mobile=mobile_view, chart_type="pie")
            st.plotly_chart(fig_status, use_container_width=True, config={"displayModeBar": False})
        
        with col2:
            # توزيع المهام حسب الفئة
            if not tasks_data.empty and "الفئة" in tasks_data.columns:
                category_counts = tasks_data["الفئة"].value_counts().reset_index()
                category_counts.columns = ["الفئة", "العدد"]
                fig_category = px.bar(category_counts, x="الفئة", y="العدد", title="توزيع المهام حسب الفئة",
                                   color="العدد", color_continuous_scale="Blues")
                fig_category = prepare_chart_layout(fig_category, "توزيع المهام حسب الفئة", is_mobile=mobile_view, chart_type="bar")
                st.plotly_chart(fig_category, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("لا توجد بيانات كافية لعرض توزيع المهام حسب الفئة.")
    
    # 2. قسم أفضل المنجزين (Top Achievers)
    st.markdown("### أفضل المنجزين")
    
    if not achievements_data.empty and "العضو" in achievements_data.columns and "النقاط" in achievements_data.columns:
        top_achievers = achievements_data.groupby("العضو")["النقاط"].sum().reset_index()
        top_achievers = top_achievers.sort_values("النقاط", ascending=False).head(5)
        
        if mobile_view:
            fig_top = px.bar(top_achievers, x="العضو", y="النقاط", title="أفضل 5 أعضاء من حيث النقاط",
                           color="النقاط", color_continuous_scale="Greens")
            fig_top = prepare_chart_layout(fig_top, "أفضل 5 أعضاء", is_mobile=mobile_view, chart_type="bar")
            st.plotly_chart(fig_top, use_container_width=True, config={"displayModeBar": False})
        else:
            col3, col4 = st.columns([2, 1])
            with col3:
                fig_top = px.bar(top_achievers, y="العضو", x="النقاط", title="أفضل 5 أعضاء من حيث النقاط",
                               color="النقاط", color_continuous_scale="Greens", orientation='h')
                fig_top = prepare_chart_layout(fig_top, "أفضل 5 أعضاء", is_mobile=mobile_view, chart_type="bar")
                st.plotly_chart(fig_top, use_container_width=True, config={"displayModeBar": False})
            
            with col4:
                st.markdown("### 🏆 لوحة الصدارة")
                
                # عرض بطاقات للأعضاء المتميزين
                for i, (_, member) in enumerate(top_achievers.iterrows()):
                    member_name = member["العضو"]
                    member_points = member["النقاط"]
                    
                    # حساب عدد المهام المنجزة للعضو
                    completed_count = achievements_data[achievements_data["العضو"] == member_name].shape[0]
                    
                    # حساب مجموع الساعات الافتراضية للعضو
                    total_member_hours = achievements_data[achievements_data["العضو"] == member_name]["الساعات الافتراضية"].sum() if "الساعات الافتراضية" in achievements_data.columns else 0
                    
                    medal = "🥇" if i == 0 else ("🥈" if i == 1 else ("🥉" if i == 2 else ""))
                    
                    st.markdown(f"""
                    <div class="member-card">
                        <div class="member-name">{medal} {member_name}</div>
                        <div class="member-stats">
                            <div class="member-stat">
                                <div class="member-stat-value">{int(member_points)}</div>
                                <div class="member-stat-label">النقاط</div>
                            </div>
                            <div class="member-stat">
                                <div class="member-stat-value">{completed_count}</div>
                                <div class="member-stat-label">المهام</div>
                            </div>
                            <div class="member-stat">
                                <div class="member-stat-value">{int(total_member_hours)}</div>
                                <div class="member-stat-label">الساعات</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("لا توجد بيانات كافية لعرض أفضل المنجزين.")
    
    # 3. أحدث الإنجازات
    st.markdown("### أحدث الإنجازات")
    
    if not achievements_data.empty and "التاريخ" in achievements_data.columns:
        achievements_data["التاريخ"] = pd.to_datetime(achievements_data["التاريخ"], errors='coerce')
        latest_achievements = achievements_data.sort_values("التاريخ", ascending=False).head(5)
        
        if latest_achievements.empty:
            st.info("لا توجد إنجازات حديثة متاحة.")
        else:
            for _, achievement in latest_achievements.iterrows():
                member_name = achievement.get("العضو", "غير معروف")
                achievement_name = achievement.get("الإنجاز", "إنجاز غير محدد")
                achievement_date = achievement.get("التاريخ", None)
                achievement_points = achievement.get("النقاط", 0)
                achievement_hours = achievement.get("الساعات الافتراضية", 0)
                achievement_category = achievement.get("الفئة", "أخرى")
                
                formatted_date = achievement_date.strftime("%Y/%m/%d") if pd.notna(achievement_date) else ""
                
                st.markdown(f"""
                <div class="task-card completed">
                    <div class="task-header">
                        <div>
                            <div class="task-title">{achievement_name}</div>
                            <div style="font-size: 0.85rem; color: #666;">{member_name}</div>
                        </div>
                        <div>
                            <span class="badge badge-green">منجزة</span>
                        </div>
                    </div>
                    <div class="task-details">
                        <span class="task-detail-item">📅 {formatted_date}</span>
                        <span class="task-detail-item">🏷️ {achievement_category}</span>
                    </div>
                    <div class="task-metrics">
                        <div class="task-metric">
                            <div class="task-metric-value">{int(achievement_points)}</div>
                            <div class="task-metric-label">النقاط</div>
                        </div>
                        <div class="task-metric">
                            <div class="task-metric-value">{int(achievement_hours)}</div>
                            <div class="task-metric-label">الساعات</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("لا توجد بيانات كافية لعرض أحدث الإنجازات.")
        
    # 4. تحليل النقاط والساعات الافتراضية حسب الشهر
    st.markdown("### تحليل زمني للإنجازات")
    
    if not achievements_data.empty and "التاريخ" in achievements_data.columns:
        # تحويل التاريخ وإضافة عمود الشهر
        achievements_data["التاريخ"] = pd.to_datetime(achievements_data["التاريخ"], errors='coerce')
        achievements_data["الشهر"] = achievements_data["التاريخ"].dt.to_period("M").astype(str)
        
        # تجميع البيانات حسب الشهر
        monthly_data = achievements_data.groupby("الشهر").agg({
            "النقاط": "sum",
            "الساعات الافتراضية": "sum"
        }).reset_index()
        
        # ترتيب حسب التاريخ
        monthly_data["sort_date"] = pd.to_datetime(monthly_data["الشهر"], format="%Y-%m")
        monthly_data = monthly_data.sort_values("sort_date").reset_index(drop=True)
        monthly_data = monthly_data.drop("sort_date", axis=1)
        
        # رسم بياني للنقاط والساعات حسب الشهر
        fig_monthly = px.line(monthly_data, x="الشهر", y=["النقاط", "الساعات الافتراضية"], 
                            title="تطور النقاط والساعات الافتراضية حسب الشهر",
                            labels={"value": "العدد", "variable": "النوع", "الشهر": "الشهر"},
                            markers=True, color_discrete_sequence=["#1e88e5", "#27AE60"])
        fig_monthly = prepare_chart_layout(fig_monthly, "تطور النقاط والساعات الافتراضية", is_mobile=mobile_view, chart_type="line")
        st.plotly_chart(fig_monthly, use_container_width=True, config={"displayModeBar": False})
        
        # رسم بياني لعدد الإنجازات حسب الشهر
        monthly_counts = achievements_data.groupby("الشهر").size().reset_index()
        monthly_counts.columns = ["الشهر", "عدد الإنجازات"]
        monthly_counts["sort_date"] = pd.to_datetime(monthly_counts["الشهر"], format="%Y-%m")
        monthly_counts = monthly_counts.sort_values("sort_date").reset_index(drop=True)
        monthly_counts = monthly_counts.drop("sort_date", axis=1)
        
        fig_monthly_counts = px.bar(monthly_counts, x="الشهر", y="عدد الإنجازات", 
                                 title="عدد الإنجازات حسب الشهر",
                                 color="عدد الإنجازات", color_continuous_scale="Blues")
        fig_monthly_counts = prepare_chart_layout(fig_monthly_counts, "عدد الإنجازات حسب الشهر", is_mobile=mobile_view, chart_type="bar")
        st.plotly_chart(fig_monthly_counts, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("لا توجد بيانات كافية لعرض التحليل الزمني للإنجازات.")

# =========================================
# =========================================
# =========================================
# القسم 12: تبويب قائمة المهام
# =========================================
with main_tabs[1]:
    st.markdown("### قائمة المهام")
    
    # دالة لعرض بطاقة المهمة بشكل صحيح
    def render_task_card(task, i):
        """تقوم بإنشاء بطاقة مهمة بطريقة مختلفة تضمن عرض HTML بشكل صحيح"""
        task_id = task.get("رقم المهمة", i+1)
        task_name = task.get("اسم المهمة", "مهمة غير محددة")
        task_description = task.get("الوصف", "")
        member_name = task.get("العضو المسؤول", "")
        member_display = member_name if pd.notna(member_name) and member_name.strip() != "" else "غير معين"
        category = task.get("الفئة", "غير مصنفة")
        start_date = format_date(task.get("تاريخ البدء", ""))
        due_date = format_date(task.get("تاريخ الاستحقاق", ""))
        completion_date = format_date(task.get("تاريخ الإنجاز", "")) if "تاريخ الإنجاز" in task and pd.notna(task["تاريخ الإنجاز"]) else "-"
        virtual_hours = int(task.get("الساعات الافتراضية", 0))
        points = int(task.get("النقاط", 0))
        status = task.get("الحالة", "غير محدد")
        priority = task.get("الأولوية", "متوسطة")
        
        # تحديد لون الأولوية
        priority_badge = "badge-red" if priority == "عالية" else ("badge-orange" if priority == "متوسطة" else "badge-blue")
        
        # تحديد صنف CSS بناءً على الحالة
        status_class = get_status_class(status)
        status_badge = get_status_badge(status)
        
        # تقسيم البطاقة إلى أجزاء لتسهيل التنقيح
        # 1. الجزء العلوي من البطاقة
        card_top = f"""
        <div class="task-card {status_class}">
            <div class="task-header">
                <div>
                    <div class="task-title">{task_name}</div>
                    <div style="font-size: 0.85rem; color: #666;">{member_display}</div>
                </div>
                <div>
                    <span class="badge {status_badge}">{status}</span>
                    <span class="badge {priority_badge}">{priority}</span>
                </div>
            </div>
            <div style="font-size: 0.85rem; margin: 8px 0;">{task_description}</div>
            <div class="task-details">
                <span class="task-detail-item">🏷️ {category}</span>
                <span class="task-detail-item">📅 تاريخ البدء: {start_date}</span>
                <span class="task-detail-item">⏳ تاريخ الاستحقاق: {due_date}</span>
        """
        
        # إضافة تاريخ الإنجاز إذا كان موجودًا
        if completion_date != "-":
            card_top += f'<span class="task-detail-item">✅ تاريخ الإنجاز: {completion_date}</span>'
        
        # إغلاق قسم التفاصيل
        card_top += "</div>"
        
        # 2. قسم المقاييس (المشكلة الرئيسية)
        # استخدام بنية HTML أبسط
        metrics_html = f"""
            <div style="display: flex; gap: 10px; margin-top: 8px;">
                <div style="text-align: center; flex-grow: 1; padding: 4px; border-radius: 5px; background-color: rgba(30, 136, 229, 0.05);">
                    <div style="font-size: 1.1rem; font-weight: bold; color: #1e88e5;">{points}</div>
                    <div style="font-size: 0.75rem; color: #666;">النقاط</div>
                </div>
                <div style="text-align: center; flex-grow: 1; padding: 4px; border-radius: 5px; background-color: rgba(30, 136, 229, 0.05);">
                    <div style="font-size: 1.1rem; font-weight: bold; color: #1e88e5;">{virtual_hours}</div>
                    <div style="font-size: 0.75rem; color: #666;">الساعات</div>
                </div>
            </div>
        </div>
        """
        
        # 3. دمج الأجزاء معًا وعرضها
        complete_html = card_top + metrics_html
        st.markdown(complete_html, unsafe_allow_html=True)
    
    # فلاتر البحث والتصفية
    st.markdown("#### بحث وتصفية")
    
    if mobile_view:
        filter_container = st.container()
        with filter_container:
            if "الحالة" in tasks_data.columns:
                all_statuses = ["الكل"] + sorted(tasks_data["الحالة"].unique().tolist())
                selected_status = st.selectbox("حالة المهمة", all_statuses, key="status_mobile")
            else: selected_status = "الكل"

            if "الفئة" in tasks_data.columns:
                all_categories = ["الكل"] + sorted(tasks_data["الفئة"].unique().tolist())
                selected_category = st.selectbox("فئة المهمة", all_categories, key="category_mobile")
            else: selected_category = "الكل"

            if "العضو المسؤول" in tasks_data.columns:
                all_members = ["الكل", "غير معين"] + sorted(tasks_data["العضو المسؤول"].dropna().unique().tolist())
                selected_member = st.selectbox("العضو المسؤول", all_members, key="member_mobile")
            else: selected_member = "الكل"

            if "الأولوية" in tasks_data.columns:
                all_priorities = ["الكل", "عالية", "متوسطة", "منخفضة"]
                selected_priority = st.selectbox("الأولوية", all_priorities, key="priority_mobile")
            else: selected_priority = "الكل"
    else: # عرض سطح المكتب
        filter_cols = st.columns([1, 1, 1, 1])
        with filter_cols[0]:
            if "الحالة" in tasks_data.columns:
                all_statuses = ["الكل"] + sorted(tasks_data["الحالة"].unique().tolist())
                selected_status = st.selectbox("حالة المهمة", all_statuses, key="status_desktop")
            else: selected_status = "الكل"
        with filter_cols[1]:
            if "الفئة" in tasks_data.columns:
                all_categories = ["الكل"] + sorted(tasks_data["الفئة"].unique().tolist())
                selected_category = st.selectbox("فئة المهمة", all_categories, key="category_desktop")
            else: selected_category = "الكل"
        with filter_cols[2]:
            if "العضو المسؤول" in tasks_data.columns:
                all_members = ["الكل", "غير معين"] + sorted(tasks_data["العضو المسؤول"].dropna().unique().tolist())
                selected_member = st.selectbox("العضو المسؤول", all_members, key="member_desktop")
            else: selected_member = "الكل"
        with filter_cols[3]:
            if "الأولوية" in tasks_data.columns:
                all_priorities = ["الكل", "عالية", "متوسطة", "منخفضة"]
                selected_priority = st.selectbox("الأولوية", all_priorities, key="priority_desktop")
            else: selected_priority = "الكل"

    # فلتر البحث بالنص
    search_query = st.text_input("البحث في المهام", placeholder="ادخل اسم المهمة أو جزء من الوصف...")

    # تطبيق الفلاتر
    filtered_tasks = tasks_data.copy()
    if selected_status != "الكل" and "الحالة" in filtered_tasks.columns: 
        filtered_tasks = filtered_tasks[filtered_tasks["الحالة"] == selected_status]
    if selected_category != "الكل" and "الفئة" in filtered_tasks.columns: 
        filtered_tasks = filtered_tasks[filtered_tasks["الفئة"] == selected_category]
    if selected_member != "الكل" and "العضو المسؤول" in filtered_tasks.columns: 
        if selected_member == "غير معين":
            filtered_tasks = filtered_tasks[filtered_tasks["العضو المسؤول"].isna() | 
                                            (filtered_tasks["العضو المسؤول"] == "") |
                                            (filtered_tasks["العضو المسؤول"] == "غير معين")]
        else:
            filtered_tasks = filtered_tasks[filtered_tasks["العضو المسؤول"] == selected_member]
    if selected_priority != "الكل" and "الأولوية" in filtered_tasks.columns: 
        filtered_tasks = filtered_tasks[filtered_tasks["الأولوية"] == selected_priority]
    if search_query:
        search_cond = False
        if "اسم المهمة" in filtered_tasks.columns:
            search_cond = search_cond | filtered_tasks["اسم المهمة"].str.contains(search_query, case=False, na=False)
        if "الوصف" in filtered_tasks.columns:
            search_cond = search_cond | filtered_tasks["الوصف"].str.contains(search_query, case=False, na=False)
        if "العضو المسؤول" in filtered_tasks.columns:
            search_cond = search_cond | filtered_tasks["العضو المسؤول"].str.contains(search_query, case=False, na=False)
        filtered_tasks = filtered_tasks[search_cond]

    # عرض قائمة المهام المصفاة
    if len(filtered_tasks) > 0:
        st.markdown(f"#### المهام المطابقة ({len(filtered_tasks)})")
        
        for i, task in filtered_tasks.iterrows():
            render_task_card(task, i)
    else:
        st.info("لا توجد مهام مطابقة للفلاتر المحددة.")
# =========================================
# القسم 13: تبويب إنجازات الأعضاء
# =========================================
with main_tabs[2]:
    st.markdown("### إنجازات الأعضاء")
    
    if not achievements_data.empty and "العضو" in achievements_data.columns:
        # حساب إجماليات كل عضو
        member_summary = achievements_data.groupby("العضو").agg({
            "النقاط": "sum",
            "الساعات الافتراضية": "sum"
        }).reset_index()
        
        # عدد الإنجازات لكل عضو
        achievement_counts = achievements_data.groupby("العضو").size().reset_index()
        achievement_counts.columns = ["العضو", "عدد الإنجازات"]
        
        # دمج البيانات
        member_summary = pd.merge(member_summary, achievement_counts, on="العضو", how="left")
        
        # ترتيب حسب النقاط تنازليًا
        member_summary = member_summary.sort_values("النقاط", ascending=False)
        
        # عرض مخطط للنقاط حسب الأعضاء
        fig_points = px.bar(member_summary, y="العضو", x="النقاط", title="توزيع النقاط حسب الأعضاء",
                          color="النقاط", orientation='h', color_continuous_scale="Blues")
        fig_points = prepare_chart_layout(fig_points, "توزيع النقاط حسب الأعضاء", is_mobile=mobile_view, chart_type="bar")
        st.plotly_chart(fig_points, use_container_width=True, config={"displayModeBar": False})
        
        # جدول تفصيلي للأعضاء
        st.markdown("#### بيانات الأعضاء التفصيلية")
        st.markdown("""
        <table class="achievements-table">
            <tr>
                <th>#</th>
                <th>العضو</th>
                <th>عدد الإنجازات</th>
                <th>مجموع النقاط</th>
                <th>مجموع الساعات</th>
                <th>متوسط النقاط</th>
            </tr>
        """, unsafe_allow_html=True)
        
        for i, (_, row) in enumerate(member_summary.iterrows()):
            member_name = row["العضو"]
            total_points = row["النقاط"]
            total_hours = row["الساعات الافتراضية"]
            achievement_count = row["عدد الإنجازات"]
            avg_points = total_points / achievement_count if achievement_count > 0 else 0
            
            st.markdown(f"""
            <tr>
                <td>{i+1}</td>
                <td>{member_name}</td>
                <td>{achievement_count}</td>
                <td>{int(total_points)}</td>
                <td>{int(total_hours)}</td>
                <td>{avg_points:.1f}</td>
            </tr>
            """, unsafe_allow_html=True)
        
        st.markdown("</table>", unsafe_allow_html=True)
        
        # إضافة قسم لعرض تفاصيل إنجازات العضو المحدد
        st.markdown("#### تفاصيل إنجازات عضو محدد")
        
        selected_detail_member = st.selectbox("اختر العضو لعرض تفاصيل إنجازاته", 
                                           ["اختر عضوًا..."] + member_summary["العضو"].tolist())
        
        if selected_detail_member != "اختر عضوًا...":
            member_achievements = achievements_data[achievements_data["العضو"] == selected_detail_member].copy()
            
            if not member_achievements.empty:
                member_achievements["التاريخ"] = pd.to_datetime(member_achievements["التاريخ"], errors='coerce')
                member_achievements = member_achievements.sort_values("التاريخ", ascending=False)
                
                # معلومات ملخصة عن العضو
                member_info = member_summary[member_summary["العضو"] == selected_detail_member].iloc[0]
                
                st.markdown(f"""
                <div style="padding: 15px; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 20px;">
                    <h3 style="margin-top: 0;">{selected_detail_member}</h3>
                    <div style="display: flex; flex-wrap: wrap; gap: 20px; margin-top: 10px;">
                        <div style="flex: 1; min-width: 150px;">
                            <div style="font-size: 1.5rem; font-weight: bold; color: #1e88e5;">{int(member_info['النقاط'])}</div>
                            <div style="font-size: 0.9rem; color: #666;">مجموع النقاط</div>
                        </div>
                        <div style="flex: 1; min-width: 150px;">
                            <div style="font-size: 1.5rem; font-weight: bold; color: #27AE60;">{int(member_info['عدد الإنجازات'])}</div>
                            <div style="font-size: 0.9rem; color: #666;">عدد الإنجازات</div>
                        </div>
                        <div style="flex: 1; min-width: 150px;">
                            <div style="font-size: 1.5rem; font-weight: bold; color: #F39C12;">{int(member_info['الساعات الافتراضية'])}</div>
                            <div style="font-size: 0.9rem; color: #666;">مجموع الساعات</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # عرض قائمة الإنجازات
                st.markdown("##### قائمة الإنجازات")
                
                for i, achievement in member_achievements.iterrows():
                    achievement_name = achievement.get("الإنجاز", "إنجاز غير محدد")
                    achievement_date = achievement.get("التاريخ", None)
                    achievement_points = achievement.get("النقاط", 0)
                    achievement_hours = achievement.get("الساعات الافتراضية", 0)
                    achievement_category = achievement.get("الفئة", "أخرى")
                    
                    formatted_date = achievement_date.strftime("%Y/%m/%d") if pd.notna(achievement_date) else ""
                    
                    st.markdown(f"""
                    <div class="task-card completed" style="margin-bottom: 8px;">
                        <div class="task-header">
                            <div>
                                <div class="task-title">{achievement_name}</div>
                            </div>
                            <div>
                                <span class="badge badge-blue">{achievement_category}</span>
                            </div>
                        </div>
                        <div class="task-details">
                            <span class="task-detail-item">📅 {formatted_date}</span>
                        </div>
                        <div class="task-metrics">
                            <div class="task-metric">
                                <div class="task-metric-value">{int(achievement_points)}</div>
                                <div class="task-metric-label">النقاط</div>
                            </div>
                            <div class="task-metric">
                                <div class="task-metric-value">{int(achievement_hours)}</div>
                                <div class="task-metric-label">الساعات</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # عرض تحليل توزيع إنجازات العضو حسب الفئة
                if "الفئة" in member_achievements.columns:
                    st.markdown("##### تحليل إنجازات العضو")
                    
                    # توزيع حسب الفئة
                    category_analysis = member_achievements.groupby("الفئة").agg({
                        "النقاط": "sum",
                        "الساعات الافتراضية": "sum"
                    }).reset_index()
                    
                    # عرض التوزيع حسب الفئة
                    fig_member_category = px.pie(category_analysis, values="النقاط", names="الفئة", 
                                               title=f"توزيع نقاط {selected_detail_member} حسب الفئة",
                                               color_discrete_sequence=px.colors.qualitative.Set2)
                    fig_member_category = prepare_chart_layout(fig_member_category, f"توزيع نقاط {selected_detail_member}", is_mobile=mobile_view, chart_type="pie")
                    st.plotly_chart(fig_member_category, use_container_width=True, config={"displayModeBar": False})
                    
                    # التحليل الزمني للإنجازات
                    if "التاريخ" in member_achievements.columns:
                        member_achievements["الشهر"] = member_achievements["التاريخ"].dt.to_period("M").astype(str)
                        monthly_analysis = member_achievements.groupby("الشهر").agg({
                            "النقاط": "sum",
                            "الساعات الافتراضية": "sum"
                        }).reset_index()
                        
                        monthly_analysis["sort_date"] = pd.to_datetime(monthly_analysis["الشهر"], format="%Y-%m")
                        monthly_analysis = monthly_analysis.sort_values("sort_date").reset_index(drop=True)
                        monthly_analysis = monthly_analysis.drop("sort_date", axis=1)
                        
                        fig_monthly_member = px.line(monthly_analysis, x="الشهر", y=["النقاط", "الساعات الافتراضية"], 
                                                   title=f"تطور نقاط وساعات {selected_detail_member} حسب الشهر",
                                                   labels={"value": "العدد", "variable": "النوع", "الشهر": "الشهر"},
                                                   markers=True, color_discrete_sequence=["#1e88e5", "#27AE60"])
                        fig_monthly_member = prepare_chart_layout(fig_monthly_member, f"تطور نقاط وساعات {selected_detail_member}", is_mobile=mobile_view, chart_type="line")
                        st.plotly_chart(fig_monthly_member, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info(f"لا توجد إنجازات متاحة للعضو {selected_detail_member}.")
    else:
        st.info("لا توجد بيانات كافية لعرض إنجازات الأعضاء.")

# =========================================
# =========================================
# القسم 14: تبويب المهام الحالية والمخطط لها
# =========================================
with main_tabs[3]:
    st.markdown("### المهام الحالية والمخطط لها")
    
    if not tasks_data.empty and "الحالة" in tasks_data.columns:
        # تقسيم التبويب الداخلي إلى جزئين: المهام الجارية والمهام المخطط لها
        inner_tabs = st.tabs(["المهام قيد التنفيذ", "المهام المخطط لها", "المهام غير المكتملة"])
        
        # 1. تبويب المهام قيد التنفيذ
        with inner_tabs[0]:
            in_progress_tasks = tasks_data[tasks_data["الحالة"] == "قيد التنفيذ"].copy()
            
            if not in_progress_tasks.empty:
                # حاول ترتيب المهام حسب تاريخ الاستحقاق إذا كان متاحًا
                if "تاريخ الاستحقاق" in in_progress_tasks.columns:
                    in_progress_tasks["تاريخ الاستحقاق"] = pd.to_datetime(in_progress_tasks["تاريخ الاستحقاق"], errors='coerce')
                    in_progress_tasks = in_progress_tasks.sort_values("تاريخ الاستحقاق")
                
                # إضافة عمود للأيام المتبقية حتى الاستحقاق
                if "تاريخ الاستحقاق" in in_progress_tasks.columns:
                    current_date = pd.to_datetime(datetime.now().date())
                    in_progress_tasks["الأيام المتبقية"] = (in_progress_tasks["تاريخ الاستحقاق"] - current_date).dt.days
                
                # عنوان وعرض عدد المهام
                st.markdown(f"#### المهام قيد التنفيذ ({len(in_progress_tasks)})")
                
                # عرض مخطط زمني للمهام
                st.markdown('<div class="achievements-timeline">', unsafe_allow_html=True)
                
                for i, task in in_progress_tasks.iterrows():
                    task_name = task.get("اسم المهمة", "مهمة غير محددة")
                    member_name = task.get("العضو المسؤول", "")
                    member_display = member_name if pd.notna(member_name) and member_name.strip() != "" else "غير معين"
                    start_date = task.get("تاريخ البدء", "")
                    due_date = task.get("تاريخ الاستحقاق", "")
                    category = task.get("الفئة", "غير مصنفة")
                    priority = task.get("الأولوية", "متوسطة")
                    days_remaining = task.get("الأيام المتبقية", None)
                    
                    formatted_start = format_date(start_date)
                    formatted_due = format_date(due_date)
                    
                    # تحديد لون المهمة بناءً على الأيام المتبقية
                    timeline_class = "in-progress"
                    days_text = ""
                    if days_remaining is not None:
                        if days_remaining < 0:
                            days_text = f"<span style='color: #E74C3C;'>متأخرة بـ {abs(days_remaining)} يوم</span>"
                        elif days_remaining == 0:
                            days_text = "<span style='color: #F39C12;'>مستحقة اليوم</span>"
                        else:
                            days_text = f"<span style='color: #27AE60;'>متبقي {days_remaining} يوم</span>"
                    
                    # تحديد لون الأولوية
                    priority_class = "badge-red" if priority == "عالية" else ("badge-orange" if priority == "متوسطة" else "badge-blue")
                    
                    st.markdown(f"""
                    <div class="timeline-item">
                        <div class="timeline-date">{formatted_due}</div>
                        <div class="timeline-content {timeline_class}">
                            <h4>{task_name}</h4>
                            <p>{member_display} • {category}</p>
                            <div class="timeline-meta">
                                <div class="timeline-meta-item">
                                    <span class="badge {priority_class}">{priority}</span>
                                </div>
                                <div class="timeline-meta-item">
                                    {days_text}
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # إضافة رسم بياني لتوزيع المهام قيد التنفيذ حسب العضو المسؤول
                if "العضو المسؤول" in in_progress_tasks.columns:
                    # التعامل مع العضو الغير معين
                    in_progress_tasks["العضو المعروض"] = in_progress_tasks["العضو المسؤول"].apply(
                        lambda x: "غير معين" if pd.isna(x) or x.strip() == "" else x
                    )
                    member_counts = in_progress_tasks["العضو المعروض"].value_counts().reset_index()
                    member_counts.columns = ["العضو المسؤول", "عدد المهام"]
                    
                    fig_members = px.bar(member_counts, y="العضو المسؤول", x="عدد المهام", 
                                      title="توزيع المهام قيد التنفيذ حسب العضو",
                                      color="عدد المهام", orientation='h', color_continuous_scale="Oranges")
                    fig_members = prepare_chart_layout(fig_members, "توزيع المهام قيد التنفيذ", is_mobile=mobile_view, chart_type="bar")
                    st.plotly_chart(fig_members, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("لا توجد مهام قيد التنفيذ حاليًا.")
        
        # 2. تبويب المهام المخطط لها
        with inner_tabs[1]:
            planned_tasks = tasks_data[tasks_data["الحالة"] == "مخطط لها"].copy()
            
            if not planned_tasks.empty:
                # إضافة تبويب جديد للتصفية بين "المهام المعينة" و"المهام غير المعينة"
                assignment_tabs = st.radio(
                    "عرض المهام المخطط لها",
                    ["جميع المهام", "المهام المعينة", "المهام غير المعينة"],
                    horizontal=True
                )
                
                # تطبيق الفلتر حسب التعيين
                filtered_planned = planned_tasks.copy()
                if assignment_tabs == "المهام المعينة":
                    filtered_planned = filtered_planned[filtered_planned["العضو المسؤول"].notna() & 
                                                     (filtered_planned["العضو المسؤول"].str.strip() != "")]
                elif assignment_tabs == "المهام غير المعينة":
                    filtered_planned = filtered_planned[filtered_planned["العضو المسؤول"].isna() | 
                                                      (filtered_planned["العضو المسؤول"].str.strip() == "")]
                
                # حاول ترتيب المهام حسب تاريخ البدء المخطط له إذا كان متاحًا
                if "تاريخ البدء" in filtered_planned.columns:
                    filtered_planned["تاريخ البدء"] = pd.to_datetime(filtered_planned["تاريخ البدء"], errors='coerce')
                    filtered_planned = filtered_planned.sort_values("تاريخ البدء")
                
                # عنوان وعرض عدد المهام
                st.markdown(f"#### المهام المخطط لها ({len(filtered_planned)})")
                
                # عرض مخطط زمني للمهام المخطط لها
                st.markdown('<div class="achievements-timeline">', unsafe_allow_html=True)
                
                for i, task in filtered_planned.iterrows():
                    task_name = task.get("اسم المهمة", "مهمة غير محددة")
                    member_name = task.get("العضو المسؤول", "")
                    member_display = member_name if pd.notna(member_name) and member_name.strip() != "" else "غير معين"
                    start_date = task.get("تاريخ البدء", "")
                    due_date = task.get("تاريخ الاستحقاق", "")
                    category = task.get("الفئة", "غير مصنفة")
                    priority = task.get("الأولوية", "متوسطة")
                    
                    formatted_start = format_date(start_date)
                    formatted_due = format_date(due_date)
                    
                    # تحديد لون الأولوية
                    priority_class = "badge-red" if priority == "عالية" else ("badge-orange" if priority == "متوسطة" else "badge-blue")
                    
                    st.markdown(f"""
                    <div class="timeline-item">
                        <div class="timeline-date">{formatted_start}</div>
                        <div class="timeline-content planned">
                            <h4>{task_name}</h4>
                            <p>{member_display} • {category}</p>
                            <div class="timeline-meta">
                                <div class="timeline-meta-item">
                                    <span class="badge {priority_class}">{priority}</span>
                                </div>
                                <div class="timeline-meta-item">
                                    تاريخ الاستحقاق: {formatted_due}
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # إضافة رسم بياني لتوزيع المهام المخطط لها حسب الفئة
                if "الفئة" in filtered_planned.columns:
                    category_counts = filtered_planned["الفئة"].value_counts().reset_index()
                    category_counts.columns = ["الفئة", "عدد المهام"]
                    
                    fig_categories = px.pie(category_counts, values="عدد المهام", names="الفئة", 
                                         title="توزيع المهام المخطط لها حسب الفئة",
                                         color_discrete_sequence=px.colors.qualitative.Set2)
                    fig_categories = prepare_chart_layout(fig_categories, "توزيع المهام المخطط لها", is_mobile=mobile_view, chart_type="pie")
                    st.plotly_chart(fig_categories, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("لا توجد مهام مخطط لها حاليًا.")
        
        # 3. تبويب المهام غير المكتملة (مدمجة)
        with inner_tabs[2]:
            # جمع المهام قيد التنفيذ والمخطط لها معًا
            incomplete_tasks = tasks_data[(tasks_data["الحالة"] == "قيد التنفيذ") | (tasks_data["الحالة"] == "مخطط لها")].copy()
            
            if not incomplete_tasks.empty:
                # جدول تفصيلي للمهام غير المكتملة
                st.markdown(f"#### جميع المهام غير المكتملة ({len(incomplete_tasks)})")
                
                # إضافة فلتر بسيط
                filter_options = ["جميع المهام", "الأولوية العالية", "المهام المتأخرة", "قيد التنفيذ فقط", "مخطط لها فقط", "غير معينة"]
                selected_filter = st.selectbox("تصفية المهام", filter_options, key="incomplete_filter")
                
                # تطبيق الفلتر المختار
                filtered_incomplete = incomplete_tasks.copy()
                if selected_filter == "الأولوية العالية":
                    filtered_incomplete = filtered_incomplete[filtered_incomplete["الأولوية"] == "عالية"]
                elif selected_filter == "المهام المتأخرة":
                    if "تاريخ الاستحقاق" in filtered_incomplete.columns:
                        filtered_incomplete["تاريخ الاستحقاق"] = pd.to_datetime(filtered_incomplete["تاريخ الاستحقاق"], errors='coerce')
                        current_date = pd.to_datetime(datetime.now().date())
                        filtered_incomplete = filtered_incomplete[filtered_incomplete["تاريخ الاستحقاق"] < current_date]
                elif selected_filter == "قيد التنفيذ فقط":
                    filtered_incomplete = filtered_incomplete[filtered_incomplete["الحالة"] == "قيد التنفيذ"]
                elif selected_filter == "مخطط لها فقط":
                    filtered_incomplete = filtered_incomplete[filtered_incomplete["الحالة"] == "مخطط لها"]
                elif selected_filter == "غير معينة":
                    filtered_incomplete = filtered_incomplete[filtered_incomplete["العضو المسؤول"].isna() | 
                                                           (filtered_incomplete["العضو المسؤول"].str.strip() == "")]
                
                # ترتيب المهام حسب الحالة ثم تاريخ الاستحقاق
                if "تاريخ الاستحقاق" in filtered_incomplete.columns:
                    filtered_incomplete["تاريخ الاستحقاق"] = pd.to_datetime(filtered_incomplete["تاريخ الاستحقاق"], errors='coerce')
                    filtered_incomplete = filtered_incomplete.sort_values(["الحالة", "تاريخ الاستحقاق"])
                
                # عرض الجدول
                if len(filtered_incomplete) > 0:
                    st.markdown("""
                    <table class="achievements-table">
                        <tr>
                            <th>المهمة</th>
                            <th>العضو المسؤول</th>
                            <th>الفئة</th>
                            <th>تاريخ الاستحقاق</th>
                            <th>الحالة</th>
                            <th>الأولوية</th>
                        </tr>
                    """, unsafe_allow_html=True)
                    
                    for _, task in filtered_incomplete.iterrows():
                        task_name = task.get("اسم المهمة", "مهمة غير محددة")
                        member_name = task.get("العضو المسؤول", "")
                        member_display = member_name if pd.notna(member_name) and member_name.strip() != "" else "غير معين"
                        category = task.get("الفئة", "غير مصنفة")
                        due_date = format_date(task.get("تاريخ الاستحقاق", ""))
                        status = task.get("الحالة", "غير محدد")
                        priority = task.get("الأولوية", "متوسطة")
                        
                        # تحديد لون الصف بناءً على الحالة
                        row_style = "background-color: rgba(243, 156, 18, 0.05);" if status == "قيد التنفيذ" else "background-color: rgba(231, 76, 60, 0.05);"
                        
                        # تحديد لون الأولوية
                        priority_class = "badge-red" if priority == "عالية" else ("badge-orange" if priority == "متوسطة" else "badge-blue")
                        
                        # تحديد لون الحالة
                        status_class = get_status_badge(status)
                        
                        st.markdown(f"""
                        <tr style="{row_style}">
                            <td>{task_name}</td>
                            <td>{member_display}</td>
                            <td>{category}</td>
                            <td>{due_date}</td>
                            <td><span class="badge {status_class}">{status}</span></td>
                            <td><span class="badge {priority_class}">{priority}</span></td>
                        </tr>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</table>", unsafe_allow_html=True)
                else:
                    st.info("لا توجد مهام مطابقة للفلتر المحدد.")
            else:
                st.info("جميع المهام منجزة!")
    else:
        st.info("لا توجد بيانات كافية لعرض المهام الحالية والمخطط لها.")
        
# =========================================
# القسم 15: تبويب تحليل الإنجازات
# =========================================
with main_tabs[4]:
    st.markdown("### تحليل الإنجازات")
    
    if not achievements_data.empty:
        # 1. تحليل توزيع الإنجازات والنقاط حسب الفئة
        st.subheader("توزيع الإنجازات حسب الفئة")
        
        if "الفئة" in achievements_data.columns:
            # حساب عدد الإنجازات لكل فئة
            category_counts = achievements_data["الفئة"].value_counts().reset_index()
            category_counts.columns = ["الفئة", "عدد الإنجازات"]
            
            # حساب مجموع النقاط لكل فئة
            category_points = achievements_data.groupby("الفئة")["النقاط"].sum().reset_index()
            category_points.columns = ["الفئة", "مجموع النقاط"]
            
            # دمج البيانات
            category_analysis = pd.merge(category_counts, category_points, on="الفئة", how="left")
            
            if mobile_view:
                # عرض توزيع عدد الإنجازات حسب الفئة
                fig_achievements = px.pie(category_counts, values="عدد الإنجازات", names="الفئة", 
                                       title="توزيع عدد الإنجازات حسب الفئة",
                                       color_discrete_sequence=px.colors.qualitative.Set2)
                fig_achievements = prepare_chart_layout(fig_achievements, "توزيع عدد الإنجازات", is_mobile=mobile_view, chart_type="pie")
                st.plotly_chart(fig_achievements, use_container_width=True, config={"displayModeBar": False})
                
                # عرض توزيع النقاط حسب الفئة
                fig_points = px.pie(category_points, values="مجموع النقاط", names="الفئة", 
                                  title="توزيع النقاط حسب الفئة",
                                  color_discrete_sequence=px.colors.qualitative.Set2)
                fig_points = prepare_chart_layout(fig_points, "توزيع النقاط", is_mobile=mobile_view, chart_type="pie")
                st.plotly_chart(fig_points, use_container_width=True, config={"displayModeBar": False})
            else:
                col1, col2 = st.columns([1, 1])
                with col1:
                    # عرض توزيع عدد الإنجازات حسب الفئة
                    fig_achievements = px.pie(category_counts, values="عدد الإنجازات", names="الفئة", 
                                           title="توزيع عدد الإنجازات حسب الفئة",
                                           color_discrete_sequence=px.colors.qualitative.Set2)
                    fig_achievements = prepare_chart_layout(fig_achievements, "توزيع عدد الإنجازات", is_mobile=mobile_view, chart_type="pie")
                    st.plotly_chart(fig_achievements, use_container_width=True, config={"displayModeBar": False})
                
                with col2:
                    # عرض توزيع النقاط حسب الفئة
                    fig_points = px.pie(category_points, values="مجموع النقاط", names="الفئة", 
                                      title="توزيع النقاط حسب الفئة",
                                      color_discrete_sequence=px.colors.qualitative.Set2)
                    fig_points = prepare_chart_layout(fig_points, "توزيع النقاط", is_mobile=mobile_view, chart_type="pie")
                    st.plotly_chart(fig_points, use_container_width=True, config={"displayModeBar": False})
            
            # جدول تفصيلي للفئات
            st.markdown("""
            <table class="achievements-table">
                <tr>
                    <th>الفئة</th>
                    <th>عدد الإنجازات</th>
                    <th>مجموع النقاط</th>
                    <th>متوسط النقاط للإنجاز</th>
                    <th>النسبة من إجمالي الإنجازات</th>
                    <th>النسبة من إجمالي النقاط</th>
                </tr>
            """, unsafe_allow_html=True)
            
            # حساب الإجماليات
            total_achievements = category_analysis["عدد الإنجازات"].sum()
            total_points = category_analysis["مجموع النقاط"].sum()
            
            for _, row in category_analysis.iterrows():
                category = row["الفئة"]
                achievement_count = row["عدد الإنجازات"]
                points_sum = row["مجموع النقاط"]
                avg_points = points_sum / achievement_count if achievement_count > 0 else 0
                achievement_percent = (achievement_count / total_achievements * 100) if total_achievements > 0 else 0
                points_percent = (points_sum / total_points * 100) if total_points > 0 else 0
                
                st.markdown(f"""
                <tr>
                    <td>{category}</td>
                    <td>{achievement_count}</td>
                    <td>{int(points_sum)}</td>
                    <td>{avg_points:.1f}</td>
                    <td>{achievement_percent:.1f}%</td>
                    <td>{points_percent:.1f}%</td>
                </tr>
                """, unsafe_allow_html=True)
            
            st.markdown("</table>", unsafe_allow_html=True)
        else:
            st.info("لا توجد بيانات للفئات في الإنجازات.")
        
        # 2. تحليل زمني للإنجازات
        st.subheader("التحليل الزمني للإنجازات")
        
        if "التاريخ" in achievements_data.columns:
            # تحويل التاريخ وإضافة عمود الشهر والسنة
            achievements_data["التاريخ"] = pd.to_datetime(achievements_data["التاريخ"], errors='coerce')
            achievements_data["الشهر"] = achievements_data["التاريخ"].dt.to_period("M").astype(str)
            achievements_data["السنة"] = achievements_data["التاريخ"].dt.year
            
            # تحليل الإنجازات حسب السنة - مع تسمية واضحة للأعمدة
            yearly_data = achievements_data.groupby("السنة").agg({
                "النقاط": "sum",
                "الساعات الافتراضية": "sum"
            }).reset_index()
            # إعادة تسمية الأعمدة بشكل واضح
            yearly_data.columns = ["السنة", "مجموع النقاط", "مجموع الساعات"]
            
            yearly_counts = achievements_data.groupby("السنة").size().reset_index()
            yearly_counts.columns = ["السنة", "عدد الإنجازات"]
            
            yearly_analysis = pd.merge(yearly_data, yearly_counts, on="السنة", how="left")
            
            # رسم بياني للإنجازات السنوية مع الأسماء الصحيحة للأعمدة
            fig_yearly = px.bar(yearly_analysis, x="السنة", y=["عدد الإنجازات", "مجموع النقاط", "مجموع الساعات"], 
                              title="تطور الإنجازات السنوية",
                              barmode="group", color_discrete_sequence=["#1e88e5", "#27AE60", "#F39C12"])
            fig_yearly = prepare_chart_layout(fig_yearly, "تطور الإنجازات السنوية", is_mobile=mobile_view, chart_type="bar")
            st.plotly_chart(fig_yearly, use_container_width=True, config={"displayModeBar": False})
            
            # تحليل شهري للسنة المختارة
            st.markdown("#### تحليل شهري للإنجازات")
            
            years_available = sorted(achievements_data["السنة"].unique(), reverse=True)
            selected_analysis_year = st.selectbox("اختر السنة للتحليل الشهري", years_available, key="analysis_year")
            
            # فلترة البيانات للسنة المختارة
            year_data = achievements_data[achievements_data["السنة"] == selected_analysis_year]
            
            if not year_data.empty:
                # تجميع البيانات حسب الشهر - مع تسمية واضحة للأعمدة
                monthly_data = year_data.groupby("الشهر").agg({
                    "النقاط": "sum",
                    "الساعات الافتراضية": "sum"
                }).reset_index()
                
                # إعادة تسمية الأعمدة بشكل واضح
                monthly_data.columns = ["الشهر", "مجموع النقاط", "مجموع الساعات"]
                
                monthly_counts = year_data.groupby("الشهر").size().reset_index()
                monthly_counts.columns = ["الشهر", "عدد الإنجازات"]
                
                monthly_analysis = pd.merge(monthly_data, monthly_counts, on="الشهر", how="left")
                
                # ترتيب حسب التاريخ
                monthly_analysis["sort_date"] = pd.to_datetime(monthly_analysis["الشهر"], format="%Y-%m")
                monthly_analysis = monthly_analysis.sort_values("sort_date").reset_index(drop=True)
                monthly_analysis = monthly_analysis.drop("sort_date", axis=1)
                
                # رسم بياني لعدد الإنجازات حسب الشهر
                fig_monthly = px.bar(monthly_analysis, x="الشهر", y="عدد الإنجازات", 
                                   title=f"عدد الإنجازات الشهرية لعام {selected_analysis_year}",
                                   color="عدد الإنجازات", color_continuous_scale="Blues")
                fig_monthly = prepare_chart_layout(fig_monthly, f"إنجازات {selected_analysis_year}", is_mobile=mobile_view, chart_type="bar")
                st.plotly_chart(fig_monthly, use_container_width=True, config={"displayModeBar": False})
                
                # رسم بياني للنقاط الشهرية
                fig_monthly_points = px.line(monthly_analysis, x="الشهر", y=["مجموع النقاط", "مجموع الساعات"], 
                                          title=f"تطور النقاط والساعات الشهرية لعام {selected_analysis_year}",
                                          markers=True, color_discrete_sequence=["#1e88e5", "#27AE60"])
                fig_monthly_points = prepare_chart_layout(fig_monthly_points, f"نقاط {selected_analysis_year}", is_mobile=mobile_view, chart_type="line")
                st.plotly_chart(fig_monthly_points, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info(f"لا توجد بيانات إنجازات متاحة لعام {selected_analysis_year}.")
        else:
            st.info("لا توجد بيانات تاريخ كافية لإجراء تحليل زمني.")
        
        # 3. تحليل العلاقة بين عدد الساعات والنقاط
        st.subheader("تحليل العلاقة بين الساعات الافتراضية والنقاط")
        
        if "النقاط" in achievements_data.columns and "الساعات الافتراضية" in achievements_data.columns:
            # إنشاء مخطط النقاط بين الساعات الافتراضية والنقاط
            fig_scatter = px.scatter(achievements_data, x="الساعات الافتراضية", y="النقاط", 
                                   color="الفئة" if "الفئة" in achievements_data.columns else None,
                                   size="النقاط", hover_name="الإنجاز" if "الإنجاز" in achievements_data.columns else None,
                                   title="العلاقة بين الساعات الافتراضية والنقاط",
                                   labels={"الساعات الافتراضية": "الساعات الافتراضية", "النقاط": "النقاط"},
                                   color_discrete_sequence=px.colors.qualitative.Set2)
            fig_scatter = prepare_chart_layout(fig_scatter, "العلاقة بين الساعات والنقاط", is_mobile=mobile_view, chart_type="scatter")
            st.plotly_chart(fig_scatter, use_container_width=True, config={"displayModeBar": False})
            
            # حساب معامل الارتباط
            correlation = achievements_data["الساعات الافتراضية"].corr(achievements_data["النقاط"])
            
            # عرض معامل الارتباط
            st.markdown(f"""
            <div style="padding: 15px; background-color: #f8f9fa; border-radius: 8px; margin: 15px 0;">
                <h4 style="margin-top: 0;">معامل الارتباط بين الساعات الافتراضية والنقاط</h4>
                <div style="font-size: 1.5rem; font-weight: bold; color: #1e88e5; text-align: center; margin: 10px 0;">{correlation:.2f}</div>
                <p style="margin-bottom: 0;">
                    {"ارتباط قوي موجب" if correlation > 0.7 else "ارتباط متوسط" if correlation > 0.4 else "ارتباط ضعيف"}
                    بين عدد الساعات الافتراضية والنقاط المكتسبة.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # حساب متوسط النقاط لكل ساعة
            avg_points_per_hour = achievements_data["النقاط"].sum() / achievements_data["الساعات الافتراضية"].sum() if achievements_data["الساعات الافتراضية"].sum() > 0 else 0
            
            st.markdown(f"""
            <div style="padding: 15px; background-color: #f0f2f6; border-radius: 8px; margin: 15px 0;">
                <h4 style="margin-top: 0;">متوسط النقاط لكل ساعة افتراضية</h4>
                <div style="font-size: 1.5rem; font-weight: bold; color: #27AE60; text-align: center; margin: 10px 0;">{avg_points_per_hour:.2f}</div>
                <p style="margin-bottom: 0;">
                    متوسط عدد النقاط المكتسبة لكل ساعة افتراضية من الإنجازات.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("لا توجد بيانات كافية لتحليل العلاقة بين الساعات الافتراضية والنقاط.")
    else:
        st.info("لا توجد بيانات كافية لإجراء تحليل الإنجازات.")
# =========================================
# القسم 16: نصائح الاستخدام وتذييل الصفحة
# =========================================
with st.expander("💡 نصائح للاستخدام", expanded=False):
    st.markdown("""
    - **منتقي السنة:** يمكنك اختيار السنة لعرض بيانات الإنجازات والمهام لتلك السنة.
    - **المؤشرات الرئيسية:** توضح ملخصًا سريعًا لإنجازات القسم من حيث المهام والنقاط والساعات.
    - **لوحة المعلومات:** تعرض نظرة عامة على الإنجازات والمهام مع رسوم بيانية تفاعلية.
    - **قائمة المهام:** تتيح البحث والتصفية في جميع المهام وعرض تفاصيلها.
    - **إنجازات الأعضاء:** تعرض إنجازات كل عضو بشكل تفصيلي مع إمكانية اختيار عضو محدد.
    - **المهام الحالية والمخطط لها:** تعرض المهام قيد التنفيذ والمخطط لها مع تنبيهات للمهام المتأخرة.
    - **تحليل الإنجازات:** يوفر تحليلات متعمقة للإنجازات حسب الفئة والوقت.
    - **الرسوم البيانية تفاعلية:** مرر الفأرة فوقها لرؤية التفاصيل.
    - **التبويبات:** انقر على التبويبات المختلفة للتنقل بين أقسام الصفحة.
    - **للعودة إلى أعلى الصفحة:** انقر على زر السهم ↑ في أسفل يسار الشاشة.
    """, unsafe_allow_html=True)

# --- إضافة نص تذييل الصفحة ---
st.markdown("""
<div style="margin-top: 50px; text-align: center; color: #888; font-size: 0.75em;">
    © قسم القراءات - جامعة الطائف {0}
</div>
""".format(datetime.now().year), unsafe_allow_html=True)
