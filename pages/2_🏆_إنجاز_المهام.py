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
import calendar

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
    
    /* تنسيق بطاقة نجم الشهر */
    .star-of-month {
        background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 3px 8px rgba(0, 0, 0, 0.12);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .star-badge {
        position: absolute;
        top: -15px;
        right: -15px;
        background-color: #f39c12;
        color: white;
        width: 70px;
        height: 70px;
        border-radius: 50%;
        transform: rotate(15deg);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.8rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .star-name {
        font-size: 1.2rem;
        font-weight: 700;
        color: #333;
        margin-top: 5px;
        margin-bottom: 10px;
    }
    .star-stats {
        display: flex;
        justify-content: space-around;
        margin-top: 15px;
    }
    .star-stat {
        text-align: center;
    }
    .star-stat-value {
        font-size: 1.3rem;
        font-weight: bold;
        color: #333;
    }
    .star-stat-label {
        font-size: 0.8rem;
        color: #555;
    }
    
    /* تنسيق لوحة الصدارة */
    .leaderboard {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08);
        margin-bottom: 20px;
    }
    .leaderboard-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e88e5;
        margin-bottom: 15px;
        border-bottom: 1px solid #f0f2f6;
        padding-bottom: 8px;
    }
    .leaderboard-item {
        display: flex;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid #f8f9fa;
    }
    .leaderboard-rank {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: #f0f2f6;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-left: 10px;
    }
    .rank-1 { background-color: #FFD700; color: #333; } /* ذهبي */
    .rank-2 { background-color: #C0C0C0; color: #333; } /* فضي */
    .rank-3 { background-color: #CD7F32; color: white; } /* برونزي */
    .leaderboard-info {
        flex-grow: 1;
    }
    .leaderboard-name {
        font-weight: 600;
        margin-bottom: 3px;
    }
    .leaderboard-details {
        font-size: 0.8rem;
        color: #666;
    }
    .leaderboard-score {
        font-weight: bold;
        color: #1e88e5;
    }
    
    /* تنسيق ترقيات الأعضاء */
    .promotions-list {
        margin-top: 15px;
    }
    .promotion-item {
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 5px;
        background-color: rgba(30, 136, 229, 0.05);
        border-right: 3px solid #1e88e5;
    }
    .promotion-name {
        font-weight: 600;
        margin-bottom: 5px;
    }
    .promotion-details {
        font-size: 0.85rem;
        color: #666;
    }
    .promotion-badge {
        display: inline-block;
        margin-left: 5px;
        font-size: 1rem;
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

        /* تعديل بطاقة نجم الشهر للجوال */
        .star-of-month { padding: 12px 10px; }
        .star-badge { width: 60px; height: 60px; font-size: 1.5rem; }
        .star-name { font-size: 1.1rem; margin-bottom: 8px; }
        .star-stat-value { font-size: 1.1rem; }
        .star-stat-label { font-size: 0.7rem; }

        /* تعديل لوحة الصدارة للجوال */
        .leaderboard { padding: 12px 10px; }
        .leaderboard-title { font-size: 1rem; }
        .leaderboard-rank { width: 35px; height: 35px; font-size: 0.9rem; }
        .leaderboard-name { font-size: 0.9rem; }
        .leaderboard-details { font-size: 0.75rem; }
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
            elif chart_type == "radar":
                layout_settings["height"] = 300
                layout_settings["margin"] = {"t": 30, "b": 30, "l": 30, "r": 30, "pad": 0}
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
            elif chart_type == "radar":
                desktop_settings["height"] = 450
                desktop_settings["margin"] = {"t": 50, "b": 30, "l": 80, "r": 80, "pad": 4}

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

def get_arabic_month_name(month_number):
    """الحصول على اسم الشهر باللغة العربية"""
    arabic_months = {
        1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل", 5: "مايو", 6: "يونيو",
        7: "يوليو", 8: "أغسطس", 9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
    }
    return arabic_months.get(month_number, "")

# =========================================
# القسم 5.1: دوال مساعدة لتحليل المستويات حسب الفئات
# =========================================

def get_achievement_level(points):
    """تحديد مستوى الإنجاز بناءً على عدد النقاط"""
    if points < 50:
        return {"name": "مبتدئ", "color": "#95A5A6", "icon": "🔘"} # رمادي للمبتدئين
    
    for level in ACHIEVEMENT_LEVELS:
        if level["min"] <= points <= level["max"]:
            return level
    
    # في حالة عدم توافق مع أي نطاق (وهذا غير متوقع بسبب المستوى الأخير الذي يصل إلى inf)
    return ACHIEVEMENT_LEVELS[-1]  # إرجاع أعلى مستوى

def calculate_points_by_category(achievements_df, member_name):
    """حساب نقاط العضو في كل فئة ومستوى الإنجاز لكل فئة"""
    if achievements_df.empty or "اسم العضو" not in achievements_df.columns or "الفئة" not in achievements_df.columns or "عدد النقاط" not in achievements_df.columns:
        return pd.DataFrame()
        
    member_achievements = achievements_df[achievements_df["اسم العضو"] == member_name]
    if member_achievements.empty:
        return pd.DataFrame()
    
    # استبعاد السجلات بدون فئة أو ذات فئة فارغة
    member_achievements = member_achievements[member_achievements["الفئة"].notna() & (member_achievements["الفئة"] != "")]
    
    if member_achievements.empty:
        return pd.DataFrame()
        
    # مجموع النقاط حسب الفئة
    category_points = member_achievements.groupby("الفئة")["عدد النقاط"].sum().reset_index()
    
    # إضافة مستوى الإنجاز لكل فئة
    category_points["مستوى_الإنجاز"] = category_points["عدد النقاط"].apply(get_achievement_level)
    category_points["مستوى"] = category_points["مستوى_الإنجاز"].apply(lambda x: x["name"])
    category_points["لون_المستوى"] = category_points["مستوى_الإنجاز"].apply(lambda x: x["color"])
    category_points["أيقونة_المستوى"] = category_points["مستوى_الإنجاز"].apply(lambda x: x["icon"])
    
    return category_points

def create_radar_chart(category_points_df, member_name, is_mobile=False):
    """إنشاء مخطط عنكبوتي/رادار لتوزيع نقاط العضو حسب الفئات"""
    if category_points_df.empty:
        return None
    
    # تحديد الألوان بناءً على مستويات الإنجاز
    colors = category_points_df["لون_المستوى"].tolist()
    
    # إنشاء المخطط العنكبوتي/الرادار
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=category_points_df["عدد النقاط"],
        theta=category_points_df["الفئة"],
        fill='toself',
        name="النقاط",
        line_color="#1e88e5",
        fillcolor="rgba(30, 136, 229, 0.3)"
    ))
    
    # إضافة نقاط لكل فئة مع اللون المناسب للمستوى
    for i, row in category_points_df.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=[row["عدد النقاط"]],
            theta=[row["الفئة"]],
            mode="markers",
            marker=dict(size=10, color=row["لون_المستوى"]),
            name=f"{row['الفئة']}: {row['مستوى']}",
            hoverinfo="text",
            hovertext=f"{row['الفئة']}<br>النقاط: {int(row['عدد النقاط'])}<br>المستوى: {row['مستوى']}"
        ))
    
    # تنسيق المخطط
    title_size = 12 if is_mobile else 16
    font_size = 8 if is_mobile else 10
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                showticklabels=True,
                tickfont=dict(size=font_size),
                range=[0, max(category_points_df["عدد النقاط"]) * 1.2]
            ),
            angularaxis=dict(
                tickfont=dict(size=font_size)
            )
        ),
        title=dict(
            text=f"توزيع نقاط {member_name} حسب الفئات",
            font=dict(size=title_size)
        ),
        font=dict(family="Tajawal"),
        margin=dict(t=50, b=30, l=80, r=80),
        height=350 if is_mobile else 450,
        showlegend=False
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

# تعريف مستويات الإنجاز حسب النقاط
ACHIEVEMENT_LEVELS = [
    {"name": "ممارس", "min": 50, "max": 200, "color": "#5DADE2", "icon": "🔹"},  # أزرق فاتح
    {"name": "متمكن", "min": 201, "max": 400, "color": "#3498DB", "icon": "🔷"},  # أزرق
    {"name": "متميز", "min": 401, "max": 600, "color": "#27AE60", "icon": "🌟"},  # أخضر
    {"name": "خبير", "min": 601, "max": 800, "color": "#F39C12", "icon": "✨"},   # برتقالي
    {"name": "رائد", "min": 801, "max": float('inf'), "color": "#E74C3C", "icon": "🏆"}, # أحمر
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
            # إذا لم يكن الملف موجودًا، عرض تنبيه وإعادة DataFrame فارغ
            st.warning(f"ملف بيانات الإنجازات غير موجود أو فارغ في المسار: {ACHIEVEMENTS_DATA_PATH}")
            return pd.DataFrame(columns=EXPECTED_ACHIEVEMENT_COLS)
            
    except Exception as e:
        st.error(f"خطأ في تحميل بيانات الإنجازات: {e}")
        return pd.DataFrame(columns=EXPECTED_ACHIEVEMENT_COLS)

@st.cache_data(ttl=3600)
def get_member_list(achievements_df):
    """استخراج قائمة أعضاء هيئة التدريس من بيانات الإنجازات"""
    # قائمة الأعضاء الفعلية في القسم
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
    
    if not achievements_df.empty and "اسم العضو" in achievements_df.columns:
        members = sorted(achievements_df["اسم العضو"].dropna().unique())
        if members:
            return members
    
    # إذا لم نجد أعضاء في البيانات، نستخدم القائمة الافتراضية
    return sorted(DEFAULT_MEMBERS)

@st.cache_data(ttl=3600)
def get_available_years(achievements_df):
    """استخراج قائمة السنوات المتاحة من بيانات الإنجازات"""
    # السنوات الافتراضية (من 2022 إلى السنة الحالية)
    current_year = datetime.now().year
    default_years = list(range(2022, current_year + 1))
    
    if not achievements_df.empty and "التاريخ" in achievements_df.columns:
        years = sorted(achievements_df["التاريخ"].dt.year.dropna().unique(), reverse=True)
        if years:
            return years
    
    # إذا لم نجد سنوات في البيانات، نستخدم القائمة الافتراضية
    return sorted(default_years, reverse=True)

@st.cache_data(ttl=3600)
def get_main_tasks_list(achievements_df):
    """استخراج قائمة المهام الرئيسية من بيانات الإنجازات"""
    # قائمة المهام الرئيسية الافتراضية
    DEFAULT_MAIN_TASKS = [
        "توصيف المقررات",
        "توصيف البرامج",
        "الاعتماد الأكاديمي",
        "تطوير مهارات الطلاب",
        "المراجعة الشاملة",
        "إدارة البرنامج",
        "تقييم مخرجات التعلم",
        "لجان فحص متقدمي الدراسات العليا",
        "إعداد الاختبارات",
        "التطوير الذاتي"
    ]
    
    if not achievements_df.empty and "المهمة الرئيسية" in achievements_df.columns:
        main_tasks = sorted(achievements_df["المهمة الرئيسية"].dropna().unique())
        # إزالة القيم الفارغة
        main_tasks = [task for task in main_tasks if task and task.strip()]
        if main_tasks:
            return ["— بدون مهمة رئيسية —"] + main_tasks
    
    # إذا لم نجد مهام رئيسية في البيانات، نستخدم القائمة الافتراضية
    return ["— بدون مهمة رئيسية —"] + DEFAULT_MAIN_TASKS

# =========================================
# القسم 8: دوال تحليل إضافية
# =========================================

def get_member_of_month(achievements_df, year=None, month=None):
    """تحديد نجم الشهر (العضو الأكثر نقاطًا في شهر محدد)"""
    if achievements_df.empty or "اسم العضو" not in achievements_df.columns or "عدد النقاط" not in achievements_df.columns:
        return None
    
    # إذا لم يتم تحديد الشهر أو السنة، نستخدم الشهر والسنة الحاليين
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month
    
    # فلترة البيانات حسب السنة والشهر
    filtered_df = achievements_df.copy()
    if "التاريخ" in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df["التاريخ"].dt.year == year) & 
            (filtered_df["التاريخ"].dt.month == month)
        ]
    
    if filtered_df.empty:
        return None
    
    # حساب مجموع النقاط لكل عضو
    member_points = filtered_df.groupby("اسم العضو")["عدد النقاط"].sum().reset_index()
    
    if member_points.empty:
        return None
    
    # تحديد العضو الأكثر نقاطًا
    top_member = member_points.sort_values("عدد النقاط", ascending=False).iloc[0]
    
    # حساب إجمالي الساعات وعدد المهام للعضو الأكثر نقاطًا
    member_data = filtered_df[filtered_df["اسم العضو"] == top_member["اسم العضو"]]
    total_hours = member_data["عدد الساعات"].sum() if "عدد الساعات" in member_data.columns else 0
    total_tasks = len(member_data)
    
    return {
        "اسم": top_member["اسم العضو"],
        "النقاط": top_member["عدد النقاط"],
        "الساعات": total_hours,
        "المهام": total_tasks,
        "الشهر": month,
        "السنة": year,
        "اسم_الشهر": get_arabic_month_name(month)
    }

