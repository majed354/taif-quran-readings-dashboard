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
# القسم 6: ثوابت وإعدادات البيانات
# =========================================

# تعريف قائمة الفئات
INITIAL_CATEGORIES = [
    "— بدون فئة —", # Default/Placeholder
    "تطوير البرامج والمناهج", "ضمان الجودة والاعتماد", "الحوكمة والإدارة",
    "الابتكار والتطوير", "المشاركة المهنية والمجتمعية", "الإرشاد والدعم الطلابي",
]

# تعريف خيارات البرامج
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

# تعريف مستويات التعقيد
COMPLEXITY_LEVELS = [
    "منخفض", "متوسط", "عالي", "عالي جداً"
]

# تعريف خيارات التصفية الزمنية
TIME_FILTER_OPTIONS = [
    "جميع المهام",
    "آخر شهر",
    "آخر ستة أشهر",
    "آخر سنة",
    "آخر ثلاث سنوات"
]

# مسار الجدول الفعلي
ACHIEVEMENTS_DATA_PATH = "data/department/achievements.csv"

# تعريف الأعمدة المتوقعة في الجدول
EXPECTED_ACHIEVEMENT_COLS = [
    "عنوان المهمة", 
    "وصف مختصر", 
    "اسم العضو", 
    "تاريخ الإنجاز", 
    "عدد الساعات", 
    "عدد النقاط", 
    "مستوى التعقيد", 
    "الفئة", 
    "المهمة الرئيسية",
    "البرنامج"
]

# =========================================
# القسم 7: دوال تحميل البيانات
# =========================================

@st.cache_data(ttl=3600)
def load_achievements_data(year=None):
    """تحميل بيانات الإنجازات من الجدول الفعلي"""
    try:
        # استخدام الجدول الموحد
        file_path = ACHIEVEMENTS_DATA_PATH
        
        # التحقق من وجود الملف
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            df = pd.read_csv(file_path)
            
            # تحويل التاريخ إلى كائن datetime
            if "تاريخ الإنجاز" in df.columns:
                df["التاريخ"] = pd.to_datetime(df["تاريخ الإنجاز"], errors='coerce')
            
            # إذا كان تم تحديد سنة، قم بتصفية البيانات
            if year is not None and "التاريخ" in df.columns:
                df = df[df["التاريخ"].dt.year == year]
                
            # ضمان وجود جميع الأعمدة المتوقعة
            for col in EXPECTED_ACHIEVEMENT_COLS:
                if col not in df.columns:
                    df[col] = ""
                    
            return df
        else:
            # إذا لم يكن الملف موجودًا، قم بإنشاء بيانات تجريبية
            st.warning(f"ملف بيانات الإنجازات غير موجود أو فارغ. سيتم استخدام بيانات تجريبية.")
            
            # إنشاء بيانات تجريبية
            sample_data = [
                {
                    "عنوان المهمة": "تطوير مقرر القراءات المتواترة",
                    "وصف مختصر": "تحديث محتوى المقرر وإضافة مخرجات تعلم جديدة",
                    "اسم العضو": "عبد الله حماد حميد القرشي",
                    "تاريخ الإنجاز": "2024-03-15",
                    "عدد الساعات": 15,
                    "عدد النقاط": 45,
                    "مستوى التعقيد": "متوسط",
                    "الفئة": "تطوير البرامج والمناهج",
                    "المهمة الرئيسية": "توصيف المقررات",
                    "البرنامج": "بكالوريوس القراءات"
                },
                {
                    "عنوان المهمة": "إعداد مصفوفة المخرجات التعليمية",
                    "وصف مختصر": "إنشاء مصفوفة تربط مخرجات تعلم البرنامج بالمقررات",
                    "اسم العضو": "ناصر سعود حمود القثامي",
                    "تاريخ الإنجاز": "2024-02-20",
                    "عدد الساعات": 18,
                    "عدد النقاط": 55,
                    "مستوى التعقيد": "عالي",
                    "الفئة": "ضمان الجودة والاعتماد",
                    "المهمة الرئيسية": "الاعتماد الأكاديمي",
                    "البرنامج": "بكالوريوس القرآن وعلومه"
                },
                {
                    "عنوان المهمة": "تنظيم ورشة عمل لمهارات القراءة",
                    "وصف مختصر": "تدريب الطلاب على مهارات القراءة الصحيحة",
                    "اسم العضو": "منال منصور محمد القرشي",
                    "تاريخ الإنجاز": "2024-04-05",
                    "عدد الساعات": 8,
                    "عدد النقاط": 25,
                    "مستوى التعقيد": "منخفض",
                    "الفئة": "المشاركة المهنية والمجتمعية",
                    "المهمة الرئيسية": "تطوير مهارات الطلاب",
                    "البرنامج": "جميع البرامج"
                },
                {
                    "عنوان المهمة": "إعداد تقرير الدراسة الذاتية",
                    "وصف مختصر": "تحليل وتوثيق جوانب القوة والضعف في البرنامج",
                    "اسم العضو": "خلود شاكر فهيد العبدلي",
                    "تاريخ الإنجاز": "2024-01-10",
                    "عدد الساعات": 25,
                    "عدد النقاط": 70,
                    "مستوى التعقيد": "عالي جداً",
                    "الفئة": "ضمان الجودة والاعتماد",
                    "المهمة الرئيسية": "الاعتماد الأكاديمي",
                    "البرنامج": "ماجستير القراءات"
                },
                {
                    "عنوان المهمة": "مراجعة توصيفات المقررات",
                    "وصف مختصر": "مراجعة وتحديث 5 توصيفات لمقررات المستوى الثالث",
                    "اسم العضو": "حاتم عابد عبد الله القرشي",
                    "تاريخ الإنجاز": "2023-11-25",
                    "عدد الساعات": 12,
                    "عدد النقاط": 36,
                    "مستوى التعقيد": "متوسط",
                    "الفئة": "تطوير البرامج والمناهج",
                    "المهمة الرئيسية": "توصيف المقررات",
                    "البرنامج": "بكالوريوس القراءات"
                },
                {
                    "عنوان المهمة": "إعداد الجدول الدراسي",
                    "وصف مختصر": "تجهيز وتنسيق الجدول الدراسي للفصل الثاني",
                    "اسم العضو": "ماجد عبد العزيز الحارثي",
                    "تاريخ الإنجاز": "2023-12-15",
                    "عدد الساعات": 10,
                    "عدد النقاط": 30,
                    "مستوى التعقيد": "متوسط",
                    "الفئة": "الحوكمة والإدارة",
                    "المهمة الرئيسية": "إدارة البرنامج",
                    "البرنامج": "دكتوراه علوم القرآن"
                }
            ]
            
            df = pd.DataFrame(sample_data)
            
            # تحويل التاريخ إلى كائن datetime
            df["التاريخ"] = pd.to_datetime(df["تاريخ الإنجاز"], errors='coerce')
            
            # إذا كان تم تحديد سنة، قم بتصفية البيانات
            if year is not None:
                df = df[df["التاريخ"].dt.year == year]
                
            return df
            
    except Exception as e:
        st.error(f"خطأ في تحميل بيانات الإنجازات: {e}")
        return pd.DataFrame(columns=EXPECTED_ACHIEVEMENT_COLS)

