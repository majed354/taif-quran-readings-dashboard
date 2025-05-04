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
# يجب أن يكون هذا الأمر هو أول أمر Streamlit في السكربت إذا لم يكن كذلك بالفعل
st.set_page_config(
    page_title="إنجاز المهام | قسم القراءات",
    page_icon="🏆",
    layout="wide"
)

# =========================================
# القسم 2: تنسيقات CSS للقائمة والصفحة
# =========================================
# ملاحظة: هذا القسم يحتوي على كتلة CSS كبيرة.
# لتحسين الصيانة بشكل أكبر، يمكن وضع هذا الكود في ملف CSS منفصل وتحميله.
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

# تطبيق CSS و HTML و JS على الصفحة
st.markdown(responsive_menu_css, unsafe_allow_html=True)
st.markdown(responsive_menu_html, unsafe_allow_html=True)
st.markdown(responsive_menu_js, unsafe_allow_html=True)

# --- العنوان الرئيسي للصفحة ---
st.markdown("<h1>🏆 إنجاز المهام</h1>", unsafe_allow_html=True)


# =========================================
# القسم 5: الدوال المساعدة العامة
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
# هذا القسم موجود بالفعل كقسم فرعي وهو منظم بشكل جيد.

def get_achievement_level(points):
    """تحديد مستوى الإنجاز الإجمالي بناءً على عدد النقاط"""
    # التأكد من أن النقاط رقمية قبل المقارنة
    try:
        points = float(points)
    except (ValueError, TypeError):
        points = 0 # قيمة افتراضية أو معالجة أخرى للخطأ

    if points < 50:
        return {"name": "مبتدئ", "color": "#95A5A6", "icon": "🔘"} # رمادي للمبتدئين
    
    # تأكد من أن ACHIEVEMENT_LEVELS معرفة قبل هذه النقطة (عادة في القسم 6)
    if 'ACHIEVEMENT_LEVELS' not in globals():
         st.error("ACHIEVEMENT_LEVELS is not defined.")
         return {"name": "خطأ", "color": "#FF0000", "icon": "❌"}

    for level in ACHIEVEMENT_LEVELS:
        if level["min"] <= points <= level["max"]:
            return level
    
    # في حالة عدم توافق مع أي نطاق (وهذا غير متوقع بسبب المستوى الأخير الذي يصل إلى inf)
    return ACHIEVEMENT_LEVELS[-1]  # إرجاع أعلى مستوى

def get_category_achievement_level(points):
    """تحديد مستوى الإنجاز لفئة معينة بناءً على عدد النقاط"""
    # التأكد من أن النقاط رقمية قبل المقارنة
    try:
        points = float(points)
    except (ValueError, TypeError):
        points = 0

    # تأكد من أن CATEGORY_ACHIEVEMENT_LEVELS معرفة قبل هذه النقطة (عادة في القسم 6)
    if 'CATEGORY_ACHIEVEMENT_LEVELS' not in globals():
         st.error("CATEGORY_ACHIEVEMENT_LEVELS is not defined.")
         return {"name": "خطأ", "color": "#FF0000", "icon": "❌"}

    for level in CATEGORY_ACHIEVEMENT_LEVELS:
        if level["min"] <= points <= level["max"]:
            return level
    
    # في حالة عدم توافق مع أي نطاق (وهذا غير متوقع بسبب المستوى الأخير الذي يصل إلى inf)
    return CATEGORY_ACHIEVEMENT_LEVELS[-1]  # إرجاع أعلى مستوى

def calculate_points_by_category(achievements_df, member_name):
    """حساب نقاط العضو في كل فئة ومستوى الإنجاز لكل فئة"""
    if achievements_df.empty or "اسم العضو" not in achievements_df.columns or "الفئة" not in achievements_df.columns or "عدد النقاط" not in achievements_df.columns:
        return pd.DataFrame()
        
    member_achievements = achievements_df[achievements_df["اسم العضو"] == member_name].copy() # Use .copy()
    if member_achievements.empty:
        return pd.DataFrame()
    
    # استبعاد السجلات بدون فئة أو ذات فئة فارغة
    member_achievements = member_achievements[member_achievements["الفئة"].notna() & (member_achievements["الفئة"] != "")]
    
    if member_achievements.empty:
        return pd.DataFrame()
        
    # تأكد من أن 'عدد النقاط' رقمي
    member_achievements['عدد النقاط'] = pd.to_numeric(member_achievements['عدد النقاط'], errors='coerce')
    member_achievements = member_achievements.dropna(subset=['عدد النقاط'])
    
    if member_achievements.empty:
        return pd.DataFrame()
        
    # مجموع النقاط حسب الفئة
    category_points = member_achievements.groupby("الفئة")["عدد النقاط"].sum().reset_index()
    
    # إضافة مستوى الإنجاز الإجمالي لكل فئة
    category_points["مستوى_الإنجاز"] = category_points["عدد النقاط"].apply(get_achievement_level)
    category_points["مستوى"] = category_points["مستوى_الإنجاز"].apply(lambda x: x["name"])
    category_points["لون_المستوى"] = category_points["مستوى_الإنجاز"].apply(lambda x: x["color"])
    category_points["أيقونة_المستوى"] = category_points["مستوى_الإنجاز"].apply(lambda x: x["icon"])
    
    # إضافة مستوى الإنجاز الخاص بالفئة
    category_points["مستوى_الفئة"] = category_points["عدد النقاط"].apply(get_category_achievement_level)
    category_points["مستوى_فئة"] = category_points["مستوى_الفئة"].apply(lambda x: x["name"])
    category_points["لون_مستوى_فئة"] = category_points["مستوى_الفئة"].apply(lambda x: x["color"])
    category_points["أيقونة_مستوى_فئة"] = category_points["مستوى_الفئة"].apply(lambda x: x["icon"])
    
    return category_points

def create_radar_chart(category_points_df, member_name, is_mobile=False):
    """إنشاء مخطط عنكبوتي/رادار لتوزيع نقاط العضو حسب الفئات"""
    if category_points_df.empty:
        return None
    
    # التأكد من وجود الأعمدة المطلوبة
    required_cols = ["الفئة", "عدد النقاط", "لون_مستوى_فئة", "مستوى_فئة"]
    if not all(col in category_points_df.columns for col in required_cols):
        st.error("DataFrame للمخطط الراداري يفتقد لأعمدة مطلوبة.")
        return None
    
    # تحديد الألوان بناءً على مستويات الإنجاز
    colors = category_points_df["لون_مستوى_فئة"].tolist()  # استخدام ألوان مستوى الفئة
    
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
            marker=dict(size=10, color=row["لون_مستوى_فئة"]),  # استخدام لون مستوى الفئة
            name=f"{row['الفئة']}: {row['مستوى_فئة']}",  # استخدام مستوى الفئة
            hoverinfo="text",
            hovertext=f"{row['الفئة']}<br>النقاط: {int(row['عدد النقاط'])}<br>المستوى: {row['مستوى_فئة']}"
        ))
    
    # تنسيق المخطط
    title_size = 12 if is_mobile else 16
    font_size = 8 if is_mobile else 10
    
    # التأكد من وجود نقاط قبل حساب الحد الأقصى
    max_points = category_points_df["عدد النقاط"].max() if not category_points_df["عدد النقاط"].empty else 10
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                showticklabels=True,
                tickfont=dict(size=font_size),
                range=[0, max_points * 1.2] # حساب النطاق ديناميكيًا
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

def get_category_leaders(achievements_df):
    """تحديد الأعضاء الأكثر نقاطًا في كل فئة"""
    # ملاحظة: هذه هي النسخة الأولى من الدالة كما في القسم 5.1 الأصلي
    if achievements_df.empty or "اسم العضو" not in achievements_df.columns or "الفئة" not in achievements_df.columns or "عدد النقاط" not in achievements_df.columns:
        return {}
    
    # استبعاد السجلات بدون فئة أو ذات فئة فارغة
    filtered_df = achievements_df[achievements_df["الفئة"].notna() & (achievements_df["الفئة"] != "")]
    
    if filtered_df.empty:
        return {}
        
    # تأكد من أن 'عدد النقاط' رقمي
    filtered_df['عدد النقاط'] = pd.to_numeric(filtered_df['عدد النقاط'], errors='coerce')
    filtered_df = filtered_df.dropna(subset=['عدد النقاط'])
    
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
            # حساب مستوى الفئة
            category_level = get_category_achievement_level(top_member["عدد النقاط"])
            top_members[category] = {
                "اسم": top_member["اسم العضو"],
                "النقاط": top_member["عدد النقاط"],
                "مستوى_الفئة": category_level # إضافة مستوى الفئة
            }
    
    return top_members

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

# تعريف مستويات الإنجاز حسب النقاط الإجمالية
ACHIEVEMENT_LEVELS = [
    {"name": "مساهم", "min": 50, "max": 200, "color": "#5DADE2", "icon": "🔹"},  # أزرق فاتح
    {"name": "نشيط", "min": 201, "max": 400, "color": "#3498DB", "icon": "🔷"},  # أزرق
    {"name": "فعّال", "min": 401, "max": 600, "color": "#27AE60", "icon": "🌟"},  # أخضر
    {"name": "متميز", "min": 601, "max": 800, "color": "#F39C12", "icon": "✨"},   # برتقالي
    {"name": "استثنائي", "min": 801, "max": float('inf'), "color": "#E74C3C", "icon": "🏆"}, # أحمر
]

