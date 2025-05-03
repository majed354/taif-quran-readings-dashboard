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
# ملاحظة: تم إضافة تنسيقات جديدة وتعديل بعض التنسيقات الموجودة
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
    .stSelectbox label, .stMultiselect label, .stRadio label { font-weight: 500; font-size: 0.95rem; }
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

    /* تنسيق قائمة المهام وجداول الأعضاء */
    .achievements-table {
        width: 100%;
        table-layout: fixed; /* ضمان اتساق عرض الأعمدة */
        border-collapse: collapse;
        direction: rtl;
        margin-top: 15px;
        overflow-x: auto; /* Add horizontal scroll for very small screens if needed */
    }
    .achievements-table th, .achievements-table td {
        text-align: center; /* Center align most columns */
        padding: 8px 10px; /* Adjust padding */
        border-bottom: 1px solid #eee;
        border-left: 1px solid #eee; /* Add vertical lines */
        font-size: 0.85rem;
        vertical-align: middle; /* Ensure vertical alignment */
        white-space: nowrap; /* Prevent text wrapping initially */
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .achievements-table th:first-child, .achievements-table td:first-child { border-right: 1px solid #eee; } /* Add right border to first column */
    .achievements-table th {
        background-color: #f0f2f6;
        font-weight: 600;
        font-size: 0.9rem;
        position: sticky; /* Make header sticky */
        top: 0; /* Stick to the top */
        z-index: 1; /* Ensure header is above table content */
    }
     .achievements-table td:nth-child(2) { /* Member name column */
        text-align: right; /* Right align member names */
        white-space: normal; /* Allow member names to wrap if needed */
    }
    .achievements-table tr:hover {
        background-color: rgba(30, 136, 229, 0.05);
    }

    /* تحديد عرض الأعمدة لجدول بيانات الأعضاء التفصيلية */
    .member-details-table th:nth-child(1), .member-details-table td:nth-child(1) { width: 5%; } /* # */
    .member-details-table th:nth-child(2), .member-details-table td:nth-child(2) { width: 30%; text-align: right;} /* العضو */
    .member-details-table th:nth-child(3), .member-details-table td:nth-child(3) { width: 12%; } /* عدد الإنجازات */
    .member-details-table th:nth-child(4), .member-details-table td:nth-child(4) { width: 13%; } /* مجموع النقاط */
    .member-details-table th:nth-child(5), .member-details-table td:nth-child(5) { width: 13%; } /* مجموع الساعات */
    .member-details-table th:nth-child(6), .member-details-table td:nth-child(6) { width: 12%; } /* متوسط النقاط */
    .member-details-table th:nth-child(7), .member-details-table td:nth-child(7) { width: 15%; } /* مستوى الإنجاز */


    /* تنسيق الشارات */
    .badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 10px;
        font-size: 0.75rem;
        font-weight: 500;
        margin-right: 4px;
        white-space: nowrap;
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

    /* تنسيق مستوى الإنجاز المرتبط بالفئة */
    .level-category-display .level-name {
        font-weight: bold;
        font-size: 1.1em; /* أكبر قليلاً */
    }
    .level-category-display .category-name {
        font-size: 0.9em;
        color: #555;
    }
    .badge-details-expander div { /* تحسين التباعد في قائمة الأوسمة */
       margin-bottom: 5px;
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
        .stSelectbox label, .stRadio label { font-size: 0.9rem !important; }
        .stTextInput label { font-size: 0.9rem !important; }

        /* تعديل الجدول للشاشات الصغيرة */
        .achievements-table th { font-size: 0.8rem; padding: 6px 8px; }
        .achievements-table td { font-size: 0.75rem; padding: 6px 8px; white-space: normal; } /* Allow wrapping in mobile */
        .achievements-table td:nth-child(2) { text-align: right; } /* Keep name right-aligned */


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

def prepare_chart_layout(fig, title, is_mobile=False, chart_type="bar", show_legend=True):
    """تطبيق تنسيق موحد على مخططات Plotly مع الاستجابة للجوال"""
    try:
        fig.update_layout(dragmode=False)
        fig.update_xaxes(fixedrange=True)
        fig.update_yaxes(fixedrange=True)

        # إعدادات التخطيط المشتركة
        layout_settings = {
            "title": {"text": title, "x": 0.5, "xanchor": "center"}, # Center title
            "font": {"family": "Tajawal"},
            "plot_bgcolor": "rgba(240, 240, 240, 0.8)",
            "paper_bgcolor": "white",
            "showlegend": show_legend,
            "legend": {
                "orientation": "h",
                "yanchor": "bottom",
                "y": -0.2, # Adjusted legend position
                "xanchor": "center",
                "x": 0.5,
            }
        }

        # تعديلات خاصة بالجوال
        if is_mobile:
            mobile_settings = {
                "height": 300 if chart_type != "heatmap" else 320, # Slightly taller for mobile
                "margin": {"t": 40, "b": 70, "l": 5, "r": 5, "pad": 0}, # Adjusted margins
                "font": {"size": 8},
                "title": {"font": {"size": 11}}, # Slightly larger title
                "legend": {"y": -0.3, "font": {"size": 7}}
            }
            layout_settings.update(mobile_settings)

            # تعديلات خاصة بنوع المخطط للجوال
            if chart_type == "pie":
                layout_settings["legend"] = {"y": -0.15} # Adjust pie legend
                fig.update_traces(textfont_size=8, textinfo='percent+label', insidetextorientation='radial')
            elif chart_type == "line":
                fig.update_traces(marker=dict(size=4)) # Slightly larger markers
            elif chart_type == "bar":
                fig.update_xaxes(tickangle=-45, tickfont={"size": 7}) # Angle ticks for better fit
                fig.update_yaxes(tickfont={"size": 7})
            elif chart_type == "heatmap":
                 fig.update_traces(textfont={"size": 8})
                 fig.update_yaxes(tickfont=dict(size=7))
            elif chart_type == "radar":
                 layout_settings["polar"] = dict(angularaxis=dict(tickfont=dict(size=7)), radialaxis=dict(tickfont=dict(size=7)))
                 layout_settings["legend"] = {"font": {"size": 7}}


        else:
            # إعدادات سطح المكتب
            desktop_settings = {
                "height": 400 if chart_type != "heatmap" else 380,
                "margin": {"t": 50, "b": 80, "l": 40, "r": 40, "pad": 4}, # Adjusted margins
                "legend": {"y": -0.15, "font": {"size": 9}}, # Adjusted legend position
                "title": {"font": {"size": 14}},
                "font": {"size": 10}
            }
            layout_settings.update(desktop_settings)
            if chart_type == "heatmap":
                 fig.update_traces(textfont={"size": 10})
                 fig.update_yaxes(tickfont=dict(size=9))
            elif chart_type == "pie":
                 fig.update_traces(textinfo='percent+label')
            elif chart_type == "radar":
                 layout_settings["polar"] = dict(angularaxis=dict(tickfont=dict(size=9)), radialaxis=dict(tickfont=dict(size=9)))
                 layout_settings["legend"] = {"font": {"size": 9}}


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
# القسم 5.1: دوال مساعدة لتحليل المستويات حسب الفئات
# =========================================

def get_achievement_level(points):
    """تحديد مستوى الإنجاز بناءً على عدد النقاط"""
    # تعريف مستويات الإنجاز حسب النقاط داخل الدالة لتجنب الاعتماد على متغير عام قد لا يكون معرفًا بعد
    ACHIEVEMENT_LEVELS_LOCAL = [
        {"name": "ممارس", "min": 50, "max": 200, "color": "#5DADE2", "icon": "🔹"},  # أزرق فاتح
        {"name": "متمكن", "min": 201, "max": 400, "color": "#3498DB", "icon": "🔷"},  # أزرق
        {"name": "متميز", "min": 401, "max": 600, "color": "#27AE60", "icon": "🌟"},  # أخضر
        {"name": "خبير", "min": 601, "max": 800, "color": "#F39C12", "icon": "✨"},   # برتقالي
        {"name": "رائد", "min": 801, "max": float('inf'), "color": "#E74C3C", "icon": "🏆"}, # أحمر
    ]

    if points < ACHIEVEMENT_LEVELS_LOCAL[0]["min"]: # Check against the first level's minimum
        return {"name": "مبتدئ", "min": 0, "max": ACHIEVEMENT_LEVELS_LOCAL[0]["min"] - 1, "color": "#95A5A6", "icon": "🔘"} # رمادي للمبتدئين

    for level in ACHIEVEMENT_LEVELS_LOCAL:
        if level["min"] <= points <= level["max"]:
            return level

    # Should not happen if points >= 50 due to the last level reaching infinity
    return ACHIEVEMENT_LEVELS_LOCAL[-1] # Return highest level as fallback

def calculate_points_by_category(achievements_df, member_name=None, filter_period=False, start_date=None, end_date=None):
    """
    حساب نقاط العضو (أو جميع الأعضاء) في كل فئة ومستوى الإنجاز لكل فئة.
    يمكن تصفية البيانات لفترة زمنية محددة.
    """
    if achievements_df is None or achievements_df.empty or "الفئة" not in achievements_df.columns or "عدد النقاط" not in achievements_df.columns:
        return pd.DataFrame(columns=["الفئة", "اسم العضو", "عدد النقاط", "مستوى_الإنجاز", "مستوى", "لون_المستوى", "أيقونة_المستوى"])

    df_processed = achievements_df.copy()

    # تصفية حسب العضو إذا تم تحديده
    if member_name:
        if "اسم العضو" not in df_processed.columns:
             return pd.DataFrame(columns=["الفئة", "اسم العضو", "عدد النقاط", "مستوى_الإنجاز", "مستوى", "لون_المستوى", "أيقونة_المستوى"])
        df_processed = df_processed[df_processed["اسم العضو"] == member_name]
        if df_processed.empty:
            return pd.DataFrame(columns=["الفئة", "اسم العضو", "عدد النقاط", "مستوى_الإنجاز", "مستوى", "لون_المستوى", "أيقونة_المستوى"])

    # تصفية حسب الفترة الزمنية إذا طُلب ذلك
    if filter_period and start_date and end_date and "التاريخ" in df_processed.columns:
         # Ensure 'التاريخ' is datetime
        if not pd.api.types.is_datetime64_any_dtype(df_processed['التاريخ']):
             df_processed['التاريخ'] = pd.to_datetime(df_processed['التاريخ'], errors='coerce')
        df_processed = df_processed.dropna(subset=['التاريخ']) # Drop rows where date conversion failed
        df_processed = df_processed[(df_processed["التاريخ"] >= start_date) & (df_processed["التاريخ"] <= end_date)]


    if df_processed.empty:
        return pd.DataFrame(columns=["الفئة", "اسم العضو", "عدد النقاط", "مستوى_الإنجاز", "مستوى", "لون_المستوى", "أيقونة_المستوى"])

    # استبعاد السجلات بدون فئة أو ذات فئة فارغة
    df_processed = df_processed[df_processed["الفئة"].notna() & (df_processed["الفئة"] != "") & (df_processed["الفئة"] != "— بدون فئة —")]

    if df_processed.empty:
        return pd.DataFrame(columns=["الفئة", "اسم العضو", "عدد النقاط", "مستوى_الإنجاز", "مستوى", "لون_المستوى", "أيقونة_المستوى"])

    # تحديد أعمدة التجميع
    grouping_cols = ["الفئة"]
    if "اسم العضو" in df_processed.columns:
         grouping_cols.append("اسم العضو")
    else:
         # If no member column, create a dummy one for aggregation logic consistency
         df_processed["اسم العضو"] = "إجمالي"
         grouping_cols.append("اسم العضو")


    # مجموع النقاط حسب الفئة (والعضو إن وجد)
    category_points = df_processed.groupby(grouping_cols)["عدد النقاط"].sum().reset_index()

    # إضافة مستوى الإنجاز لكل فئة (أو فئة/عضو)
    category_points["مستوى_الإنجاز"] = category_points["عدد النقاط"].apply(get_achievement_level)
    category_points["مستوى"] = category_points["مستوى_الإنجاز"].apply(lambda x: x["name"])
    category_points["لون_المستوى"] = category_points["مستوى_الإنجاز"].apply(lambda x: x["color"])
    category_points["أيقونة_المستوى"] = category_points["مستوى_الإنجاز"].apply(lambda x: x["icon"])

    return category_points


def create_radar_chart(category_points_df, member_name, is_mobile=False):
    """إنشاء مخطط عنكبوتي/رادار لتوزيع نقاط العضو حسب الفئات"""
    if category_points_df is None or category_points_df.empty:
        st.info(f"لا توجد بيانات نقاط كافية حسب الفئة للعضو {member_name} لإنشاء المخطط.")
        return None

    # التأكد من وجود الأعمدة المطلوبة
    required_cols = ["الفئة", "عدد النقاط", "لون_المستوى", "مستوى"]
    if not all(col in category_points_df.columns for col in required_cols):
        st.error("بيانات الفئات للعضو المحدد غير مكتملة لإنشاء المخطط العنكبوتي.")
        return None

    # Ensure numeric points
    category_points_df["عدد النقاط"] = pd.to_numeric(category_points_df["عدد النقاط"], errors='coerce').fillna(0)

    # تحديد الألوان بناءً على مستويات الإنجاز
    colors = category_points_df["لون_المستوى"].tolist()
    max_points = category_points_df["عدد النقاط"].max()
    if max_points == 0: # Avoid division by zero or empty range
        max_points = 10 # Set a default small range if no points

    # إنشاء المخطط العنكبوتي/الرادار
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=category_points_df["عدد النقاط"],
        theta=category_points_df["الفئة"],
        fill='toself',
        name="النقاط",
        line_color="#1e88e5",
        fillcolor="rgba(30, 136, 229, 0.3)",
        hoverinfo="skip" # Skip hover for the main area
    ))

    # إضافة نقاط لكل فئة مع اللون المناسب للمستوى وتلميح مخصص
    for i, row in category_points_df.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=[row["عدد النقاط"]],
            theta=[row["الفئة"]],
            mode="markers+text", # Show markers
            marker=dict(size=10 if not is_mobile else 8, color=row["لون_المستوى"]),
            name=f"{row['الفئة']}", # Legend entry per category
            hoverinfo="text",
            hovertext=f"<b>{row['الفئة']}</b><br>النقاط: {int(row['عدد النقاط'])}<br>المستوى: {row['مستوى']}<extra></extra>", # Use <extra> to remove trace info
            showlegend=False # Hide individual points from legend
        ))

    # تنسيق المخطط
    title_text = f"توزيع نقاط {member_name} حسب الفئات"
    fig = prepare_chart_layout(fig, title_text, is_mobile=is_mobile, chart_type="radar", show_legend=False) # Use helper

    # Specific radar layout adjustments
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                showticklabels=True,
                range=[0, max(10, max_points * 1.1)] # Ensure a minimum range and some padding
            )
        ),
         margin=dict(t=60, b=40, l=60, r=60) # Adjust margins for radar labels
    )


    return fig

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