@st.cache_data(ttl=3600)
def get_member_list(achievements_df):
    """استخراج قائمة أعضاء هيئة التدريس من بيانات الإنجازات"""
    if not achievements_df.empty and "اسم العضو" in achievements_df.columns:
        members = sorted(achievements_df["اسم العضو"].unique())
        return members
    else:
        # قائمة افتراضية في حالة عدم وجود بيانات
        return [
            "عبد الله حماد حميد القرشي", "ناصر سعود حمود القثامي", "حاتم عابد عبد الله القرشي",
            "ماجد عبد العزيز الحارثي", "رجاء محمد هوساوي", "عبد الله عيدان الزهراني",
            "منال منصور محمد القرشي", "خلود شاكر فهيد العبدلي"
        ]

@st.cache_data(ttl=3600)
def get_available_years(achievements_df):
    """استخراج قائمة السنوات المتاحة من بيانات الإنجازات"""
    if not achievements_df.empty and "التاريخ" in achievements_df.columns:
        years = sorted(achievements_df["التاريخ"].dt.year.unique(), reverse=True)
        return years
    else:
        # قائمة افتراضية في حالة عدم وجود بيانات
        current_year = datetime.now().year
        return list(range(current_year, current_year-3, -1))

@st.cache_data(ttl=3600)
def get_main_tasks_list(achievements_df):
    """استخراج قائمة المهام الرئيسية من بيانات الإنجازات"""
    if not achievements_df.empty and "المهمة الرئيسية" in achievements_df.columns:
        main_tasks = sorted(achievements_df["المهمة الرئيسية"].dropna().unique())
        return ["— بدون مهمة رئيسية —"] + main_tasks
    else:
        # قائمة افتراضية في حالة عدم وجود بيانات
        return [
            "— بدون مهمة رئيسية —",
            "توصيف المقررات",
            "الاعتماد الأكاديمي",
            "تطوير مهارات الطلاب",
            "إدارة البرنامج"
        ]

# =========================================
# القسم 8: تحميل البيانات الأولية
# =========================================
mobile_view = is_mobile()

# تحميل بيانات الإنجازات
achievements_data = load_achievements_data()

# استخراج قوائم الاختيارات
available_years = get_available_years(achievements_data)
members_list = get_member_list(achievements_data)
main_tasks_list = get_main_tasks_list(achievements_data)

# تهيئة متغيرات الجلسة لحالة التصفية
if "time_filter" not in st.session_state:
    st.session_state.time_filter = TIME_FILTER_OPTIONS[0]
if "selected_member" not in st.session_state:
    st.session_state.selected_member = "الكل"
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "الكل"
if "selected_program" not in st.session_state:
    st.session_state.selected_program = "الكل"
if "selected_main_task" not in st.session_state:
    st.session_state.selected_main_task = "الكل"
if "selected_year" not in st.session_state and available_years:
    st.session_state.selected_year = available_years[0] if available_years else datetime.now().year

# =========================================
# القسم 9: حساب المؤشرات الرئيسية
# =========================================
# حساب المؤشرات الرئيسية من البيانات المتاحة
total_tasks = len(achievements_data) if not achievements_data.empty else 0
total_members = len(members_list) if members_list else 0
active_members = 0  # سيتم حسابها لاحقًا

total_points = 0
total_hours = 0

if not achievements_data.empty:
    if "عدد النقاط" in achievements_data.columns:
        total_points = achievements_data["عدد النقاط"].astype(float).sum()
    
    if "عدد الساعات" in achievements_data.columns:
        total_hours = achievements_data["عدد الساعات"].astype(float).sum()

# حساب المؤشرات المتعلقة بالأعضاء
member_achievements = None
if not achievements_data.empty and "اسم العضو" in achievements_data.columns:
    member_achievements = achievements_data.groupby("اسم العضو").size().reset_index()
    member_achievements.columns = ["اسم العضو", "عدد الإنجازات"]
    active_members = len(member_achievements[member_achievements["عدد الإنجازات"] > 0])
    
    # حساب مجموع النقاط لكل عضو
    if "عدد النقاط" in achievements_data.columns:
        member_points = achievements_data.groupby("اسم العضو")["عدد النقاط"].sum().reset_index()
        member_points.columns = ["اسم العضو", "مجموع النقاط"]
        member_achievements = pd.merge(member_achievements, member_points, on="اسم العضو", how="left")
    
    # حساب مجموع الساعات لكل عضو
    if "عدد الساعات" in achievements_data.columns:
        member_hours = achievements_data.groupby("اسم العضو")["عدد الساعات"].sum().reset_index()
        member_hours.columns = ["اسم العضو", "مجموع الساعات"]
        member_achievements = pd.merge(member_achievements, member_hours, on="اسم العضو", how="left")