def get_category_leaders(achievements_df):
    """تحديد الأعضاء الأكثر نقاطًا في كل فئة"""
    if achievements_df.empty or "اسم العضو" not in achievements_df.columns or "الفئة" not in achievements_df.columns or "عدد النقاط" not in achievements_df.columns:
        return {}
    
    # استبعاد السجلات بدون فئة أو ذات فئة فارغة
    filtered_df = achievements_df[achievements_df["الفئة"].notna() & (achievements_df["الفئة"] != "")]
    
    if filtered_df.empty:
        return {}
    
    # حساب مجموع النقاط لكل عضو في كل فئة
    category_data = filtered_df.groupby(["الفئة", "اسم العضو"])["عدد النقاط"].sum().reset_index()
    
    # تحديد العضو الأكثر نقاطًا في كل فئة
    top_members = {}
    for category in category_data["الفئة"].unique():
        category_members = category_data[category_data["الفئة"] == category]
        if not category_members.empty:
            top_member = category_members.sort_values("عدد النقاط", ascending=False).iloc[0]
            top_members[category] = {
                "اسم": top_member["اسم العضو"],
                "النقاط": top_member["عدد النقاط"]
            }
    
    return top_members

def detect_member_promotions(achievements_df, lookback_days=30):
    """اكتشاف الأعضاء الذين ترقوا إلى مستويات أعلى في الفترة الأخيرة"""
    if achievements_df.empty or "اسم العضو" not in achievements_df.columns or "عدد النقاط" not in achievements_df.columns:
        return []
    
    # تحديد نطاق زمني للبحث عن الترقيات (مثلاً، آخر 30 يومًا)
    current_date = datetime.now()
    lookback_date = current_date - timedelta(days=lookback_days)
    
    # تقسيم البيانات إلى مجموعتين: قبل تاريخ البحث وبعده
    recent_df = achievements_df[achievements_df["التاريخ"] >= lookback_date].copy()
    older_df = achievements_df[achievements_df["التاريخ"] < lookback_date].copy()
    
    if recent_df.empty or older_df.empty:
        return []
    
    # حساب مجموع النقاط لكل عضو قبل وبعد تاريخ البحث
    recent_points = recent_df.groupby("اسم العضو")["عدد النقاط"].sum().to_dict()
    
    # حساب مجموع النقاط الكلي لكل عضو قبل تاريخ البحث
    older_total_points = older_df.groupby("اسم العضو")["عدد النقاط"].sum().to_dict()
    
    # البحث عن الترقيات
    promotions = []
    
    for member, recent_member_points in recent_points.items():
        # إذا كان العضو موجودًا في البيانات القديمة، نحسب إجمالي نقاطه
        old_points = older_total_points.get(member, 0)
        new_total_points = old_points + recent_member_points
        
        # تحديد المستوى القديم والجديد
        old_level = get_achievement_level(old_points)
        new_level = get_achievement_level(new_total_points)
        
        # إذا كان هناك ترقية، نضيفها إلى القائمة
        if old_level["name"] != new_level["name"] and new_level["name"] != "مبتدئ":
            promotions.append({
                "اسم": member,
                "المستوى_السابق": old_level["name"],
                "المستوى_الجديد": new_level["name"],
                "النقاط_السابقة": old_points,
                "النقاط_الجديدة": new_total_points,
                "النقاط_المكتسبة": recent_member_points,
                "لون_المستوى": new_level["color"],
                "أيقونة_المستوى": new_level["icon"]
            })
    
    # ترتيب الترقيات حسب المستوى الجديد (الأعلى أولاً)
    level_rank = {level["name"]: i for i, level in enumerate(reversed(ACHIEVEMENT_LEVELS + [{"name": "مبتدئ"}]))}
    promotions.sort(key=lambda x: level_rank.get(x["المستوى_الجديد"], 0), reverse=True)
    
    return promotions

# =========================================
# القسم 9: تحميل البيانات الأولية
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
if "selected_member_detail" not in st.session_state:
    st.session_state.selected_member_detail = None

# =========================================
# القسم 10: حساب المؤشرات الرئيسية
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
# القسم 11: عرض المقاييس الإجمالية (المحدّثة للنظرة العامة)
# =========================================
st.subheader("نظرة عامة")

# حساب المؤشرات للنظرة العامة
total_tasks = len(achievements_data)
total_hours = achievements_data["عدد الساعات"].astype(float).sum() if "عدد الساعات" in achievements_data.columns else 0
active_members_count = achievements_data["اسم العضو"].nunique() if "اسم العضو" in achievements_data.columns else 0
active_percentage = (active_members_count / total_members) * 100 if total_members > 0 else 0

# تحديد العضو الأكثر نشاطًا (حسب الساعات)
most_active_member = None
if not achievements_data.empty and "اسم العضو" in achievements_data.columns and "عدد الساعات" in achievements_data.columns:
    member_hours = achievements_data.groupby("اسم العضو")["عدد الساعات"].sum()
    if not member_hours.empty:
        most_active_member = member_hours.idxmax()

# تحديد المهمة الأساسية الأكثر ساعات
top_main_task = None
if not achievements_data.empty and "المهمة الرئيسية" in achievements_data.columns and "عدد الساعات" in achievements_data.columns:
    # استبعاد القيم الفارغة
    task_data = achievements_data[achievements_data["المهمة الرئيسية"].notna() & (achievements_data["المهمة الرئيسية"] != "")]
    if not task_data.empty:
        main_task_hours = task_data.groupby("المهمة الرئيسية")["عدد الساعات"].sum()
        if not main_task_hours.empty:
            top_main_task = main_task_hours.idxmax()

# عرض المقاييس في صف (أو 3x2 في الجوال)
if mobile_view:
    row1_cols = st.columns(2)
    row2_cols = st.columns(2)
    row3_cols = st.columns(1)
    metric_cols = [row1_cols[0], row1_cols[1], row2_cols[0], row2_cols[1], row3_cols[0]]
else:
    metric_cols = st.columns(5)

# عرض المؤشرات الرئيسية الخمسة
with metric_cols[0]:
    st.metric("إجمالي المهام", f"{total_tasks:,}")

with metric_cols[1]:
    st.metric("إجمالي الساعات", f"{total_hours:,.0f}")

with metric_cols[2]:
    st.metric(
        "الأعضاء النشطين", 
        f"{active_members_count:,} ({active_percentage:.0f}%)"
    )

with metric_cols[3]:
    if most_active_member:
        st.metric("الأكثر نشاطًا", f"{most_active_member}")
    else:
        st.metric("الأكثر نشاطًا", "لا توجد بيانات")

with metric_cols[4]:
    if top_main_task:
        # اختصار اسم المهمة إذا كان طويلاً
        task_name = top_main_task if len(top_main_task) < 15 else top_main_task[:12] + "..."
        st.metric("المهمة الأكثر ساعات", f"{task_name}")
    else:
        st.metric("المهمة الأكثر ساعات", "لا توجد بيانات")

# =========================================
# القسم 12: إعداد التبويبات الرئيسية (المُعدّلة)
# =========================================
main_tabs = st.tabs(["توزيعات المهام", "إنجازات الأعضاء", "قائمة المهام"])