# تعريف مستويات الإنجاز حسب النقاط (Global definition for reference)
ACHIEVEMENT_LEVELS = [
    {"name": "ممارس", "min": 50, "max": 200, "color": "#5DADE2", "icon": "🔹"},  # أزرق فاتح
    {"name": "متمكن", "min": 201, "max": 400, "color": "#3498DB", "icon": "🔷"},  # أزرق
    {"name": "متميز", "min": 401, "max": 600, "color": "#27AE60", "icon": "🌟"},  # أخضر
    {"name": "خبير", "min": 601, "max": 800, "color": "#F39C12", "icon": "✨"},   # برتقالي
    {"name": "رائد", "min": 801, "max": float('inf'), "color": "#E74C3C", "icon": "🏆"}, # أحمر
]
# Add 'مبتدئ' for consistency
BEGINNER_LEVEL = {"name": "مبتدئ", "min": 0, "max": 49, "color": "#95A5A6", "icon": "🔘"}


# تعريف خيارات التصفية الزمنية للنظرة العامة (جديد)
OVERVIEW_TIME_FILTER_OPTIONS = {
    "آخر شهر": 1,
    "آخر 6 أشهر": 6,
    "آخر سنة": 12,
    "آخر 3 سنوات": 36,
    "آخر 5 سنوات": 60,
    "كل الوقت": None # Use None to represent all time
}
OVERVIEW_TIME_FILTER_LABELS = list(OVERVIEW_TIME_FILTER_OPTIONS.keys())