# تعريف مستويات الإنجاز حسب نقاط الفئة الواحدة
CATEGORY_ACHIEVEMENT_LEVELS = [
    {"name": "مبتدئ", "min": 0, "max": 200, "color": "#5DADE2", "icon": "🔹"},  # أزرق فاتح
    {"name": "ممارس", "min": 201, "max": 400, "color": "#3498DB", "icon": "🔷"},  # أزرق
    {"name": "متقدم", "min": 401, "max": 600, "color": "#27AE60", "icon": "🌟"},  # أخضر
    {"name": "خبير", "min": 601, "max": float('inf'), "color": "#F39C12", "icon": "✨"},   # برتقالي
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
    "البرنامج",
    # تمت إضافة عمود التاريخ المعالج لاحقًا في الدوال
    # "التاريخ"
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
                # استخدام errors='coerce' لتحويل القيم غير الصالحة إلى NaT
                df["التاريخ"] = pd.to_datetime(df["تاريخ الإنجاز"], errors='coerce')
                # إزالة الصفوف التي فشل تحويل تاريخها (اختياري لكن يفضل)
                # df = df.dropna(subset=["التاريخ"])
            else:
                 # إذا لم يكن عمود التاريخ موجودًا، قم بإنشائه بقيم فارغة لتجنب أخطاء لاحقة
                 df["التاريخ"] = pd.NaT

            # إذا كان تم تحديد سنة، قم بتصفية البيانات
            # تأكد من وجود عمود 'التاريخ' وأنه من نوع datetime قبل التصفية
            if year is not None and "التاريخ" in df.columns and pd.api.types.is_datetime64_any_dtype(df['التاريخ']):
                 # تجاهل القيم NaT عند التصفية
                df = df[df["التاريخ"].dt.year == year]
                
            # ضمان وجود جميع الأعمدة المتوقعة وملء القيم المفقودة إذا لزم الأمر
            for col in EXPECTED_ACHIEVEMENT_COLS:
                if col not in df.columns:
                    # تحديد نوع البيانات المناسب أو تركه كـ object
                    if col in ["عدد الساعات", "عدد النقاط"]:
                         df[col] = 0.0 # أو np.nan إذا كنت تفضل
                    else:
                         df[col] = "" # أو np.nan

            # تحويل الأعمدة الرقمية إلى رقمية، معالجة الأخطاء
            if "عدد الساعات" in df.columns:
                df["عدد الساعات"] = pd.to_numeric(df["عدد الساعات"], errors='coerce').fillna(0)
            if "عدد النقاط" in df.columns:
                df["عدد النقاط"] = pd.to_numeric(df["عدد النقاط"], errors='coerce').fillna(0)

            return df
        else:
            # إذا لم يكن الملف موجودًا، عرض تنبيه وإعادة DataFrame فارغ
            st.warning(f"ملف بيانات الإنجازات غير موجود أو فارغ في المسار: {ACHIEVEMENTS_DATA_PATH}")
            # إنشاء DataFrame فارغ بالأعمدة المتوقعة وأنواع بيانات مناسبة
            empty_df = pd.DataFrame(columns=EXPECTED_ACHIEVEMENT_COLS + ["التاريخ"])
            empty_df['التاريخ'] = pd.to_datetime(empty_df['التاريخ'])
            empty_df['عدد الساعات'] = pd.to_numeric(empty_df['عدد الساعات'])
            empty_df['عدد النقاط'] = pd.to_numeric(empty_df['عدد النقاط'])
            return empty_df
            
    except Exception as e:
        st.error(f"خطأ في تحميل بيانات الإنجازات: {e}")
        # إنشاء DataFrame فارغ بالأعمدة المتوقعة وأنواع بيانات مناسبة
        empty_df = pd.DataFrame(columns=EXPECTED_ACHIEVEMENT_COLS + ["التاريخ"])
        empty_df['التاريخ'] = pd.to_datetime(empty_df['التاريخ'])
        empty_df['عدد الساعات'] = pd.to_numeric(empty_df['عدد الساعات'])
        empty_df['عدد النقاط'] = pd.to_numeric(empty_df['عدد النقاط'])
        return empty_df

@st.cache_data(ttl=3600)
def get_member_list(achievements_df):
    """استخراج قائمة أعضاء هيئة التدريس من بيانات الإنجازات"""
    # قائمة الأعضاء الفعلية في القسم (احتياطية)
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
        # إزالة القيم الفارغة (NaN, None, '') قبل استخراج الفريد والفرز
        members = sorted(achievements_df["اسم العضو"].dropna().astype(str).unique())
        # إزالة السلاسل النصية الفارغة بعد التحويل إلى نص
        members = [m for m in members if m and m.strip()]
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
    
    # تأكد أن عمود التاريخ موجود وأنه datetime
    if not achievements_df.empty and "التاريخ" in achievements_df.columns and pd.api.types.is_datetime64_any_dtype(achievements_df['التاريخ']):
        # إزالة القيم NaT قبل استخراج السنة
        years = sorted(achievements_df["التاريخ"].dropna().dt.year.unique(), reverse=True)
        # تحويل السنوات إلى int للتأكد
        years = [int(y) for y in years]
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
        # إزالة القيم الفارغة (NaN, None, '') قبل استخراج الفريد والفرز
        main_tasks = sorted(achievements_df["المهمة الرئيسية"].dropna().astype(str).unique())
        # إزالة السلاسل النصية الفارغة بعد التحويل إلى نص وإزالة الفراغات الزائدة
        main_tasks = [task.strip() for task in main_tasks if task and task.strip()]
        if main_tasks:
            # التأكد من عدم إضافة placeholder إذا كان موجودًا بالفعل
            if "— بدون مهمة رئيسية —" not in main_tasks:
                 return ["— بدون مهمة رئيسية —"] + main_tasks
            else:
                 # إذا كان موجودًا، تأكد من أنه الأول
                 main_tasks.remove("— بدون مهمة رئيسية —")
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
    current_time = datetime.now()
    if year is None:
        year = current_time.year
    if month is None:
        month = current_time.month
    
    # فلترة البيانات حسب السنة والشهر
    filtered_df = achievements_df.copy()
    # التأكد من وجود عمود التاريخ وأنه datetime
    if "التاريخ" in filtered_df.columns and pd.api.types.is_datetime64_any_dtype(filtered_df['التاريخ']):
        # تجاهل NaT عند الفلترة
        filtered_df = filtered_df[
            (filtered_df["التاريخ"].dt.year == year) & 
            (filtered_df["التاريخ"].dt.month == month)
        ]
    else:
         # إذا لم يكن التاريخ صالحًا، لا يمكن تحديد نجم الشهر
         return None
    
    if filtered_df.empty:
        return None
    
    # التأكد من أن 'عدد النقاط' و 'عدد الساعات' رقمية قبل التجميع
    filtered_df['عدد النقاط'] = pd.to_numeric(filtered_df['عدد النقاط'], errors='coerce').fillna(0)
    filtered_df['عدد الساعات'] = pd.to_numeric(filtered_df['عدد الساعات'], errors='coerce').fillna(0)

    # حساب مجموع النقاط لكل عضو
    member_points = filtered_df.groupby("اسم العضو")["عدد النقاط"].sum().reset_index()
    
    if member_points.empty:
        return None
    
    # تحديد العضو الأكثر نقاطًا
    top_member = member_points.loc[member_points["عدد النقاط"].idxmax()]

    # التحقق مما إذا كان هناك نقاط بالفعل (أكبر من صفر)
    if top_member["عدد النقاط"] <= 0:
        return None # لا يوجد نجم إذا لم يحقق أحد نقاطًا

    # حساب إجمالي الساعات وعدد المهام للعضو الأكثر نقاطًا
    member_data = filtered_df[filtered_df["اسم العضو"] == top_member["اسم العضو"]]
    total_hours = member_data["عدد الساعات"].sum()
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
    # ملاحظة: هذه هي النسخة الثانية من الدالة كما في القسم 8 الأصلي.
    # هي أبسط من النسخة في 5.1 لأنها لا تحسب المستويات.
    # قد يكون هذا تكرارًا غير مقصود في الكود الأصلي.
    if achievements_df.empty or "اسم العضو" not in achievements_df.columns or "الفئة" not in achievements_df.columns or "عدد النقاط" not in achievements_df.columns:
        return {}
    
    # استبعاد السجلات بدون فئة أو ذات فئة فارغة
    filtered_df = achievements_df[achievements_df["الفئة"].notna() & (achievements_df["الفئة"] != "")]
    
    if filtered_df.empty:
        return {}
    
    # تأكد من أن 'عدد النقاط' رقمي
    filtered_df['عدد النقاط'] = pd.to_numeric(filtered_df['عدد النقاط'], errors='coerce')
    filtered_df = filtered_df.dropna(subset=['عدد النقاط'])
    
    if filtered_df.empty:
        return {}

    # حساب مجموع النقاط لكل عضو في كل فئة
    category_data = filtered_df.groupby(["الفئة", "اسم العضو"])["عدد النقاط"].sum().reset_index()
    
    # تحديد العضو الأكثر نقاطًا في كل فئة
    top_members = {}
    for category in category_data["الفئة"].unique():
        category_members = category_data[category_data["الفئة"] == category]
        if not category_members.empty:
            # الحصول على الصف الذي يحتوي على أقصى عدد نقاط
            top_member_row = category_members.loc[category_members["عدد النقاط"].idxmax()]
            # التأكد من أن النقاط أكبر من صفر
            if top_member_row["عدد النقاط"] > 0:
                 top_members[category] = {
                     "اسم": top_member_row["اسم العضو"],
                     "النقاط": top_member_row["عدد النقاط"]
                 }
    
    return top_members

def detect_member_promotions(achievements_df, lookback_days=30):
    """اكتشاف الأعضاء الذين ترقوا إلى مستويات أعلى في الفترة الأخيرة"""
    if achievements_df.empty or "اسم العضو" not in achievements_df.columns or "عدد النقاط" not in achievements_df.columns:
        return []
        
    # التأكد من وجود عمود التاريخ وأنه datetime
    if "التاريخ" not in achievements_df.columns or not pd.api.types.is_datetime64_any_dtype(achievements_df['التاريخ']):
        st.warning("لا يمكن اكتشاف الترقيات لعدم وجود عمود تاريخ صالح.")
        return []
        
    # التأكد من أن النقاط رقمية
    achievements_df['عدد النقاط'] = pd.to_numeric(achievements_df['عدد النقاط'], errors='coerce').fillna(0)

    # تحديد نطاق زمني للبحث عن الترقيات (مثلاً، آخر 30 يومًا)
    current_date = datetime.now()
    lookback_date = current_date - timedelta(days=lookback_days)
    
    # تجاهل NaT عند التقسيم
    recent_df = achievements_df[achievements_df["التاريخ"] >= lookback_date].copy()
    older_df = achievements_df[achievements_df["التاريخ"] < lookback_date].copy()
    
    # لا يمكن اكتشاف ترقيات إذا لم تكن هناك بيانات قديمة للمقارنة
    if older_df.empty:
        return []
    
    # حساب مجموع النقاط لكل عضو قبل وبعد تاريخ البحث
    recent_points = recent_df.groupby("اسم العضو")["عدد النقاط"].sum().to_dict()
    older_total_points = older_df.groupby("اسم العضو")["عدد النقاط"].sum().to_dict()
    
    # حساب مجموع النقاط الكلي الحالي لكل الأعضاء
    all_points_total = achievements_df.groupby("اسم العضو")["عدد النقاط"].sum().to_dict()
    
    # البحث عن الترقيات
    promotions = []
    
    # المرور على كل الأعضاء الذين لديهم نقاط (قديمة أو حديثة)
    all_members = set(older_total_points.keys()) | set(recent_points.keys())
    
    for member in all_members:
        old_points = older_total_points.get(member, 0)
        current_total_points = all_points_total.get(member, 0) # استخدام الإجمالي الحالي
        gained_points = recent_points.get(member, 0) # النقاط المكتسبة في الفترة الأخيرة
        
        # تحديد المستوى القديم والجديد
        old_level = get_achievement_level(old_points)
        new_level = get_achievement_level(current_total_points)
        
        # إذا كان هناك ترقية (المستوى تغير ولم يعد مبتدئًا)
        # وأيضًا تأكد من أن هناك نقاط مكتسبة مؤخرًا لمنع ترقية أعضاء قدامى لم يسجلوا شيئًا مؤخرًا
        if old_level["name"] != new_level["name"] and new_level["name"] != "مبتدئ" and gained_points > 0:
            promotions.append({
                "اسم": member,
                "المستوى_السابق": old_level["name"],
                "المستوى_الجديد": new_level["name"],
                "النقاط_السابقة": old_points,
                "النقاط_الجديدة": current_total_points, # النقاط الكلية الحالية
                "النقاط_المكتسبة": gained_points, # النقاط المكتسبة في الفترة الأخيرة
                "لون_المستوى": new_level["color"],
                "أيقونة_المستوى": new_level["icon"]
            })
    
    # ترتيب الترقيات حسب المستوى الجديد (الأعلى أولاً)، ثم حسب النقاط المكتسبة
    # تأكد من أن ACHIEVEMENT_LEVELS معرفة
    if 'ACHIEVEMENT_LEVELS' in globals():
        level_rank = {level["name"]: i for i, level in enumerate(reversed(ACHIEVEMENT_LEVELS + [{"name": "مبتدئ"}]))}
        promotions.sort(key=lambda x: (level_rank.get(x["المستوى_الجديد"], -1), x["النقاط_المكتسبة"]), reverse=True)
    else:
        # ترتيب بسيط إذا كانت المستويات غير معرفة
         promotions.sort(key=lambda x: x["النقاط_المكتسبة"], reverse=True)

    
    return promotions


# =========================================
# القسم 9: تحميل البيانات الأولية وتهيئة حالة الجلسة
# =========================================
# تحديد ما إذا كان العرض للجوال (استخدم الدالة من القسم 5)
mobile_view = is_mobile()

# تحميل بيانات الإنجازات باستخدام الدالة من القسم 7
# يتم تمرير None لتحميل كل السنوات في البداية
achievements_data = load_achievements_data()

# استخراج قوائم الاختيارات باستخدام الدوال من القسم 7
available_years = get_available_years(achievements_data)
members_list = get_member_list(achievements_data)
main_tasks_list = get_main_tasks_list(achievements_data) # لاحظ أن هذه الدالة تضيف "-- بدون مهمة رئيسية --"

# تهيئة متغيرات الجلسة لحالة التصفية إن لم تكن موجودة
if "time_filter" not in st.session_state:
    # استخدام TIME_FILTER_OPTIONS من القسم 6
    st.session_state.time_filter = TIME_FILTER_OPTIONS[0] # "جميع المهام"
if "selected_member" not in st.session_state:
    st.session_state.selected_member = "الكل"
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "الكل"
if "selected_program" not in st.session_state:
    st.session_state.selected_program = "الكل"
if "selected_main_task" not in st.session_state:
    # القيمة الأولية يجب أن تكون "الكل" لتطابق الخيارات المتاحة في الواجهة
    st.session_state.selected_main_task = "الكل"
if "selected_year" not in st.session_state:
    # استخدام available_years المستخرجة أعلاه
    st.session_state.selected_year = available_years[0] if available_years else datetime.now().year
# متغير لحفظ العضو المختار لعرض التفاصيل في تبويب إنجازات الأعضاء
if "selected_member_detail" not in st.session_state:
    st.session_state.selected_member_detail = None # لا يوجد عضو محدد افتراضيًا

# =========================================
# القسم 10: حساب المؤشرات الرئيسية الإجمالية الأولية
# =========================================
# حساب المؤشرات الرئيسية من البيانات الكاملة المحملة (achievements_data)
total_tasks_overall = 0
total_members_overall = len(members_list) if members_list else 0
active_members_overall = 0
total_points_overall = 0
total_hours_overall = 0
member_achievements_summary = None

if not achievements_data.empty:
    total_tasks_overall = len(achievements_data)

    # التأكد من أن الأعمدة رقمية قبل الحساب
    if "عدد النقاط" in achievements_data.columns:
        # تحويل إلى رقمي وتجاهل الأخطاء وملء NaN بـ 0
        total_points_overall = pd.to_numeric(achievements_data["عدد النقاط"], errors='coerce').fillna(0).sum()
    
    if "عدد الساعات" in achievements_data.columns:
        total_hours_overall = pd.to_numeric(achievements_data["عدد الساعات"], errors='coerce').fillna(0).sum()

    # حساب المؤشرات المتعلقة بالأعضاء النشطين
    if "اسم العضو" in achievements_data.columns:
        # إزالة الأعضاء الفارغين قبل التجميع
        valid_members_df = achievements_data.dropna(subset=['اسم العضو'])
        valid_members_df = valid_members_df[valid_members_df['اسم العضو'] != '']
        
        if not valid_members_df.empty:
            # حساب عدد الأعضاء الفريدين الذين لديهم إنجازات
            active_members_overall = valid_members_df["اسم العضو"].nunique()

            # تجميع بيانات الأعضاء (النقاط، الساعات، عدد المهام)
            # التأكد من أن الأعمدة رقمية
            valid_members_df['عدد النقاط'] = pd.to_numeric(valid_members_df['عدد النقاط'], errors='coerce').fillna(0)
            valid_members_df['عدد الساعات'] = pd.to_numeric(valid_members_df['عدد الساعات'], errors='coerce').fillna(0)

            member_achievements_summary = valid_members_df.groupby("اسم العضو").agg(
                عدد_الإنجازات=('اسم العضو', 'size'),
                مجموع_النقاط=('عدد النقاط', 'sum'),
                مجموع_الساعات=('عدد الساعات', 'sum')
            ).reset_index()
        else:
            active_members_overall = 0 # لا يوجد أعضاء صالحون
            member_achievements_summary = pd.DataFrame(columns=["اسم العضو", "عدد_الإنجازات", "مجموع_النقاط", "مجموع_الساعات"])

else:
    # حالة عدم وجود بيانات على الإطلاق
    total_tasks_overall = 0
    total_members_overall = len(members_list) # قد يكون هناك أعضاء افتراضيون
    active_members_overall = 0
    total_points_overall = 0
    total_hours_overall = 0
    member_achievements_summary = pd.DataFrame(columns=["اسم العضو", "عدد_الإنجازات", "مجموع_النقاط", "مجموع_الساعات"])


# حساب الإنجازات في الشهر الحالي (كمثال لمؤشر إضافي قد تحتاجه لاحقًا)
current_month_achievements_count = 0
# التأكد من أن التاريخ صالح قبل الفلترة
if not achievements_data.empty and "التاريخ" in achievements_data.columns and pd.api.types.is_datetime64_any_dtype(achievements_data['التاريخ']):
    current_date = datetime.now()
    # إنشاء قناع للقيم غير الفارغة والتاريخ ضمن الشهر الحالي
    current_month_mask = (achievements_data["التاريخ"].notna()) & \
                         (achievements_data["التاريخ"].dt.year == current_date.year) & \
                         (achievements_data["التاريخ"].dt.month == current_date.month)
    current_month_achievements_count = achievements_data[current_month_mask].shape[0]

# ملاحظة: المؤشرات المحسوبة هنا (مثل total_points_overall) هي للإجمالي العام.
# سيتم استخدامها أو إعادة حسابها لاحقًا عند عرض المقاييس أو التصفية.

# -*- coding: utf-8 -*-

# ... (الكود من القسم 1 إلى 10 يجب أن يكون هنا) ...

# =========================================
# القسم 11: عرض المقاييس الإجمالية (للنظرة العامة)
# =========================================
st.subheader("نظرة عامة")

# استخدام المؤشرات الإجمالية المحسوبة في القسم 10
# total_tasks_overall, total_hours_overall, active_members_overall, total_members_overall

# حساب نسبة الأعضاء النشطين
active_percentage_overall = (active_members_overall / total_members_overall) * 100 if total_members_overall > 0 else 0

# تحديد العضو الأكثر نشاطًا (حسب الساعات) - يتطلب إعادة حساب بناءً على البيانات الكاملة
most_active_member_overall = None
if member_achievements_summary is not None and not member_achievements_summary.empty and "مجموع_الساعات" in member_achievements_summary.columns:
     # التأكد من أن هناك ساعات مسجلة
    if member_achievements_summary["مجموع_الساعات"].sum() > 0:
        # استخدام idxmax للحصول على index الصف صاحب القيمة القصوى ثم loc للوصول لبيانات الصف
        most_active_member_overall = member_achievements_summary.loc[member_achievements_summary["مجموع_الساعات"].idxmax()]["اسم العضو"]

# تحديد المهمة الأساسية الأكثر ساعات - يتطلب إعادة حساب بناءً على البيانات الكاملة
top_main_task_overall = None
if not achievements_data.empty and "المهمة الرئيسية" in achievements_data.columns and "عدد الساعات" in achievements_data.columns:
    # استبعاد القيم الفارغة وغير النصية في المهمة الرئيسية والساعات الصالحة
    task_data_overall = achievements_data[
        achievements_data["المهمة الرئيسية"].notna() &
        (achievements_data["المهمة الرئيسية"] != "") &
        pd.to_numeric(achievements_data["عدد الساعات"], errors='coerce').notna() &
        (pd.to_numeric(achievements_data["عدد الساعات"], errors='coerce') > 0) # فقط المهام التي لها ساعات
    ].copy() # استخدام .copy()

    if not task_data_overall.empty:
        # التأكد من أن عدد الساعات رقمي
        task_data_overall['عدد الساعات'] = pd.to_numeric(task_data_overall['عدد الساعات'], errors='coerce')
        main_task_hours_overall = task_data_overall.groupby("المهمة الرئيسية")["عدد الساعات"].sum()
        if not main_task_hours_overall.empty:
            top_main_task_overall = main_task_hours_overall.idxmax()

# عرض المقاييس في صف (أو أعمدة متتالية في الجوال)
# استخدام mobile_view المحدد في القسم 9
if mobile_view:
    # تقسيم إلى صفوف متعددة في الجوال لتحسين العرض
    row1_cols_overview = st.columns(2)
    row2_cols_overview = st.columns(2)
    row3_cols_overview = st.columns(1) # عنصر أخير في صف لوحده
    metric_cols_overview = [
        row1_cols_overview[0], row1_cols_overview[1],
        row2_cols_overview[0], row2_cols_overview[1],
        row3_cols_overview[0]
    ]
else:
    # عرض كأعمدة في صف واحد لسطح المكتب
    metric_cols_overview = st.columns(5)

# عرض المؤشرات الرئيسية الخمسة
with metric_cols_overview[0]:
    st.metric("إجمالي المهام", f"{total_tasks_overall:,}")

with metric_cols_overview[1]:
    st.metric("إجمالي الساعات", f"{total_hours_overall:,.0f}")

with metric_cols_overview[2]:
    st.metric(
        "الأعضاء النشطين",
        f"{active_members_overall:,} / {total_members_overall:,} ({active_percentage_overall:.0f}%)"
    )

with metric_cols_overview[3]:
    if most_active_member_overall:
        # اختصار الاسم إذا كان طويلاً جداً
        display_name_active = most_active_member_overall if len(most_active_member_overall) < 20 else most_active_member_overall[:18] + "..."
        st.metric("الأكثر نشاطًا", f"{display_name_active}", help=f"العضو الأكثر تسجيلاً للساعات: {most_active_member_overall}")
    else:
        st.metric("الأكثر نشاطًا", "-")

with metric_cols_overview[4]:
    if top_main_task_overall:
        # اختصار اسم المهمة إذا كان طويلاً
        display_name_task = top_main_task_overall if len(top_main_task_overall) < 20 else top_main_task_overall[:18] + "..."
        st.metric("المهمة الأكثر ساعات", f"{display_name_task}", help=f"المهمة الرئيسية الأكثر استهلاكًا للساعات: {top_main_task_overall}")
    else:
        st.metric("المهمة الأكثر ساعات", "-")


# =========================================
# القسم 12: إعداد التبويبات الرئيسية
# =========================================
# تأكد من أن أسماء التبويبات واضحة وتعكس المحتوى
main_tabs = st.tabs([
    "📊 توزيعات المهام",
    "👥 إنجازات الأعضاء",
    "📝 قائمة المهام التفصيلية"
 ])

# =========================================
# القسم 13: تبويب توزيعات المهام
# =========================================
with main_tabs[0]: # تبويب توزيعات المهام
    st.markdown("### 📊 توزيعات المهام")

    # تصفية زمنية خاصة بهذا التبويب
    st.markdown('<div class="time-filter" style="margin-bottom: 15px;">', unsafe_allow_html=True)
    st.markdown('<label class="time-filter-title" style="font-weight: 500; margin-left: 10px;">تصفية المهام في هذا التبويب حسب:</label>', unsafe_allow_html=True)
    # خيارات زمنية مناسبة للتوزيعات (قد تختلف عن الفلتر العام)
    distribution_time_options = ["الأسبوع الحالي", "الشهر الحالي", "الربع الحالي", "السنة الحالية", "كل الفترات"]
    selected_time_period_dist = st.radio(
        "", # لا حاجة لعنوان هنا
        options=distribution_time_options,
        horizontal=True,
        key="distribution_time_filter",
        label_visibility="collapsed" # إخفاء العنوان المتبقي
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # تطبيق الفلتر الزمني على نسخة محلية من البيانات لهذا التبويب
    filtered_dist_data = achievements_data.copy()

    # التأكد من أن عمود التاريخ موجود وصالح قبل الفلترة
    if "التاريخ" in filtered_dist_data.columns and pd.api.types.is_datetime64_any_dtype(filtered_dist_data['التاريخ']):
        filter_date_dist = None
        now_dist = datetime.now()

        if selected_time_period_dist == "الأسبوع الحالي":
             # بداية الأسبوع الحالي (لنفترض أنه الأحد)
             # Note: weekday() returns 0 for Monday, 6 for Sunday. Adjust if needed.
             # Assuming Sunday start:
             start_of_week = now_dist - timedelta(days=(now_dist.weekday() + 1) % 7)
             start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
             filter_date_dist = start_of_week
        elif selected_time_period_dist == "الشهر الحالي":
            start_of_month = now_dist.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            filter_date_dist = start_of_month
        elif selected_time_period_dist == "الربع الحالي":
            current_quarter = (now_dist.month - 1) // 3 + 1
            start_month_of_quarter = 3 * (current_quarter - 1) + 1
            start_of_quarter = now_dist.replace(month=start_month_of_quarter, day=1, hour=0, minute=0, second=0, microsecond=0)
            filter_date_dist = start_of_quarter
        elif selected_time_period_dist == "السنة الحالية":
            start_of_year = now_dist.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            filter_date_dist = start_of_year

        # تطبيق الفلتر فقط إذا تم تحديد فترة زمنية غير "كل الفترات"
        if filter_date_dist:
            # تجاهل NaT عند الفلترة
            filtered_dist_data = filtered_dist_data[filtered_dist_data["التاريخ"].notna() & (filtered_dist_data["التاريخ"] >= filter_date_dist)]

    else:
         # إذا لم يكن التاريخ صالحًا، قد نعرض رسالة أو نستخدم البيانات كاملة
         if selected_time_period_dist != "كل الفترات":
              st.warning("لا يمكن تطبيق الفلتر الزمني لعدم وجود عمود تاريخ صالح.")
              # قد ترغب في إفراغ البيانات هنا لمنع عرض نتائج غير صحيحة
              # filtered_dist_data = pd.DataFrame()


    # عرض التوزيعات المختلفة فقط إذا كانت هناك بيانات بعد الفلترة
    if not filtered_dist_data.empty:

        # --- 13.1: توزيع المهام حسب الفئة ---
        st.subheader("توزيع المهام حسب الفئة")
        if "الفئة" in filtered_dist_data.columns and "عدد النقاط" in filtered_dist_data.columns and "عدد الساعات" in filtered_dist_data.columns:
            # تجهيز البيانات: استبعاد الفئات الفارغة والتأكد من أن الأعمدة رقمية
            category_data_dist = filtered_dist_data[
                filtered_dist_data["الفئة"].notna() & (filtered_dist_data["الفئة"] != "")
            ].copy()
            category_data_dist['عدد النقاط'] = pd.to_numeric(category_data_dist['عدد النقاط'], errors='coerce').fillna(0)
            category_data_dist['عدد الساعات'] = pd.to_numeric(category_data_dist['عدد الساعات'], errors='coerce').fillna(0)

            if not category_data_dist.empty:
                # حساب الإحصاءات حسب الفئة
                category_stats_dist = category_data_dist.groupby("الفئة").agg(
                    عدد_المهام=('الفئة', 'size'),
                    مجموع_النقاط=('عدد النقاط', 'sum'),
                    مجموع_الساعات=('عدد الساعات', 'sum')
                ).reset_index()

                # ترتيب البيانات حسب عدد المهام تنازليًا
                category_stats_dist = category_stats_dist.sort_values("عدد_المهام", ascending=False)

                # تحضير مخططات العرض
                if mobile_view:
                    # مخطط 1: توزيع عدد المهام
                    fig_cat_tasks = px.pie(category_stats_dist, values="عدد_المهام", names="الفئة", title="عدد المهام حسب الفئة", color_discrete_sequence=px.colors.qualitative.Pastel)
                    fig_cat_tasks = prepare_chart_layout(fig_cat_tasks, "", is_mobile=mobile_view, chart_type="pie") # إزالة العنوان المكرر
                    st.plotly_chart(fig_cat_tasks, use_container_width=True, config={"displayModeBar": False})

                    # مخطط 2: توزيع النقاط
                    fig_cat_points = px.pie(category_stats_dist, values="مجموع_النقاط", names="الفئة", title="النقاط حسب الفئة", color_discrete_sequence=px.colors.qualitative.Pastel)
                    fig_cat_points = prepare_chart_layout(fig_cat_points, "", is_mobile=mobile_view, chart_type="pie")
                    st.plotly_chart(fig_cat_points, use_container_width=True, config={"displayModeBar": False})

                    # مخطط 3: توزيع الساعات (عمودي للجوال)
                    fig_cat_hours = px.bar(category_stats_dist, x="الفئة", y="مجموع_الساعات", title="الساعات حسب الفئة", color="مجموع_الساعات", color_continuous_scale="Blues")
                    fig_cat_hours = prepare_chart_layout(fig_cat_hours, "", is_mobile=mobile_view, chart_type="bar")
                    st.plotly_chart(fig_cat_hours, use_container_width=True, config={"displayModeBar": False})
                else:
                    # عرض لسطح المكتب (عمودين)
                    col1_cat, col2_cat = st.columns(2)
                    with col1_cat:
                        fig_cat_tasks = px.pie(category_stats_dist, values="عدد_المهام", names="الفئة", title="عدد المهام حسب الفئة", color_discrete_sequence=px.colors.qualitative.Pastel)
                        fig_cat_tasks = prepare_chart_layout(fig_cat_tasks, "", is_mobile=mobile_view, chart_type="pie")
                        st.plotly_chart(fig_cat_tasks, use_container_width=True, config={"displayModeBar": False})
                    with col2_cat:
                        fig_cat_points = px.pie(category_stats_dist, values="مجموع_النقاط", names="الفئة", title="النقاط حسب الفئة", color_discrete_sequence=px.colors.qualitative.Pastel)
                        fig_cat_points = prepare_chart_layout(fig_cat_points, "", is_mobile=mobile_view, chart_type="pie")
                        st.plotly_chart(fig_cat_points, use_container_width=True, config={"displayModeBar": False})

                    # مخطط الساعات (أفقي لسطح المكتب)
                    fig_cat_hours = px.bar(category_stats_dist.sort_values("مجموع_الساعات", ascending=True), y="الفئة", x="مجموع_الساعات", title="الساعات حسب الفئة", color="مجموع_الساعات", orientation='h', color_continuous_scale="Blues")
                    fig_cat_hours = prepare_chart_layout(fig_cat_hours, "", is_mobile=mobile_view, chart_type="bar")
                    st.plotly_chart(fig_cat_hours, use_container_width=True, config={"displayModeBar": False})

                # جدول ملخص الفئات
                with st.expander("عرض إحصاءات تفصيلية للفئات", expanded=False):
                    # حساب معدلات ونسب لإثراء البيانات، مع تجنب القسمة على صفر
                    category_stats_dist["متوسط النقاط لكل مهمة"] = (category_stats_dist["مجموع_النقاط"] / category_stats_dist["عدد_المهام"]).replace([np.inf, -np.inf], 0).fillna(0)
                    category_stats_dist["متوسط الساعات لكل مهمة"] = (category_stats_dist["مجموع_الساعات"] / category_stats_dist["عدد_المهام"]).replace([np.inf, -np.inf], 0).fillna(0)
                    category_stats_dist["النقاط لكل ساعة"] = (category_stats_dist["مجموع_النقاط"] / category_stats_dist["مجموع_الساعات"]).replace([np.inf, -np.inf], 0).fillna(0)

                    # حساب النسب المئوية
                    total_tasks_count_dist = category_stats_dist["عدد_المهام"].sum()
                    total_points_count_dist = category_stats_dist["مجموع_النقاط"].sum()
                    total_hours_count_dist = category_stats_dist["مجموع_الساعات"].sum()

                    if total_tasks_count_dist > 0: category_stats_dist["نسبة المهام %"] = (category_stats_dist["عدد_المهام"] / total_tasks_count_dist) * 100
                    else: category_stats_dist["نسبة المهام %"] = 0
                    if total_points_count_dist > 0: category_stats_dist["نسبة النقاط %"] = (category_stats_dist["مجموع_النقاط"] / total_points_count_dist) * 100
                    else: category_stats_dist["نسبة النقاط %"] = 0
                    if total_hours_count_dist > 0: category_stats_dist["نسبة الساعات %"] = (category_stats_dist["مجموع_الساعات"] / total_hours_count_dist) * 100
                    else: category_stats_dist["نسبة الساعات %"] = 0

                    # عرض الجدول المحسن
                    st.dataframe(
                        category_stats_dist,
                        column_config={
                            "الفئة": st.column_config.TextColumn("الفئة"),
                            "عدد_المهام": st.column_config.NumberColumn("عدد المهام"),
                            "مجموع_النقاط": st.column_config.NumberColumn("مجموع النقاط", format="%.0f"),
                            "مجموع_الساعات": st.column_config.NumberColumn("مجموع الساعات", format="%.1f"),
                            "متوسط النقاط لكل مهمة": st.column_config.NumberColumn("متوسط النقاط/مهمة", format="%.1f"),
                            "متوسط الساعات لكل مهمة": st.column_config.NumberColumn("متوسط الساعات/مهمة", format="%.1f"),
                            "النقاط لكل ساعة": st.column_config.NumberColumn("النقاط/ساعة", format="%.1f"),
                            "نسبة المهام %": st.column_config.ProgressColumn("نسبة المهام", format="%.1f%%", min_value=0, max_value=100),
                            "نسبة النقاط %": st.column_config.ProgressColumn("نسبة النقاط", format="%.1f%%", min_value=0, max_value=100),
                            "نسبة الساعات %": st.column_config.ProgressColumn("نسبة الساعات", format="%.1f%%", min_value=0, max_value=100),
                        },
                        hide_index=True,
                        use_container_width=True
                    )
            else:
                st.info("لا توجد بيانات مصنفة بفئات في الفترة المحددة.")
        else:
            st.info("البيانات لا تحتوي على الأعمدة المطلوبة (الفئة, عدد النقاط, عدد الساعات) لعرض هذا التحليل.")
        st.markdown("---") # فاصل

        # --- 13.2: توزيع المهام حسب البرنامج ---
        st.subheader("توزيع المهام حسب البرنامج")
        if "البرنامج" in filtered_dist_data.columns and "عدد النقاط" in filtered_dist_data.columns and "عدد الساعات" in filtered_dist_data.columns:
            program_data_dist = filtered_dist_data[
                filtered_dist_data["البرنامج"].notna() & (filtered_dist_data["البرنامج"] != "")
            ].copy()
            program_data_dist['عدد النقاط'] = pd.to_numeric(program_data_dist['عدد النقاط'], errors='coerce').fillna(0)
            program_data_dist['عدد الساعات'] = pd.to_numeric(program_data_dist['عدد الساعات'], errors='coerce').fillna(0)

            if not program_data_dist.empty:
                program_stats_dist = program_data_dist.groupby("البرنامج").agg(
                    عدد_المهام=('البرنامج', 'size'),
                    مجموع_النقاط=('عدد النقاط', 'sum'),
                    مجموع_الساعات=('عدد الساعات', 'sum')
                ).reset_index().sort_values("عدد_المهام", ascending=False)

                if mobile_view:
                    # مخطط 1: توزيع عدد المهام
                    fig_prog_tasks = px.pie(program_stats_dist, values="عدد_المهام", names="البرنامج", title="عدد المهام حسب البرنامج", color_discrete_sequence=px.colors.qualitative.Set2)
                    fig_prog_tasks = prepare_chart_layout(fig_prog_tasks, "", is_mobile=mobile_view, chart_type="pie")
                    st.plotly_chart(fig_prog_tasks, use_container_width=True, config={"displayModeBar": False})
                    # مخطط 2: توزيع النقاط (عمودي للجوال)
                    fig_prog_points = px.bar(program_stats_dist, x="البرنامج", y="مجموع_النقاط", title="النقاط حسب البرنامج", color="مجموع_النقاط", color_continuous_scale="Greens")
                    fig_prog_points = prepare_chart_layout(fig_prog_points, "", is_mobile=mobile_view, chart_type="bar")
                    st.plotly_chart(fig_prog_points, use_container_width=True, config={"displayModeBar": False})
                else:
                    col1_prog, col2_prog = st.columns(2)
                    with col1_prog:
                        fig_prog_tasks = px.pie(program_stats_dist, values="عدد_المهام", names="البرنامج", title="عدد المهام حسب البرنامج", color_discrete_sequence=px.colors.qualitative.Set2)
                        fig_prog_tasks = prepare_chart_layout(fig_prog_tasks, "", is_mobile=mobile_view, chart_type="pie")
                        st.plotly_chart(fig_prog_tasks, use_container_width=True, config={"displayModeBar": False})
                    with col2_prog:
                        # مخطط 2: توزيع النقاط (أفقي للمكتب)
                        fig_prog_points = px.bar(program_stats_dist.sort_values("مجموع_النقاط", ascending=True), y="البرنامج", x="مجموع_النقاط", title="النقاط حسب البرنامج", color="مجموع_النقاط", orientation='h', color_continuous_scale="Greens")
                        fig_prog_points = prepare_chart_layout(fig_prog_points, "", is_mobile=mobile_view, chart_type="bar")
                        st.plotly_chart(fig_prog_points, use_container_width=True, config={"displayModeBar": False})

                with st.expander("عرض إحصاءات تفصيلية للبرامج", expanded=False):
                     st.dataframe(program_stats_dist, hide_index=True, use_container_width=True,
                                  column_config={"مجموع_النقاط": st.column_config.NumberColumn(format="%.0f"),
                                                 "مجموع_الساعات": st.column_config.NumberColumn(format="%.1f")})

            else:
                st.info("لا توجد بيانات مرتبطة ببرامج في الفترة المحددة.")
        else:
             st.info("البيانات لا تحتوي على الأعمدة المطلوبة (البرنامج, عدد النقاط, عدد الساعات) لعرض هذا التحليل.")
        st.markdown("---") # فاصل

        # --- 13.3: توزيع المهام حسب المهمة الرئيسية ---
        st.subheader("توزيع المهام حسب المهمة الرئيسية")
        if "المهمة الرئيسية" in filtered_dist_data.columns and "عدد النقاط" in filtered_dist_data.columns and "عدد الساعات" in filtered_dist_data.columns:
            main_task_data_dist = filtered_dist_data[
                filtered_dist_data["المهمة الرئيسية"].notna() & (filtered_dist_data["المهمة الرئيسية"] != "")
            ].copy()
            main_task_data_dist['عدد النقاط'] = pd.to_numeric(main_task_data_dist['عدد النقاط'], errors='coerce').fillna(0)
            main_task_data_dist['عدد الساعات'] = pd.to_numeric(main_task_data_dist['عدد الساعات'], errors='coerce').fillna(0)

            if not main_task_data_dist.empty:
                main_task_stats_dist = main_task_data_dist.groupby("المهمة الرئيسية").agg(
                    عدد_المهام=('المهمة الرئيسية', 'size'),
                    مجموع_النقاط=('عدد النقاط', 'sum'),
                    مجموع_الساعات=('عدد الساعات', 'sum')
                ).reset_index().sort_values("عدد_المهام", ascending=False)

                # اختيار أهم N مهام رئيسية لتحسين العرض المرئي
                top_n_main_tasks = 10
                top_main_tasks_dist = main_task_stats_dist.head(top_n_main_tasks).copy()

                if mobile_view:
                    # مخطط 1: عدد المهام (عمودي للجوال)
                    fig_maintask_tasks = px.bar(top_main_tasks_dist, x="المهمة الرئيسية", y="عدد_المهام", title=f"أهم {top_n_main_tasks} مهام رئيسية (عدد المهام)", color="عدد_المهام", color_continuous_scale="Oranges")
                    fig_maintask_tasks = prepare_chart_layout(fig_maintask_tasks, "", is_mobile=mobile_view, chart_type="bar")
                    st.plotly_chart(fig_maintask_tasks, use_container_width=True, config={"displayModeBar": False})
                    # مخطط 2: الساعات (عمودي للجوال)
                    fig_maintask_hours = px.bar(top_main_tasks_dist.sort_values("مجموع_الساعات", ascending=False), x="المهمة الرئيسية", y="مجموع_الساعات", title=f"أهم {top_n_main_tasks} مهام رئيسية (الساعات)", color="مجموع_الساعات", color_continuous_scale="Oranges")
                    fig_maintask_hours = prepare_chart_layout(fig_maintask_hours, "", is_mobile=mobile_view, chart_type="bar")
                    st.plotly_chart(fig_maintask_hours, use_container_width=True, config={"displayModeBar": False})
                else:
                    col1_maintask, col2_maintask = st.columns(2)
                    with col1_maintask:
                        # مخطط 1: عدد المهام (أفقي للمكتب)
                        fig_maintask_tasks = px.bar(top_main_tasks_dist.sort_values("عدد_المهام", ascending=True), y="المهمة الرئيسية", x="عدد_المهام", title=f"أهم {top_n_main_tasks} مهام رئيسية (عدد المهام)", color="عدد_المهام", orientation='h', color_continuous_scale="Oranges")
                        fig_maintask_tasks = prepare_chart_layout(fig_maintask_tasks, "", is_mobile=mobile_view, chart_type="bar")
                        st.plotly_chart(fig_maintask_tasks, use_container_width=True, config={"displayModeBar": False})
                    with col2_maintask:
                         # مخطط 2: الساعات (أفقي للمكتب)
                        fig_maintask_hours = px.bar(top_main_tasks_dist.sort_values("مجموع_الساعات", ascending=True), y="المهمة الرئيسية", x="مجموع_الساعات", title=f"أهم {top_n_main_tasks} مهام رئيسية (الساعات)", color="مجموع_الساعات", orientation='h', color_continuous_scale="Oranges")
                        fig_maintask_hours = prepare_chart_layout(fig_maintask_hours, "", is_mobile=mobile_view, chart_type="bar")
                        st.plotly_chart(fig_maintask_hours, use_container_width=True, config={"displayModeBar": False})

                with st.expander("عرض إحصاءات تفصيلية للمهام الرئيسية", expanded=False):
                    # حساب معدلات
                    main_task_stats_dist["متوسط النقاط/مهمة"] = (main_task_stats_dist["مجموع_النقاط"] / main_task_stats_dist["عدد_المهام"]).replace([np.inf, -np.inf], 0).fillna(0)
                    main_task_stats_dist["متوسط الساعات/مهمة"] = (main_task_stats_dist["مجموع_الساعات"] / main_task_stats_dist["عدد_المهام"]).replace([np.inf, -np.inf], 0).fillna(0)
                    main_task_stats_dist["النقاط/ساعة"] = (main_task_stats_dist["مجموع_النقاط"] / main_task_stats_dist["مجموع_الساعات"]).replace([np.inf, -np.inf], 0).fillna(0)

                    st.dataframe(
                        main_task_stats_dist,
                        column_config={
                            "المهمة الرئيسية": st.column_config.TextColumn("المهمة الرئيسية"),
                            "عدد_المهام": st.column_config.NumberColumn("عدد المهام"),
                            "مجموع_النقاط": st.column_config.NumberColumn("مجموع النقاط", format="%.0f"),
                            "مجموع_الساعات": st.column_config.NumberColumn("مجموع الساعات", format="%.1f"),
                            "متوسط النقاط/مهمة": st.column_config.NumberColumn("متوسط النقاط/مهمة", format="%.1f"),
                            "متوسط الساعات/مهمة": st.column_config.NumberColumn("متوسط الساعات/مهمة", format="%.1f"),
                            "النقاط/ساعة": st.column_config.NumberColumn("النقاط/ساعة", format="%.1f"),
                        },
                         hide_index=True, use_container_width=True
                    )
            else:
                st.info("لا توجد بيانات مرتبطة بمهام رئيسية في الفترة المحددة.")
        else:
            st.info("البيانات لا تحتوي على الأعمدة المطلوبة (المهمة الرئيسية, عدد النقاط, عدد الساعات) لعرض هذا التحليل.")
        st.markdown("---") # فاصل

        # --- 13.4: التوزيع الزمني للمهام والنقاط ---
        st.subheader("التوزيع الزمني للمهام والنقاط")
        if "التاريخ" in filtered_dist_data.columns and pd.api.types.is_datetime64_any_dtype(filtered_dist_data['التاريخ']):
            # تأكد أن الأعمدة المطلوبة رقمية
            temporal_data = filtered_dist_data.copy()
            temporal_data['عدد النقاط'] = pd.to_numeric(temporal_data['عدد النقاط'], errors='coerce').fillna(0)
            temporal_data['عدد الساعات'] = pd.to_numeric(temporal_data['عدد الساعات'], errors='coerce').fillna(0)

            # إضافة بيانات الشهر والسنة
            temporal_data["الشهر-السنة"] = temporal_data["التاريخ"].dt.strftime("%Y-%m")

            # حساب الإحصاءات الشهرية
            monthly_stats_dist = temporal_data.groupby("الشهر-السنة").agg(
                عدد_المهام=('الشهر-السنة', 'size'),
                مجموع_النقاط=('عدد النقاط', 'sum'),
                مجموع_الساعات=('عدد الساعات', 'sum')
            ).reset_index()

            # إضافة عمود تاريخ للترتيب الصحيح
            monthly_stats_dist["تاريخ_للترتيب"] = pd.to_datetime(monthly_stats_dist["الشهر-السنة"] + "-01", errors='coerce')
            # إزالة أي صفوف فشل تحويل تاريخها
            monthly_stats_dist = monthly_stats_dist.dropna(subset=["تاريخ_للترتيب"])
            monthly_stats_dist = monthly_stats_dist.sort_values("تاريخ_للترتيب")

            if not monthly_stats_dist.empty:
                 # حساب متوسط النقاط والساعات لكل مهمة
                monthly_stats_dist["متوسط النقاط/مهمة"] = (monthly_stats_dist["مجموع_النقاط"] / monthly_stats_dist["عدد_المهام"]).replace([np.inf, -np.inf], 0).fillna(0)
                monthly_stats_dist["متوسط الساعات/مهمة"] = (monthly_stats_dist["مجموع_الساعات"] / monthly_stats_dist["عدد_المهام"]).replace([np.inf, -np.inf], 0).fillna(0)

                # إنشاء مخطط تطور عدد المهام والنقاط عبر الزمن
                fig_time_series = px.line(
                    monthly_stats_dist,
                    x="الشهر-السنة",
                    y=["عدد_المهام", "مجموع_النقاط", "مجموع_الساعات"], # إضافة الساعات
                    title="تطور الإنجازات عبر الزمن",
                    markers=True,
                    labels={"value": "القيمة", "variable": "المقياس", "الشهر-السنة": "الشهر"},
                    color_discrete_map={"عدد_المهام": "#1e88e5", "مجموع_النقاط": "#27AE60", "مجموع_الساعات": "#F39C12"}
                )
                fig_time_series.update_layout(legend_title_text='المقاييس')
                fig_time_series = prepare_chart_layout(fig_time_series, "", is_mobile=mobile_view, chart_type="line")
                st.plotly_chart(fig_time_series, use_container_width=True, config={"displayModeBar": False})

                # عرض مخطط متوسط النقاط والساعات لكل مهمة
                fig_avg_time_series = px.line(
                    monthly_stats_dist,
                    x="الشهر-السنة",
                    y=["متوسط النقاط/مهمة", "متوسط الساعات/مهمة"],
                    title="تطور متوسط النقاط والساعات لكل مهمة",
                    markers=True,
                    labels={"value": "المتوسط", "variable": "المقياس", "الشهر-السنة": "الشهر"},
                    color_discrete_map={"متوسط النقاط/مهمة": "#E74C3C", "متوسط الساعات/مهمة": "#8E44AD"}
                )
                fig_avg_time_series.update_layout(legend_title_text='المقاييس')
                fig_avg_time_series = prepare_chart_layout(fig_avg_time_series, "", is_mobile=mobile_view, chart_type="line")
                st.plotly_chart(fig_avg_time_series, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("لا توجد بيانات مجمعة شهريًا في الفترة المحددة.")
        else:
            st.info("البيانات لا تحتوي على عمود تاريخ صالح لعرض التوزيع الزمني.")

    else:
         st.info(f"لا توجد بيانات إنجازات مسجلة للفترة الزمنية المحددة: '{selected_time_period_dist}'.")

# =========================================
# القسم 14: تبويب إنجازات الأعضاء (مقسم)
# =========================================
with main_tabs[1]: # تبويب إنجازات الأعضاء
    st.markdown("### 👥 إنجازات الأعضاء")

    # --- 14.1: إعداد التبويب والفلترة الزمنية وحساب الإحصائيات الأولية ---
    st.markdown('<div class="time-filter" style="margin-bottom: 15px;">', unsafe_allow_html=True)
    st.markdown('<label class="time-filter-title" style="font-weight: 500; margin-left: 10px;">تصفية إنجازات الأعضاء في هذا التبويب حسب:</label>', unsafe_allow_html=True)
    achievement_time_options = ["الشهر الحالي", "الربع الحالي", "السنة الحالية", "كل الفترات"]
    # استخدام مفتاح فريد لفلتر هذا التبويب
    achievement_time_period_members = st.radio(
        "",
        options=achievement_time_options,
        horizontal=True,
        key="achievement_time_filter_members_tab", # مفتاح فريد
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # تطبيق الفلتر الزمني على نسخة محلية من البيانات لهذا التبويب
    members_filtered_data = achievements_data.copy()
    member_stats = pd.DataFrame() # تهيئة كـ DataFrame فارغ

    # التأكد من أن عمود التاريخ موجود وصالح قبل الفلترة
    if "التاريخ" in members_filtered_data.columns and pd.api.types.is_datetime64_any_dtype(members_filtered_data['التاريخ']):
        filter_date_members = None
        now_members = datetime.now()

        if achievement_time_period_members == "الشهر الحالي":
            start_of_month = now_members.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            filter_date_members = start_of_month
        elif achievement_time_period_members == "الربع الحالي":
            current_quarter = (now_members.month - 1) // 3 + 1
            start_month_of_quarter = 3 * (current_quarter - 1) + 1
            start_of_quarter = now_members.replace(month=start_month_of_quarter, day=1, hour=0, minute=0, second=0, microsecond=0)
            filter_date_members = start_of_quarter
        elif achievement_time_period_members == "السنة الحالية":
            start_of_year = now_members.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            filter_date_members = start_of_year

        if filter_date_members:
            members_filtered_data = members_filtered_data[members_filtered_data["التاريخ"].notna() & (members_filtered_data["التاريخ"] >= filter_date_members)]
    elif achievement_time_period_members != "كل الفترات":
        st.warning("لا يمكن تطبيق الفلتر الزمني لعدم وجود عمود تاريخ صالح.")
        members_filtered_data = pd.DataFrame() # إفراغ البيانات إذا كان الفلتر مطلوبًا

    # التحقق من وجود بيانات وأعمدة ضرورية *بعد* الفلترة
    if not members_filtered_data.empty and all(col in members_filtered_data.columns for col in ["اسم العضو", "عدد النقاط", "عدد الساعات"]):
        try:
            # التأكد من أن الأعمدة الرقمية هي بالفعل رقمية ومعالجة الأخطاء
            members_filtered_data['عدد النقاط'] = pd.to_numeric(members_filtered_data['عدد النقاط'], errors='coerce').fillna(0)
            members_filtered_data['عدد الساعات'] = pd.to_numeric(members_filtered_data['عدد الساعات'], errors='coerce').fillna(0)
            # إزالة الصفوف التي تحتوي على اسم عضو فارغ
            members_filtered_data = members_filtered_data.dropna(subset=['اسم العضو'])
            members_filtered_data = members_filtered_data[members_filtered_data['اسم العضو'] != '']

            # حساب إحصائيات الأعضاء للفترة المحددة
            if not members_filtered_data.empty:
                member_stats = members_filtered_data.groupby("اسم العضو").agg(
                    عدد_المهام=('اسم العضو', 'size'),
                    عدد_النقاط=('عدد النقاط', 'sum'),
                    عدد_الساعات=('عدد الساعات', 'sum')
                ).reset_index()

                # فرز member_stats حسب النقاط قبل إضافة المستويات
                member_stats = member_stats.sort_values("عدد_النقاط", ascending=False)

                # إضافة مستوى الإنجاز لكل عضو بناءً على النقاط في الفترة المحددة
                # استخدام الدالة get_achievement_level من القسم 5.1
                member_stats["مستوى_الإنجاز"] = member_stats["عدد_النقاط"].apply(get_achievement_level)
                member_stats["مستوى"] = member_stats["مستوى_الإنجاز"].apply(lambda x: x["name"])
                member_stats["لون_المستوى"] = member_stats["مستوى_الإنجاز"].apply(lambda x: x["color"])
                member_stats["أيقونة_المستوى"] = member_stats["مستوى_الإنجاز"].apply(lambda x: x["icon"])

        except Exception as e:
            st.error(f"خطأ في معالجة البيانات الرقمية للأعضاء: {e}")
            members_filtered_data = pd.DataFrame() # إفراغ البيانات عند حدوث خطأ
            member_stats = pd.DataFrame()

    # --- 14.2: عرض أبرز الإنجازات العامة (لا تعتمد على فلتر التبويب الزمني) ---
    # استخدام البيانات الأصلية achievements_data
    # 14.2.1: نجم الشهر
    try:
        current_month = datetime.now().month
        current_year = datetime.now().year
        # استخدام الدالة get_member_of_month من القسم 8
        star_of_month = get_member_of_month(achievements_data, current_year, current_month)
        if star_of_month:
            st.subheader(f"🌟 نجم شهر {star_of_month['اسم_الشهر']}")
            st.markdown(f"""
            <div class="star-of-month" style="background: linear-gradient(135deg, #fceabb 0%, #f8b500 100%); padding: 20px; border-radius: 15px; text-align: center; color: #333; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                <div style="font-size: 3rem; margin-bottom: 10px;">🏆</div>
                <div class="star-name" style="font-size: 1.8rem; font-weight: bold; color: #BF360C; margin-bottom: 15px;">{star_of_month["اسم"]}</div>
                <div class="star-stats" style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 15px;">
                    <div style="background-color: rgba(255, 255, 255, 0.5); padding: 10px; border-radius: 10px; min-width: 80px;">
                        <div style="font-size: 1.5rem; font-weight: bold;">{int(star_of_month["النقاط"])}</div>
                        <div style="font-size: 0.9rem;">النقاط</div>
                    </div>
                    <div style="background-color: rgba(255, 255, 255, 0.5); padding: 10px; border-radius: 10px; min-width: 80px;">
                        <div style="font-size: 1.5rem; font-weight: bold;">{int(star_of_month["الساعات"])}</div>
                        <div style="font-size: 0.9rem;">الساعات</div>
                    </div>
                    <div style="background-color: rgba(255, 255, 255, 0.5); padding: 10px; border-radius: 10px; min-width: 80px;">
                        <div style="font-size: 1.5rem; font-weight: bold;">{star_of_month["المهام"]}</div>
                        <div style="font-size: 0.9rem;">المهام</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info(f"لم يتم تحديد نجم لشهر {get_arabic_month_name(current_month)} بعد.")
    except NameError:
        st.error("الدالة get_member_of_month غير معرفة.")
    except Exception as e:
         st.error(f"حدث خطأ عند عرض نجم الشهر: {e}")

    # 14.2.2: أحدث الترقيات
    try:
        # استخدام دالة detect_member_promotions من القسم 8
        promotions = detect_member_promotions(achievements_data, lookback_days=30)
        if promotions:
            st.subheader("🚀 أحدث ترقيات الأعضاء (آخر 30 يوم)")
            st.markdown('<div class="promotions-list" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-top: 15px;">', unsafe_allow_html=True)
            for promotion in promotions[:6]: # عرض أول 6 ترقيات
                member_name = promotion.get('اسم', 'N/A')
                level_color = promotion.get('لون_المستوى', '#777')
                level_icon = promotion.get('أيقونة_المستوى', '')
                prev_level = promotion.get('المستوى_السابق', 'N/A')
                new_level = promotion.get('المستوى_الجديد', 'N/A')
                gained_points = int(promotion.get('النقاط_المكتسبة', 0))
                st.markdown(f"""
                <div class="promotion-item" style="background-color: #e8f5e9; padding: 15px; border-radius: 8px; border-left: 5px solid {level_color}; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                    <div class="promotion-name" style="font-weight: 600; font-size: 1.05rem; color:#1E8449;">{member_name} <span class="promotion-badge" style="color: {level_color};">{level_icon}</span></div>
                    <div class="promotion-details" style="font-size: 0.85rem; margin-top: 8px; color: #333;">
                        ترقى من <span style="color: #777; font-weight: 500;">{prev_level}</span> إلى <span style="color: {level_color}; font-weight: 600;">{new_level}</span>
                        <div style="margin-top: 5px; font-size: 0.8rem; color: #555;">( +{gained_points} نقطة خلال الفترة )</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    except NameError:
         st.error("الدالة detect_member_promotions غير معرفة.")
    except Exception as e:
         st.error(f"حدث خطأ عند عرض الترقيات: {e}")

    st.markdown("---") # فاصل

    # --- 14.3: عرض ملخصات الفترة المحددة ---
    # استخدام member_stats المحسوبة في 14.1
    if not member_stats.empty:
        # 14.3.1: لوحة الصدارة للفترة المحددة
        st.subheader(f"🏆 لوحة الصدارة (الفترة: {achievement_time_period_members})")
        leaderboard_cols = st.columns([3, 2]) if not mobile_view else (st.container(), st.container())
        with leaderboard_cols[0]: # العمود الأيسر للمخطط
             top_n_leaderboard = 10
             top_members_period = member_stats.head(top_n_leaderboard).copy()
             if not top_members_period.empty:
                 top_members_period = top_members_period.sort_values("عدد_النقاط", ascending=True)
                 try:
                     fig_top_members = px.bar(
                         top_members_period,
                         y="اسم العضو" if not mobile_view else "عدد_النقاط",
                         x="عدد_النقاط" if not mobile_view else "اسم العضو",
                         orientation='h' if not mobile_view else 'v',
                         color="عدد_النقاط", color_continuous_scale=px.colors.sequential.Viridis,
                         text="مستوى" if not mobile_view else None, height=400,
                         title=f"أعلى {top_n_leaderboard} أعضاء (حسب النقاط)"
                     )
                     fig_top_members.update_layout(yaxis_title="اسم العضو" if not mobile_view else "النقاط", xaxis_title="عدد النقاط" if not mobile_view else "اسم العضو", coloraxis_showscale=False)
                     if not mobile_view: fig_top_members.update_traces(textposition='outside')
                     fig_top_members = prepare_chart_layout(fig_top_members, "", is_mobile=mobile_view, chart_type="bar")
                     st.plotly_chart(fig_top_members, use_container_width=True, config={"displayModeBar": False})
                 except NameError: st.error("الدالة prepare_chart_layout غير معرفة.")
                 except Exception as e: st.error(f"حدث خطأ عند رسم مخطط أعلى الأعضاء: {e}")
             else: st.info("لا توجد بيانات كافية لعرض مخطط أعلى الأعضاء لهذه الفترة.")

        with leaderboard_cols[1]: # العمود الأيمن لقائمة المتصدرين
             st.markdown('<div class="leaderboard" style="background-color: #ffffff; border: 1px solid #eee; padding: 15px; border-radius: 10px; height: 400px; overflow-y: auto;">', unsafe_allow_html=True)
             st.markdown('<div class="leaderboard-title" style="text-align: center; font-weight: bold; margin-bottom: 15px; font-size: 1.1rem; color: #333;">قائمة المتصدرين</div>', unsafe_allow_html=True)
             if not member_stats.empty:
                 for i, row in member_stats.head(5).iterrows():
                     rank_color = "#FFD700" if i == 0 else ("#C0C0C0" if i == 1 else ("#CD7F32" if i == 2 else "#6c757d"))
                     rank_icon = "🥇" if i == 0 else ("🥈" if i == 1 else ("🥉" if i == 2 else f"<span style='font-size:0.9em;'>{i+1}.</span>"))
                     member_name = row.get('اسم العضو', 'N/A'); level_icon = row.get('أيقونة_المستوى', ''); level_name = row.get('مستوى', 'N/A')
                     tasks_count = int(row.get('عدد_المهام', 0)); hours_count = float(row.get('عدد_الساعات', 0)); level_color = row.get('لون_المستوى', '#777'); points_count = int(row.get('عدد_النقاط', 0))
                     if points_count > 0:
                         st.markdown(f"""<div class="leaderboard-item" style="display: flex; align-items: center; margin-bottom: 12px; padding: 8px; border-radius: 6px; background-color: {'#f8f9fa' if i>=3 else 'transparent'}; border-right: 5px solid {rank_color};"><div class="leaderboard-rank" style="font-weight: bold; color: {rank_color}; font-size: 1.1rem; margin-left: 10px; min-width: 30px; text-align: center;">{rank_icon}</div><div class="leaderboard-info" style="flex-grow: 1; margin-left: 10px;"><div class="leaderboard-name" style="font-weight: 600; font-size: 0.95rem;">{member_name} <span style="font-size: 0.9rem;">{level_icon}</span></div><div class="leaderboard-details" style="font-size: 0.75rem; color: #555;">{level_name} • {tasks_count} مهمة • {hours_count:.1f} س</div></div><div class="leaderboard-score" style="font-weight: bold; font-size: 1.1rem; color: {level_color};">{points_count}</div></div>""", unsafe_allow_html=True)
             else: st.info("لا توجد بيانات لعرض لوحة الصدارة لهذه الفترة.")
             st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("---") # فاصل

        # 14.3.2: قادة الفئات للفترة المحددة
        # استخدام members_filtered_data المحسوبة في 14.1
        try:
            # استخدام دالة get_category_leaders من القسم 8
            category_leaders = get_category_leaders(members_filtered_data)
            if category_leaders:
                st.subheader(f"🏅 قادة الفئات (الفترة: {achievement_time_period_members})")
                categories = list(category_leaders.keys())
                num_categories = len(categories)
                num_cols = min(num_categories, 4) if not mobile_view else 2
                if num_cols > 0:
                    cols = st.columns(num_cols)
                    col_index = 0
                    for category in sorted(categories):
                        leader = category_leaders[category]
                        leader_name = leader.get('اسم', 'N/A'); leader_points = int(leader.get('النقاط', 0))
                        with cols[col_index % num_cols]:
                            st.markdown(f"""<div style="padding: 12px; border-radius: 8px; background-color: #e3f2fd; text-align: center; height: 100%; margin-bottom: 10px; border: 1px solid #bbdefb;"><div style="font-size: 0.9rem; color: #1565c0; margin-bottom: 5px; font-weight: 600; min-height: 3em; display: flex; align-items: center; justify-content: center;">{category}</div><div style="font-weight: 600; color: #0d47a1; font-size: 1rem; margin-bottom: 5px;">{leader_name}</div><div><span style="font-weight: bold; font-size: 1.1rem; color: #1e88e5;">{leader_points}</span> <span style="font-size: 0.75rem; color: #555;">نقطة</span></div></div>""", unsafe_allow_html=True)
                        col_index += 1
                # else: st.info("لا توجد فئات لها قادة في الفترة المحددة.") # يمكن إزالة هذه الرسالة
            # else: st.info("لا يوجد قادة فئات لهذه الفترة.") # يمكن إزالة هذه الرسالة
        except NameError: st.error("الدالة get_category_leaders غير معرفة.")
        except Exception as e: st.error(f"حدث خطأ عند عرض قادة الفئات: {e}")
        st.markdown("---") # فاصل

        # --- 14.4: إعداد واجهة اختيار العضو للتفاصيل ---
        st.subheader("👤 تفاصيل إنجازات الأعضاء")

        # دوال مساعدة (يمكن نقلها للقسم 5)
        def create_metric_card(value, label, color_hex):
            bg_color_map = {"#1e88e5": "#e3f2fd", "#27AE60": "#e8f5e9", "#F39C12": "#fff3e0", "#E74C3C": "#fdecea"}
            bg_color = bg_color_map.get(color_hex, "#f8f9fa")
            try: formatted_value = f"{int(value):,}"
            except: formatted_value = str(value)
            return f"""<div style="flex: 1; min-width: 120px; text-align: center; background-color: {bg_color}; padding: 15px; border-radius: 8px; margin: 5px;"> <div style="font-size: 2rem; font-weight: bold; color: {color_hex}; line-height: 1.2;">{formatted_value}</div> <div style="font-size: 0.9rem; color: #555; margin-top: 5px;">{label}</div> </div>"""

        def set_selected_member(member_name):
            # استخدام مفتاح حالة الجلسة الخاص بتفاصيل العضو
            if st.session_state.get('selected_member_detail', None) == member_name:
                 st.session_state.selected_member_detail = None
            else: st.session_state.selected_member_detail = member_name

        # فلاتر لتخصيص قائمة الأعضاء للاختيار منها
        filter_cols_detail = st.columns([2, 2, 2]) if not mobile_view else st.columns(1)

        # تحديد القوائم المتاحة للفلاتر بناءً على البيانات المفلترة زمنيا members_filtered_data
        available_categories_for_filter = ["الكل"] + sorted([c for c in members_filtered_data["الفئة"].dropna().unique() if c]) if "الفئة" in members_filtered_data.columns else ["الكل"]
        available_programs_for_filter = ["الكل"] + sorted([p for p in members_filtered_data["البرنامج"].dropna().unique() if p]) if "البرنامج" in members_filtered_data.columns else ["الكل"]
        available_levels_for_filter = ["الكل"] + sorted([lvl for lvl in member_stats["مستوى"].unique() if lvl])

        with filter_cols_detail[0]:
             category_filter_detail = st.selectbox("تصفية الأعضاء حسب الفئة", available_categories_for_filter, key="category_filter_select_detail")
        with filter_cols_detail[1 % len(filter_cols_detail)]:
             program_filter_detail = st.selectbox("تصفية الأعضاء حسب البرنامج", available_programs_for_filter, key="program_filter_select_detail")
        with filter_cols_detail[2 % len(filter_cols_detail)]:
             level_filter_detail = st.selectbox("تصفية الأعضاء حسب المستوى", available_levels_for_filter, key="level_filter_select_detail")

        # تطبيق الفلاتر على قائمة الأعضاء (member_stats)
        filtered_members_list_df = member_stats.copy()
        if level_filter_detail != "الكل": filtered_members_list_df = filtered_members_list_df[filtered_members_list_df["مستوى"] == level_filter_detail]
        if program_filter_detail != "الكل":
             program_members_in_period = members_filtered_data[members_filtered_data["البرنامج"] == program_filter_detail]["اسم العضو"].unique()
             filtered_members_list_df = filtered_members_list_df[filtered_members_list_df["اسم العضو"].isin(program_members_in_period)]
        if category_filter_detail != "الكل":
             category_members_in_period = members_filtered_data[members_filtered_data["الفئة"] == category_filter_detail]["اسم العضو"].unique()
             filtered_members_list_df = filtered_members_list_df[filtered_members_list_df["اسم العضو"].isin(category_members_in_period)]

        # عرض القائمة المصفاة كأزرار قابلة للنقر
        final_filtered_member_list = filtered_members_list_df["اسم العضو"].tolist()
        st.markdown("##### اختر عضوًا لعرض تفاصيله:")
        if final_filtered_member_list:
            max_cols_buttons = 4 if not mobile_view else 2
            list_cols_buttons = st.columns(max_cols_buttons)
            member_index_btn = 0
            for member_name in final_filtered_member_list:
                 with list_cols_buttons[member_index_btn % max_cols_buttons]:
                     member_row_df = filtered_members_list_df[filtered_members_list_df["اسم العضو"] == member_name]
                     if not member_row_df.empty:
                         member_row = member_row_df.iloc[0]
                         icon = member_row.get('أيقونة_المستوى', ''); points = int(member_row.get('عدد_النقاط', 0))
                         button_label = f"{member_name} ({icon} {points} ن)"
                         button_key = f"member_button_{member_name.replace(' ', '_').replace('.', '_')}"
                         # استخدام مفتاح حالة الجلسة الصحيح للتحقق
                         button_type = "primary" if st.session_state.get('selected_member_detail', None) == member_name else "secondary"
                         st.button(button_label, key=button_key, on_click=set_selected_member, args=(member_name,), use_container_width=True, type=button_type)
                 member_index_btn += 1
            st.markdown("---")
        else:
            st.info("لا يوجد أعضاء يطابقون معايير التصفية المحددة.")
            st.markdown("---")

        # --- 14.5: عرض تفاصيل العضو المختار ---
        # استخدام مفتاح حالة الجلسة الصحيح
        selected_member_to_display = st.session_state.get('selected_member_detail', None)

        if selected_member_to_display:
            # الحصول على بيانات هذا العضو *ضمن الفترة المحددة للتبويب*
            member_detail_data = members_filtered_data[members_filtered_data["اسم العضو"] == selected_member_to_display].copy()
            # الحصول على الإحصائيات المجمعة لهذا العضو *ضمن الفترة المحددة للتبويب*
            member_info_rows = filtered_members_list_df[filtered_members_list_df["اسم العضو"] == selected_member_to_display]

            if not member_detail_data.empty and not member_info_rows.empty:
                member_info = member_info_rows.iloc[0]
                try:
                    achievement_level = member_info["مستوى_الإنجاز"]
                    total_points = member_info["عدد_النقاط"]; total_hours = member_info["عدد_الساعات"]; total_tasks = member_info["عدد_المهام"]

                    # عرض بطاقة المعلومات الأساسية
                    st.markdown(f"""<div style="padding: 20px; background-color: #ffffff; border-radius: 12px; margin-top: 20px; margin-bottom: 20px; direction: rtl; text-align: right; border: 1px solid #dee2e6; box-shadow: 0 2px 5px rgba(0,0,0,0.05);"><h4 style="margin-top: 0; margin-bottom: 15px; color: {achievement_level['color']}; border-bottom: 2px solid {achievement_level['color']}; padding-bottom: 10px;">{selected_member_to_display} {achievement_level['icon']}</h4><div style="margin-bottom: 20px;"><span style="font-size: 1.1rem; color: {achievement_level['color']}; font-weight: bold; background-color: {achievement_level['color']}15; padding: 5px 10px; border-radius: 5px;">المستوى ({achievement_time_period_members}): {achievement_level['name']}</span></div><div style="display: flex; flex-wrap: wrap; gap: 10px; justify-content: space-around;">{create_metric_card(total_points, "مجموع النقاط", "#1e88e5")}{create_metric_card(total_tasks, "عدد المهام", "#27AE60")}{create_metric_card(total_hours, "مجموع الساعات", "#F39C12")}</div></div>""", unsafe_allow_html=True)

                    # عرض المخططات والجدول التفصيلي
                    member_charts_cols = st.columns([3, 2]) if not mobile_view else (st.container(), st.container())
                    with member_charts_cols[0]: # الجزء الأكبر للمخططات
                         # 14.5.1: مخطط الرادار للفئات
                         if "الفئة" in member_detail_data.columns:
                             category_points_member = calculate_points_by_category(member_detail_data, selected_member_to_display)
                             if not category_points_member.empty:
                                 st.markdown("##### توزيع نقاط العضو حسب الفئات")
                                 radar_chart = create_radar_chart(category_points_member, selected_member_to_display, is_mobile=mobile_view)
                                 if radar_chart: st.plotly_chart(radar_chart, use_container_width=True, config={"displayModeBar": False})
                                 # else: st.info(f"لا يمكن رسم مخطط الفئات للعضو.") # يمكن إزالة الرسالة
                             # else: st.info(f"لا توجد بيانات فئات للعضو {selected_member_to_display} في الفترة المحددة.") # يمكن إزالة الرسالة

                         # 14.5.2: مخطط التطور الزمني
                         if "التاريخ" in member_detail_data.columns and pd.api.types.is_datetime64_any_dtype(member_detail_data['التاريخ']):
                             if len(member_detail_data) > 1:
                                 st.markdown("##### تطور إنجازات العضو الشهرية")
                                 member_data_ts = member_detail_data.copy()
                                 member_data_ts["الشهر-السنة"] = member_data_ts["التاريخ"].dt.strftime("%Y-%m")
                                 member_monthly_stats = member_data_ts.groupby("الشهر-السنة").agg(عدد_النقاط=('عدد النقاط', 'sum'), عدد_الساعات=('عدد الساعات', 'sum'), عدد_المهام=('اسم العضو', 'size')).reset_index()
                                 member_monthly_stats["تاريخ_للترتيب"] = pd.to_datetime(member_monthly_stats["الشهر-السنة"] + "-01", errors='coerce')
                                 member_monthly_stats = member_monthly_stats.dropna(subset=["تاريخ_للترتيب"]).sort_values("تاريخ_للترتيب")
                                 if not member_monthly_stats.empty:
                                     fig_member_time = px.line(member_monthly_stats, x="الشهر-السنة", y=["عدد_النقاط", "عدد_الساعات", "عدد_المهام"], markers=True, labels={"value": "القيمة", "variable": "المقياس", "الشهر-السنة": "الشهر"}, color_discrete_map={"عدد_النقاط": "#1e88e5", "عدد_الساعات": "#F39C12", "عدد_المهام": "#27AE60"})
                                     fig_member_time.update_layout(legend_title_text='المقاييس')
                                     fig_member_time = prepare_chart_layout(fig_member_time, "", is_mobile=mobile_view, chart_type="line")
                                     st.plotly_chart(fig_member_time, use_container_width=True, config={"displayModeBar": False})
                                 # else: st.info(f"لا توجد بيانات زمنية كافية لعرض تطور إنجازات {selected_member_to_display}.") # يمكن إزالة الرسالة
                             # else: st.info(f"لا توجد بيانات زمنية كافية لعرض تطور إنجازات {selected_member_to_display}.") # يمكن إزالة الرسالة

                    with member_charts_cols[1]: # الجزء الأصغر للجداول/القوائم
                         # 14.5.3: جدول تفاصيل الفئات
                         if 'category_points_member' in locals() and not category_points_member.empty:
                             st.markdown("##### تفاصيل الفئات")
                             st.dataframe(category_points_member[['الفئة', 'عدد النقاط', 'مستوى_فئة', 'أيقونة_مستوى_فئة']].sort_values("عدد النقاط", ascending=False), column_config={"الفئة": st.column_config.TextColumn("الفئة"), "عدد النقاط": st.column_config.NumberColumn("النقاط", format="%d"), "مستوى_فئة": st.column_config.TextColumn("المستوى"), "أيقونة_المستوى_فئة": st.column_config.TextColumn(" ")}, hide_index=True, use_container_width=True)

                         # 14.5.4: آخر 5 مهام
                         st.markdown("##### آخر 5 مهام للعضو")
                         if "التاريخ" in member_detail_data.columns and pd.api.types.is_datetime64_any_dtype(member_detail_data['التاريخ']):
                             latest_tasks_member = member_detail_data.sort_values("التاريخ", ascending=False, na_position='last').head(5)
                             if not latest_tasks_member.empty:
                                 for _, task in latest_tasks_member.iterrows():
                                     task_title = task.get("عنوان المهمة", "مهمة غير محددة"); task_date = task.get("التاريخ", None); task_points = float(task.get("عدد النقاط", 0))
                                     formatted_date = task_date.strftime("%Y/%m/%d") if pd.notna(task_date) else "-"
                                     st.markdown(f"""<div style="font-size: 0.85rem; padding: 5px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between;"><span>{task_title} ({formatted_date})</span><span style="color: #1e88e5; font-weight: 500;">{int(task_points)} ن</span></div>""", unsafe_allow_html=True)
                             else: st.info(f"لا توجد مهام مسجلة للعضو {selected_member_to_display} في الفترة المحددة.")
                         else: st.warning("لا يمكن عرض آخر المهام لعدم وجود عمود تاريخ صالح.")

                except NameError as ne: st.error(f"خطأ: الدالة المساعدة غير معرفة: {ne}.")
                except Exception as detail_error: st.error(f"حدث خطأ أثناء عرض تفاصيل العضو '{selected_member_to_display}': {detail_error}")
            # else: st.warning(f"لا توجد بيانات للعضو المحدد '{selected_member_to_display}' ضمن معايير التصفية الحالية.") # يمكن إزالة الرسالة

        # else: # إذا لم يتم اختيار عضو
            # st.info("يرجى النقر على اسم عضو من القائمة أعلاه لعرض تفاصيله.") # هذه الرسالة قد لا تكون ضرورية مع وجود الأزرار

    else: # إذا كانت member_stats فارغة (بعد الفلترة الزمنية والتحقق الأولي)
        st.info(f"لا توجد إحصائيات متاحة للأعضاء في الفترة الزمنية المحددة: '{achievement_time_period_members}'.")


# =========================================
# القسم 15: تبويب قائمة المهام التفصيلية
# =========================================
with main_tabs[2]: # تبويب قائمة المهام
    st.markdown("### 📝 قائمة المهام التفصيلية")

    # --- 15.1: فلاتر البحث والتصفية ---
    st.markdown("#### بحث وتصفية المهام")
    if mobile_view:
        filter_container_list = st.container()
        with filter_container_list:
             st.radio("تصفية حسب الفترة:", options=TIME_FILTER_OPTIONS, key="time_filter_list", horizontal=True) # استخدام مفتاح حالة الجلسة العام
             members_options_list = ["الكل"] + members_list
             st.selectbox("عضو هيئة التدريس:", options=members_options_list, key="selected_member_list") # استخدام مفتاح حالة الجلسة العام
             category_options_list = ["الكل"] + sorted([c for c in achievements_data["الفئة"].dropna().unique() if c]) if "الفئة" in achievements_data.columns else ["الكل"]
             st.selectbox("الفئة:", options=category_options_list, key="selected_category_list") # استخدام مفتاح حالة الجلسة العام
             program_options_list = ["الكل"] + sorted([p for p in achievements_data["البرنامج"].dropna().unique() if p]) if "البرنامج" in achievements_data.columns else ["الكل"]
             st.selectbox("البرنامج:", options=program_options_list, key="selected_program_list") # استخدام مفتاح حالة الجلسة العام
             main_task_options_list = ["الكل"] + main_tasks_list
             st.selectbox("المهمة الرئيسية:", options=main_task_options_list, key="selected_main_task_list") # استخدام مفتاح حالة الجلسة العام
    else:
         filter_cols_list = st.columns([2, 2, 2, 2, 3])
         with filter_cols_list[0]: st.radio("الفترة:", options=TIME_FILTER_OPTIONS, key="time_filter_list", horizontal=False, label_visibility="collapsed")
         with filter_cols_list[1]:
              members_options_list = ["الكل"] + members_list
              st.selectbox("العضو:", options=members_options_list, key="selected_member_list", label_visibility="collapsed")
         with filter_cols_list[2]:
              category_options_list = ["الكل"] + sorted([c for c in achievements_data["الفئة"].dropna().unique() if c]) if "الفئة" in achievements_data.columns else ["الكل"]
              st.selectbox("الفئة:", options=category_options_list, key="selected_category_list", label_visibility="collapsed")
         with filter_cols_list[3]:
              program_options_list = ["الكل"] + sorted([p for p in achievements_data["البرنامج"].dropna().unique() if p]) if "البرنامج" in achievements_data.columns else ["الكل"]
              st.selectbox("البرنامج:", options=program_options_list, key="selected_program_list", label_visibility="collapsed")
         with filter_cols_list[4]:
             main_task_options_list = ["الكل"] + main_tasks_list
             st.selectbox("المهمة الرئيسية:", options=main_task_options_list, key="selected_main_task_list", label_visibility="collapsed")

    search_query = st.text_input("البحث في عنوان أو وصف المهمة:", placeholder="ادخل كلمة للبحث...", key="search_query_list_input")

    # --- 15.2: تطبيق الفلاتر ---
    filtered_tasks = achievements_data.copy()
    # تطبيق الفلتر الزمني
    if "التاريخ" in filtered_tasks.columns and pd.api.types.is_datetime64_any_dtype(filtered_tasks['التاريخ']):
        current_date = datetime.now()
        time_filter_value = st.session_state.get("time_filter_list", TIME_FILTER_OPTIONS[0])
        filter_date_list = None
        if time_filter_value == "آخر شهر": filter_date_list = current_date - timedelta(days=30)
        elif time_filter_value == "آخر ستة أشهر": filter_date_list = current_date - timedelta(days=180)
        elif time_filter_value == "آخر سنة": filter_date_list = current_date - timedelta(days=365)
        elif time_filter_value == "آخر ثلاث سنوات": filter_date_list = current_date - timedelta(days=365*3)
        if filter_date_list: filtered_tasks = filtered_tasks[filtered_tasks["التاريخ"].notna() & (filtered_tasks["التاريخ"] >= filter_date_list)]
    elif st.session_state.get("time_filter_list") != TIME_FILTER_OPTIONS[0]: st.warning("لا يمكن تطبيق الفلتر الزمني لعدم وجود عمود تاريخ صالح.")

    # تطبيق باقي الفلاتر
    selected_member_value = st.session_state.get("selected_member_list", "الكل")
    if selected_member_value != "الكل" and "اسم العضو" in filtered_tasks.columns: filtered_tasks = filtered_tasks[filtered_tasks["اسم العضو"] == selected_member_value]
    selected_category_value = st.session_state.get("selected_category_list", "الكل")
    if selected_category_value != "الكل" and "الفئة" in filtered_tasks.columns: filtered_tasks = filtered_tasks[filtered_tasks["الفئة"] == selected_category_value]
    selected_program_value = st.session_state.get("selected_program_list", "الكل")
    if selected_program_value != "الكل" and "البرنامج" in filtered_tasks.columns: filtered_tasks = filtered_tasks[filtered_tasks["البرنامج"] == selected_program_value]
    selected_main_task_value = st.session_state.get("selected_main_task_list", "الكل")
    if selected_main_task_value != "الكل" and "المهمة الرئيسية" in filtered_tasks.columns:
        if selected_main_task_value == "— بدون مهمة رئيسية —": filtered_tasks = filtered_tasks[filtered_tasks["المهمة الرئيسية"].isna() | (filtered_tasks["المهمة الرئيسية"] == "")]
        else: filtered_tasks = filtered_tasks[filtered_tasks["المهمة الرئيسية"] == selected_main_task_value]
    # تطبيق فلتر البحث النصي
    if search_query:
        search_cond = pd.Series(False, index=filtered_tasks.index)
        if "عنوان المهمة" in filtered_tasks.columns: search_cond = search_cond | filtered_tasks["عنوان المهمة"].astype(str).str.contains(search_query, case=False, na=False)
        if "وصف مختصر" in filtered_tasks.columns: search_cond = search_cond | filtered_tasks["وصف مختصر"].astype(str).str.contains(search_query, case=False, na=False)
        filtered_tasks = filtered_tasks[search_cond]

    # --- 15.3: عرض قائمة المهام المصفاة ---
    st.markdown("---")
    if not filtered_tasks.empty:
        st.markdown(f"#### المهام المطابقة ({len(filtered_tasks)})")
        if "التاريخ" in filtered_tasks.columns and pd.api.types.is_datetime64_any_dtype(filtered_tasks['التاريخ']):
             filtered_tasks = filtered_tasks.sort_values(by="التاريخ", ascending=False, na_position='last')

        for i, task in filtered_tasks.iterrows():
             with st.container():
                 st.markdown("<div class='task-card completed' style='border-right-color: #27AE60;'>", unsafe_allow_html=True)
                 task_title = task.get("عنوان المهمة", "-"); task_desc = task.get("وصف مختصر", ""); member_name = task.get("اسم العضو", "-")
                 date_display = task.get("التاريخ", None); formatted_date = date_display.strftime("%Y/%m/%d") if pd.notna(date_display) else "-"
                 hours = float(task.get("عدد الساعات", 0)); points = float(task.get("عدد النقاط", 0)); complexity = task.get("مستوى التعقيد", "-")
                 category = task.get("الفئة", "-"); program = task.get("البرنامج", "-"); main_task = task.get("المهمة الرئيسية", "")
                 complexity_color_map = {"منخفض": "#27AE60", "متوسط": "#F39C12", "عالي": "#E74C3C", "عالي جداً": "#C0392B"}
                 complexity_color = complexity_color_map.get(complexity, "#3498DB")
                 st.markdown(f"""<div class="task-header"><div><div class="task-title">{task_title}</div><div style="font-size: 0.85rem; color: #666;">{member_name}</div></div><div><span style="background-color: {complexity_color}20; color: {complexity_color}; padding: 3px 8px; border-radius: 10px; font-size: 0.75rem; font-weight: 500;">{complexity}</span></div></div>""", unsafe_allow_html=True)
                 if task_desc: st.markdown(f'<div style="font-size: 0.85rem; margin: 8px 0; color: #555;">{task_desc}</div>', unsafe_allow_html=True)
                 st.markdown(f"""<div class="task-details" style="margin-bottom: 10px;"><span class="task-detail-item">📅 {formatted_date}</span><span class="task-detail-item">🏷️ {category}</span><span class="task-detail-item">📚 {program}</span>{f'<span class="task-detail-item">🔗 {main_task}</span>' if main_task else ''}</div>""", unsafe_allow_html=True)
                 st.markdown(f"""<div class="task-metrics" style="justify-content: flex-end;"><div class="task-metric"><div class="task-metric-value" style="color: #1e88e5;">{int(points)}</div><div class="task-metric-label">النقاط</div></div><div class="task-metric"><div class="task-metric-value" style="color: #F39C12;">{hours:.1f}</div><div class="task-metric-label">الساعات</div></div></div>""", unsafe_allow_html=True)
                 st.markdown("</div>", unsafe_allow_html=True)
                 st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    else:
        st.info("لا توجد مهام تطابق معايير البحث والتصفية المحددة.")


# =========================================
# القسم 16: نصائح الاستخدام والتذييل (كان القسم الأخير)
# =========================================
st.markdown("---") # خط فاصل قبل التذييل

with st.expander("💡 نصائح للاستخدام", expanded=False):
    st.markdown("""
    * **التصفية الزمنية:** يمكنك اختيار نطاق زمني في كل تبويب لعرض البيانات ضمن فترة محددة.
    * **توزيعات المهام:** يعرض تحليلات لتوزيع المهام حسب الفئة، البرنامج، المهمة الرئيسية، والزمن.
    * **إنجازات الأعضاء:** يعرض ملخصًا لإنجازات الأعضاء، نجم الشهر، لوحة الصدارة، وقادة الفئات للفترة المحددة، ويتيح استكشاف تفاصيل عضو محدد.
    * **قائمة المهام:** تتيح تصفية وبحث المهام حسب معايير متعددة وعرض تفاصيل كل مهمة.
    * **الرسوم البيانية:** مرر الفأرة فوقها لرؤية التفاصيل. يمكنك تكبيرها وتنزيلها كصور من الأزرار التي تظهر عند التمرير (في وضع سطح المكتب).
    * **العودة للأعلى:** انقر على زر السهم ↑ في أسفل يسار الشاشة.
    """, unsafe_allow_html=True)

# --- إضافة نص تذييل الصفحة مع السنة الحالية ---
current_year_footer = datetime.now().year
st.markdown(f"""
<div style="margin-top: 50px; padding: 15px; text-align: center; color: #888; font-size: 0.8em; border-top: 1px solid #eee;">
    © قسم القراءات - جامعة الطائف {current_year_footer}
</div>
""", unsafe_allow_html=True)