# =========================================
# القسم 13: تبويب توزيعات المهام
# =========================================
with main_tabs[0]:
    st.markdown("### توزيعات المهام")
    
    # تصفية زمنية
    st.markdown('<div class="time-filter">', unsafe_allow_html=True)
    st.markdown('<div class="time-filter-title">تصفية المهام حسب الفترة الزمنية:</div>', unsafe_allow_html=True)
    selected_time_period = st.radio(
        "",
        options=["الأسبوع الحالي", "الشهر الحالي", "الربع الحالي", "السنة الحالية", "كل الفترات"],
        horizontal=True,
        key="distribution_time_filter"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # تطبيق الفلتر الزمني على البيانات
    filtered_data = achievements_data.copy()
    
    if selected_time_period != "كل الفترات":
        if selected_time_period == "الأسبوع الحالي":
            filter_date = datetime.now() - timedelta(days=7)
        elif selected_time_period == "الشهر الحالي":
            filter_date = datetime.now() - timedelta(days=30)
        elif selected_time_period == "الربع الحالي":
            filter_date = datetime.now() - timedelta(days=90)
        elif selected_time_period == "السنة الحالية":
            filter_date = datetime.now() - timedelta(days=365)
            
        filtered_data = filtered_data[filtered_data["التاريخ"] >= filter_date]
    
    # عرض التوزيعات المختلفة
    if not filtered_data.empty:
        # 1. توزيع المهام حسب الفئة
        st.subheader("توزيع المهام حسب الفئة")
        
        if "الفئة" in filtered_data.columns:
            # تجهيز البيانات
            category_data = filtered_data[filtered_data["الفئة"].notna() & (filtered_data["الفئة"] != "")].copy()
            
            if not category_data.empty:
                # حساب الإحصاءات حسب الفئة
                category_counts = category_data.groupby("الفئة").size().reset_index(name="عدد المهام")
                category_points = category_data.groupby("الفئة")["عدد النقاط"].sum().reset_index()
                category_hours = category_data.groupby("الفئة")["عدد الساعات"].sum().reset_index()
                
                # دمج البيانات
                category_stats = pd.merge(category_counts, category_points, on="الفئة", how="left")
                category_stats = pd.merge(category_stats, category_hours, on="الفئة", how="left")
                
                # ترتيب البيانات حسب عدد المهام تنازليًا
                category_stats = category_stats.sort_values("عدد المهام", ascending=False)
                
                # تحضير مخططات العرض
                if mobile_view:
                    # للجوال: عرض المخططات في أعمدة منفصلة
                    
                    # مخطط 1: توزيع عدد المهام حسب الفئة
                    fig_category_tasks = px.pie(
                        category_stats, 
                        values="عدد المهام", 
                        names="الفئة",
                        title="توزيع عدد المهام حسب الفئة",
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig_category_tasks = prepare_chart_layout(fig_category_tasks, "توزيع المهام حسب الفئة", is_mobile=mobile_view, chart_type="pie")
                    st.plotly_chart(fig_category_tasks, use_container_width=True, config={"displayModeBar": False})
                    
                    # مخطط 2: توزيع النقاط حسب الفئة
                    fig_category_points = px.pie(
                        category_stats, 
                        values="عدد النقاط", 
                        names="الفئة",
                        title="توزيع النقاط حسب الفئة",
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig_category_points = prepare_chart_layout(fig_category_points, "توزيع النقاط حسب الفئة", is_mobile=mobile_view, chart_type="pie")
                    st.plotly_chart(fig_category_points, use_container_width=True, config={"displayModeBar": False})
                    
                    # مخطط 3: توزيع الساعات حسب الفئة
                    fig_category_hours = px.bar(
                        category_stats, 
                        x="الفئة", 
                        y="عدد الساعات",
                        title="توزيع الساعات حسب الفئة",
                        color="عدد الساعات",
                        color_continuous_scale="Blues"
                    )
                    fig_category_hours = prepare_chart_layout(fig_category_hours, "توزيع الساعات حسب الفئة", is_mobile=mobile_view, chart_type="bar")
                    st.plotly_chart(fig_category_hours, use_container_width=True, config={"displayModeBar": False})
                else:
                    # لسطح المكتب: عرض المخططات في صفين
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # مخطط 1: توزيع عدد المهام حسب الفئة
                        fig_category_tasks = px.pie(
                            category_stats, 
                            values="عدد المهام", 
                            names="الفئة",
                            title="توزيع عدد المهام حسب الفئة",
                            color_discrete_sequence=px.colors.qualitative.Pastel
                        )
                        fig_category_tasks = prepare_chart_layout(fig_category_tasks, "توزيع المهام حسب الفئة", is_mobile=mobile_view, chart_type="pie")
                        st.plotly_chart(fig_category_tasks, use_container_width=True, config={"displayModeBar": False})
                    
                    with col2:
                        # مخطط 2: توزيع النقاط حسب الفئة
                        fig_category_points = px.pie(
                            category_stats, 
                            values="عدد النقاط", 
                            names="الفئة",
                            title="توزيع النقاط حسب الفئة",
                            color_discrete_sequence=px.colors.qualitative.Pastel
                        )
                        fig_category_points = prepare_chart_layout(fig_category_points, "توزيع النقاط حسب الفئة", is_mobile=mobile_view, chart_type="pie")
                        st.plotly_chart(fig_category_points, use_container_width=True, config={"displayModeBar": False})
                    
                    # مخطط 3: توزيع الساعات حسب الفئة (في صف كامل)
                    fig_category_hours = px.bar(
                        category_stats, 
                        y="الفئة", 
                        x="عدد الساعات",
                        title="توزيع الساعات حسب الفئة",
                        color="عدد الساعات",
                        orientation='h',
                        color_continuous_scale="Blues"
                    )
                    fig_category_hours = prepare_chart_layout(fig_category_hours, "توزيع الساعات حسب الفئة", is_mobile=mobile_view, chart_type="bar")
                    st.plotly_chart(fig_category_hours, use_container_width=True, config={"displayModeBar": False})
                
                # جدول ملخص الفئات
                with st.expander("عرض إحصاءات تفصيلية للفئات", expanded=False):
                    # حساب معدلات لإثراء البيانات
                    category_stats["متوسط النقاط لكل مهمة"] = category_stats["عدد النقاط"] / category_stats["عدد المهام"]
                    category_stats["متوسط الساعات لكل مهمة"] = category_stats["عدد الساعات"] / category_stats["عدد المهام"]
                    category_stats["النقاط لكل ساعة"] = category_stats["عدد النقاط"] / category_stats["عدد الساعات"]
                    
                    # حساب النسب المئوية
                    total_tasks_count = category_stats["عدد المهام"].sum()
                    total_points_count = category_stats["عدد النقاط"].sum()
                    total_hours_count = category_stats["عدد الساعات"].sum()
                    
                    category_stats["نسبة المهام"] = (category_stats["عدد المهام"] / total_tasks_count) * 100
                    category_stats["نسبة النقاط"] = (category_stats["عدد النقاط"] / total_points_count) * 100
                    category_stats["نسبة الساعات"] = (category_stats["عدد الساعات"] / total_hours_count) * 100
                    
                    # عرض الجدول المحسن
                    st.dataframe(
                        category_stats,
                        column_config={
                            "الفئة": st.column_config.TextColumn("الفئة"),
                            "عدد المهام": st.column_config.NumberColumn("عدد المهام"),
                            "عدد النقاط": st.column_config.NumberColumn("مجموع النقاط", format="%.1f"),
                            "عدد الساعات": st.column_config.NumberColumn("مجموع الساعات", format="%.1f"),
                            "متوسط النقاط لكل مهمة": st.column_config.NumberColumn("متوسط النقاط/مهمة", format="%.1f"),
                            "متوسط الساعات لكل مهمة": st.column_config.NumberColumn("متوسط الساعات/مهمة", format="%.1f"),
                            "النقاط لكل ساعة": st.column_config.NumberColumn("النقاط/ساعة", format="%.1f"),
                            "نسبة المهام": st.column_config.NumberColumn("نسبة المهام", format="%.1f%%"),
                            "نسبة النقاط": st.column_config.NumberColumn("نسبة النقاط", format="%.1f%%"),
                            "نسبة الساعات": st.column_config.NumberColumn("نسبة الساعات", format="%.1f%%"),
                        },
                        hide_index=True,
                        use_container_width=True
                    )
            else:
                st.info("لا توجد بيانات مصنفة بفئات في الفترة المحددة.")
        else:
            st.info("البيانات لا تحتوي على عمود الفئة.")
        
        # 2. توزيع المهام حسب البرنامج
        st.subheader("توزيع المهام حسب البرنامج")
        
        if "البرنامج" in filtered_data.columns:
            # تجهيز البيانات
            program_data = filtered_data[filtered_data["البرنامج"].notna() & (filtered_data["البرنامج"] != "")].copy()
            
            if not program_data.empty:
                # حساب الإحصاءات حسب البرنامج
                program_counts = program_data.groupby("البرنامج").size().reset_index(name="عدد المهام")
                program_points = program_data.groupby("البرنامج")["عدد النقاط"].sum().reset_index()
                program_hours = program_data.groupby("البرنامج")["عدد الساعات"].sum().reset_index()
                
                # دمج البيانات
                program_stats = pd.merge(program_counts, program_points, on="البرنامج", how="left")
                program_stats = pd.merge(program_stats, program_hours, on="البرنامج", how="left")
                
                # ترتيب البيانات حسب عدد المهام تنازليًا
                program_stats = program_stats.sort_values("عدد المهام", ascending=False)
                
                # تحضير مخططات العرض
                if mobile_view:
                    # للجوال: عرض المخططات في أعمدة منفصلة
                    
                    # مخطط 1: توزيع عدد المهام حسب البرنامج
                    fig_program_tasks = px.pie(
                        program_stats, 
                        values="عدد المهام", 
                        names="البرنامج",
                        title="توزيع عدد المهام حسب البرنامج",
                        color_discrete_sequence=px.colors.qualitative.Set2
                    )
                    fig_program_tasks = prepare_chart_layout(fig_program_tasks, "توزيع المهام حسب البرنامج", is_mobile=mobile_view, chart_type="pie")
                    st.plotly_chart(fig_program_tasks, use_container_width=True, config={"displayModeBar": False})
                    
                    # مخطط 2: توزيع النقاط حسب البرنامج
                    fig_program_points = px.bar(
                        program_stats, 
                        x="البرنامج", 
                        y="عدد النقاط",
                        title="توزيع النقاط حسب البرنامج",
                        color="عدد النقاط",
                        color_continuous_scale="Greens"
                    )
                    fig_program_points = prepare_chart_layout(fig_program_points, "توزيع النقاط حسب البرنامج", is_mobile=mobile_view, chart_type="bar")
                    st.plotly_chart(fig_program_points, use_container_width=True, config={"displayModeBar": False})
                else:
                    # لسطح المكتب: عرض المخططات في صفين
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # مخطط 1: توزيع عدد المهام حسب البرنامج
                        fig_program_tasks = px.pie(
                            program_stats, 
                            values="عدد المهام", 
                            names="البرنامج",
                            title="توزيع عدد المهام حسب البرنامج",
                            color_discrete_sequence=px.colors.qualitative.Set2
                        )
                        fig_program_tasks = prepare_chart_layout(fig_program_tasks, "توزيع المهام حسب البرنامج", is_mobile=mobile_view, chart_type="pie")
                        st.plotly_chart(fig_program_tasks, use_container_width=True, config={"displayModeBar": False})
                    
                    with col2:
                        # مخطط 2: توزيع النقاط حسب البرنامج
                        fig_program_points = px.bar(
                            program_stats.sort_values("عدد النقاط", ascending=True), 
                            y="البرنامج", 
                            x="عدد النقاط",
                            title="توزيع النقاط حسب البرنامج",
                            color="عدد النقاط",
                            orientation='h',
                            color_continuous_scale="Greens"
                        )
                        fig_program_points = prepare_chart_layout(fig_program_points, "توزيع النقاط حسب البرنامج", is_mobile=mobile_view, chart_type="bar")
                        st.plotly_chart(fig_program_points, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("لا توجد بيانات مرتبطة ببرامج في الفترة المحددة.")
        else:
            st.info("البيانات لا تحتوي على عمود البرنامج.")
        
        # 3. توزيع المهام حسب المهمة الرئيسية
        st.subheader("توزيع المهام حسب المهمة الرئيسية")
        
        if "المهمة الرئيسية" in filtered_data.columns:
            # تجهيز البيانات
            main_task_data = filtered_data[filtered_data["المهمة الرئيسية"].notna() & (filtered_data["المهمة الرئيسية"] != "")].copy()
            
            if not main_task_data.empty:
                # حساب الإحصاءات حسب المهمة الرئيسية
                main_task_counts = main_task_data.groupby("المهمة الرئيسية").size().reset_index(name="عدد المهام")
                main_task_points = main_task_data.groupby("المهمة الرئيسية")["عدد النقاط"].sum().reset_index()
                main_task_hours = main_task_data.groupby("المهمة الرئيسية")["عدد الساعات"].sum().reset_index()
                
                # دمج البيانات
                main_task_stats = pd.merge(main_task_counts, main_task_points, on="المهمة الرئيسية", how="left")
                main_task_stats = pd.merge(main_task_stats, main_task_hours, on="المهمة الرئيسية", how="left")
                
                # ترتيب البيانات حسب عدد المهام تنازليًا
                main_task_stats = main_task_stats.sort_values("عدد المهام", ascending=False)
                
                # اختيار أهم 10 مهام رئيسية لتحسين العرض المرئي
                top_main_tasks = main_task_stats.head(10).copy()
                
                # تحضير مخططات العرض
                if mobile_view:
                    # للجوال: عرض المخططات في أعمدة منفصلة
                    
                    # مخطط 1: توزيع عدد المهام حسب المهمة الرئيسية
                    fig_main_tasks = px.bar(
                        top_main_tasks.sort_values("عدد المهام", ascending=False), 
                        x="المهمة الرئيسية", 
                        y="عدد المهام",
                        title="توزيع المهام حسب المهمة الرئيسية (أهم 10)",
                        color="عدد المهام",
                        color_continuous_scale="Oranges"
                    )
                    fig_main_tasks = prepare_chart_layout(fig_main_tasks, "توزيع المهام الرئيسية", is_mobile=mobile_view, chart_type="bar")
                    st.plotly_chart(fig_main_tasks, use_container_width=True, config={"displayModeBar": False})
                    
                    # مخطط 2: توزيع الساعات حسب المهمة الرئيسية
                    fig_main_task_hours = px.bar(
                        top_main_tasks.sort_values("عدد الساعات", ascending=False), 
                        x="المهمة الرئيسية", 
                        y="عدد الساعات",
                        title="توزيع الساعات حسب المهمة الرئيسية (أهم 10)",
                        color="عدد الساعات",
                        color_continuous_scale="Oranges"
                    )
                    fig_main_task_hours = prepare_chart_layout(fig_main_task_hours, "توزيع ساعات المهام الرئيسية", is_mobile=mobile_view, chart_type="bar")
                    st.plotly_chart(fig_main_task_hours, use_container_width=True, config={"displayModeBar": False})
                else:
                    # لسطح المكتب: عرض المخططات في صفين
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # مخطط 1: توزيع عدد المهام حسب المهمة الرئيسية
                        fig_main_tasks = px.bar(
                            top_main_tasks.sort_values("عدد المهام", ascending=True), 
                            y="المهمة الرئيسية", 
                            x="عدد المهام",
                            title="توزيع المهام حسب المهمة الرئيسية (أهم 10)",
                            color="عدد المهام",
                            orientation='h',
                            color_continuous_scale="Oranges"
                        )
                        fig_main_tasks = prepare_chart_layout(fig_main_tasks, "توزيع المهام الرئيسية", is_mobile=mobile_view, chart_type="bar")
                        st.plotly_chart(fig_main_tasks, use_container_width=True, config={"displayModeBar": False})
                    
                    with col2:
                        # مخطط 2: توزيع الساعات حسب المهمة الرئيسية
                        fig_main_task_hours = px.bar(
                            top_main_tasks.sort_values("عدد الساعات", ascending=True), 
                            y="المهمة الرئيسية", 
                            x="عدد الساعات",
                            title="توزيع الساعات حسب المهمة الرئيسية (أهم 10)",
                            color="عدد الساعات",
                            orientation='h',
                            color_continuous_scale="Oranges"
                        )
                        fig_main_task_hours = prepare_chart_layout(fig_main_task_hours, "توزيع ساعات المهام الرئيسية", is_mobile=mobile_view, chart_type="bar")
                        st.plotly_chart(fig_main_task_hours, use_container_width=True, config={"displayModeBar": False})
                
                # عرض جدول المهام الرئيسية
                with st.expander("عرض إحصاءات تفصيلية للمهام الرئيسية", expanded=False):
                    # حساب معدلات لإثراء البيانات
                    main_task_stats["متوسط النقاط لكل مهمة"] = main_task_stats["عدد النقاط"] / main_task_stats["عدد المهام"]
                    main_task_stats["متوسط الساعات لكل مهمة"] = main_task_stats["عدد الساعات"] / main_task_stats["عدد المهام"]
                    main_task_stats["النقاط لكل ساعة"] = main_task_stats["عدد النقاط"] / main_task_stats["عدد الساعات"].replace(0, np.nan)
                    
                    # عرض الجدول المحسن
                    st.dataframe(
                        main_task_stats.sort_values("عدد المهام", ascending=False),
                        column_config={
                            "المهمة الرئيسية": st.column_config.TextColumn("المهمة الرئيسية"),
                            "عدد المهام": st.column_config.NumberColumn("عدد المهام"),
                            "عدد النقاط": st.column_config.NumberColumn("مجموع النقاط", format="%.1f"),
                            "عدد الساعات": st.column_config.NumberColumn("مجموع الساعات", format="%.1f"),
                            "متوسط النقاط لكل مهمة": st.column_config.NumberColumn("متوسط النقاط/مهمة", format="%.1f"),
                            "متوسط الساعات لكل مهمة": st.column_config.NumberColumn("متوسط الساعات/مهمة", format="%.1f"),
                            "النقاط لكل ساعة": st.column_config.NumberColumn("النقاط/ساعة", format="%.1f"),
                        },
                        hide_index=True,
                        use_container_width=True
                    )
            else:
                st.info("لا توجد بيانات مرتبطة بمهام رئيسية في الفترة المحددة.")
        else:
            st.info("البيانات لا تحتوي على عمود المهمة الرئيسية.")
        
        # 4. التوزيع الزمني للمهام والنقاط
        st.subheader("التوزيع الزمني للمهام والنقاط")
        
        if "التاريخ" in filtered_data.columns:
            # إضافة بيانات الشهر والسنة
            filtered_data["الشهر"] = filtered_data["التاريخ"].dt.month
            filtered_data["السنة"] = filtered_data["التاريخ"].dt.year
            filtered_data["الشهر-السنة"] = filtered_data["التاريخ"].dt.strftime("%Y-%m")
            
            # حساب الإحصاءات الشهرية
            monthly_counts = filtered_data.groupby("الشهر-السنة").size().reset_index(name="عدد المهام")
            monthly_points = filtered_data.groupby("الشهر-السنة")["عدد النقاط"].sum().reset_index()
            monthly_hours = filtered_data.groupby("الشهر-السنة")["عدد الساعات"].sum().reset_index()
            
            # دمج البيانات
            monthly_stats = pd.merge(monthly_counts, monthly_points, on="الشهر-السنة", how="left")
            monthly_stats = pd.merge(monthly_stats, monthly_hours, on="الشهر-السنة", how="left")
            
            # إضافة عمود تاريخ للترتيب
            monthly_stats["تاريخ_للترتيب"] = pd.to_datetime(monthly_stats["الشهر-السنة"])
            monthly_stats = monthly_stats.sort_values("تاريخ_للترتيب")
            
            # حساب متوسط النقاط والساعات لكل مهمة
            monthly_stats["متوسط النقاط/مهمة"] = monthly_stats["عدد النقاط"] / monthly_stats["عدد المهام"]
            monthly_stats["متوسط الساعات/مهمة"] = monthly_stats["عدد الساعات"] / monthly_stats["عدد المهام"]
            
            # إنشاء مخطط تطور عدد المهام والنقاط عبر الزمن
            fig_time_series = px.line(
                monthly_stats, 
                x="الشهر-السنة", 
                y=["عدد المهام", "عدد النقاط"],
                title="تطور عدد المهام والنقاط عبر الزمن",
                markers=True,
                color_discrete_sequence=["#1e88e5", "#27AE60"]
            )
            fig_time_series = prepare_chart_layout(fig_time_series, "تطور المهام والنقاط", is_mobile=mobile_view, chart_type="line")
            st.plotly_chart(fig_time_series, use_container_width=True, config={"displayModeBar": False})
            
            # عرض مخطط متوسط النقاط والساعات لكل مهمة
            fig_avg_time_series = px.line(
                monthly_stats, 
                x="الشهر-السنة", 
                y=["متوسط النقاط/مهمة", "متوسط الساعات/مهمة"],
                title="تطور متوسط النقاط والساعات لكل مهمة",
                markers=True,
                color_discrete_sequence=["#F39C12", "#E74C3C"]
            )
            fig_avg_time_series = prepare_chart_layout(fig_avg_time_series, "تطور متوسط النقاط والساعات", is_mobile=mobile_view, chart_type="line")
            st.plotly_chart(fig_avg_time_series, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("البيانات لا تحتوي على عمود التاريخ.")
    else:
        st.info("لا توجد بيانات كافية في الفترة المحددة لعرض التوزيعات.")

# =========================================
# القسم 14: تبويب إنجازات الأعضاء
# =========================================
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- دوال وهمية (استبدلها بالدوال الفعلية لديك) ---
# (نفس الدوال المساعدة من الإصدار السابق: get_achievement_level, get_member_of_month, ...)
# --- دوال وهمية (استبدلها بالدوال الفعلية لديك) ---
def get_achievement_level(points):
    """يحسب مستوى الإنجاز بناءً على النقاط."""
    # التأكد من أن النقاط هي قيمة رقمية
    try:
        points = float(points)
    except (ValueError, TypeError):
        points = 0 # قيمة افتراضية إذا لم تكن رقمية

    if points >= 200:
        return {"name": "خبير", "color": "#D32F2F", "icon": "🏆"}
    elif points >= 100:
        return {"name": "ممارس", "color": "#1976D2", "icon": "🏅"}
    elif points >= 50:
        return {"name": "متعلم", "color": "#388E3C", "icon": "🧑‍🎓"}
    else:
        return {"name": "مبتدئ", "color": "#7B1FA2", "icon": "🌱"}

def get_member_of_month(df, year, month):
    """يحصل على نجم الشهر."""
    # تأكد من أن عمود التاريخ هو من نوع datetime والأعمدة الأخرى موجودة
    if not all(col in df.columns for col in ["التاريخ", "اسم العضو", "عدد النقاط", "عدد الساعات"]):
         st.warning("أعمدة مطلوبة مفقودة في بيانات الإنجازات لحساب نجم الشهر.")
         return None
    try:
        df['التاريخ'] = pd.to_datetime(df['التاريخ'], errors='coerce')
        # التأكد من أن الأعمدة الرقمية رقمية
        df['عدد النقاط'] = pd.to_numeric(df['عدد النقاط'], errors='coerce')
        df['عدد الساعات'] = pd.to_numeric(df['عدد الساعات'], errors='coerce')
        df = df.dropna(subset=['التاريخ', 'اسم العضو', 'عدد النقاط', 'عدد الساعات']) # إزالة الصفوف التي تحتوي على قيم فارغة في الأعمدة الأساسية
    except Exception as e:
        st.error(f"خطأ في تحويل أنواع البيانات لحساب نجم الشهر: {e}")
        return None

    df_filtered = df[(df['التاريخ'].dt.year == year) & (df['التاريخ'].dt.month == month)].copy()
    if df_filtered.empty:
        return None # لا يوجد بيانات للشهر المحدد

    member_points = df_filtered.groupby("اسم العضو")["عدد النقاط"].sum()
    if member_points.empty:
        return None

    star_name = member_points.idxmax()
    star_data = df_filtered[df_filtered["اسم العضو"] == star_name]
    if star_data.empty:
        return None

    # الحصول على اسم الشهر بالعربي
    try:
        months_ar = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]
        month_name_ar = months_ar[month - 1]
    except IndexError:
        month_name_ar = f"شهر {month}" # اسم احتياطي

    return {
        "اسم": star_name,
        "النقاط": int(star_data["عدد النقاط"].sum()),
        "الساعات": int(star_data["عدد الساعات"].sum()),
        "المهام": len(star_data),
        "اسم_الشهر": month_name_ar
    }


def detect_member_promotions(df, lookback_days=30):
    """يكتشف ترقيات الأعضاء الأخيرة."""
    if not all(col in df.columns for col in ["التاريخ", "اسم العضو", "عدد النقاط"]):
         st.warning("أعمدة مطلوبة مفقودة في بيانات الإنجازات لكشف الترقيات.")
         return []
    try:
        df['التاريخ'] = pd.to_datetime(df['التاريخ'], errors='coerce')
        df['عدد النقاط'] = pd.to_numeric(df['عدد النقاط'], errors='coerce')
        df = df.dropna(subset=['التاريخ', 'اسم العضو', 'عدد النقاط'])
    except Exception as e:
        st.error(f"خطأ في تحويل أنواع البيانات لكشف الترقيات: {e}")
        return []


    end_date = datetime.now()
    start_date_current = end_date - timedelta(days=lookback_days)
    # start_date_previous = start_date_current - timedelta(days=lookback_days) # فترة المقارنة - تم تبسيط المنطق أدناه

    # حساب النقاط الكلية حتى نهاية الفترة الحالية وحتى بداية الفترة الحالية
    total_points_at_end = df[df["التاريخ"] <= end_date].groupby("اسم العضو")["عدد النقاط"].sum()
    total_points_at_start = df[df["التاريخ"] < start_date_current].groupby("اسم العضو")["عدد النقاط"].sum()
    points_in_period = df[(df["التاريخ"] >= start_date_current) & (df["التاريخ"] <= end_date)].groupby("اسم العضو")["عدد النقاط"].sum()


    promotions = []
    for member, current_total in total_points_at_end.items():
        previous_total = total_points_at_start.get(member, 0)
        points_gained = points_in_period.get(member, 0) # النقاط المكتسبة في الفترة الحالية

        level_current = get_achievement_level(current_total)
        level_previous = get_achievement_level(previous_total)

        # التحقق من حدوث ترقية وأن هناك نقاط مكتسبة في الفترة
        if level_current["name"] != level_previous["name"] and current_total > previous_total and points_gained > 0:
             promotions.append({
                "اسم": member,
                "المستوى_السابق": level_previous["name"],
                "المستوى_الجديد": level_current["name"],
                "لون_المستوى": level_current["color"],
                "أيقونة_المستوى": level_current["icon"],
                "النقاط_المكتسبة": points_gained # إظهار النقاط المكتسبة في الفترة
            })

    # فرز الترقيات حسب النقاط المكتسبة (الأعلى أولاً)
    promotions.sort(key=lambda x: x['النقاط_المكتسبة'], reverse=True)
    return promotions


def get_category_leaders(df):
    """يحصل على قادة الفئات."""
    if not all(col in df.columns for col in ["الفئة", "اسم العضو", "عدد النقاط"]):
        st.warning("أعمدة مطلوبة مفقودة في بيانات الإنجازات لحساب قادة الفئات.")
        return {}
    try:
        df['عدد النقاط'] = pd.to_numeric(df['عدد النقاط'], errors='coerce')
        df = df.dropna(subset=['الفئة', 'اسم العضو', 'عدد النقاط'])
        df['عدد النقاط'] = df['عدد النقاط'].astype(int)
    except Exception as e:
         st.error(f"خطأ في تحويل أنواع البيانات لحساب قادة الفئات: {e}")
         return {}


    category_leaders = {}
    valid_categories = df["الفئة"].unique() # لا داعي لإزالة NaN هنا، تم بالفعل
    for category in valid_categories:
        category_data = df[df["الفئة"] == category]
        # لا داعي للتحقق من category_data.empty هنا
        leader_points = category_data.groupby("اسم العضو")["عدد النقاط"].sum()
        if not leader_points.empty:
            leader_name = leader_points.idxmax()
            category_leaders[category] = {
                "اسم": leader_name,
                "النقاط": leader_points.max()
            }
    return category_leaders

def calculate_points_by_category(df, member_name):
    """يحسب توزيع نقاط عضو معين حسب الفئة."""
    if not all(col in df.columns for col in ["اسم العضو", "الفئة", "عدد النقاط"]):
         st.warning(f"أعمدة مطلوبة مفقودة لحساب نقاط الفئات للعضو {member_name}.")
         return pd.DataFrame()
    try:
        member_data = df[df["اسم العضو"] == member_name].copy()
        if member_data.empty:
            # st.info(f"لا توجد بيانات للعضو {member_name} في الفترة المحددة.") # يمكن إزالة هذه الرسالة لتجنب التكرار
            return pd.DataFrame()

        member_data['عدد النقاط'] = pd.to_numeric(member_data['عدد النقاط'], errors='coerce')
        member_data = member_data.dropna(subset=['الفئة', 'عدد النقاط'])
        member_data['عدد النقاط'] = member_data['عدد النقاط'].astype(int)
    except Exception as e:
        st.error(f"خطأ في تحويل البيانات لحساب نقاط الفئات للعضو {member_name}: {e}")
        return pd.DataFrame()


    category_points = member_data.groupby("الفئة")["عدد النقاط"].sum().reset_index()
    if category_points.empty:
        return pd.DataFrame()

    # حساب مستوى الإنجاز لكل فئة
    category_points["مستوى_الإنجاز"] = category_points["عدد النقاط"].apply(get_achievement_level)
    category_points["مستوى"] = category_points["مستوى_الإنجاز"].apply(lambda x: x["name"])
    category_points["لون_المستوى"] = category_points["مستوى_الإنجاز"].apply(lambda x: x["color"])
    category_points["أيقونة_المستوى"] = category_points["مستوى_الإنجاز"].apply(lambda x: x["icon"])
    return category_points

def create_radar_chart(category_points_df, member_name, is_mobile=False):
    """ينشئ مخطط رادار لتوزيع نقاط العضو حسب الفئة."""
    if category_points_df.empty:
        # st.info("لا توجد بيانات فئات لإنشاء مخطط الرادار.") # يمكن إزالة هذه الرسالة
        return None

    if not all(col in category_points_df.columns for col in ["الفئة", "عدد النقاط"]):
        st.warning("بيانات الفئات غير مكتملة لإنشاء المخطط.")
        return None

    try:
        category_points_df['عدد النقاط'] = pd.to_numeric(category_points_df['عدد النقاط'], errors='coerce')
        category_points_df = category_points_df.dropna(subset=['عدد النقاط'])
        if category_points_df.empty:
            # st.info("لا توجد بيانات نقاط صالحة لإنشاء المخطط.") # يمكن إزالة هذه الرسالة
            return None
    except Exception as e:
         st.error(f"خطأ في تحويل نقاط الفئات للرادار: {e}")
         return None


    fig = px.line_polar(category_points_df, r='عدد النقاط', theta='الفئة', line_close=True,
                        # title=f"توزيع نقاط {member_name} حسب الفئة", # العنوان سيتم إضافته في prepare_chart_layout
                        markers=True,
                        color_discrete_sequence=px.colors.sequential.Plasma_r)

    fig.update_traces(fill='toself')

    fig = prepare_chart_layout(fig, f"توزيع نقاط {member_name} حسب الفئة", is_mobile=is_mobile, chart_type="polar") # استخدام prepare_chart_layout

    # تحسينات خاصة بالرادار
    max_r_value = category_points_df['عدد النقاط'].max()
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max_r_value * 1.1 if max_r_value > 0 else 10] # تحديد النطاق ديناميكيًا مع حد أدنى
            )),
        showlegend=False,
         margin=dict(l=40, r=40, t=80, b=40) # ضبط الهوامش للرادار
    )
    return fig