# تعريف خيارات التصفية الزمنية لقائمة المهام (الأصلي)
TASK_LIST_TIME_FILTER_OPTIONS = [
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
# القسم 7: دوال تحميل ومعالجة البيانات
# =========================================

@st.cache_data(ttl=3600)
def load_achievements_data():
    """تحميل بيانات الإنجازات من الجدول الفعلي ومعالجتها"""
    try:
        file_path = ACHIEVEMENTS_DATA_PATH

        # التحقق من وجود الملف
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            df = pd.read_csv(file_path)

            # ضمان وجود جميع الأعمدة المتوقعة وملء القيم المفقودة المناسبة
            for col in EXPECTED_ACHIEVEMENT_COLS:
                if col not in df.columns:
                    if col in ["عدد الساعات", "عدد النقاط"]:
                        df[col] = 0 # Default numeric to 0
                    else:
                        df[col] = "" # Default others to empty string

            # --- المعالجة الأساسية ---
            # 1. تحويل التاريخ
            if "تاريخ الإنجاز" in df.columns:
                df["التاريخ"] = pd.to_datetime(df["تاريخ الإنجاز"], errors='coerce')
                # Drop rows where date conversion failed as they cannot be filtered
                df.dropna(subset=["التاريخ"], inplace=True)
            else:
                 st.warning("عمود 'تاريخ الإنجاز' غير موجود. لا يمكن تطبيق الفلاتر الزمنية.")
                 # Create a dummy date column if it doesn't exist to avoid errors later?
                 # df['التاريخ'] = pd.NaT # Or handle this case explicitly where filtering is done
                 return pd.DataFrame(columns=EXPECTED_ACHIEVEMENT_COLS + ["التاريخ"]) # Return empty with date column

            # 2. تحويل الأعمدة الرقمية والتأكد من أنها رقمية
            numeric_cols = ["عدد الساعات", "عدد النقاط"]
            for col in numeric_cols:
                 if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0) # Convert and fill NaN with 0
                 else:
                     df[col] = 0 # Ensure column exists and is numeric

            # 3. تنظيف الأعمدة النصية (إزالة الفراغات الزائدة)
            string_cols = ["عنوان المهمة", "وصف مختصر", "اسم العضو", "مستوى التعقيد", "الفئة", "المهمة الرئيسية", "البرنامج"]
            for col in string_cols:
                 if col in df.columns:
                     df[col] = df[col].astype(str).str.strip().fillna("غير محدد") # Convert to string, strip whitespace, fill NaN
                     # Replace empty strings after stripping with 'غير محدد'
                     df[col] = df[col].replace('', 'غير محدد')


            # 4. استبدال القيم الفارغة أو المحددة بـ "— بدون فئة —" في عمود الفئة
            if "الفئة" in df.columns:
                df["الفئة"] = df["الفئة"].replace(["غير محدد", ""], "— بدون فئة —")


            # 5. التأكد من أن عمود اسم العضو ليس فارغًا
            if "اسم العضو" in df.columns:
                 df = df[df["اسم العضو"].notna() & (df["اسم العضو"] != "غير محدد") & (df["اسم العضو"] != "")]


            return df
        else:
            # إذا لم يكن الملف موجودًا، عرض تنبيه وإعادة DataFrame فارغ
            st.warning(f"ملف بيانات الإنجازات غير موجود أو فارغ في المسار: {ACHIEVEMENTS_DATA_PATH}")
            # Return an empty DataFrame with expected columns plus 'التاريخ'
            return pd.DataFrame(columns=EXPECTED_ACHIEVEMENT_COLS + ["التاريخ"])

    except Exception as e:
        st.error(f"خطأ في تحميل أو معالجة بيانات الإنجازات: {e}")
        # Return an empty DataFrame with expected columns plus 'التاريخ'
        return pd.DataFrame(columns=EXPECTED_ACHIEVEMENT_COLS + ["التاريخ"])


def filter_data_by_time(df, time_filter_label):
    """تصفية DataFrame بناءً على فلتر زمني محدد من النظرة العامة"""
    if df is None or df.empty or "التاريخ" not in df.columns:
        return df # Return original df if no date column or df is empty

    # Ensure 'التاريخ' is datetime
    if not pd.api.types.is_datetime64_any_dtype(df['التاريخ']):
        df['التاريخ'] = pd.to_datetime(df['التاريخ'], errors='coerce')
        df = df.dropna(subset=['التاريخ']) # Drop rows where conversion failed

    if df.empty:
        return df

    months_to_subtract = OVERVIEW_TIME_FILTER_OPTIONS.get(time_filter_label)

    if months_to_subtract is None: # "كل الوقت"
        return df
    else:
        current_date = pd.Timestamp.now().normalize() # Use pandas Timestamp
        # Use dateutil.relativedelta for accurate month subtraction
        start_date = current_date - dateutil.relativedelta.relativedelta(months=months_to_subtract)
        # Filter between start_date (inclusive) and current_date (inclusive)
        return df[(df["التاريخ"] >= start_date) & (df["التاريخ"] <= current_date)]