# حساب الإنجازات في الشهر الحالي
current_month_achievements = 0
if not achievements_data.empty and "التاريخ" in achievements_data.columns:
    current_date = datetime.now()
    first_day_of_month = datetime(current_date.year, current_date.month, 1)
    current_month_mask = (achievements_data["التاريخ"] >= first_day_of_month) & (achievements_data["التاريخ"] <= current_date)
    current_month_achievements = achievements_data[current_month_mask].shape[0]

# =========================================
# القسم 10: عرض المقاييس الإجمالية
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
with metric_cols[1]: st.metric("الأعضاء النشطين", f"{active_members:,} من {total_members:,}")
with metric_cols[2]: st.metric("مجموع النقاط", f"{total_points:,.0f}")
with metric_cols[3]: st.metric("مجموع الساعات", f"{total_hours:,.0f}")
with metric_cols[4]: st.metric("متوسط النقاط", f"{total_points/total_tasks:.1f}" if total_tasks > 0 else "0")
with metric_cols[5]: st.metric("إنجازات الشهر", f"{current_month_achievements:,}")

# =========================================
# القسم 11: إعداد التبويبات الرئيسية
# =========================================
main_tabs = st.tabs(["لوحة المعلومات", "قائمة المهام", "إنجازات الأعضاء", "تحليل الإنجازات"])