def prepare_chart_layout(fig, title, is_mobile=False, chart_type="bar"):
    """يجهز تنسيق المخطط."""
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center'), # طريقة أفضل لتوسيط العنوان
        font=dict(family="Arial, sans-serif", size=12 if not is_mobile else 10, color="#333"),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=60, b=20), # تعديل الهوامش الافتراضية
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial") # تحسين صندوق المعلومات
    )
    # إعدادات خاصة بنوع المخطط
    if chart_type == "bar":
         fig.update_layout(
             xaxis=dict(showgrid=False, zeroline=False),
             yaxis=dict(showgrid=True, gridcolor='#e0e0e0', zeroline=False),
             bargap=0.2 # إضافة فجوة بين الأعمدة
         )
         fig.update_traces(marker_line_width=0)
    elif chart_type == "line":
         fig.update_layout(
             xaxis=dict(gridcolor='#e0e0e0'),
             yaxis=dict(gridcolor='#e0e0e0')
         )
    elif chart_type == "pie":
         fig.update_traces(textposition='inside', textinfo='percent+label', marker_line=dict(color='#ffffff', width=1)) # إضافة حدود للشرائح
         fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=60, b=20)) # هوامش خاصة للفطيرة
    elif chart_type == "polar":
         # تم نقل إعدادات polar إلى دالة create_radar_chart
         pass

    # إعدادات المحاور العامة (يمكن تخصيصها أكثر إذا لزم الأمر)
    fig.update_xaxes(title_font=dict(size=14), tickfont=dict(size=12))
    fig.update_yaxes(title_font=dict(size=14), tickfont=dict(size=12))

    return fig

