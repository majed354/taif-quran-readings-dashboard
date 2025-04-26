# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os # تأكد من وجود هذا الاستيراد

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="إنجاز المهام | قسم القراءات",
    page_icon="🏆",
    layout="wide"
)

# --- CSS و HTML للقائمة العلوية المتجاوبة (RTL) ---
# ملاحظة: تم إبقاء الكود كما هو لأنه لا يسبب الخطأ
responsive_menu_html_css = '''
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
        width: 100%; box-sizing: border-box; display: none;
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
    .back-to-top { position: fixed; bottom: 15px; left: 15px; width: 35px; height: 35px; background-color: #1e88e5; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; z-index: 998; cursor: pointer; box-shadow: 0 2px 5px rgba(0,0,0,0.2); opacity: 0; transition: opacity 0.3s, transform 0.3s; transform: scale(0); }
    .back-to-top.visible { opacity: 1; transform: scale(1); }
    .back-to-top span { font-size: 1rem; }

    /* --- قواعد Media Query للتبديل بين القائمتين وتحسين عرض الجوال --- */
    @media only screen and (max-width: 768px) {
        .top-navbar { display: none; }
        .mobile-menu-trigger { display: block; }
        .main .block-container { padding-right: 0.8rem !important; padding-left: 0.8rem !important; padding-top: 40px !important; }
        h1 { font-size: 1.3rem; margin-bottom: 15px; padding-bottom: 8px; }
        h2 { font-size: 1.1rem; margin-top: 20px; margin-bottom: 10px; }
        h3 { font-size: 1.0rem; margin-top: 18px; margin-bottom: 8px; }
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

<nav class="top-navbar">
    <ul>
        <li><a href="/">🏠 الرئيسية</a></li>
        <li><a href="/هيئة_التدريس">👥 هيئة التدريس</a></li>
        <li><a href="/إنجاز_المهام">🏆 إنجاز المهام</a></li>
        <li><a href="/بكالوريوس_القرآن_وعلومه">📚 بكالوريوس القرآن وعلومه</a></li>
        <li><a href="/بكالوريوس_القراءات">📖 بكالوريوس القراءات</a></li>
        <li><a href="/ماجستير_الدراسات_القرآنية">🎓 ماجستير الدراسات القرآنية</a></li>
        <li><a href="/ماجستير_القراءات">📜 ماجستير القراءات</a></li>
        <li><a href="/دكتوراه_علوم_القرآن">🔍 دكتوراه علوم القرآن</a></li>
        <li><a href="/دكتوراه_القراءات">📘 دكتوراه القراءات</a></li>
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
        <li><a href="/بكالوريوس_القرآن_وعلومه">📚 بكالوريوس القرآن وعلومه</a></li>
        <li><a href="/بكالوريوس_القراءات">📖 بكالوريوس القراءات</a></li>
        <li><a href="/ماجستير_الدراسات_القرآنية">🎓 ماجستير الدراسات القرآنية</a></li>
        <li><a href="/ماجستير_القراءات">📜 ماجستير القراءات</a></li>
        <li><a href="/دكتوراه_علوم_القرآن">🔍 دكتوراه علوم القرآن</a></li>
        <li><a href="/دكتوراه_القراءات">📘 دكتوراه القراءات</a></li>
    </ul>
</div>

<div class="back-to-top" onclick="scrollToTop()">
    <span style="font-size: 1.2rem;">↑</span>
</div>

<script>
    // منطق التمرير إلى الأعلى
    window.scrollToTop = function() {
        try { window.scrollTo({ top: 0, behavior: 'smooth' }); }
        catch(e){ console.error("خطأ في التمرير للأعلى:", e); }
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
'''

# تطبيق CSS والقائمة المتجاوبة
st.markdown(responsive_menu_html_css, unsafe_allow_html=True)

# --- العنوان الرئيسي للصفحة ---
st.markdown("<h1>🏆 إنجاز المهام</h1>", unsafe_allow_html=True)

# =========================================
# القسم 1: الدوال المساعدة (إذا لزم الأمر)
# =========================================
# يمكن وضع الدوال المساعدة هنا إذا كانت مشتركة بين الصفحات
# def load_data(year):
#     # تحميل البيانات للسنة المحددة
#     pass

# --- قاموس رموز البرامج (إذا استخدم في هذه الصفحة) ---
# PROGRAM_MAP = { ... }

# =========================================
# القسم 2: منتقي السنة (إذا لزم الأمر)
# =========================================
# أمثلة للسنوات المتاحة (يجب استبدالها بالتحميل الفعلي أو قائمة ديناميكية)
AVAILABLE_YEARS = list(range(2022, 2026))
selected_year = st.selectbox("اختر السنة", AVAILABLE_YEARS[::-1])

# =========================================
# القسم 3: محتوى التبويبات أو الصفحة
# =========================================

    main_tabs = st.tabs(["الإنجازات", "التحليلات البيانية", "تقرير الشارات"])
    with main_tabs[0]:
        st.info("محتوى الإنجازات سيضاف لاحقاً")
    with main_tabs[1]:
        st.info("محتوى التحليلات سيضاف لاحقاً")
    with main_tabs[2]:
        st.info("محتوى تقرير الشارات سيضاف لاحقاً")


# مثال لمحتوى بديل إذا لم تكن هناك تبويبات
# if not ("إنجاز_المهام" == "هيئة_التدريس" or "إنجاز_المهام" == "إنجاز_المهام" or "None" is not None):
#     st.write(f"محتوى صفحة 'إنجاز المهام' قيد الإنشاء.")
#     # يمكنك إضافة تحميل بيانات أو رسوم بيانية هنا بناءً على selected_year


# =========================================
# القسم 4: نصائح الاستخدام
# =========================================
with st.expander("💡 نصائح للاستخدام", expanded=False):
    st.markdown("""

    - **منتقي السنة:** يمكنك اختيار السنة لعرض بيانات تلك السنة.
    - **شريط التنقل العلوي:** يعرض الأقسام الرئيسية والبرامج الأكاديمية.
    - **على الجوال:** تظهر القائمة بشكل رأسي عند النقر على أيقونة القائمة (☰).
    - **زر العودة للأعلى:** انقر على زر السهم ↑ في أسفل الصفحة للعودة إلى أعلى الصفحة بسرعة.
    
    """, unsafe_allow_html=True) # استخدم unsafe_allow_html=True إذا كان النص يحتوي على HTML

# --- إضافة نص تذييل الصفحة ---
st.markdown("""
<div style="margin-top: 50px; text-align: center; color: #888; font-size: 0.75em;">
    © كلية القرآن الكريم والدراسات الإسلامية - جامعة الطائف {{0}}
</div>
""".format(datetime.now().year), unsafe_allow_html=True)