# =========================================
# القسم 12: تبويب لوحة المعلومات
# =========================================
with main_tabs[0]:
    st.markdown("### لوحة معلومات الإنجازات")
    
    # 1. توزيع المهام حسب مستوى التعقيد
    if not achievements_data.empty and "مستوى التعقيد" in achievements_data.columns:
        complexity_counts = achievements_data["مستوى التعقيد"].value_counts().reset_index()
        complexity_counts.columns = ["مستوى التعقيد", "العدد"]
        
        # ضمان ترتيب مستويات التعقيد بشكل منطقي
        complexity_order = {level: i for i, level in enumerate(COMPLEXITY_LEVELS)}
        complexity_counts["الترتيب"] = complexity_counts["مستوى التعقيد"].map(complexity_order)
        complexity_counts = complexity_counts.sort_values("الترتيب").drop("الترتيب", axis=1)
        
        # تعيين ألوان حسب مستوى التعقيد
        complexity_colors = {
            "منخفض": "#27AE60",  # أخضر
            "متوسط": "#F39C12",  # برتقالي
            "عالي": "#E74C3C",    # أحمر
            "عالي جداً": "#C0392B"  # أحمر داكن
        }
        
        if mobile_view:
            fig_complexity = px.pie(complexity_counts, values="العدد", names="مستوى التعقيد", title="توزيع المهام حسب مستوى التعقيد",
                              color="مستوى التعقيد", color_discrete_map=complexity_colors)
            fig_complexity = prepare_chart_layout(fig_complexity, "توزيع المهام حسب مستوى التعقيد", is_mobile=mobile_view, chart_type="pie")
            st.plotly_chart(fig_complexity, use_container_width=True, config={"displayModeBar": False})
            
            # توزيع المهام حسب الفئة
            if "الفئة" in achievements_data.columns:
                category_counts = achievements_data["الفئة"].value_counts().reset_index()
                category_counts.columns = ["الفئة", "العدد"]
                fig_category = px.bar(category_counts, x="الفئة", y="العدد", title="توزيع المهام حسب الفئة",
                                   color="العدد", color_continuous_scale="Blues")
                fig_category = prepare_chart_layout(fig_category, "توزيع المهام حسب الفئة", is_mobile=mobile_view, chart_type="bar")
                st.plotly_chart(fig_category, use_container_width=True, config={"displayModeBar": False})
        else:
            col1, col2 = st.columns([1, 1])
            with col1:
                fig_complexity = px.pie(complexity_counts, values="العدد", names="مستوى التعقيد", title="توزيع المهام حسب مستوى التعقيد",
                                  color="مستوى التعقيد", color_discrete_map=complexity_colors)
                fig_complexity = prepare_chart_layout(fig_complexity, "توزيع المهام حسب مستوى التعقيد", is_mobile=mobile_view, chart_type="pie")
                st.plotly_chart(fig_complexity, use_container_width=True, config={"displayModeBar": False})
            
            with col2:
                # توزيع المهام حسب الفئة
                if "الفئة" in achievements_data.columns:
                    category_counts = achievements_data["الفئة"].value_counts().reset_index()
                    category_counts.columns = ["الفئة", "العدد"]
                    fig_category = px.bar(category_counts, x="الفئة", y="العدد", title="توزيع المهام حسب الفئة",
                                       color="العدد", color_continuous_scale="Blues")
                    fig_category = prepare_chart_layout(fig_category, "توزيع المهام حسب الفئة", is_mobile=mobile_view, chart_type="bar")
                    st.plotly_chart(fig_category, use_container_width=True, config={"displayModeBar": False})
                else:
                    st.info("لا توجد بيانات كافية لعرض توزيع المهام حسب الفئة.")
    
    # 2. قسم أفضل المنجزين (Top Achievers)
    st.markdown("### أفضل المنجزين")
    
    if member_achievements is not None and "مجموع النقاط" in member_achievements.columns:
        top_achievers = member_achievements.sort_values("مجموع النقاط", ascending=False).head(5)
        
        if mobile_view:
            fig_top = px.bar(top_achievers, x="اسم العضو", y="مجموع النقاط", title="أفضل 5 أعضاء من حيث النقاط",
                           color="مجموع النقاط", color_continuous_scale="Greens")
            fig_top = prepare_chart_layout(fig_top, "أفضل 5 أعضاء", is_mobile=mobile_view, chart_type="bar")
            st.plotly_chart(fig_top, use_container_width=True, config={"displayModeBar": False})
        else:
            col3, col4 = st.columns([2, 1])
            with col3:
                fig_top = px.bar(top_achievers, y="اسم العضو", x="مجموع النقاط", title="أفضل 5 أعضاء من حيث النقاط",
                               color="مجموع النقاط", color_continuous_scale="Greens", orientation='h')
                fig_top = prepare_chart_layout(fig_top, "أفضل 5 أعضاء", is_mobile=mobile_view, chart_type="bar")
                st.plotly_chart(fig_top, use_container_width=True, config={"displayModeBar": False})
            
            with col4:
                st.markdown("### 🏆 لوحة الصدارة")
                
                # عرض بطاقات للأعضاء المتميزين
                for i, (_, member) in enumerate(top_achievers.iterrows()):
                    member_name = member["اسم العضو"]
                    member_points = member["مجموع النقاط"]
                    
                    # حساب عدد المهام المنجزة للعضو
                    completed_count = member["عدد الإنجازات"]
                    
                    # حساب مجموع الساعات للعضو
                    total_member_hours = member["مجموع الساعات"] if "مجموع الساعات" in member else 0
                    
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
        latest_achievements = achievements_data.sort_values("التاريخ", ascending=False).head(5)
        
        if latest_achievements.empty:
            st.info("لا توجد إنجازات حديثة متاحة.")
        else:
            for _, achievement in latest_achievements.iterrows():
                member_name = achievement.get("اسم العضو", "غير معروف")
                achievement_title = achievement.get("عنوان المهمة", "مهمة غير محددة")
                achievement_desc = achievement.get("وصف مختصر", "")
                achievement_date = achievement.get("التاريخ", None)
                achievement_points = float(achievement.get("عدد النقاط", 0))
                achievement_hours = float(achievement.get("عدد الساعات", 0))
                achievement_category = achievement.get("الفئة", "غير مصنفة")
                achievement_complexity = achievement.get("مستوى التعقيد", "غير محدد")
                
                formatted_date = achievement_date.strftime("%Y/%m/%d") if pd.notna(achievement_date) else ""
                complexity_class = "badge-green" if achievement_complexity == "منخفض" else ("badge-orange" if achievement_complexity == "متوسط" else "badge-red")
                
                st.markdown(f"""
                <div class="task-card completed">
                    <div class="task-header">
                        <div>
                            <div class="task-title">{achievement_title}</div>
                            <div style="font-size: 0.85rem; color: #666;">{member_name}</div>
                        </div>
                        <div>
                            <span class="badge badge-green">منجزة</span>
                            <span class="badge {complexity_class}">{achievement_complexity}</span>
                        </div>
                    </div>
                    <div style="font-size: 0.85rem; margin: 8px 0;">{achievement_desc}</div>
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
        
    # 4. تحليل النقاط والساعات حسب الشهر
    st.markdown("### تحليل زمني للإنجازات")
    
    if not achievements_data.empty and "التاريخ" in achievements_data.columns:
        # تحويل التاريخ وإضافة عمود الشهر
        achievements_data["الشهر"] = achievements_data["التاريخ"].dt.to_period("M").astype(str)
        
        # تجميع البيانات حسب الشهر
        monthly_data = achievements_data.groupby("الشهر").agg({
            "عدد النقاط": "sum",
            "عدد الساعات": "sum"
        }).reset_index()
        
        # ترتيب حسب التاريخ
        monthly_data["sort_date"] = pd.to_datetime(monthly_data["الشهر"], format="%Y-%m")
        monthly_data = monthly_data.sort_values("sort_date").reset_index(drop=True)
        monthly_data = monthly_data.drop("sort_date", axis=1)
        
        # رسم بياني للنقاط والساعات حسب الشهر
        fig_monthly = px.line(monthly_data, x="الشهر", y=["عدد النقاط", "عدد الساعات"], 
                            title="تطور النقاط والساعات حسب الشهر",
                            labels={"value": "العدد", "variable": "النوع", "الشهر": "الشهر"},
                            markers=True, color_discrete_sequence=["#1e88e5", "#27AE60"])
        fig_monthly = prepare_chart_layout(fig_monthly, "تطور النقاط والساعات", is_mobile=mobile_view, chart_type="line")
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
# القسم 13: تبويب قائمة المهام
# =========================================
with main_tabs[1]:
    st.markdown("### قائمة المهام")
    
    # فلاتر البحث والتصفية
    st.markdown("#### بحث وتصفية")
    
    # تصفية زمنية
    st.markdown('<div class="time-filter">', unsafe_allow_html=True)
    st.markdown('<div class="time-filter-title">تصفية المهام حسب الفترة الزمنية:</div>', unsafe_allow_html=True)
    st.session_state.time_filter = st.radio(
        "",
        options=TIME_FILTER_OPTIONS,
        horizontal=True,
        key="time_filter_radio"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # فلاتر إضافية
    if mobile_view:
        filter_container = st.container()
        with filter_container:
            # اختيار العضو
            members_options = ["الكل"] + members_list
            st.session_state.selected_member = st.selectbox(
                "عضو هيئة التدريس", 
                options=members_options, 
                key="member_mobile"
            )
            
            # اختيار الفئة
            category_options = ["الكل"]
            if not achievements_data.empty and "الفئة" in achievements_data.columns:
                categories = achievements_data["الفئة"].dropna().unique()
                category_options += sorted(categories)
            
            st.session_state.selected_category = st.selectbox(
                "الفئة", 
                options=category_options, 
                key="category_mobile"
            )
            
            # اختيار البرنامج
            program_options = ["الكل"]
            if not achievements_data.empty and "البرنامج" in achievements_data.columns:
                programs = achievements_data["البرنامج"].dropna().unique()
                program_options += sorted(programs)
            
            st.session_state.selected_program = st.selectbox(
                "البرنامج", 
                options=program_options, 
                key="program_mobile"
            )
            
            # اختيار المهمة الرئيسية
            st.session_state.selected_main_task = st.selectbox(
                "المهمة الرئيسية", 
                options=["الكل"] + main_tasks_list, 
                key="main_task_mobile"
            )
            
    else:  # عرض سطح المكتب
        filter_cols = st.columns([1, 1, 1, 1])
        with filter_cols[0]:
            # اختيار العضو
            members_options = ["الكل"] + members_list
            st.session_state.selected_member = st.selectbox(
                "عضو هيئة التدريس", 
                options=members_options, 
                key="member_desktop"
            )
        
        with filter_cols[1]:
            # اختيار الفئة
            category_options = ["الكل"]
            if not achievements_data.empty and "الفئة" in achievements_data.columns:
                categories = achievements_data["الفئة"].dropna().unique()
                category_options += sorted(categories)
            
            st.session_state.selected_category = st.selectbox(
                "الفئة", 
                options=category_options, 
                key="category_desktop"
            )
        
        with filter_cols[2]:
            # اختيار البرنامج
            program_options = ["الكل"]
            if not achievements_data.empty and "البرنامج" in achievements_data.columns:
                programs = achievements_data["البرنامج"].dropna().unique()
                program_options += sorted(programs)
            
            st.session_state.selected_program = st.selectbox(
                "البرنامج", 
                options=program_options, 
                key="program_desktop"
            )
        
        with filter_cols[3]:
            # اختيار المهمة الرئيسية
            st.session_state.selected_main_task = st.selectbox(
                "المهمة الرئيسية", 
                options=["الكل"] + main_tasks_list, 
                key="main_task_desktop"
            )

    # فلتر البحث بالنص
    search_query = st.text_input("البحث في المهام", placeholder="ادخل عنوان المهمة أو جزء من الوصف...")

    # تطبيق الفلاتر
    filtered_tasks = achievements_data.copy()
    
    # تطبيق الفلتر الزمني
    current_date = datetime.now()
    if st.session_state.time_filter == "آخر شهر":
        filter_date = current_date - timedelta(days=30)
        filtered_tasks = filtered_tasks[filtered_tasks["التاريخ"] >= filter_date]
    elif st.session_state.time_filter == "آخر ستة أشهر":
        filter_date = current_date - timedelta(days=180)
        filtered_tasks = filtered_tasks[filtered_tasks["التاريخ"] >= filter_date]
    elif st.session_state.time_filter == "آخر سنة":
        filter_date = current_date - timedelta(days=365)
        filtered_tasks = filtered_tasks[filtered_tasks["التاريخ"] >= filter_date]
    elif st.session_state.time_filter == "آخر ثلاث سنوات":
        filter_date = current_date - timedelta(days=365*3)
        filtered_tasks = filtered_tasks[filtered_tasks["التاريخ"] >= filter_date]
    
    # تطبيق فلتر العضو
    if st.session_state.selected_member != "الكل" and "اسم العضو" in filtered_tasks.columns:
        filtered_tasks = filtered_tasks[filtered_tasks["اسم العضو"] == st.session_state.selected_member]
    
    # تطبيق فلتر الفئة
    if st.session_state.selected_category != "الكل" and "الفئة" in filtered_tasks.columns:
        filtered_tasks = filtered_tasks[filtered_tasks["الفئة"] == st.session_state.selected_category]
    
    # تطبيق فلتر البرنامج
    if st.session_state.selected_program != "الكل" and "البرنامج" in filtered_tasks.columns:
        filtered_tasks = filtered_tasks[filtered_tasks["البرنامج"] == st.session_state.selected_program]
    
    # تطبيق فلتر المهمة الرئيسية
    if st.session_state.selected_main_task != "الكل" and "المهمة الرئيسية" in filtered_tasks.columns:
        if st.session_state.selected_main_task == "— بدون مهمة رئيسية —":
            filtered_tasks = filtered_tasks[(filtered_tasks["المهمة الرئيسية"].isna()) | 
                                           (filtered_tasks["المهمة الرئيسية"] == "")]
        else:
            filtered_tasks = filtered_tasks[filtered_tasks["المهمة الرئيسية"] == st.session_state.selected_main_task]
    
    # تطبيق فلتر البحث النصي
    if search_query:
        search_cond = pd.Series(False, index=filtered_tasks.index)
        
        if "عنوان المهمة" in filtered_tasks.columns:
            search_cond = search_cond | filtered_tasks["عنوان المهمة"].astype(str).str.contains(search_query, case=False, na=False)
        
        if "وصف مختصر" in filtered_tasks.columns:
            search_cond = search_cond | filtered_tasks["وصف مختصر"].astype(str).str.contains(search_query, case=False, na=False)
        
        filtered_tasks = filtered_tasks[search_cond]

    # عرض قائمة المهام المصفاة
    if len(filtered_tasks) > 0:
        st.markdown(f"#### المهام المطابقة ({len(filtered_tasks)})")
        filtered_tasks = filtered_tasks.sort_values(by="التاريخ", ascending=False)
        
        for i, task in filtered_tasks.iterrows():
            with st.container():
                st.markdown("<div class='task-card completed'>", unsafe_allow_html=True)
                
                # معلومات المهمة الأساسية
                task_title = task.get("عنوان المهمة", "مهمة غير محددة")
                task_desc = task.get("وصف مختصر", "")
                member_name = task.get("اسم العضو", "غير معين")
                date_display = task.get("التاريخ", None)
                formatted_date = date_display.strftime("%Y/%m/%d") if pd.notna(date_display) else ""
                
                # معلومات المهمة الإضافية
                hours = float(task.get("عدد الساعات", 0))
                points = float(task.get("عدد النقاط", 0))
                complexity = task.get("مستوى التعقيد", "غير محدد")
                category = task.get("الفئة", "غير مصنفة")
                program = task.get("البرنامج", "غير محدد")
                main_task = task.get("المهمة الرئيسية", "")
                
                # تحديد لون مستوى التعقيد
                complexity_class = ""
                if complexity == "منخفض":
                    complexity_class = "badge-green"
                elif complexity == "متوسط":
                    complexity_class = "badge-orange"
                elif complexity in ["عالي", "عالي جداً"]:
                    complexity_class = "badge-red"
                else:
                    complexity_class = "badge-blue"
                
                # عرض معلومات المهمة
                st.markdown(f"""
                <div class="task-header">
                    <div>
                        <div class="task-title">{task_title}</div>
                        <div style="font-size: 0.85rem; color: #666;">{member_name}</div>
                    </div>
                    <div>
                        <span class="badge {complexity_class}">{complexity}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # عرض وصف المهمة إذا كان متوفرًا
                if task_desc:
                    st.markdown(f'<div style="font-size: 0.85rem; margin: 8px 0;">{task_desc}</div>', unsafe_allow_html=True)
                
                # عرض تفاصيل المهمة
                st.markdown(f"""
                <div class="task-details">
                    <span class="task-detail-item">📅 {formatted_date}</span>
                    <span class="task-detail-item">🏷️ {category}</span>
                    <span class="task-detail-item">📚 {program}</span>
                    {f'<span class="task-detail-item">🔗 {main_task}</span>' if main_task else ''}
                </div>
                """, unsafe_allow_html=True)
                
                # عرض المقاييس
                st.markdown(f"""
                <div class="task-metrics">
                    <div class="task-metric">
                        <div class="task-metric-value">{int(points)}</div>
                        <div class="task-metric-label">النقاط</div>
                    </div>
                    <div class="task-metric">
                        <div class="task-metric-value">{int(hours)}</div>
                        <div class="task-metric-label">الساعات</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("لا توجد مهام مطابقة للفلاتر المحددة.")

# =========================================
# القسم 14: تبويب إنجازات الأعضاء
# =========================================
with main_tabs[2]:
    st.markdown("### إنجازات الأعضاء")
    
    if not achievements_data.empty and "اسم العضو" in achievements_data.columns:
        # حساب إجماليات كل عضو
        member_summary = achievements_data.groupby("اسم العضو").agg({
            "عدد النقاط": "sum",
            "عدد الساعات": "sum"
        }).reset_index()
        
        # عدد الإنجازات لكل عضو
        achievement_counts = achievements_data.groupby("اسم العضو").size().reset_index()
        achievement_counts.columns = ["اسم العضو", "عدد الإنجازات"]
        
        # دمج البيانات
        member_summary = pd.merge(member_summary, achievement_counts, on="اسم العضو", how="left")
        
        # ترتيب حسب النقاط تنازليًا
        member_summary = member_summary.sort_values("عدد النقاط", ascending=False)
        
        # عرض مخطط للنقاط حسب الأعضاء
        fig_points = px.bar(member_summary, y="اسم العضو", x="عدد النقاط", title="توزيع النقاط حسب الأعضاء",
                          color="عدد النقاط", orientation='h', color_continuous_scale="Blues")
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
            member_name = row["اسم العضو"]
            total_points = row["عدد النقاط"]
            total_hours = row["عدد الساعات"]
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
                                           ["اختر عضوًا..."] + members_list)
        
        if selected_detail_member != "اختر عضوًا...":
            member_achievements = achievements_data[achievements_data["اسم العضو"] == selected_detail_member].copy()
            
            if not member_achievements.empty:
                member_achievements = member_achievements.sort_values("التاريخ", ascending=False)
                
                # معلومات ملخصة عن العضو
                member_info = member_summary[member_summary["اسم العضو"] == selected_detail_member].iloc[0]
                
                st.markdown(f"""
                <div style="padding: 15px; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 20px;">
                    <h3 style="margin-top: 0;">{selected_detail_member}</h3>
                    <div style="display: flex; flex-wrap: wrap; gap: 20px; margin-top: 10px;">
                        <div style="flex: 1; min-width: 150px;">
                            <div style="font-size: 1.5rem; font-weight: bold; color: #1e88e5;">{int(member_info['عدد النقاط'])}</div>
                            <div style="font-size: 0.9rem; color: #666;">مجموع النقاط</div>
                        </div>
                        <div style="flex: 1; min-width: 150px;">
                            <div style="font-size: 1.5rem; font-weight: bold; color: #27AE60;">{int(member_info['عدد الإنجازات'])}</div>
                            <div style="font-size: 0.9rem; color: #666;">عدد الإنجازات</div>
                        </div>
                        <div style="flex: 1; min-width: 150px;">
                            <div style="font-size: 1.5rem; font-weight: bold; color: #F39C12;">{int(member_info['عدد الساعات'])}</div>
                            <div style="font-size: 0.9rem; color: #666;">مجموع الساعات</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # عرض قائمة الإنجازات
                st.markdown("##### قائمة الإنجازات")
                
                for i, achievement in member_achievements.iterrows():
                    achievement_title = achievement.get("عنوان المهمة", "مهمة غير محددة")
                    achievement_desc = achievement.get("وصف مختصر", "")
                    achievement_date = achievement.get("التاريخ", None)
                    achievement_points = float(achievement.get("عدد النقاط", 0))
                    achievement_hours = float(achievement.get("عدد الساعات", 0))
                    achievement_category = achievement.get("الفئة", "غير مصنفة")
                    achievement_complexity = achievement.get("مستوى التعقيد", "غير محدد")
                    
                    formatted_date = achievement_date.strftime("%Y/%m/%d") if pd.notna(achievement_date) else ""
                    complexity_class = "badge-green" if achievement_complexity == "منخفض" else ("badge-orange" if achievement_complexity == "متوسط" else "badge-red")
                    
                    st.markdown(f"""
                    <div class="task-card completed" style="margin-bottom: 8px;">
                        <div class="task-header">
                            <div>
                                <div class="task-title">{achievement_title}</div>
                            </div>
                            <div>
                                <span class="badge {complexity_class}">{achievement_complexity}</span>
                            </div>
                        </div>
                        {f'<div style="font-size: 0.85rem; margin: 8px 0;">{achievement_desc}</div>' if achievement_desc else ''}
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
                
                # عرض تحليل توزيع إنجازات العضو حسب الفئة
                if "الفئة" in member_achievements.columns:
                    st.markdown("##### تحليل إنجازات العضو")
                    
                    # توزيع حسب الفئة
                    category_analysis = member_achievements.groupby("الفئة").agg({
                        "عدد النقاط": "sum",
                        "عدد الساعات": "sum"
                    }).reset_index()
                    
                    # عرض التوزيع حسب الفئة
                    fig_member_category = px.pie(category_analysis, values="عدد النقاط", names="الفئة", 
                                               title=f"توزيع نقاط {selected_detail_member} حسب الفئة",
                                               color_discrete_sequence=px.colors.qualitative.Set2)
                    fig_member_category = prepare_chart_layout(fig_member_category, f"توزيع نقاط {selected_detail_member}", is_mobile=mobile_view, chart_type="pie")
                    st.plotly_chart(fig_member_category, use_container_width=True, config={"displayModeBar": False})
                    
                    # التحليل الزمني للإنجازات
                    if "التاريخ" in member_achievements.columns:
                        member_achievements["الشهر"] = member_achievements["التاريخ"].dt.to_period("M").astype(str)
                        monthly_analysis = member_achievements.groupby("الشهر").agg({
                            "عدد النقاط": "sum",
                            "عدد الساعات": "sum"
                        }).reset_index()
                        
                        monthly_analysis["sort_date"] = pd.to_datetime(monthly_analysis["الشهر"], format="%Y-%m")
                        monthly_analysis = monthly_analysis.sort_values("sort_date").reset_index(drop=True)
                        monthly_analysis = monthly_analysis.drop("sort_date", axis=1)
                        
                        fig_monthly_member = px.line(monthly_analysis, x="الشهر", y=["عدد النقاط", "عدد الساعات"], 
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
# القسم 15: تبويب تحليل الإنجازات
# =========================================
with main_tabs[3]:
    st.markdown("### تحليل الإنجازات")
    
    if not achievements_data.empty:
        # 1. تحليل توزيع الإنجازات والنقاط حسب الفئة
        st.subheader("توزيع الإنجازات حسب الفئة")
        
        if "الفئة" in achievements_data.columns:
            # حساب عدد الإنجازات لكل فئة
            category_counts = achievements_data["الفئة"].value_counts().reset_index()
            category_counts.columns = ["الفئة", "عدد الإنجازات"]
            
            # حساب مجموع النقاط لكل فئة
            category_points = achievements_data.groupby("الفئة")["عدد النقاط"].sum().reset_index()
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
            
            # جدول تفصيلي للفئات (مع تعديل ترتيب الأعمدة وضمان المساواة)
            st.markdown("""
            <style>
                /* تنسيق خاص للجدول لضمان المحاذاة الصحيحة */
                .aligned-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                    direction: rtl;
                }
                .aligned-table th, .aligned-table td {
                    border: 1px solid #e7e7e7;
                    text-align: center;
                    padding: 8px;
                }
                .aligned-table th {
                    background-color: #f0f2f6;
                    font-weight: 600;
                }
                .aligned-table tr:nth-child(even) {
                    background-color: #f8f9fa;
                }
            </style>
            <table class="aligned-table">
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
            achievements_data["الشهر"] = achievements_data["التاريخ"].dt.to_period("M").astype(str)
            achievements_data["السنة"] = achievements_data["التاريخ"].dt.year
            
            # تحليل الإنجازات حسب السنة - مع تسمية واضحة للأعمدة
            yearly_data = achievements_data.groupby("السنة").agg({
                "عدد النقاط": "sum",
                "عدد الساعات": "sum"
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
                    "عدد النقاط": "sum",
                    "عدد الساعات": "sum"
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
        st.subheader("تحليل العلاقة بين الساعات والنقاط")
        
        if "عدد النقاط" in achievements_data.columns and "عدد الساعات" in achievements_data.columns:
            # إنشاء مخطط النقاط بين الساعات والنقاط
            fig_scatter = px.scatter(achievements_data, x="عدد الساعات", y="عدد النقاط", 
                                   color="الفئة" if "الفئة" in achievements_data.columns else None,
                                   size="عدد النقاط", hover_name="عنوان المهمة" if "عنوان المهمة" in achievements_data.columns else None,
                                   title="العلاقة بين الساعات والنقاط",
                                   labels={"عدد الساعات": "الساعات", "عدد النقاط": "النقاط"},
                                   color_discrete_sequence=px.colors.qualitative.Set2)
            fig_scatter = prepare_chart_layout(fig_scatter, "العلاقة بين الساعات والنقاط", is_mobile=mobile_view, chart_type="scatter")
            st.plotly_chart(fig_scatter, use_container_width=True, config={"displayModeBar": False})
            
            # حساب معامل الارتباط
            correlation = achievements_data["عدد الساعات"].corr(achievements_data["عدد النقاط"])
            
            # عرض معامل الارتباط
            st.markdown(f"""
            <div style="padding: 15px; background-color: #f8f9fa; border-radius: 8px; margin: 15px 0;">
                <h4 style="margin-top: 0;">معامل الارتباط بين الساعات والنقاط</h4>
                <div style="font-size: 1.5rem; font-weight: bold; color: #1e88e5; text-align: center; margin: 10px 0;">{correlation:.2f}</div>
                <p style="margin-bottom: 0;">
                    {"ارتباط قوي موجب" if correlation > 0.7 else "ارتباط متوسط" if correlation > 0.4 else "ارتباط ضعيف"}
                    بين عدد الساعات والنقاط المكتسبة.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # حساب متوسط النقاط لكل ساعة
            avg_points_per_hour = achievements_data["عدد النقاط"].sum() / achievements_data["عدد الساعات"].sum() if achievements_data["عدد الساعات"].sum() > 0 else 0
            
            st.markdown(f"""
            <div style="padding: 15px; background-color: #f0f2f6; border-radius: 8px; margin: 15px 0;">
                <h4 style="margin-top: 0;">متوسط النقاط لكل ساعة</h4>
                <div style="font-size: 1.5rem; font-weight: bold; color: #27AE60; text-align: center; margin: 10px 0;">{avg_points_per_hour:.2f}</div>
                <p style="margin-bottom: 0;">
                    متوسط عدد النقاط المكتسبة لكل ساعة من الإنجازات.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # 4. تحليل حسب مستوى التعقيد
            if "مستوى التعقيد" in achievements_data.columns:
                st.subheader("تحليل حسب مستوى التعقيد")
                
                # تجميع البيانات حسب مستوى التعقيد
                complexity_data = achievements_data.groupby("مستوى التعقيد").agg({
                    "عدد النقاط": ["sum", "mean"],
                    "عدد الساعات": ["sum", "mean"]
                }).reset_index()
                
                # تنظيم الأعمدة
                complexity_data.columns = ["مستوى التعقيد", "مجموع النقاط", "متوسط النقاط", "مجموع الساعات", "متوسط الساعات"]
                
                # ترتيب مستويات التعقيد
                complexity_order = {level: i for i, level in enumerate(COMPLEXITY_LEVELS)}
                complexity_data["الترتيب"] = complexity_data["مستوى التعقيد"].map(complexity_order)
                complexity_data = complexity_data.sort_values("الترتيب").drop("الترتيب", axis=1)
                
                # إنشاء جدول تفصيلي
                st.markdown("""
                <table class="aligned-table">
                    <tr>
                        <th>مستوى التعقيد</th>
                        <th>عدد المهام</th>
                        <th>مجموع النقاط</th>
                        <th>متوسط النقاط</th>
                        <th>مجموع الساعات</th>
                        <th>متوسط الساعات</th>
                        <th>متوسط النقاط/ساعة</th>
                    </tr>
                """, unsafe_allow_html=True)
                
                complexity_counts = achievements_data["مستوى التعقيد"].value_counts().to_dict()
                
                for _, row in complexity_data.iterrows():
                    complexity = row["مستوى التعقيد"]
                    task_count = complexity_counts.get(complexity, 0)
                    total_points = row["مجموع النقاط"]
                    avg_points = row["متوسط النقاط"]
                    total_hours = row["مجموع الساعات"]
                    avg_hours = row["متوسط الساعات"]
                    points_per_hour = avg_points / avg_hours if avg_hours > 0 else 0
                    
                    st.markdown(f"""
                    <tr>
                        <td>{complexity}</td>
                        <td>{task_count}</td>
                        <td>{int(total_points)}</td>
                        <td>{avg_points:.1f}</td>
                        <td>{int(total_hours)}</td>
                        <td>{avg_hours:.1f}</td>
                        <td>{points_per_hour:.2f}</td>
                    </tr>
                    """, unsafe_allow_html=True)
                
                st.markdown("</table>", unsafe_allow_html=True)
                
                # إنشاء رسم بياني لمتوسط النقاط والساعات حسب مستوى التعقيد
                fig_avg_complexity = px.bar(complexity_data, x="مستوى التعقيد", y=["متوسط النقاط", "متوسط الساعات"], 
                                         barmode="group", title="متوسط النقاط والساعات حسب مستوى التعقيد",
                                         color_discrete_sequence=["#1e88e5", "#27AE60"])
                fig_avg_complexity = prepare_chart_layout(fig_avg_complexity, "متوسط النقاط والساعات", is_mobile=mobile_view, chart_type="bar")
                st.plotly_chart(fig_avg_complexity, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("لا توجد بيانات كافية لتحليل العلاقة بين الساعات والنقاط.")
    else:
        st.info("لا توجد بيانات كافية لإجراء تحليل الإنجازات.")

# نصائح الاستخدام وتذييل الصفحة
# =========================================
with st.expander("💡 نصائح للاستخدام", expanded=False):
    st.markdown("""
    - **منتقي السنة:** يمكنك اختيار السنة لعرض بيانات الإنجازات والمهام لتلك السنة.
    - **المؤشرات الرئيسية:** توضح ملخصًا سريعًا لإنجازات القسم من حيث المهام والنقاط والساعات.
    - **لوحة المعلومات:** تعرض نظرة عامة على الإنجازات والمهام مع رسوم بيانية تفاعلية.
    - **قائمة المهام:** تتيح البحث والتصفية في جميع المهام وعرض تفاصيلها.
    - **إنجازات الأعضاء:** تعرض إنجازات كل عضو بشكل تفصيلي مع إمكانية اختيار عضو محدد.
    - **تحليل الإنجازات:** يوفر تحليلات متعمقة للإنجازات حسب الفئة والوقت ومستوى التعقيد.
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