# --- بيانات وهمية (استبدلها ببياناتك الفعلية من Google Sheets أو مصدر آخر) ---
data = {
    "التاريخ": pd.to_datetime([
        "2025-04-15", "2025-04-20", "2025-04-25", "2025-05-01", "2025-05-02", "2025-03-10", "2025-04-18", "2025-05-03",
        "2025-04-10", "2025-04-22", "2025-04-28", "2025-05-01", "2025-05-03", "2025-03-15", "2025-04-19", "2025-05-02",
        "2025-04-05", "2025-04-12", "2025-04-30", "2025-05-01", "2025-05-03", "2025-02-20", "2025-04-21", "2025-05-01"
    ]),
    "اسم العضو": [
        "آمنة جمعة", "آمنة جمعة", "آمنة جمعة", "آمنة جمعة", "آمنة جمعة", "آمنة جمعة", "آمنة جمعة", "آمنة جمعة", # 8 مهام لآمنة
        "فاطمة علي", "فاطمة علي", "فاطمة علي", "فاطمة علي", "فاطمة علي", "فاطمة علي", "فاطمة علي", "فاطمة علي", # 8 مهام لفاطمة
        "محمد حسن", "محمد حسن", "محمد حسن", "محمد حسن", "محمد حسن", "محمد حسن", "محمد حسن", "محمد حسن"  # 8 مهام لمحمد
    ],
    "الفئة": [
        "التطوير", "التصميم", "الكتابة", "التطوير", "التسويق", "التصميم", "الكتابة", "التطوير",
        "التصميم", "التطوير", "التسويق", "الكتابة", "التصميم", "التطوير", "الكتابة", "التسويق",
        "الكتابة", "التسويق", "التطوير", "التصميم", "الكتابة", "التسويق", "التطوير", "التصميم"
    ],
    "البرنامج": [
        "البرنامج أ", "البرنامج ب", "البرنامج أ", "البرنامج ج", "البرنامج ب", "البرنامج أ", "البرنامج ج", "البرنامج أ",
        "البرنامج ب", "البرنامج أ", "البرنامج ج", "البرنامج ب", "البرنامج أ", "البرنامج ج", "البرنامج ب", "البرنامج أ",
        "البرنامج ج", "البرنامج أ", "البرنامج ب", "البرنامج ج", "البرنامج أ", "البرنامج ب", "البرنامج ج", "البرنامج أ"
    ],
    "عدد النقاط": [
        50, 30, 40, 60, 25, 35, 45, 55, # آمنة
        45, 55, 20, 35, 50, 60, 40, 30, # فاطمة
        65, 25, 50, 40, 30, 55, 35, 45  # محمد
    ],
    "عدد الساعات": [
        5, 3, 4, 6, 2.5, 3.5, 4.5, 5.5, # آمنة
        4.5, 5.5, 2, 3.5, 5, 6, 4, 3, # فاطمة
        6.5, 2.5, 5, 4, 3, 5.5, 3.5, 4.5 # محمد
    ],
    "عنوان المهمة": [f"مهمة {i+1}" for i in range(24)],
    "وصف مختصر": [f"وصف للمهمة {i+1}" for i in range(24)]
}
achievements_data = pd.DataFrame(data)
# تحويل عمود التاريخ إلى datetime إذا لم يكن كذلك بالفعل
try:
    achievements_data['التاريخ'] = pd.to_datetime(achievements_data['التاريخ'], errors='coerce')
except Exception as e:
    st.error(f"خطأ في تحويل عمود التاريخ الرئيسي: {e}")
    # يمكنك إيقاف التنفيذ هنا أو استخدام بيانات فارغة
    achievements_data = pd.DataFrame()


# --- إعدادات Streamlit ---
st.set_page_config(layout="wide", page_title="لوحة تحكم الإنجازات")

# --- محاكاة Tabs ---
# في تطبيقك الفعلي، ستكون هذه جزءًا من st.tabs
class MockTab:
    def __init__(self, label):
        self.label = label
        self._container = st.container() # إنشاء حاوية لكل "تبويب"

    def __enter__(self):
        self._container.__enter__() # الدخول إلى الحاوية
        # st.subheader(self.label) # يمكنك إضافة عنوان للتبويب هنا إذا أردت
        return self

    def __exit__(self, type, value, traceback):
         self._container.__exit__(type, value, traceback) # الخروج من الحاوية

# إنشاء تبويبات وهمية
main_tabs = [MockTab("التبويب 1"), MockTab("إنجازات الأعضاء")]