@st.cache_data(ttl=3600)
def get_member_list(achievements_df):
    """استخراج قائمة أعضاء هيئة التدريس من بيانات الإنجازات"""
    # قائمة الأعضاء الافتراضية في حالة عدم وجود بيانات
    DEFAULT_MEMBERS = [
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

    if achievements_df is not None and not achievements_df.empty and "اسم العضو" in achievements_df.columns:
        # Filter out any potential placeholder values if necessary
        members = sorted(achievements_df[achievements_df["اسم العضو"] != "غير محدد"]["اسم العضو"].dropna().unique())
        if members:
            return members

    # إذا لم نجد أعضاء في البيانات، نستخدم القائمة الافتراضية
    st.info("لم يتم العثور على أسماء أعضاء في البيانات، سيتم استخدام القائمة الافتراضية.")
    return sorted(DEFAULT_MEMBERS)


@st.cache_data(ttl=3600)
def get_main_tasks_list(achievements_df):
    """استخراج قائمة المهام الرئيسية من بيانات الإنجازات"""
    DEFAULT_MAIN_TASKS = [
        "توصيف المقررات", "توصيف البرامج", "الاعتماد الأكاديمي",
        "تطوير مهارات الطلاب", "المراجعة الشاملة", "إدارة البرنامج",
        "تقييم مخرجات التعلم", "لجان فحص متقدمي الدراسات العليا",
        "إعداد الاختبارات", "التطوير الذاتي"
    ]

    if achievements_df is not None and not achievements_df.empty and "المهمة الرئيسية" in achievements_df.columns:
         # Filter out placeholder values before getting unique tasks
        main_tasks = sorted(achievements_df[achievements_df["المهمة الرئيسية"] != "غير محدد"]["المهمة الرئيسية"].dropna().unique())
         # إزالة القيم الفارغة
        main_tasks = [task for task in main_tasks if task and task.strip()]
        if main_tasks:
            return ["— بدون مهمة رئيسية —"] + main_tasks

    st.info("لم يتم العثور على مهام رئيسية في البيانات، سيتم استخدام القائمة الافتراضية.")
    return ["— بدون مهمة رئيسية —"] + DEFAULT_MAIN_TASKS

@st.cache_data(ttl=3600)
def get_category_list(achievements_df):
    """استخراج قائمة الفئات المتاحة من بيانات الإنجازات"""
    if achievements_df is not None and not achievements_df.empty and "الفئة" in achievements_df.columns:
        # Exclude the placeholder category from the list of options
        categories = sorted(achievements_df[achievements_df["الفئة"] != "— بدون فئة —"]["الفئة"].dropna().unique())
        if categories:
            return categories
    st.info("لم يتم العثور على فئات في البيانات، سيتم استخدام القائمة الافتراضية.")
    # Return default list excluding the placeholder
    return [cat for cat in INITIAL_CATEGORIES if cat != "— بدون فئة —"]

@st.cache_data(ttl=3600)
def get_program_list(achievements_df):
    """استخراج قائمة البرامج المتاحة من بيانات الإنجازات"""
    if achievements_df is not None and not achievements_df.empty and "البرنامج" in achievements_df.columns:
         # Filter out placeholder values before getting unique programs
        programs = sorted(achievements_df[achievements_df["البرنامج"] != "غير محدد"]["البرنامج"].dropna().unique())
        if programs:
            return programs
    st.info("لم يتم العثور على برامج في البيانات، سيتم استخدام القائمة الافتراضية.")
     # Return default list excluding the placeholder
    return [prog for prog in PROGRAM_OPTIONS if prog != "— اختر البرنامج —"]


# =========================================
# القسم 8: تحميل البيانات الأولية وإعدادات الجلسة
# =========================================
mobile_view = is_mobile()

# تحميل بيانات الإنجازات الأولية (الكاملة)
all_achievements_data = load_achievements_data()

# استخراج قوائم الاختيارات من البيانات الكاملة
members_list = get_member_list(all_achievements_data)
main_tasks_list = get_main_tasks_list(all_achievements_data)
category_list = get_category_list(all_achievements_data)
program_list = get_program_list(all_achievements_data)


# تهيئة متغيرات الجلسة لحالة التصفية
if "overview_time_filter" not in st.session_state:
    st.session_state.overview_time_filter = OVERVIEW_TIME_FILTER_LABELS[-1] # Default to "كل الوقت"
if "task_list_time_filter" not in st.session_state:
    st.session_state.task_list_time_filter = TASK_LIST_TIME_FILTER_OPTIONS[0] # Default to "جميع المهام"
if "selected_member_filter" not in st.session_state: # Renamed for clarity
    st.session_state.selected_member_filter = "الكل"
if "selected_category_filter" not in st.session_state: # Renamed for clarity
    st.session_state.selected_category_filter = "الكل"
if "selected_program_filter" not in st.session_state: # Renamed for clarity
    st.session_state.selected_program_filter = "الكل"
if "selected_main_task_filter" not in st.session_state: # Renamed for clarity
    st.session_state.selected_main_task_filter = "الكل"
if "selected_member_details" not in st.session_state: # For member details view
    st.session_state.selected_member_details = None


# =========================================
# القسم 9: عرض النظرة العامة وفلترها الزمني
# =========================================
st.subheader("نظرة عامة")

# --- فلتر النظرة العامة الزمني ---
st.session_state.overview_time_filter = st.selectbox(
    "تحديد الفترة الزمنية للنظرة العامة:",
    options=OVERVIEW_TIME_FILTER_LABELS,
    index=OVERVIEW_TIME_FILTER_LABELS.index(st.session_state.overview_time_filter), # Maintain selection
    key="overview_time_filter_selector"
)

# --- تصفية البيانات بناءً على فلتر النظرة العامة ---
overview_filtered_data = filter_data_by_time(all_achievements_data, st.session_state.overview_time_filter)

# --- حساب المؤشرات الرئيسية من البيانات المصفاة للنظرة العامة ---
total_tasks_overview = 0
total_points_overview = 0
total_hours_overview = 0
active_members_overview = 0
badges_earned_overview = 0
badge_details_list = [] # قائمة لتفاصيل الأوسمة المكتسبة

if overview_filtered_data is not None and not overview_filtered_data.empty:
    total_tasks_overview = len(overview_filtered_data)
    total_points_overview = overview_filtered_data["عدد النقاط"].sum()
    total_hours_overview = overview_filtered_data["عدد الساعات"].sum()

    # حساب الأعضاء النشطين في الفترة المحددة
    if "اسم العضو" in overview_filtered_data.columns:
        active_members_overview = overview_filtered_data["اسم العضو"].nunique()

    # --- حساب الأوسمة المكتسبة في الفترة المحددة ---
    # حساب النقاط لكل عضو في كل فئة خلال الفترة المحددة
    member_category_points_period = calculate_points_by_category(
        overview_filtered_data,
        member_name=None, # Calculate for all members
        filter_period=False # Data is already filtered for the period
    )


    if not member_category_points_period.empty:
         # تحديد المستوى لكل عضو في كل فئة بناءً على نقاط الفترة
        member_category_points_period["مستوى_الفترة"] = member_category_points_period["عدد النقاط"].apply(get_achievement_level)

        # تصفية المستويات التي تعتبر "أوسمة" (غير مبتدئ)
        earned_badges_df = member_category_points_period[member_category_points_period["مستوى"] != "مبتدئ"]

        badges_earned_overview = len(earned_badges_df)

        # إعداد قائمة تفاصيل الأوسمة للعرض
        badge_details_list = earned_badges_df.apply(
             lambda row: {
                 "member": row["اسم العضو"],
                 "level_name": row["مستوى"],
                 "category": row["الفئة"],
                 "level_icon": row["أيقونة_المستوى"],
                 "level_color": row["لون_المستوى"]
             },
             axis=1
        ).tolist()
         # Sort badge details maybe by member then category
        badge_details_list.sort(key=lambda x: (x["member"], x["category"]))


# حساب إجمالي الأعضاء من القائمة الكاملة
total_members_historical = len(members_list) if members_list else 0


# --- عرض المقاييس في صف ---
if mobile_view:
    row1_cols = st.columns(2)
    row2_cols = st.columns(2)
    row3_cols = st.columns(2)
    metric_cols = [row1_cols[0], row1_cols[1], row2_cols[0], row2_cols[1], row3_cols[0], row3_cols[1]]
else:
    metric_cols = st.columns(6)

# عرض المقاييس (استخدام البيانات المصفاة للفترة)
with metric_cols[0]: st.metric("إجمالي المهام (الفترة)", f"{total_tasks_overview:,}")
with metric_cols[1]: st.metric("الأعضاء النشطين (الفترة)", f"{active_members_overview:,} من {total_members_historical:,}")
with metric_cols[2]: st.metric("مجموع النقاط (الفترة)", f"{total_points_overview:,.0f}")
with metric_cols[3]: st.metric("مجموع الساعات (الفترة)", f"{total_hours_overview:,.0f}")
with metric_cols[4]: st.metric("متوسط النقاط (الفترة)", f"{total_points_overview/total_tasks_overview:.1f}" if total_tasks_overview > 0 else "0")
# مقياس الأوسمة الجديد
with metric_cols[5]: st.metric("الأوسمة المكتسبة (الفترة)", f"{badges_earned_overview:,}")

# --- عرض تفاصيل الأوسمة المكتسبة ---
if badge_details_list:
    with st.expander("🏅 تفاصيل الأوسمة المكتسبة في الفترة المحددة", expanded=False):
        st.markdown('<div class="badge-details-expander">', unsafe_allow_html=True)
        current_member = None
        for badge in badge_details_list:
            if badge["member"] != current_member:
                if current_member is not None: # Add a small separator between members
                     st.markdown("---")
                st.markdown(f"**{badge['member']}**")
                current_member = badge["member"]

            # عرض المستوى والفئة مع التنسيق المطلوب
            st.markdown(f"""
            <div class="level-category-display" style="margin-right: 15px; display: flex; align-items: center; gap: 8px;">
                 <span style="font-size: 1.1rem;">{badge['level_icon']}</span>
                 <div>
                     <span class="level-name" style="color: {badge['level_color']};">{badge['level_name']}</span>
                     <span class="category-name"> في {badge['category']}</span>
                 </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
else:
     st.info("لم يتم اكتساب أوسمة (مستوى ممارس فأعلى) في الفترة الزمنية المحددة.")


# =========================================
# القسم 10: إعداد التبويبات الرئيسية (جديد)
# =========================================
# استخدام البيانات المصفاة للنظرة العامة في التبويب الأول
# استخدام البيانات الكاملة (التاريخية) في التبويب الثاني بشكل أساسي

tab1, tab2 = st.tabs(["📊 عرض موجز", "👥 إنجازات الأعضاء"])

# =========================================
# القسم 11: تبويب عرض موجز (جديد)
# =========================================
with tab1:
    st.markdown(f"### عرض موجز للإنجازات ({st.session_state.overview_time_filter})")

    if overview_filtered_data is None or overview_filtered_data.empty:
        st.warning(f"لا توجد بيانات متاحة للفترة المحددة: {st.session_state.overview_time_filter}")
    else:
        col1, col2 = st.columns(2)

        with col1:
            # 1. توزيع الإنجازات حسب الفئة (النقاط)
            st.markdown("#### توزيع النقاط حسب الفئة")
            if "الفئة" in overview_filtered_data.columns:
                category_points_dist = overview_filtered_data[overview_filtered_data["الفئة"] != "— بدون فئة —"].groupby("الفئة")["عدد النقاط"].sum().reset_index()
                category_points_dist = category_points_dist[category_points_dist["عدد النقاط"] > 0] # Filter out categories with 0 points

                if not category_points_dist.empty:
                    fig_cat_points = px.pie(category_points_dist, values="عدد النقاط", names="الفئة",
                                            title="توزيع النقاط حسب الفئة", hole=0.3,
                                            color_discrete_sequence=px.colors.qualitative.Pastel)
                    fig_cat_points = prepare_chart_layout(fig_cat_points, "", is_mobile=mobile_view, chart_type="pie", show_legend=True)
                    fig_cat_points.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig_cat_points, use_container_width=True, config={"displayModeBar": False})
                else:
                    st.info("لا توجد نقاط مسجلة حسب الفئات في الفترة المحددة.")
            else:
                st.info("عمود 'الفئة' غير موجود لتحليل التوزيع.")

        with col2:
            # 2. توزيع الإنجازات حسب البرنامج (النقاط)
            st.markdown("#### توزيع النقاط حسب البرنامج")
            if "البرنامج" in overview_filtered_data.columns:
                program_points_dist = overview_filtered_data[overview_filtered_data["البرنامج"] != "غير محدد"].groupby("البرنامج")["عدد النقاط"].sum().reset_index()
                program_points_dist = program_points_dist[program_points_dist["عدد النقاط"] > 0] # Filter out programs with 0 points

                if not program_points_dist.empty:
                    fig_prog_points = px.pie(program_points_dist, values="عدد النقاط", names="البرنامج",
                                             title="توزيع النقاط حسب البرنامج", hole=0.3,
                                             color_discrete_sequence=px.colors.qualitative.Set2)
                    fig_prog_points = prepare_chart_layout(fig_prog_points, "", is_mobile=mobile_view, chart_type="pie", show_legend=True)
                    fig_prog_points.update_traces(textposition='inside', textinfo='percent+label')

                    st.plotly_chart(fig_prog_points, use_container_width=True, config={"displayModeBar": False})
                else:
                    st.info("لا توجد نقاط مسجلة حسب البرامج في الفترة المحددة.")
            else:
                st.info("عمود 'البرنامج' غير موجود لتحليل التوزيع.")

        st.markdown("---") # Separator

        col3, col4 = st.columns([3, 2]) # Adjust column ratio

        with col3:
            # 3. لوحة الصدارة (للفترة المحددة)
            st.markdown("#### 🏆 لوحة الصدارة (الفترة المحددة)")
            if "اسم العضو" in overview_filtered_data.columns:
                 member_summary_period = overview_filtered_data.groupby("اسم العضو").agg(
                     عدد_النقاط=("عدد النقاط", "sum"),
                     عدد_المهام=("عنوان المهمة", "count"), # Count tasks
                     عدد_الساعات=("عدد الساعات", "sum")
                 ).reset_index()
                 member_summary_period = member_summary_period.sort_values("عدد_النقاط", ascending=False).head(5) # Top 5 for the period

                 if not member_summary_period.empty:
                     # Add overall level for context (calculated historically)
                     member_summary_period["مستوى_الإنجاز_الإجمالي"] = member_summary_period["اسم العضو"].apply(
                         lambda name: get_achievement_level(
                             all_achievements_data[all_achievements_data["اسم العضو"] == name]["عدد النقاط"].sum()
                         )
                     )
                     member_summary_period["مستوى_إجمالي"] = member_summary_period["مستوى_الإنجاز_الإجمالي"].apply(lambda x: x["name"])
                     member_summary_period["لون_إجمالي"] = member_summary_period["مستوى_الإنجاز_الإجمالي"].apply(lambda x: x["color"])
                     member_summary_period["أيقونة_إجمالي"] = member_summary_period["مستوى_الإنجاز_الإجمالي"].apply(lambda x: x["icon"])


                     # Chart for leaderboard
                     level_colors_map = {level["name"]: level["color"] for level in ACHIEVEMENT_LEVELS}
                     level_colors_map[BEGINNER_LEVEL["name"]] = BEGINNER_LEVEL["color"]

                     fig_leaderboard = px.bar(member_summary_period,
                                              y="اسم العضو", x="عدد_النقاط",
                                              title="أعلى 5 أعضاء نقاطًا (الفترة)",
                                              orientation='h',
                                              color="مستوى_إجمالي", # Color by overall level
                                              color_discrete_map=level_colors_map,
                                              labels={"عدد_النقاط": "النقاط في الفترة", "اسم العضو": "العضو", "مستوى_إجمالي": "المستوى الإجمالي"},
                                              text="عدد_النقاط" # Show points on bars
                                             )
                     fig_leaderboard.update_layout(yaxis={'categoryorder':'total ascending'}) # Sort bars by value
                     fig_leaderboard = prepare_chart_layout(fig_leaderboard, "", is_mobile=mobile_view, chart_type="bar", show_legend=False)
                     st.plotly_chart(fig_leaderboard, use_container_width=True, config={"displayModeBar": False})

                 else:
                     st.info("لا توجد بيانات كافية لعرض لوحة الصدارة للفترة المحددة.")

            else:
                 st.info("عمود 'اسم العضو' غير موجود لعرض لوحة الصدارة.")


        with col4:
            # 4. أحدث الإنجازات (للفترة المحددة)
            st.markdown("#### ✨ أحدث الإنجازات (الفترة المحددة)")
            latest_achievements = overview_filtered_data.sort_values("التاريخ", ascending=False).head(5)
            if not latest_achievements.empty:
                for _, task in latest_achievements.iterrows():
                     task_title = task.get("عنوان المهمة", "مهمة غير محددة")
                     member_name = task.get("اسم العضو", "غير معين")
                     date_display = task.get("التاريخ", None)
                     formatted_date = date_display.strftime("%Y/%m/%d") if pd.notna(date_display) else ""
                     category = task.get("الفئة", "غير مصنفة")
                     points = int(task.get("عدد النقاط", 0))

                     st.markdown(f"""
                     <div style="font-size: 0.85rem; margin-bottom: 8px; padding: 5px; background-color: #f9f9f9; border-radius: 4px;">
                         <span style="font-weight: 500;">{task_title}</span> ({points} نقطة)
                         <br>
                         <span style="color: #555;">{member_name} - {formatted_date} - [{category}]</span>
                     </div>
                     """, unsafe_allow_html=True)
            else:
                st.info("لا توجد إنجازات حديثة في الفترة المحددة.")

        st.markdown("---") # Separator

        # 5. التطور الزمني للإنجازات حسب الشهر (للفترة المحددة)
        st.markdown("#### التطور الزمني للإنجازات حسب الشهر (الفترة المحددة)")
        if "التاريخ" in overview_filtered_data.columns:
            # Ensure 'التاريخ' is datetime before extracting month/year
            if not pd.api.types.is_datetime64_any_dtype(overview_filtered_data['التاريخ']):
                 overview_filtered_data['التاريخ'] = pd.to_datetime(overview_filtered_data['التاريخ'], errors='coerce')

            monthly_summary = overview_filtered_data.copy()
            # Check if 'التاريخ' column exists and is valid datetime after potential conversion
            if 'التاريخ' in monthly_summary.columns and pd.api.types.is_datetime64_any_dtype(monthly_summary['التاريخ']):
                monthly_summary = monthly_summary.dropna(subset=['التاريخ']) # Ensure no NaT dates
                monthly_summary["الشهر_السنة"] = monthly_summary["التاريخ"].dt.to_period("M").astype(str)
                monthly_analysis = monthly_summary.groupby("الشهر_السنة").agg(
                    عدد_النقاط=("عدد النقاط", "sum"),
                    عدد_المهام=("عنوان المهمة", "count") # Count tasks per month
                ).reset_index()

                # Sort by date for the line chart
                monthly_analysis["sort_date"] = pd.to_datetime(monthly_analysis["الشهر_السنة"], format="%Y-%m")
                monthly_analysis = monthly_analysis.sort_values("sort_date").reset_index(drop=True)

                if not monthly_analysis.empty:
                    fig_monthly_trend = go.Figure()
                    # Add Points line
                    fig_monthly_trend.add_trace(go.Scatter(x=monthly_analysis["الشهر_السنة"], y=monthly_analysis["عدد_النقاط"],
                                                           mode='lines+markers', name='مجموع النقاط', yaxis='y1',
                                                           line=dict(color='#1e88e5')))
                    # Add Tasks line/bar on secondary axis
                    fig_monthly_trend.add_trace(go.Bar(x=monthly_analysis["الشهر_السنة"], y=monthly_analysis["عدد_المهام"],
                                                        name='عدد المهام', yaxis='y2',
                                                        marker=dict(color='rgba(39, 174, 96, 0.6)'))) # Semi-transparent green bar


                    # Configure layout with dual axes
                    fig_monthly_trend.update_layout(
                        title="تطور النقاط وعدد المهام حسب الشهر (الفترة)",
                        xaxis_title="الشهر",
                        yaxis=dict(
                            title="مجموع النقاط",
                            titlefont=dict(color="#1e88e5"),
                            tickfont=dict(color="#1e88e5")
                        ),
                        yaxis2=dict(
                            title="عدد المهام",
                            titlefont=dict(color="#27AE60"),
                            tickfont=dict(color="#27AE60"),
                            overlaying="y",
                            side="left", # Place secondary axis on the left
                            showgrid=False # Hide grid for secondary axis
                        ),
                        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                    )

                    fig_monthly_trend = prepare_chart_layout(fig_monthly_trend, "", is_mobile=mobile_view, chart_type="line", show_legend=True)
                    st.plotly_chart(fig_monthly_trend, use_container_width=True, config={"displayModeBar": False})

                else:
                    st.info("لا توجد بيانات شهرية كافية لعرض التطور الزمني في الفترة المحددة.")
            else:
                 st.info("لا يمكن إنشاء التطور الزمني بسبب مشاكل في بيانات التاريخ.")
        else:
            st.info("عمود 'التاريخ' غير موجود لعرض التطور الزمني.")

# =========================================
# القسم 12: تبويب إنجازات الأعضاء (معدل)
# =========================================
with tab2:
    st.markdown("### إنجازات الأعضاء (التاريخية والتفصيلية)")

    if all_achievements_data is None or all_achievements_data.empty:
         st.warning("لا توجد بيانات إنجازات لعرضها.")
    else:
        # --- حساب الإجماليات التاريخية لكل عضو ---
        member_summary_historical = all_achievements_data.groupby("اسم العضو").agg(
            عدد_النقاط_الإجمالي=("عدد النقاط", "sum"),
            عدد_الساعات_الإجمالي=("عدد الساعات", "sum"),
            عدد_الإنجازات_الإجمالي=("عنوان المهمة", "count")
        ).reset_index()

        # إضافة مستوى الإنجاز الإجمالي (التاريخي)
        member_summary_historical["مستوى_الإنجاز_الإجمالي"] = member_summary_historical["عدد_النقاط_الإجمالي"].apply(get_achievement_level)
        member_summary_historical["مستوى_إجمالي"] = member_summary_historical["مستوى_الإنجاز_الإجمالي"].apply(lambda x: x["name"])
        member_summary_historical["لون_إجمالي"] = member_summary_historical["مستوى_الإنجاز_الإجمالي"].apply(lambda x: x["color"])
        member_summary_historical["أيقونة_إجمالي"] = member_summary_historical["مستوى_الإنجاز_الإجمالي"].apply(lambda x: x["icon"])

        # حساب متوسط النقاط التاريخي
        member_summary_historical["متوسط_النقاط_الإجمالي"] = member_summary_historical.apply(
            lambda row: row["عدد_النقاط_الإجمالي"] / row["عدد_الإنجازات_الإجمالي"] if row["عدد_الإنجازات_الإجمالي"] > 0 else 0, axis=1
        )

        # ترتيب حسب النقاط تنازليًا
        member_summary_historical = member_summary_historical.sort_values("عدد_النقاط_الإجمالي", ascending=False).reset_index(drop=True)


        # --- 1. قائمة الصدارة التاريخية (أعلى 10) ---
        st.markdown("#### 🏆 قائمة الصدارة التاريخية (أعلى 10 أعضاء)")
        top_10_historical = member_summary_historical.head(10)

        # إنشاء جدول HTML لقائمة الصدارة
        st.markdown("""
        <table class="achievements-table">
            <thead>
                <tr>
                    <th style="width: 5%;">#</th>
                    <th style="width: 40%; text-align: right;">العضو</th>
                    <th style="width: 20%;">مجموع النقاط (الإجمالي)</th>
                    <th style="width: 20%;">عدد الإنجازات (الإجمالي)</th>
                    <th style="width: 15%;">المستوى الإجمالي</th>
                </tr>
            </thead>
            <tbody>
        """, unsafe_allow_html=True)

        for i, (_, row) in enumerate(top_10_historical.iterrows()):
            st.markdown(f"""
                <tr>
                    <td>{i+1}</td>
                    <td style="text-align: right;">{row['اسم العضو']}</td>
                    <td>{int(row['عدد_النقاط_الإجمالي'])}</td>
                    <td>{row['عدد_الإنجازات_الإجمالي']}</td>
                    <td style="color: {row['لون_إجمالي']}; font-weight: bold;">{row['أيقونة_إجمالي']} {row['مستوى_إجمالي']}</td>
                </tr>
            """, unsafe_allow_html=True)

        st.markdown("</tbody></table>", unsafe_allow_html=True)
        st.markdown("---") # Separator


        # --- 2. بيانات الأعضاء التفصيلية (الجدول التاريخي) ---
        st.markdown("#### بيانات الأعضاء التفصيلية (الإجمالية)")

        # استخدام الفئة CSS المخصصة للتحكم في عرض الأعمدة
        st.markdown('<div style="overflow-x: auto;">', unsafe_allow_html=True) # Add scroll for smaller screens
        st.markdown('<table class="achievements-table member-details-table">', unsafe_allow_html=True) # Apply specific class
        st.markdown("""
            <thead>
                <tr>
                    <th>#</th>
                    <th>العضو</th>
                    <th>عدد الإنجازات</th>
                    <th>مجموع النقاط</th>
                    <th>مجموع الساعات</th>
                    <th>متوسط النقاط</th>
                    <th>مستوى الإنجاز</th>
                </tr>
            </thead>
            <tbody>
        """, unsafe_allow_html=True)

        for i, (_, row) in enumerate(member_summary_historical.iterrows()):
            member_name = row["اسم العضو"]
            total_points = row["عدد_النقاط_الإجمالي"]
            total_hours = row["عدد_الساعات_الإجمالي"]
            achievement_count = row["عدد_الإنجازات_الإجمالي"]
            avg_points = row["متوسط_النقاط_الإجمالي"]
            level_name = row["مستوى_إجمالي"]
            level_color = row["لون_إجمالي"]
            level_icon = row["أيقونة_إجمالي"]

            # جعل اسم العضو قابلاً للنقر لتحديث حالة الجلسة
            # We'll use a selectbox below instead for better Streamlit compatibility
            member_display_name = member_name # Keep the name simple here

            st.markdown(f"""
            <tr>
                <td>{i+1}</td>
                <td style="text-align: right;">{member_display_name}</td>
                <td>{achievement_count}</td>
                <td>{int(total_points)}</td>
                <td>{int(total_hours)}</td>
                <td>{avg_points:.1f}</td>
                <td style="color: {level_color}; font-weight: bold;">{level_icon} {level_name}</td>
            </tr>
            """, unsafe_allow_html=True)

        st.markdown("</tbody></table>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True) # Close scroll div
        st.markdown("---") # Separator


        # --- 3. تفاصيل إنجازات عضو محدد (باستخدام selectbox) ---
        st.markdown("#### تفاصيل إنجازات عضو محدد")

        # استخدام قائمة الأعضاء المرتبة تاريخياً
        member_options = ["اختر عضوًا..."] + member_summary_historical["اسم العضو"].tolist()

        # الحصول على العضو المحدد حاليًا من حالة الجلسة أو تركه None
        current_selection = st.session_state.selected_member_details
        try:
            # Find the index of the currently selected member, default to 0 ("اختر عضوًا...") if not found or None
            default_index = member_options.index(current_selection) if current_selection in member_options else 0
        except ValueError:
            default_index = 0 # Fallback if index not found

        selected_detail_member = st.selectbox(
            "اختر العضو لعرض تفاصيل إنجازاته:",
            options=member_options,
            index=default_index, # Set the initial selection based on session state
            key="member_detail_selector" # Unique key for this selectbox
            )

        # تحديث حالة الجلسة عند تغيير الاختيار
        if selected_detail_member != "اختر عضوًا...":
            st.session_state.selected_member_details = selected_detail_member
        else:
            st.session_state.selected_member_details = None # Reset if "اختر عضوًا..." is selected


        # عرض التفاصيل فقط إذا تم اختيار عضو
        if st.session_state.selected_member_details:
            member_name_to_display = st.session_state.selected_member_details
            member_achievements_details = all_achievements_data[all_achievements_data["اسم العضو"] == member_name_to_display].copy()

            if not member_achievements_details.empty:
                member_achievements_details = member_achievements_details.sort_values("التاريخ", ascending=False)

                # --- معلومات ملخصة عن العضو (تاريخية) ---
                member_info_hist = member_summary_historical[member_summary_historical["اسم العضو"] == member_name_to_display].iloc[0]
                member_points_hist = member_info_hist["عدد_النقاط_الإجمالي"]
                level_info_hist = member_info_hist["مستوى_الإنجاز_الإجمالي"]
                level_name_hist = level_info_hist["name"]
                level_color_hist = level_info_hist["color"]
                level_icon_hist = level_info_hist["icon"]

                # حساب النقاط المتبقية للمستوى التالي (تاريخي)
                next_level_hist = None
                points_to_next_level_hist = 0
                current_level_min_hist = level_info_hist["min"]
                current_level_max_hist = level_info_hist["max"]

                if level_name_hist != "رائد":
                    for i, level in enumerate(ACHIEVEMENT_LEVELS):
                         if level["name"] == level_name_hist and i < len(ACHIEVEMENT_LEVELS) - 1:
                             next_level_hist = ACHIEVEMENT_LEVELS[i + 1]
                             points_to_next_level_hist = next_level_hist["min"] - member_points_hist
                             break
                         elif level["name"] == level_name_hist and level_name_hist == ACHIEVEMENT_LEVELS[-1]["name"]: # Already at max level defined
                              break # No next level
                    # Handle beginner case separately if needed
                    if level_name_hist == BEGINNER_LEVEL["name"]:
                         next_level_hist = ACHIEVEMENT_LEVELS[0] # First real level
                         points_to_next_level_hist = next_level_hist["min"] - member_points_hist


                # حساب نسبة الإكمال للمستوى الحالي (تاريخي)
                level_range_hist = current_level_max_hist - current_level_min_hist if current_level_max_hist != float('inf') else member_points_hist # Avoid infinity issues
                level_progress_hist = 0
                if level_range_hist > 0:
                     level_progress_hist = min(100, ((member_points_hist - current_level_min_hist) / level_range_hist) * 100)
                elif member_points_hist >= current_level_min_hist : # Handle cases like 'Raaed' or single point levels
                     level_progress_hist = 100


                # --- عرض معلومات العضو مع مستوى الإنجاز الإجمالي والتقدم ---
                st.markdown(f"""
                <div style="padding: 15px; background-color: #f0f8ff; border-radius: 8px; margin-bottom: 20px; border: 1px solid #d6eaff;">
                    <h3 style="margin-top: 0; color: #0056b3;">{member_name_to_display}</h3>
                    <div style="margin-top: 10px; margin-bottom: 15px;">
                        <span style="font-size: 1.2rem; color: {level_color_hist}; font-weight: bold;">{level_icon_hist} المستوى الإجمالي: {level_name_hist}</span>
                        <div style="background-color: #e9ecef; height: 10px; border-radius: 5px; margin-top: 8px; overflow: hidden;">
                            <div style="background-color: {level_color_hist}; height: 100%; width: {level_progress_hist}%; border-radius: 5px;"></div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-top: 5px; font-size: 0.8rem;">
                            <span>{current_level_min_hist} نقطة</span>
                            <span>{int(current_level_max_hist) if current_level_max_hist != float('inf') else '∞'} نقطة</span>
                        </div>
                    </div>

                    <div style="display: flex; flex-wrap: wrap; gap: 20px; margin-top: 10px; justify-content: space-around;">
                        <div style="text-align: center;">
                            <div style="font-size: 1.5rem; font-weight: bold; color: #1e88e5;">{int(member_info_hist['عدد_النقاط_الإجمالي'])}</div>
                            <div style="font-size: 0.9rem; color: #666;">مجموع النقاط</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 1.5rem; font-weight: bold; color: #27AE60;">{int(member_info_hist['عدد_الإنجازات_الإجمالي'])}</div>
                            <div style="font-size: 0.9rem; color: #666;">عدد الإنجازات</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 1.5rem; font-weight: bold; color: #F39C12;">{int(member_info_hist['عدد_الساعات_الإجمالي'])}</div>
                            <div style="font-size: 0.9rem; color: #666;">مجموع الساعات</div>
                        </div>
                    </div>

                    {f'''
                    <div style="margin-top: 15px; padding: 10px; background-color: #e8f4fc; border-radius: 5px; text-align: center; font-size: 0.9em;">
                        <span>متبقي {int(points_to_next_level_hist)} نقطة للوصول إلى مستوى {next_level_hist["name"]} {next_level_hist["icon"]}</span>
                    </div>
                    ''' if next_level_hist and points_to_next_level_hist > 0 else ''}
                </div>
                """, unsafe_allow_html=True)


                # --- قسم مستويات الإنجاز حسب الفئة (تاريخي للعضو المحدد) ---
                category_points_hist = calculate_points_by_category(all_achievements_data, member_name_to_display)

                if not category_points_hist.empty:
                    st.markdown("##### مستويات الإنجاز حسب الفئة (الإجمالي)")

                    # إنشاء المخطط العنكبوتي/الرادار لتوزيع النقاط حسب الفئة
                    radar_fig_hist = create_radar_chart(category_points_hist, member_name_to_display, is_mobile=mobile_view)

                    # تقسيم الصفحة إلى عمودين
                    radar_col, table_col = st.columns([3, 2]) # Adjust ratio if needed

                    with radar_col:
                        if radar_fig_hist:
                            st.plotly_chart(radar_fig_hist, use_container_width=True, config={"displayModeBar": False})
                        else:
                            st.info("لا يمكن عرض المخطط العنكبوتي.")

                    with table_col:
                        # عرض جدول الفئات والمستويات
                        st.markdown('<div style="max-height: 400px; overflow-y: auto;">', unsafe_allow_html=True) # Make table scrollable if too long
                        st.markdown("""
                        <table class="achievements-table">
                            <thead>
                                <tr>
                                    <th>الفئة</th>
                                    <th>النقاط</th>
                                    <th>المستوى</th>
                                </tr>
                            </thead>
                            <tbody>
                        """, unsafe_allow_html=True)

                        for _, row in category_points_hist.iterrows():
                            category = row["الفئة"]
                            points = int(row["عدد النقاط"])
                            level = row["مستوى"]
                            level_color = row["لون_المستوى"]
                            level_icon = row["أيقونة_المستوى"]

                            st.markdown(f"""
                                <tr>
                                    <td>{category}</td>
                                    <td>{points}</td>
                                    <td style="color: {level_color}; font-weight: bold;">{level_icon} {level}</td>
                                </tr>
                                """, unsafe_allow_html=True)

                        st.markdown("</tbody></table>", unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True) # Close scroll div
                else:
                    st.info(f"لا توجد بيانات إنجازات موزعة حسب الفئات للعضو {member_name_to_display}.")


                # --- قائمة إنجازات العضو المحدد (تاريخية) ---
                st.markdown("##### قائمة إنجازات العضو (جميع الأوقات)")

                # (اختياري: إضافة فلاتر لهذه القائمة إذا لزم الأمر، مثل الفلترة بالفئة أو الفترة الزمنية)
                # filter_cols_member = st.columns(2)
                # with filter_cols_member[0]:
                #     categories_member = ["الكل"] + category_points_hist["الفئة"].tolist()
                #     selected_category_member = st.selectbox("تصفية حسب الفئة:", categories_member, key="member_cat_filter")
                # with filter_cols_member[1]:
                #     # Add time filter?
                #     pass

                # Apply filters if added
                # member_achievements_display = member_achievements_details.copy()
                # if selected_category_member != "الكل":
                #     member_achievements_display = member_achievements_display[member_achievements_display["الفئة"] == selected_category_member]


                st.markdown(f"<div>إجمالي المهام: <span style='font-weight: bold;'>{len(member_achievements_details)}</span></div>", unsafe_allow_html=True)

                # Display tasks in cards
                for _, achievement in member_achievements_details.iterrows():
                    achievement_title = achievement.get("عنوان المهمة", "مهمة غير محددة")
                    achievement_desc = achievement.get("وصف مختصر", "")
                    achievement_date = achievement.get("التاريخ", None)
                    achievement_points = float(achievement.get("عدد النقاط", 0))
                    achievement_hours = float(achievement.get("عدد الساعات", 0))
                    achievement_category = achievement.get("الفئة", "غير مصنفة")
                    achievement_complexity = achievement.get("مستوى التعقيد", "غير محدد")
                    achievement_program = achievement.get("البرنامج", "غير محدد")
                    achievement_main_task = achievement.get("المهمة الرئيسية", "")


                    formatted_date = achievement_date.strftime("%Y/%m/%d") if pd.notna(achievement_date) else ""

                    # Complexity badge color
                    complexity_class = ""
                    if achievement_complexity == "منخفض": complexity_class = "badge-green"
                    elif achievement_complexity == "متوسط": complexity_class = "badge-orange"
                    elif achievement_complexity in ["عالي", "عالي جداً"]: complexity_class = "badge-red"
                    else: complexity_class = "badge-blue"

                    # Category color (using historical category points for consistency)
                    category_color = "#dddddd" # Default grey
                    category_icon = "📁"
                    if not category_points_hist.empty and achievement_category in category_points_hist["الفئة"].values:
                         category_info = category_points_hist[category_points_hist["الفئة"] == achievement_category].iloc[0]
                         category_color = category_info["لون_المستوى"] # Use level color associated with category for the member
                         # category_icon = category_info["أيقونة_المستوى"] # Or use level icon? Let's stick to a generic icon.


                    st.markdown(f"""
                    <div class="task-card completed" style="margin-bottom: 8px; border-right-color: {category_color};">
                        <div class="task-header">
                            <div>
                                <div class="task-title">{achievement_title}</div>
                                <div style="font-size: 0.8rem; color: #666;">{formatted_date}</div>
                            </div>
                            <div>
                                <span class="badge {complexity_class}">{achievement_complexity}</span>
                            </div>
                        </div>
                        {f'<div style="font-size: 0.85rem; margin: 8px 0; color: #444;">{achievement_desc}</div>' if achievement_desc and achievement_desc != 'غير محدد' else ''}
                        <div class="task-details">
                            <span class="task-detail-item" style="background-color: {category_color}20;">{category_icon} {achievement_category}</span>
                             {f'<span class="task-detail-item">📚 {achievement_program}</span>' if achievement_program != 'غير محدد' else ''}
                             {f'<span class="task-detail-item">🔗 {achievement_main_task}</span>' if achievement_main_task and achievement_main_task != 'غير محدد' else ''}
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
                st.info(f"لا توجد إنجازات مسجلة للعضو المحدد: {member_name_to_display}")
        else:
            st.info("الرجاء اختيار عضو من القائمة أعلاه لعرض تفاصيله.")


# =========================================
# القسم 13: (سابقًا 12) تبويب لوحة المعلومات (أصبح الآن غير مستخدم ومحتوياته وزعت)
# =========================================
# يمكن إزالة هذا القسم أو تركه فارغًا

# =========================================
# القسم 14: (سابقًا 13) تبويب قائمة المهام (أصبح الآن غير مستخدم ومحتوياته وزعت)
# =========================================
# يمكن إزالة هذا القسم أو تركه فارغًا


# =========================================
# القسم 15: (سابقًا 14) تبويب تحليل الإنجازات (أصبح الآن غير مستخدم ومحتوياته وزعت)
# =========================================
# يمكن إزالة هذا القسم أو تركه فارغًا


# =========================================
# القسم 16: نصائح الاستخدام وتذييل الصفحة
# =========================================
with st.expander("💡 نصائح للاستخدام", expanded=False):
    st.markdown("""
    - **فلتر النظرة العامة:** يؤثر على المقاييس والرسوم البيانية في تبويب "عرض موجز".
    - **عرض موجز:** يقدم ملخصًا للإنجازات ولوحة الصدارة وأحدث المهام والتطور الزمني *للفترة المحددة*.
    - **إنجازات الأعضاء:**
        - يعرض **قائمة الصدارة التاريخية** (أعلى 10) بناءً على **كامل** البيانات.
        - يعرض **جدول بيانات تفصيلي تاريخي** لجميع الأعضاء.
        - استخدم **القائمة المنسدلة** لاختيار عضو وعرض **تفاصيله التاريخية الكاملة** (المستوى الإجمالي، المستويات حسب الفئة، قائمة جميع مهامه).
    - **الرسوم البيانية تفاعلية:** مرر الفأرة فوقها لرؤية التفاصيل.
    - **التبويبات:** انقر على التبويبات المختلفة للتنقل بين الأقسام الرئيسية.
    - **للعودة إلى أعلى الصفحة:** انقر على زر السهم ↑ في أسفل يسار الشاشة.
    """, unsafe_allow_html=True)

# --- إضافة نص تذييل الصفحة ---
st.markdown("""
<div style="margin-top: 50px; text-align: center; color: #888; font-size: 0.75em;">
    © قسم القراءات - جامعة الطائف {0}
</div>
""".format(datetime.now().year), unsafe_allow_html=True)