# --- متغيرات وهمية أخرى ---
mobile_view = st.checkbox("عرض الجوال (للمحاكاة)") # محاكاة عرض الجوال
ACHIEVEMENT_LEVELS = [ # تعريف مستويات الإنجاز
    {"name": "مبتدئ", "color": "#7B1FA2", "icon": "🌱", "min_points": 0},
    {"name": "متعلم", "color": "#388E3C", "icon": "🧑‍🎓", "min_points": 50},
    {"name": "ممارس", "color": "#1976D2", "icon": "🏅", "min_points": 100},
    {"name": "خبير", "color": "#D32F2F", "icon": "🏆", "min_points": 200}
]

# --- بداية القسم 14 ---
with main_tabs[1]: # نفترض أن التبويب الثاني هو "إنجازات الأعضاء"
    st.markdown("### إنجازات الأعضاء")

    # --- تهيئة متغير الجلسة ---
    if 'selected_member_detail' not in st.session_state:
        st.session_state.selected_member_detail = "اختر عضوًا..." # قيمة افتراضية

    # تصفية زمنية
    st.markdown('<div class="time-filter">', unsafe_allow_html=True)
    st.markdown('<div class="time-filter-title">تصفية حسب الفترة الزمنية:</div>', unsafe_allow_html=True)
    achievement_time_period = st.radio(
        "", # إزالة العنوان من هنا لتقليل المساحة
        options=["الشهر الحالي", "الربع الحالي", "السنة الحالية", "كل الفترات"],
        horizontal=True,
        key="achievement_time_filter",
        label_visibility="collapsed" # إخفاء العنوان المتبقي
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # تطبيق الفلتر الزمني على البيانات
    members_filtered_data = achievements_data.copy()

    # التأكد من أن عمود التاريخ موجود وصالح قبل الفلترة
    if "التاريخ" in members_filtered_data.columns and pd.api.types.is_datetime64_any_dtype(members_filtered_data['التاريخ']):
        filter_date = None # إعادة تعيين filter_date
        now = datetime.now()

        if achievement_time_period == "الشهر الحالي":
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            filter_date = start_of_month
        elif achievement_time_period == "الربع الحالي":
            current_quarter = (now.month - 1) // 3 + 1
            start_month_of_quarter = 3 * (current_quarter - 1) + 1
            start_of_quarter = now.replace(month=start_month_of_quarter, day=1, hour=0, minute=0, second=0, microsecond=0)
            filter_date = start_of_quarter
        elif achievement_time_period == "السنة الحالية":
            start_of_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            filter_date = start_of_year

        # تطبيق الفلتر فقط إذا تم تحديد فترة زمنية غير "كل الفترات"
        if filter_date:
            # التأكد من أن filter_date هو datetime object
             if isinstance(filter_date, datetime):
                 members_filtered_data = members_filtered_data[members_filtered_data["التاريخ"] >= filter_date].copy() # استخدام .copy() لتجنب SettingWithCopyWarning

    else:
         st.warning("عمود 'التاريخ' غير موجود أو ليس بتنسيق تاريخ صالح.")
         members_filtered_data = pd.DataFrame() # إفراغ البيانات لتجنب أخطاء لاحقة


    # التحقق من وجود بيانات وأعمدة ضرورية قبل المتابعة
    # يجب أن يتم هذا التحقق *بعد* الفلترة الزمنية
    if not members_filtered_data.empty and all(col in members_filtered_data.columns for col in ["اسم العضو", "عدد النقاط", "عدد الساعات"]):

        try:
            # التأكد من أن الأعمدة الرقمية هي بالفعل رقمية
            members_filtered_data['عدد النقاط'] = pd.to_numeric(members_filtered_data['عدد النقاط'], errors='coerce')
            members_filtered_data['عدد الساعات'] = pd.to_numeric(members_filtered_data['عدد الساعات'], errors='coerce')
            # إزالة الصفوف التي تحتوي على قيم غير رقمية في الأعمدة الأساسية بعد التحويل
            members_filtered_data = members_filtered_data.dropna(subset=['اسم العضو', 'عدد النقاط', 'عدد الساعات']) # التأكد من عدم وجود اسم عضو فارغ أيضًا
            # تحويل الأعمدة إلى نوع int إذا كانت الحاجة (بعد التأكد من عدم وجود NaN)
            members_filtered_data['عدد النقاط'] = members_filtered_data['عدد النقاط'].astype(int)
            members_filtered_data['عدد الساعات'] = members_filtered_data['عدد الساعات'].astype(int)
        except Exception as e:
            st.error(f"خطأ في معالجة البيانات الرقمية: {e}")
            members_filtered_data = pd.DataFrame() # إفراغ البيانات عند حدوث خطأ

        # --- حساب الإحصائيات فقط إذا كانت البيانات لا تزال موجودة ---
        if not members_filtered_data.empty:
            # حساب نقاط كل عضو
            member_points_df = members_filtered_data.groupby("اسم العضو")["عدد النقاط"].sum().reset_index()


            # حساب ساعات كل عضو
            member_hours_df = members_filtered_data.groupby("اسم العضو")["عدد الساعات"].sum().reset_index()

            # حساب عدد المهام لكل عضو
            member_tasks_df = members_filtered_data.groupby("اسم العضو").size().reset_index(name="عدد المهام")

            # دمج البيانات - التأكد من أن DataFrame النقاط ليس فارغًا
            if not member_points_df.empty:
                member_stats = pd.merge(member_points_df, member_hours_df, on="اسم العضو", how="left")
                member_stats = pd.merge(member_stats, member_tasks_df, on="اسم العضو", how="left")

                # ملء القيم المفقودة (NaN) بصفر في الأعمدة الرقمية بعد الدمج
                for col in ["عدد النقاط", "عدد الساعات", "عدد المهام"]:
                     if col in member_stats.columns:
                         member_stats[col] = member_stats[col].fillna(0).astype(int)
                     else:
                          # إذا لم يكن العمود موجودًا بعد الدمج (حالة نادرة)، قم بإنشائه بصفر
                          member_stats[col] = 0


                # فرز member_stats حسب النقاط قبل إضافة المستويات
                member_stats = member_stats.sort_values("عدد النقاط", ascending=False)


                # إضافة مستوى الإنجاز لكل عضو
                member_stats["مستوى_الإنجاز"] = member_stats["عدد النقاط"].apply(get_achievement_level)
                member_stats["مستوى"] = member_stats["مستوى_الإنجاز"].apply(lambda x: x["name"])
                member_stats["لون_المستوى"] = member_stats["مستوى_الإنجاز"].apply(lambda x: x["color"])
                member_stats["أيقونة_المستوى"] = member_stats["مستوى_الإنجاز"].apply(lambda x: x["icon"])

                # --- عرض المكونات المختلفة ---

                # 1. قسم نجم الشهر (يجب أن يظل يعمل حتى لو كانت member_stats فارغة)
                current_month = datetime.now().month
                current_year = datetime.now().year
                star_of_month = get_member_of_month(achievements_data, current_year, current_month) # استخدام البيانات الأصلية

                if star_of_month:
                    st.subheader("🌟 نجم الشهر")
                    st.markdown(f"""
                    <div class="star-of-month" style="background: linear-gradient(135deg, #fceabb 0%, #f8b500 100%); padding: 20px; border-radius: 15px; text-align: center; color: #333; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                        <div class="star-badge" style="font-size: 3rem; margin-bottom: 10px;">🏆</div>
                        <h3 style="margin-top: 5px; margin-bottom: 5px; font-weight: bold; font-size: 1.4rem;">نجم شهر {star_of_month["اسم_الشهر"]}</h3>
                        <div class="star-name" style="font-size: 1.8rem; font-weight: bold; color: #BF360C; margin-bottom: 15px;">{star_of_month["اسم"]}</div>
                        <div class="star-stats" style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 15px;">
                            <div class="star-stat" style="background-color: rgba(255, 255, 255, 0.5); padding: 10px; border-radius: 10px; min-width: 80px;">
                                <div class="star-stat-value" style="font-size: 1.5rem; font-weight: bold;">{int(star_of_month["النقاط"])}</div>
                                <div class="star-stat-label" style="font-size: 0.9rem;">النقاط</div>
                            </div>
                            <div class="star-stat" style="background-color: rgba(255, 255, 255, 0.5); padding: 10px; border-radius: 10px; min-width: 80px;">
                                <div class="star-stat-value" style="font-size: 1.5rem; font-weight: bold;">{int(star_of_month["الساعات"])}</div>
                                <div class="star-stat-label" style="font-size: 0.9rem;">الساعات</div>
                            </div>
                            <div class="star-stat" style="background-color: rgba(255, 255, 255, 0.5); padding: 10px; border-radius: 10px; min-width: 80px;">
                                <div class="star-stat-value" style="font-size: 1.5rem; font-weight: bold;">{star_of_month["المهام"]}</div>
                                <div class="star-stat-label" style="font-size: 0.9rem;">المهام</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                     st.info("لم يتم تحديد نجم الشهر بعد.")


                # 2. لوحة الصدارة (تعتمد على member_stats)
                st.subheader("🏆 لوحة الصدارة (حسب الفترة المحددة)")
                leaderboard_cols = st.columns([3, 2]) if not mobile_view else (st.container(), st.container())

                with leaderboard_cols[0]:
                     top_10_members = member_stats.head(10).copy()
                     if not top_10_members.empty:
                         top_10_members = top_10_members.sort_values("عدد النقاط", ascending=True)
                         fig_top_members = px.bar(
                             top_10_members,
                             y="اسم العضو" if not mobile_view else "عدد النقاط",
                             x="عدد النقاط" if not mobile_view else "اسم العضو",
                             orientation='h' if not mobile_view else 'v',
                             color="عدد النقاط",
                             color_continuous_scale=px.colors.sequential.Viridis,
                             text="مستوى" if not mobile_view else None,
                             height=400
                         )
                         fig_top_members.update_layout(
                             yaxis_title="اسم العضو" if not mobile_view else "النقاط",
                             xaxis_title="عدد النقاط" if not mobile_view else "اسم العضو",
                             coloraxis_showscale=False,
                         )
                         if not mobile_view:
                             fig_top_members.update_traces(textposition='outside')
                         fig_top_members = prepare_chart_layout(fig_top_members, "أعلى 10 أعضاء", is_mobile=mobile_view, chart_type="bar")
                         st.plotly_chart(fig_top_members, use_container_width=True, config={"displayModeBar": False})
                     else:
                         st.info("لا توجد بيانات كافية لعرض مخطط أعلى الأعضاء.")

                with leaderboard_cols[1]:
                    st.markdown('<div class="leaderboard" style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; height: 400px; overflow-y: auto;">', unsafe_allow_html=True)
                    st.markdown('<div class="leaderboard-title" style="text-align: center; font-weight: bold; margin-bottom: 15px; font-size: 1.2rem;">قائمة المتصدرين</div>', unsafe_allow_html=True)
                    if not member_stats.empty:
                         for i, (_, row) in enumerate(member_stats.head(5).iterrows()):
                             rank_color = "#FFD700" if i == 0 else ("#C0C0C0" if i == 1 else ("#CD7F32" if i == 2 else "#6c757d"))
                             rank_icon = "🥇" if i == 0 else ("🥈" if i == 1 else ("🥉" if i == 2 else f"{i+1}."))
                             st.markdown(f"""
                             <div class="leaderboard-item" style="display: flex; align-items: center; margin-bottom: 12px; padding: 8px; border-radius: 6px; background-color: {'rgba(255, 255, 255, 0.7)' if i>=3 else 'transparent'}; border-left: 5px solid {rank_color};">
                                 <div class="leaderboard-rank" style="font-weight: bold; color: {rank_color}; font-size: 1.1rem; margin-right: 10px; min-width: 30px; text-align: center;">{rank_icon}</div>
                                 <div class="leaderboard-info" style="flex-grow: 1; margin-right: 10px;">
                                     <div class="leaderboard-name" style="font-weight: 600; font-size: 1rem;">{row['اسم العضو']} <span style="font-size: 0.9rem;">{row['أيقونة_المستوى']}</span></div>
                                     <div class="leaderboard-details" style="font-size: 0.8rem; color: #555;">{row['مستوى']} • {int(row['عدد المهام'])} مهمة • {int(row['عدد الساعات'])} ساعة</div>
                                 </div>
                                 <div class="leaderboard-score" style="font-weight: bold; font-size: 1.1rem; color: {row['لون_المستوى']};">{int(row['عدد النقاط'])}</div>
                             </div>
                             """, unsafe_allow_html=True)
                    else:
                         st.info("لا توجد بيانات لعرض لوحة الصدارة.")
                    st.markdown('</div>', unsafe_allow_html=True)


                # 3. ترقيات الأعضاء الأخيرة (تعتمد على achievements_data)
                promotions = detect_member_promotions(achievements_data, lookback_days=30)
                if promotions:
                    st.subheader("🚀 أحدث ترقيات الأعضاء (آخر 30 يوم)")
                    st.markdown('<div class="promotions-list" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-top: 15px;">', unsafe_allow_html=True)
                    for promotion in promotions[:6]:
                        st.markdown(f"""
                        <div class="promotion-item" style="background-color: #e8f5e9; padding: 15px; border-radius: 8px; border-left: 5px solid {promotion['لون_المستوى']};">
                            <div class="promotion-name" style="font-weight: 600; font-size: 1.1rem;">{promotion['اسم']} <span class="promotion-badge" style="color: {promotion['لون_المستوى']};">{promotion['أيقونة_المستوى']}</span></div>
                            <div class="promotion-details" style="font-size: 0.9rem; margin-top: 8px; color: #333;">
                                ترقى من <span style="color: #777; font-weight: 500;">{promotion['المستوى_السابق']}</span> إلى <span style="color: {promotion['لون_المستوى']}; font-weight: 600;">{promotion['المستوى_الجديد']}</span>
                                <div style="margin-top: 5px; font-size: 0.85rem; color: #555;">+{int(promotion['النقاط_المكتسبة'])} نقطة</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)


                # 4. قادة الفئات (تعتمد على members_filtered_data)
                category_leaders = get_category_leaders(members_filtered_data)
                if category_leaders:
                    st.subheader("🏅 قادة الفئات (حسب الفترة المحددة)")
                    categories = list(category_leaders.keys())
                    num_categories = len(categories)
                    num_cols = min(num_categories, 4)
                    if num_cols > 0:
                         cols = st.columns(num_cols)
                         col_index = 0
                         for category in categories:
                             leader = category_leaders[category]
                             with cols[col_index % num_cols]:
                                 st.markdown(f"""
                                 <div style="padding: 12px; border-radius: 8px; background-color: #e3f2fd; text-align: center; height: 100%; margin-bottom: 10px; border: 1px solid #bbdefb;">
                                     <div style="font-size: 0.9rem; color: #1565c0; margin-bottom: 5px; font-weight: 600;">{category}</div>
                                     <div style="font-weight: 600; color: #0d47a1; font-size: 1.1rem; margin-bottom: 5px;">{leader['اسم']}</div>
                                     <div><span style="font-weight: bold; font-size: 1.2rem; color: #1e88e5;">{int(leader['النقاط'])}</span> <span style="font-size: 0.8rem; color: #555;">نقطة</span></div>
                                 </div>
                                 """, unsafe_allow_html=True)
                             col_index += 1
                    else:
                         st.info("لا توجد فئات لعرض القادة في الفترة المحددة.")


                # 5. عرض تفاصيل إنجازات الأعضاء باختيار عضو محدد
                st.subheader("👤 تفاصيل إنجازات الأعضاء")
                st.markdown("---") # خط فاصل

                # إضافة فلاتر لتخصيص التصفية
                filter_cols = st.columns([2, 2, 2])

                # --- تحديد القوائم المتاحة للفلاتر بناءً على member_stats ---
                # (لأن الفلاتر تعمل على قائمة الأعضاء الإجمالية للفترة)
                available_categories_for_filter = ["الكل"]
                if "الفئة" in members_filtered_data.columns: # نستخدم البيانات المفلترة زمنياً لتحديد الفئات المتاحة فعلاً
                    available_categories_for_filter += sorted(members_filtered_data["الفئة"].dropna().unique())

                available_programs_for_filter = ["الكل"]
                if "البرنامج" in members_filtered_data.columns: # نستخدم البيانات المفلترة زمنياً لتحديد البرامج المتاحة فعلاً
                    available_programs_for_filter += sorted(members_filtered_data["البرنامج"].dropna().unique())

                available_levels_for_filter = ["الكل"] + sorted(member_stats["مستوى"].unique())


                with filter_cols[0]:
                    category_filter = st.selectbox(
                        "تصفية حسب الفئة",
                        available_categories_for_filter, # استخدام القائمة المحدثة
                        key="category_filter_detail"
                    )

                with filter_cols[1]:
                    program_filter = st.selectbox(
                        "تصفية حسب البرنامج",
                         available_programs_for_filter, # استخدام القائمة المحدثة
                        key="program_filter_detail"
                    )

                with filter_cols[2]:
                    level_filter = st.selectbox(
                        "تصفية حسب المستوى",
                         available_levels_for_filter, # استخدام القائمة المحدثة
                        key="level_filter_detail"
                    )

                # --- تطبيق الفلاتر على قائمة الأعضاء (member_stats) ---
                filtered_members_df = member_stats.copy() # ابدأ بنسخة من إحصائيات الأعضاء المحسوبة للفترة الزمنية

                # فلترة حسب المستوى (من member_stats)
                if level_filter != "الكل":
                    filtered_members_df = filtered_members_df[filtered_members_df["مستوى"] == level_filter]

                # فلترة حسب البرنامج (يتطلب الرجوع إلى members_filtered_data)
                if program_filter != "الكل":
                    program_members_in_period = members_filtered_data[members_filtered_data["البرنامج"] == program_filter]["اسم العضو"].unique()
                    filtered_members_df = filtered_members_df[filtered_members_df["اسم العضو"].isin(program_members_in_period)]

                # فلترة حسب الفئة (يتطلب الرجوع إلى members_filtered_data)
                if category_filter != "الكل":
                     category_members_in_period = members_filtered_data[members_filtered_data["الفئة"] == category_filter]["اسم العضو"].unique()
                     filtered_members_df = filtered_members_df[filtered_members_df["اسم العضو"].isin(category_members_in_period)]


                # --- عرض القائمة المصفاة ---
                final_filtered_member_list = filtered_members_df["اسم العضو"].tolist()

                st.markdown("##### الأعضاء المطابقون للتصفية:")
                if final_filtered_member_list:
                    # عرض القائمة في أعمدة لتحسين التنسيق
                    max_cols = 4 # عدد الأعمدة المرغوب
                    num_members = len(final_filtered_member_list)
                    members_per_col = (num_members + max_cols - 1) // max_cols # حساب عدد الأعضاء لكل عمود

                    list_cols = st.columns(max_cols)
                    member_index = 0
                    for col in list_cols:
                        with col:
                            for i in range(members_per_col):
                                if member_index < num_members:
                                    member_name = final_filtered_member_list[member_index]
                                    # عرض اسم العضو مع أيقونة المستوى والنقاط
                                    member_row = filtered_members_df[filtered_members_df["اسم العضو"] == member_name].iloc[0]
                                    icon = member_row['أيقونة_المستوى']
                                    points = member_row['عدد النقاط']
                                    st.markdown(f"- {member_name} ({icon} {points} نقطة)")
                                    member_index += 1
                                else:
                                    break # الخروج من الحلقة الداخلية إذا انتهت القائمة
                    st.markdown("---") # خط فاصل بعد القائمة
                else:
                    st.info("لا يوجد أعضاء يطابقون معايير التصفية المحددة.")
                    st.markdown("---") # خط فاصل

                # --- القائمة المنسدلة للاختيار ---
                # لا تزال القائمة المنسدلة مفيدة لتحديد العضو الذي سيتم عرض تفاصيله
                if final_filtered_member_list:
                     # تحديد القيمة الافتراضية للمربع المنسدل
                     # إذا كان العضو المحدد سابقًا لا يزال في القائمة المصفاة، احتفظ به. وإلا، ارجع إلى "اختر عضوًا..."
                     default_index = 0
                     if st.session_state.selected_member_detail in final_filtered_member_list:
                         default_index = (["اختر عضوًا..."] + final_filtered_member_list).index(st.session_state.selected_member_detail)
                     else:
                         # إذا لم يعد العضو المحدد سابقًا موجودًا بسبب الفلترة، أعد التعيين
                         st.session_state.selected_member_detail = "اختر عضوًا..."


                     current_selection = st.selectbox(
                         "اختر عضوًا من القائمة أعلاه لعرض تفاصيله", # تغيير التسمية
                         ["اختر عضوًا..."] + final_filtered_member_list,
                         index=default_index, # استخدام الفهرس الافتراضي المحسوب
                         key="member_select"
                     )
                     # تحديث session_state فقط إذا تغير الاختيار
                     if current_selection != st.session_state.selected_member_detail:
                          st.session_state.selected_member_detail = current_selection
                          st.rerun() # إعادة تشغيل السكربت لتحديث العرض بناءً على الاختيار الجديد
                # else: # لا داعي لعرض selectbox إذا كانت القائمة فارغة


                # --- عرض تفاصيل العضو المحدد ---
                selected_member_to_display = st.session_state.selected_member_detail

                if selected_member_to_display and selected_member_to_display != "اختر عضوًا...":
                    # الحصول على بيانات العضو المحدد *من البيانات المفلترة زمنياً*
                    member_data = members_filtered_data[members_filtered_data["اسم العضو"] == selected_member_to_display].copy()

                    if not member_data.empty:
                        # الحصول على معلومات العضو *من إحصائيات الفترة المحددة* (filtered_members_df)
                        # التأكد من أن العضو لا يزال موجودًا في filtered_members_df
                        member_info_rows = filtered_members_df[filtered_members_df["اسم العضو"] == selected_member_to_display]
                        if not member_info_rows.empty:
                            member_info = member_info_rows.iloc[0]

                            # حساب مستوى الإنجاز ومعلومات إضافية للفترة المحددة
                            achievement_level = member_info["مستوى_الإنجاز"]
                            total_points = member_info["عدد النقاط"]
                            total_hours = member_info["عدد الساعات"]
                            total_tasks = member_info["عدد المهام"]

                            # حساب توزيع النقاط حسب الفئة *للفترة المحددة*
                            category_points = calculate_points_by_category(member_data, selected_member_to_display)

                            # --- عرض معلومات العضو (للفترة المحددة) ---
                            st.markdown(f"""
                            <div style="padding: 20px; background-color: #ffffff; border-radius: 12px; margin-top: 20px; margin-bottom: 20px; direction: rtl; text-align: right; border: 1px solid #dee2e6; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                                <h3 style="margin-top: 0; margin-bottom: 15px; color: {achievement_level['color']}; border-bottom: 2px solid {achievement_level['color']}; padding-bottom: 10px;">{selected_member_to_display} {achievement_level['icon']}</h3>
                                <div style="margin-bottom: 20px;">
                                    <span style="font-size: 1.3rem; color: {achievement_level['color']}; font-weight: bold; background-color: {achievement_level['color']}20; padding: 5px 10px; border-radius: 5px;">المستوى ({achievement_time_period}): {achievement_level['name']}</span>
                                </div>

                                <div style="display: flex; flex-direction: row-reverse; flex-wrap: wrap; gap: 20px; justify-content: space-around;">
                                    {create_metric_card(int(total_points), "مجموع النقاط", "#1e88e5")}
                                    {create_metric_card(int(total_tasks), "عدد المهام", "#27AE60")}
                                    {create_metric_card(int(total_hours), "مجموع الساعات", "#F39C12")}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                            # --- عرض المخططات والجدول للعضو المحدد ---
                            member_charts_cols = st.columns([3, 2]) if not mobile_view else (st.container(), st.container())

                            with member_charts_cols[0]: # العمود الأكبر للمخططات
                                # عرض التحليل حسب الفئة (Radar Chart)
                                 if not category_points.empty:
                                     st.markdown("#### توزيع نقاط العضو حسب الفئات")
                                     radar_chart = create_radar_chart(category_points, selected_member_to_display, is_mobile=mobile_view)
                                     if radar_chart:
                                         st.plotly_chart(radar_chart, use_container_width=True, config={"displayModeBar": False})
                                     # else: # لا داعي لعرض رسالة هنا
                                 else:
                                     st.info(f"لا توجد بيانات فئات للعضو {selected_member_to_display} في الفترة المحددة.")


                                 # عرض مخطط التطور الزمني للنقاط (إذا كان هناك تاريخ)
                                 if "التاريخ" in member_data.columns and pd.api.types.is_datetime64_any_dtype(member_data['التاريخ']):
                                     st.markdown("#### تطور نقاط العضو عبر الزمن")
                                     if len(member_data) > 1:
                                         member_data_ts = member_data.copy()
                                         member_data_ts["الشهر-السنة"] = member_data_ts["التاريخ"].dt.strftime("%Y-%m")
                                         member_monthly_stats = member_data_ts.groupby("الشهر-السنة").agg(
                                             عدد_النقاط=('عدد النقاط', 'sum'),
                                             عدد_الساعات=('عدد الساعات', 'sum'),
                                             عدد_المهام=('اسم العضو', 'size')
                                         ).reset_index()
                                         member_monthly_stats["تاريخ_للترتيب"] = pd.to_datetime(member_monthly_stats["الشهر-السنة"] + "-01")
                                         member_monthly_stats = member_monthly_stats.sort_values("تاريخ_للترتيب")

                                         fig_member_time_series = px.line(
                                             member_monthly_stats, x="الشهر-السنة", y=["عدد_النقاط", "عدد_الساعات", "عدد_المهام"],
                                             markers=True, labels={"value": "القيمة", "variable": "المقياس", "الشهر-السنة": "الشهر"},
                                             color_discrete_map={"عدد_النقاط": "#1e88e5", "عدد_الساعات": "#F39C12", "عدد_المهام": "#27AE60"}
                                         )
                                         fig_member_time_series.update_layout(legend_title_text='المقاييس')
                                         fig_member_time_series = prepare_chart_layout(fig_member_time_series, f"تطور إنجازات {selected_member_to_display} الشهرية", is_mobile=mobile_view, chart_type="line")
                                         st.plotly_chart(fig_member_time_series, use_container_width=True, config={"displayModeBar": False})
                                     else:
                                         st.info(f"لا توجد بيانات زمنية كافية لعرض تطور إنجازات {selected_member_to_display}.")


                                 # عرض مخطط توزيع النقاط حسب البرنامج (إذا كان هناك برامج)
                                 if "البرنامج" in member_data.columns:
                                     program_data = member_data[member_data["البرنامج"].notna() & (member_data["البرنامج"] != "")].copy()
                                     if not program_data.empty:
                                         st.markdown("#### توزيع نقاط العضو حسب البرنامج")
                                         program_points = program_data.groupby("البرنامج")["عدد النقاط"].sum().reset_index().sort_values("عدد النقاط", ascending=False)
                                         fig_program_points = px.pie(
                                             program_points, values="عدد النقاط", names="البرنامج",
                                             color_discrete_sequence=px.colors.qualitative.Pastel, hole=0.3
                                         )
                                         fig_program_points = prepare_chart_layout(fig_program_points, f"توزيع نقاط {selected_member_to_display} حسب البرنامج", is_mobile=mobile_view, chart_type="pie")
                                         st.plotly_chart(fig_program_points, use_container_width=True, config={"displayModeBar": False})
                                     # else: # لا داعي لرسالة هنا

                            with member_charts_cols[1]: # العمود الأصغر للجدول والمهام
                                # عرض جدول تفصيلي للفئات ومستويات الإنجاز
                                 if not category_points.empty:
                                     st.markdown("##### تفاصيل الفئات والمستويات")
                                     st.markdown("""
                                     <style>
                                         .achievements-table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 0.9rem; }
                                         .achievements-table th, .achievements-table td { border: 1px solid #ddd; padding: 8px; text-align: right; }
                                         .achievements-table th { background-color: #f2f2f2; font-weight: bold; }
                                         .achievements-table tr:nth-child(even){background-color: #f9f9f9;}
                                         .achievements-table tr:hover {background-color: #e9e9e9;}
                                     </style>
                                     <table class="achievements-table">
                                         <tr><th>الفئة</th><th>النقاط</th><th>المستوى</th></tr>
                                     """, unsafe_allow_html=True)
                                     for _, row in category_points.sort_values("عدد النقاط", ascending=False).iterrows():
                                         st.markdown(f"""
                                         <tr>
                                             <td>{row["الفئة"]}</td>
                                             <td>{int(row["عدد النقاط"])}</td>
                                             <td style="color: {row['لون_المستوى']}; font-weight: 500;">{row['أيقونة_المستوى']} {row['مستوى']}</td>
                                         </tr>
                                         """, unsafe_allow_html=True)
                                     st.markdown("</table>", unsafe_allow_html=True)


                                 # عرض قائمة آخر 5 مهام للعضو
                                 st.markdown("#### آخر مهام العضو (آخر 5)")
                                 if "التاريخ" in member_data.columns and pd.api.types.is_datetime64_any_dtype(member_data['التاريخ']):
                                     latest_tasks = member_data.sort_values("التاريخ", ascending=False).head(5)
                                     if not latest_tasks.empty:
                                         for _, task in latest_tasks.iterrows():
                                             task_title = task.get("عنوان المهمة", "مهمة غير محددة")
                                             task_desc = task.get("وصف مختصر", "")
                                             task_date = task.get("التاريخ", None)
                                             task_points = float(task.get("عدد النقاط", 0))
                                             task_hours = float(task.get("عدد الساعات", 0))
                                             task_category = task.get("الفئة", "غير مصنفة")
                                             task_program = task.get("البرنامج", "غير محدد")
                                             formatted_date = task_date.strftime("%Y/%m/%d") if pd.notna(task_date) else "غير محدد"
                                             st.markdown(f"""
                                             <div class="task-card completed" style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 12px; margin-bottom: 10px; background-color: #fff;">
                                                 <div class="task-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                                                     <div class="task-title" style="font-weight: 600; color: #333;">{task_title}</div>
                                                 </div>
                                                 {f'<div style="font-size: 0.85rem; margin-bottom: 8px; color: #666;">{task_desc}</div>' if task_desc else ''}
                                                 <div class="task-details" style="font-size: 0.8rem; color: #777; margin-bottom: 8px; display: flex; flex-wrap: wrap; gap: 10px;">
                                                     <span class="task-detail-item">📅 {formatted_date}</span>
                                                     <span class="task-detail-item">🏷️ {task_category}</span>
                                                     <span class="task-detail-item">📚 {task_program}</span>
                                                 </div>
                                                 <div class="task-metrics" style="display: flex; gap: 15px; justify-content: flex-end;">
                                                     <div class="task-metric" style="text-align: center;">
                                                         <div class="task-metric-value" style="font-weight: bold; color: #1e88e5;">{int(task_points)}</div>
                                                         <div class="task-metric-label" style="font-size: 0.75rem;">النقاط</div>
                                                     </div>
                                                     <div class="task-metric" style="text-align: center;">
                                                         <div class="task-metric-value" style="font-weight: bold; color: #F39C12;">{int(task_hours)}</div>
                                                         <div class="task-metric-label" style="font-size: 0.75rem;">الساعات</div>
                                                     </div>
                                                 </div>
                                             </div>
                                             """, unsafe_allow_html=True)
                                     else:
                                         st.info(f"لا توجد مهام مسجلة للعضو {selected_member_to_display} في الفترة المحددة.")
                                 else:
                                     st.warning("لا يمكن عرض آخر المهام لعدم وجود عمود تاريخ صالح.")

                        else:
                             # هذه الحالة تحدث إذا تم اختيار عضو لم يعد موجودًا في filtered_members_df بعد تغيير الفلاتر
                             st.warning(f"العضو المحدد '{selected_member_to_display}' لا يطابق الفلاتر الحالية.")


                    else:
                        # هذه الحالة تحدث إذا كانت member_data فارغة للعضو المحدد
                        st.warning(f"لم يتم العثور على بيانات إنجازات للعضو المحدد '{selected_member_to_display}' في الفترة الزمنية المحددة.")

            # --- نهاية قسم عرض التفاصيل ---

            else:
                 # إذا لم يتم اختيار عضو (القيمة هي "اختر عضوًا...")
                 st.info("يرجى اختيار عضو من القائمة أعلاه لعرض تفاصيله.")


        else:
            # هذه الحالة تحدث إذا كانت member_stats فارغة بعد الدمج الأولي
            st.info("لا توجد إحصائيات متاحة للأعضاء في الفترة الزمنية المحددة.")

    else:
        # هذه الحالة تحدث إذا كانت members_filtered_data فارغة من البداية أو تفتقد للأعمدة الأساسية
        st.info("لا توجد بيانات كافية لإظهار إنجازات الأعضاء للفترة الزمنية المحددة.")


# --- دالة مساعدة لإنشاء بطاقات المقاييس ---
def create_metric_card(value, label, color):
    """ينشئ كود HTML لبطاقة مقياس."""
    # تحديد لون الخلفية بناءً على لون النص الرئيسي لمزيد من التباين
    bg_color_map = {
        "#1e88e5": "#e3f2fd", # أزرق -> سماوي فاتح
        "#27AE60": "#e8f5e9", # أخضر -> أخضر فاتح
        "#F39C12": "#fff3e0"  # برتقالي -> برتقالي فاتح
    }
    bg_color = bg_color_map.get(color, "#f8f9fa") # لون افتراضي
    return f"""
    <div style="flex: 1; min-width: 120px; text-align: center; background-color: {bg_color}; padding: 15px; border-radius: 8px;">
        <div style="font-size: 2rem; font-weight: bold; color: {color}; line-height: 1.2;">{value}</div>
        <div style="font-size: 0.9rem; color: #555; margin-top: 5px;">{label}</div>
    </div>
    """
# =========================================
# القسم 15: تبويب قائمة المهام
# =========================================
with main_tabs[2]:
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

# نصائح الاستخدام وتذييل الصفحة
# =========================================
with st.expander("💡 نصائح للاستخدام", expanded=False):
    st.markdown("""
    - **تصفية زمنية:** يمكنك اختيار نطاق زمني لعرض البيانات ضمن فترة محددة.
    - **توزيعات المهام:** تعرض تحليلات وإحصاءات عن توزيع المهام حسب الفئة والبرنامج والمهمة الرئيسية.
    - **إنجازات الأعضاء:** تعرض معلومات عن إنجازات الأعضاء ومستوياتهم، وتتيح استكشاف إنجازات عضو محدد.
    - **نجم الشهر:** يعرض العضو الأكثر نقاطًا في الشهر الحالي.
    - **قادة الفئات:** تعرض الأعضاء الأكثر نقاطًا في كل فئة.
    - **قائمة المهام:** تتيح تصفية وبحث المهام حسب معايير متعددة.
    - **الرسوم البيانية تفاعلية:** مرر الفأرة فوقها لرؤية التفاصيل.
    - **للعودة إلى أعلى الصفحة:** انقر على زر السهم ↑ في أسفل يسار الشاشة.
    """, unsafe_allow_html=True)

# --- إضافة نص تذييل الصفحة ---
st.markdown("""
<div style="margin-top: 50px; text-align: center; color: #888; font-size: 0.75em;">
    © قسم القراءات - جامعة الطائف {0}
</div>
""".format(datetime.now().year), unsafe_allow_html=True)
