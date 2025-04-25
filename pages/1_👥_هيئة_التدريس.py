# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import hashlib
import os

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="هيئة التدريس | قسم القراءات",
    page_icon="👥",
    layout="wide"
)

# --- CSS و HTML للقائمة العلوية المتجاوبة (RTL) - مأخوذ من الكود الرئيسي ---
# (نفس الكود المستخدم في Home.py لضمان التناسق)
responsive_menu_html_css = """
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

    /* --- تنسيقات خاصة بصفحة هيئة التدريس --- */
    .faculty-profile-card {
        background-color: white;
        border-radius: 8px; /* تناسق مع البطاقات الأخرى */
        border-right: 4px solid #1e88e5;
        padding: 15px; /* تقليل الحشو قليلاً */
        margin-bottom: 12px; /* تناسق مع البطاقات الأخرى */
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08); /* تناسق مع البطاقات الأخرى */
        display: flex;
        flex-direction: row;
        align-items: flex-start;
    }
    .profile-avatar {
        width: 65px; /* تصغير الأفاتار */
        height: 65px;
        border-radius: 50%;
        background-color: #f0f2f6;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.8rem; /* تصغير خط الأفاتار */
        color: #1e88e5;
        margin-left: 12px; /* تقليل الهامش */
        flex-shrink: 0;
    }
    .profile-info { flex-grow: 1; }
    .profile-name {
        font-size: 1.1rem; /* تصغير خط الاسم */
        font-weight: 600;
        color: #1e88e5;
        margin-bottom: 3px; /* تقليل الهامش */
    }
    .profile-title {
        font-size: 0.85rem; /* تصغير خط اللقب */
        color: #666;
        margin-bottom: 8px; /* تقليل الهامش */
    }
    .profile-details { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 5px; }
    .profile-detail-item {
        font-size: 0.8rem; /* تصغير خط التفاصيل */
        background-color: #f0f2f6;
        padding: 3px 6px; /* تقليل الحشو */
        border-radius: 4px;
        white-space: nowrap;
    }
    .profile-metrics { display: flex; gap: 10px; margin-top: 8px; }
    .profile-metric { text-align: center; flex-grow: 1; padding: 4px; border-radius: 5px; background-color: rgba(30, 136, 229, 0.05); }
    .profile-metric-value {
        font-size: 1.1rem; /* تصغير خط قيمة المقياس */
        font-weight: bold;
        color: #1e88e5;
    }
    .profile-metric-label {
        font-size: 0.75rem; /* تصغير خط تسمية المقياس */
        color: #666;
    }

    /* تنسيق شارات المؤشرات */
    .badge { display: inline-block; padding: 3px 8px; border-radius: 10px; font-size: 0.75rem; font-weight: 500; margin-right: 4px; } /* تصغير الخط والهامش */
    .badge-blue { background-color: rgba(30, 136, 229, 0.1); color: #1e88e5; }
    .badge-green { background-color: rgba(39, 174, 96, 0.1); color: #27AE60; }
    .badge-orange { background-color: rgba(243, 156, 18, 0.1); color: #F39C12; }
    .badge-red { background-color: rgba(231, 76, 60, 0.1); color: #E74C3C; }

    /* تنسيق الترقيات والأعضاء الجدد والمغادرين */
    .changes-container { 
        margin-top: 20px; 
        padding: 10px; 
        background-color: rgba(240, 240, 240, 0.3);
        border-radius: 8px;
        border: 1px solid #eee;
    }
    .changes-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #666;
        margin-bottom: 10px;
    }
    .changes-item {
        padding: 8px; 
        margin-bottom: 8px; 
        border-radius: 5px;
    }
    .new-member {
        border-right: 3px solid #27AE60; 
        background-color: rgba(39, 174, 96, 0.1);
    }
    .departed-member {
        border-right: 3px solid #E74C3C; 
        background-color: rgba(231, 76, 60, 0.1);
    }
    .promotion-item {
        border-right: 3px solid #1e88e5; 
        background-color: rgba(30, 136, 229, 0.1);
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

        /* تصغير خطوط بطاقات هيئة التدريس والإنجازات في الجوال */
        .faculty-card h5 { font-size: 0.9rem !important; margin-bottom: 2px !important; }
        .faculty-card p { font-size: 0.8em !important; }
        .achievement-item p:first-of-type { font-size: 0.85em !important; margin-bottom: 1px !important; }
        .achievement-item p:nth-of-type(2) { font-size: 0.8em !important; margin-bottom: 1px !important; }
        .achievement-item p:last-of-type { font-size: 0.7em !important; }

         /* تصغير خطوط التبويبات */
        button[data-baseweb="tab"] {
            font-size: 0.85rem !important;
            padding-top: 8px !important;
            padding-bottom: 8px !important;
        }
         /* تصغير خط منتقي السنة والفلاتر الأخرى */
        .stSelectbox label { font-size: 0.9rem !important; }
        .stTextInput label { font-size: 0.9rem !important; } /* لفلتر البحث */

        /* تجاوب بطاقة العضو للشاشات الصغيرة */
        .faculty-profile-card {
            flex-direction: column;
            padding: 12px; /* تعديل الحشو للجوال */
        }
        .profile-avatar {
            width: 55px; /* تصغير الأفاتار أكثر للجوال */
            height: 55px;
            font-size: 1.5rem;
            margin-left: 0;
            margin-bottom: 10px; /* تقليل الهامش */
            align-self: center;
        }
        .profile-name { font-size: 1rem; } /* تصغير اسم العضو للجوال */
        .profile-title { font-size: 0.8rem; margin-bottom: 6px; } /* تصغير اللقب للجوال */
        .profile-details { gap: 5px; } /* تقليل الفجوة */
        .profile-detail-item { font-size: 0.75rem; padding: 2px 5px;} /* تصغير خط وحشو التفاصيل للجوال */
        .profile-metrics { flex-direction: row; gap: 8px; } /* جعل المقاييس أفقية مرة أخرى ولكن بفجوة أقل */
        .profile-metric-value { font-size: 1rem; } /* تصغير قيمة المقياس للجوال */
        .profile-metric-label { font-size: 0.7rem; } /* تصغير تسمية المقياس للجوال */

        /* تصغير خطوط بيانات التغييرات */
        .changes-container { padding: 8px; }
        .changes-title { font-size: 0.9rem; margin-bottom: 8px; }
        .changes-item { padding: 6px; margin-bottom: 6px; }
        .changes-item h4 { font-size: 0.85rem !important; margin: 0 !important; }
        .changes-item p { font-size: 0.75rem !important; margin: 2px 0 !important; }
    }

    @media only screen and (min-width: 769px) {
        .top-navbar { display: block; } /* إظهار القائمة العلوية في شاشات اللابتوب والأكبر */
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
# تطبيق القائمة العلوية و CSS العام وزر العودة للأعلى
st.markdown(responsive_menu_html_css, unsafe_allow_html=True)

# --- العنوان الرئيسي للصفحة ---
st.markdown("<h1>👥 هيئة التدريس</h1>", unsafe_allow_html=True)

# --- دوال مساعدة ---
# --- دوال مساعدة ---
def is_mobile():
    """التحقق من كون العرض الحالي محتملاً أن يكون جهاز محمول"""
    # ملاحظة: هذه الدالة تحتاج إلى طريقة لتحديد عرض الشاشة بشكل فعلي.
    # يمكنك استخدام مكون مثل streamlit_js_eval أو اختبار العرض يدويًا بتغيير حجم المتصفح.
    # حاليًا، ستُرجع False دائمًا.
    return False # غير القيمة إلى True لاختبار تنسيقات الجوال

def prepare_chart_layout(fig, title, is_mobile=False, chart_type="bar"):
    """تطبيق تنسيق موحد على مخططات Plotly مع الاستجابة للجوال (نفس دالة الصفحة الرئيسية)"""
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

        # تعديلات خاصة بالجوال (تم تحسينها)
        if is_mobile:
            mobile_settings = {
                "height": 260 if chart_type != "heatmap" else 300, # تصغير الارتفاع أكثر
                "margin": {"t": 30, "b": 60, "l": 5, "r": 5, "pad": 0}, # تقليل الهوامش أكثر
                "font": {"size": 8}, # تصغير الخط أكثر
                "title": {"font": {"size": 10}}, # تصغير خط العنوان أكثر
                "legend": {"y": -0.3, "font": {"size": 7}} # تصغير خط وسيلة الإيضاح وتحريكها
            }
            layout_settings.update(mobile_settings)

            # تعديلات خاصة بنوع المخطط للجوال
            if chart_type == "pie":
                layout_settings["showlegend"] = False
                fig.update_traces(textfont_size=8) # تصغير خط النص داخل الدائري
            elif chart_type == "line":
                fig.update_traces(marker=dict(size=3)) # تصغير حجم العلامات
            elif chart_type == "bar":
                # تعديل زاوية الخط للمحور السيني في الجوال إذا كان عموديًا
                if fig.layout.orientation is None or fig.layout.orientation == 'v':
                     fig.update_xaxes(tickangle=-45, tickfont={"size": 7}) # تعديل الزاوية وتصغير الخط
                else: # إذا كان أفقيًا
                     fig.update_xaxes(tickfont={"size": 7})
                fig.update_yaxes(tickfont={"size": 7}) # تصغير خط المحور الصادي
            elif chart_type == "heatmap":
                 fig.update_traces(textfont={"size": 8}) # تصغير خط النص داخل الخريطة الحرارية
                 fig.update_yaxes(tickfont=dict(size=7)) # تصغير خط المحور الصادي للخريطة الحرارية
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
            elif chart_type == "bar": # إعادة زاوية الخط للوضع الافتراضي لسطح المكتب
                 fig.update_xaxes(tickangle=0)


        fig.update_layout(**layout_settings)
    except Exception as e:
        st.warning(f"تعذر تطبيق إعدادات التخطيط للرسم '{title}': {e}")

    return fig


def get_avatar_placeholder(name):
    """توليد حرف أولي من الاسم لاستخدامه كصورة افتراضية"""
    if not name or len(name) == 0:
        return "👤"
    # الحصول على الحرف الأول من الاسم بعد تجاوز أي بادئات شائعة
    parts = name.split()
    if len(parts) > 1 and parts[0] in ['د.', 'أ.', 'أ.د.', 'م.']:
        initial = parts[1][0] if len(parts[1]) > 0 else parts[0][0]
    else:
        initial = parts[0][0] if len(parts) > 0 and len(parts[0]) > 0 else "؟"
    return initial

# --- دوال تحميل البيانات ---
@st.cache_data(ttl=3600)
def load_faculty_data(year=None):
    """تحميل بيانات أعضاء هيئة التدريس للسنة المحددة"""
    try:
        available_years = list(range(2022, 2026)) # يتم تحديث السنوات المتوفرة حسب الملفات المتاحة

        if year is None:
            year = max(available_years)

        # المسار بناءً على هيكل المستودع والسنة
        file_path = f"data/department/{year}/faculty_{year}.csv"

        # التحقق من وجود الملف، وإلا حاول تحميل الملف القديم
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df["year"] = year # إضافة عمود السنة للتمييز لاحقاً
            return df
        else:
            # إذا لم يجد ملف السنة المحددة، ابحث عن أقرب سنة متاحة
            for y in sorted(available_years, reverse=True):
                alt_file_path = f"data/department/{y}/faculty_{y}.csv"
                if os.path.exists(alt_file_path):
                    st.warning(f"بيانات سنة {year} غير متوفرة. تم تحميل بيانات سنة {y} بدلاً عنها.")
                    df = pd.read_csv(alt_file_path)
                    df["year"] = y # إضافة عمود السنة الفعلية
                    return df

            # إذا لم يجد أي ملف، استخدم بيانات تجريبية
            st.warning(f"بيانات سنة {year} غير متوفرة. استخدام بيانات تجريبية.")
            return generate_sample_faculty_data(year)

    except Exception as e:
        st.error(f"خطأ في تحميل بيانات أعضاء هيئة التدريس: {e}")
        return pd.DataFrame()

def generate_sample_faculty_data(year):
    """توليد بيانات تجريبية عند عدم وجود ملف"""
    # بيانات تجريبية لأعضاء هيئة التدريس
    data = [
        {"الاسم": "د. محمد أحمد علي", "الرتبة": "أستاذ مشارك", "التخصص": "قراءات", "حالة الموظف": "رأس العمل", "الجنس": "ذكر", "الجنسية": "سعودي", "البريد الإلكتروني": "m.ahmed@example.edu", "عدد البحوث": 12},
        {"الاسم": "د. عائشة محمد سعيد", "الرتبة": "أستاذ", "التخصص": "علوم القرآن", "حالة الموظف": "رأس العمل", "الجنس": "أنثى", "الجنسية": "سعودية", "البريد الإلكتروني": "a.saeed@example.edu", "عدد البحوث": 18},
        {"الاسم": "د. عبدالله محمد خالد", "الرتبة": "أستاذ مساعد", "التخصص": "قراءات", "حالة الموظف": "رأس العمل", "الجنس": "ذكر", "الجنسية": "سعودي", "البريد الإلكتروني": "a.khalid@example.edu", "عدد البحوث": 8},
        {"الاسم": "د. فاطمة علي حسن", "الرتبة": "أستاذ مشارك", "التخصص": "الدراسات القرآنية", "حالة الموظف": "رأس العمل", "الجنس": "أنثى", "الجنسية": "سعودية", "البريد الإلكتروني": "f.hassan@example.edu", "عدد البحوث": 15},
        {"الاسم": "د. خالد إبراهيم عمر", "الرتبة": "أستاذ", "التخصص": "قراءات", "حالة الموظف": "متعاون", "الجنس": "ذكر", "الجنسية": "مصري", "البريد الإلكتروني": "k.ibrahim@example.edu", "عدد البحوث": 22},
        {"الاسم": "د. نورا سعيد أحمد", "الرتبة": "أستاذ مساعد", "التخصص": "علوم القرآن", "حالة الموظف": "رأس العمل", "الجنس": "أنثى", "الجنسية": "سعودية", "البريد الإلكتروني": "n.ahmed@example.edu", "عدد البحوث": 6},
        {"الاسم": "د. ياسر محمود علي", "الرتبة": "محاضر", "التخصص": "قراءات", "حالة الموظف": "رأس العمل", "الجنس": "ذكر", "الجنسية": "سعودي", "البريد الإلكتروني": "y.mahmoud@example.edu", "عدد البحوث": 4},
        {"الاسم": "د. هدى سالم مبارك", "الرتبة": "أستاذ مساعد", "التخصص": "الدراسات القرآنية", "حالة الموظف": "رأس العمل", "الجنس": "أنثى", "الجنسية": "سعودية", "البريد الإلكتروني": "h.mubarak@example.edu", "عدد البحوث": 7},
        {"الاسم": "أ. عمر سعد الدين", "الرتبة": "معيد", "التخصص": "قراءات", "حالة الموظف": "رأس العمل", "الجنس": "ذكر", "الجنسية": "سعودي", "البريد الإلكتروني": "o.saadeddin@example.edu", "عدد البحوث": 2}
    ]
    df = pd.DataFrame(data)
    df["year"] = year
    return df

# --- دالة لتحميل بيانات السنة السابقة للمقارنة ---
@st.cache_data(ttl=3600)
def load_previous_year_data(current_year):
    """تحميل بيانات السنة السابقة للمقارنة"""
    previous_year = current_year - 1

    try:
        file_path = f"data/department/{previous_year}/faculty_{previous_year}.csv"
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df["year"] = previous_year # إضافة عمود السنة
            return df
        else:
            # توليد بيانات تجريبية للسنة السابقة إذا لم توجد
            return generate_sample_faculty_data(previous_year)
    except Exception as e:
        st.error(f"خطأ في تحميل بيانات السنة السابقة: {e}")
        return None

# --- دالة لتحليل التغييرات بين السنوات ---
def analyze_faculty_changes(current_data, previous_data):
    """تحليل التغييرات في هيئة التدريس بين السنتين"""
    if previous_data is None or current_data.empty or previous_data.empty:
        return None, None, None, 0

    # استخراج الأسماء من كل مجموعة بيانات
    current_names = set(current_data["الاسم"].tolist())
    previous_names = set(previous_data["الاسم"].tolist())

    # تحديد الأعضاء الجدد والمغادرين
    new_members = current_names - previous_names
    departed_members = previous_names - current_names

    # الأعضاء المستمرين (موجودين في كلا السنتين)
    continuing_members = current_names.intersection(previous_names)

    # البحث عن ترقيات (تغيير في الرتبة الأكاديمية)
    promotions = []
    for member in continuing_members:
        # تأكد من وجود العضو في كلا الإطارين قبل محاولة الوصول إلى الرتبة
        current_member_data = current_data[current_data["الاسم"] == member]
        previous_member_data = previous_data[previous_data["الاسم"] == member]
        if not current_member_data.empty and not previous_member_data.empty:
            current_rank = current_member_data["الرتبة"].iloc[0]
            previous_rank = previous_member_data["الرتبة"].iloc[0]

            if current_rank != previous_rank:
                promotions.append({
                    "الاسم": member,
                    "الرتبة السابقة": previous_rank,
                    "الرتبة الحالية": current_rank
                })

    # إجمالي البحوث في السنة الحالية مقارنة بالسنة السابقة
    current_research_total = current_data["عدد البحوث"].sum() if "عدد البحوث" in current_data.columns else 0
    previous_research_total = previous_data["عدد البحوث"].sum() if "عدد البحوث" in previous_data.columns else 0
    research_increase = current_research_total - previous_research_total

    # الأعضاء المضافين (الجدد) مع بياناتهم الكاملة
    new_members_data = current_data[current_data["الاسم"].isin(new_members)]

    # الأعضاء المغادرين مع بياناتهم الكاملة
    departed_members_data = previous_data[previous_data["الاسم"].isin(departed_members)]

    return new_members_data, departed_members_data, promotions, research_increase

@st.cache_data(ttl=3600)
def load_faculty_achievements():
    """تحميل بيانات إنجازات أعضاء هيئة التدريس"""
    try:
        file_path = "data/department/achievements_latest.csv"
        if os.path.exists(file_path):
            return pd.read_csv(file_path)
        else:
            # بيانات إنجازات تجريبية
            achievements = [
                {"العضو": "د. محمد أحمد علي", "الإنجاز": "نشر بحث في مجلة عالمية", "التاريخ": "2025-04-15", "النقاط": 50},
                {"العضو": "د. عائشة محمد سعيد", "الإنجاز": "إطلاق مبادرة تعليمية", "التاريخ": "2025-04-10", "النقاط": 40},
                {"العضو": "د. عبدالله محمد خالد", "الإنجاز": "المشاركة في مؤتمر دولي", "التاريخ": "2025-04-05", "النقاط": 35},
                {"العضو": "د. فاطمة علي حسن", "الإنجاز": "تطوير مقرر دراسي", "التاريخ": "2025-04-01", "النقاط": 30},
                {"العضو": "د. خالد إبراهيم عمر", "الإنجاز": "تقديم ورشة عمل", "التاريخ": "2025-03-25", "النقاط": 25},
                {"العضو": "د. نورا سعيد أحمد", "الإنجاز": "تأليف كتاب", "التاريخ": "2025-03-20", "النقاط": 60},
                {"العضو": "د. ياسر محمود علي", "الإنجاز": "إعداد دورة تدريبية", "التاريخ": "2025-03-15", "النقاط": 20},
                {"العضو": "د. هدى سالم مبارك", "الإنجاز": "المشاركة في لجنة علمية", "التاريخ": "2025-03-10", "النقاط": 15},
                {"العضو": "أ. عمر سعد الدين", "الإنجاز": "تقديم محاضرة عامة", "التاريخ": "2025-03-05", "النقاط": 10},
            ]
            return pd.DataFrame(achievements)
    except Exception as e:
        st.error(f"خطأ في تحميل بيانات الإنجازات: {e}")
        return pd.DataFrame()

# --- تحديد عرض الجوال ---
mobile_view = is_mobile()

# --- محتوى صفحة هيئة التدريس ---

# --- إضافة منتقي السنة ---
YEAR_LIST = list(range(2022, 2026)) # تُحدَّث سنويًا
selected_year = st.selectbox("اختر السنة", YEAR_LIST[::-1], index=0) # القيمة الافتراضية هي أحدث سنة

# --- تحميل البيانات ---
faculty_data = load_faculty_data(selected_year)

# تحميل بيانات السنة السابقة للمقارنة
previous_year = selected_year - 1
previous_year_data = load_previous_year_data(selected_year)

# تحليل التغييرات بين السنتين (إذا كانت البيانات السابقة متوفرة)
new_members_data, departed_members_data, promotions, research_increase = analyze_faculty_changes(faculty_data, previous_year_data)

# تحميل بيانات الإنجازات
faculty_achievements = load_faculty_achievements()

if faculty_data.empty:
    st.warning("لا تتوفر بيانات أعضاء هيئة التدريس. يرجى التحقق من مصدر البيانات.")
else:
    # --- المقاييس الإجمالية (مع إضافة الدلتا للمقارنة مع السنة السابقة) ---
    st.subheader("نظرة عامة") # عنوان فرعي للمقاييس
    
    # حساب قيم المقاييس الحالية
    total_faculty = len(faculty_data)
    male_count = len(faculty_data[faculty_data["الجنس"] == "ذكر"])
    female_count = len(faculty_data[faculty_data["الجنس"] == "أنثى"])
    total_research = faculty_data["عدد البحوث"].sum() if "عدد البحوث" in faculty_data.columns else 0
    
    # حساب قيم السنة السابقة إذا كانت متوفرة
    prev_total_faculty = len(previous_year_data) if previous_year_data is not None else None
    prev_male_count = len(previous_year_data[previous_year_data["الجنس"] == "ذكر"]) if previous_year_data is not None else None
    prev_female_count = len(previous_year_data[previous_year_data["الجنس"] == "أنثى"]) if previous_year_data is not None else None
    prev_total_research = previous_year_data["عدد البحوث"].sum() if previous_year_data is not None and "عدد البحوث" in previous_year_data.columns else None
    
    # حساب الفروقات (الدلتا)
    delta_total = total_faculty - prev_total_faculty if prev_total_faculty is not None else None
    delta_male = male_count - prev_male_count if prev_male_count is not None else None
    delta_female = female_count - prev_female_count if prev_female_count is not None else None
    delta_research = total_research - prev_total_research if prev_total_research is not None else None

    # عرض المقاييس في صف (أو 2x2 في الجوال)
    if mobile_view:
        row1_cols = st.columns(2)
        row2_cols = st.columns(2)
        metric_cols = [row1_cols[0], row1_cols[1], row2_cols[0], row2_cols[1]]
    else:
        metric_cols = st.columns(4)

    # إضافة المقاييس مع الدلتا
    with metric_cols[0]:
        st.metric("إجمالي الأعضاء", f"{total_faculty:,}", 
                 delta=f"{delta_total:+}" if delta_total is not None else None)
    with metric_cols[1]:
        st.metric("أعضاء (ذكور)", f"{male_count:,}", 
                 delta=f"{delta_male:+}" if delta_male is not None else None)
    with metric_cols[2]:
        st.metric("أعضاء (إناث)", f"{female_count:,}", 
                 delta=f"{delta_female:+}" if delta_female is not None else None)
    with metric_cols[3]:
        st.metric("إجمالي البحوث", f"{total_research:,}", 
                 delta=f"{delta_research:+}" if delta_research is not None else None)
    
    # عرض ملخص التغييرات (الأعضاء الجدد والمغادرين والترقيات) في قسم مطوي
    if previous_year_data is not None:
        with st.expander("📊 عرض تفاصيل التغييرات عن العام السابق", expanded=False):
            # هنا نضع تفاصيل التغييرات
            
            # حاوية للتغييرات
            st.markdown('<div class="changes-container">', unsafe_allow_html=True)
            
            # عرض الترقيات
            if promotions and len(promotions) > 0:
                st.markdown('<div class="changes-title">🔄 الترقيات الأكاديمية</div>', unsafe_allow_html=True)
                for promotion in promotions:
                    st.markdown(f"""
                    <div class="changes-item promotion-item">
                        <h4 style="margin: 0; font-size: 0.9rem; color: #1e88e5;">{promotion["الاسم"]}</h4>
                        <p style="margin: 3px 0; font-size: 0.8rem;">ترقية من {promotion["الرتبة السابقة"]} إلى {promotion["الرتبة الحالية"]}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # عرض الأعضاء الجدد
            if new_members_data is not None and len(new_members_data) > 0:
                st.markdown('<div class="changes-title">➕ الأعضاء الجدد</div>', unsafe_allow_html=True)
                for _, row in new_members_data.iterrows():
                    name = row.get("الاسم", "غير متوفر")
                    gender = row.get("الجنس", "")
                    rank = row.get("الرتبة", "")
                    spec = row.get("التخصص", "")

                    st.markdown(f"""
                    <div class="changes-item new-member">
                        <h4 style="margin: 0; font-size: 0.9rem; color: #27AE60;">{name}</h4>
                        <p style="margin: 3px 0; font-size: 0.8rem;">{rank} - {spec} - {gender}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # عرض الأعضاء المغادرين
            if departed_members_data is not None and len(departed_members_data) > 0:
                st.markdown('<div class="changes-title">➖ الأعضاء المغادرون</div>', unsafe_allow_html=True)
                for _, row in departed_members_data.iterrows():
                    name = row.get("الاسم", "غير متوفر")
                    gender = row.get("الجنس", "")
                    rank = row.get("الرتبة", "")
                    spec = row.get("التخصص", "")

                    st.markdown(f"""
                    <div class="changes-item departed-member">
                        <h4 style="margin: 0; font-size: 0.9rem; color: #E74C3C;">{name}</h4>
                        <p style="margin: 3px 0; font-size: 0.8rem;">{rank} - {spec} - {gender}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # إغلاق حاوية التغييرات
            st.markdown('</div>', unsafe_allow_html=True)
            
            # عرض مقارنة التوزيع حسب الرتبة
            if "الرتبة" in faculty_data.columns and "الرتبة" in previous_year_data.columns:
                st.markdown("### مقارنة التوزيع حسب الرتبة")
                
                current_rank_counts = faculty_data["الرتبة"].value_counts().reset_index()
                current_rank_counts.columns = ["الرتبة", "العدد"]
                current_rank_counts["السنة"] = selected_year

                previous_rank_counts = previous_year_data["الرتبة"].value_counts().reset_index()
                previous_rank_counts.columns = ["الرتبة", "العدد"]
                previous_rank_counts["السنة"] = previous_year

                # دمج البيانات للمقارنة
                rank_comparison = pd.concat([previous_rank_counts, current_rank_counts])

                # رسم بياني للمقارنة
                fig_rank_compare = px.bar(
                    rank_comparison,
                    x="الرتبة",
                    y="العدد",
                    color="السنة",
                    title="مقارنة أعداد أعضاء هيئة التدريس حسب الرتبة",
                    barmode="group",
                    color_discrete_sequence=["#777777", "#1e88e5"]
                )
                fig_rank_compare = prepare_chart_layout(fig_rank_compare, "مقارنة حسب الرتبة", is_mobile=mobile_view, chart_type="bar")
                st.plotly_chart(fig_rank_compare, use_container_width=True, config={"displayModeBar": False})
                
                # مقارنة عدد الذكور والإناث
                st.markdown("### مقارنة التوزيع حسب الجنس")
                gender_comparison = pd.DataFrame({
                    "السنة": [previous_year, selected_year],
                    "ذكور": [prev_male_count, male_count],
                    "إناث": [prev_female_count, female_count]
                })

                # رسم بياني للمقارنة
                fig_gender_compare = px.bar(
                    gender_comparison,
                    x="السنة",
                    y=["ذكور", "إناث"],
                    title="مقارنة أعداد أعضاء هيئة التدريس حسب الجنس",
                    barmode="group",
                    color_discrete_sequence=["#1e88e5", "#E83E8C"]
                )
                fig_gender_compare = prepare_chart_layout(fig_gender_compare, "مقارنة حسب الجنس", is_mobile=mobile_view, chart_type="bar")
                st.plotly_chart(fig_gender_compare, use_container_width=True, config={"displayModeBar": False})

    # --- تحليلات هيئة التدريس ---
    st.subheader("توزيع أعضاء هيئة التدريس")

    # تحليل البيانات لتجهيز الرسوم
    rank_distribution = None
    specialization_distribution = None
    status_distribution = None
    nationality_distribution = None

    if "الرتبة" in faculty_data.columns:
        rank_distribution = faculty_data["الرتبة"].value_counts().reset_index()
        rank_distribution.columns = ["الرتبة", "العدد"]

    if "التخصص" in faculty_data.columns:
        specialization_distribution = faculty_data["التخصص"].value_counts().reset_index()
        specialization_distribution.columns = ["التخصص", "العدد"]

    if "حالة الموظف" in faculty_data.columns:
        status_distribution = faculty_data["حالة الموظف"].value_counts().reset_index()
        status_distribution.columns = ["حالة الموظف", "العدد"]

    if "الجنسية" in faculty_data.columns:
        nationality_distribution = faculty_data["الجنسية"].value_counts().reset_index()
        nationality_distribution.columns = ["الجنسية", "العدد"]

    # عرض الرسوم البيانية في تبويبات - تمت إزالة تبويب المقارنة السنوية
    tabs = st.tabs(["توزيع الرتب", "التخصصات", "حالة الموظف", "توزيع البحوث"])

    # التبويب 1: توزيع الرتب
    with tabs[0]:
        if rank_distribution is not None and not rank_distribution.empty:
            # تحديد تخطيط الأعمدة بناءً على عرض الشاشة
            if mobile_view:
                # رسم دائري لتوزيع الرتب الأكاديمية
                fig_rank_pie = px.pie(
                    rank_distribution,
                    values="العدد",
                    names="الرتبة",
                    title="توزيع الرتب الأكاديمية",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_rank_pie = prepare_chart_layout(fig_rank_pie, "توزيع الرتب الأكاديمية", is_mobile=mobile_view, chart_type="pie")
                st.plotly_chart(fig_rank_pie, use_container_width=True, config={"displayModeBar": False})

                st.markdown("---") # فاصل في الجوال

                # رسم شريطي للرتب حسب الجنس (عمودي في الجوال)
                if "الجنس" in faculty_data.columns:
                    gender_rank_df = pd.crosstab(faculty_data['الرتبة'], faculty_data['الجنس'])
                    fig_gender_rank = px.bar(
                        gender_rank_df,
                        barmode='group',
                        title="توزيع الرتب حسب الجنس",
                        labels={"value": "العدد", "الجنس": "الجنس", "الرتبة": "الرتبة"},
                        color_discrete_sequence=["#1e88e5", "#E83E8C"]
                    )
                    fig_gender_rank = prepare_chart_layout(fig_gender_rank, "توزيع الرتب حسب الجنس", is_mobile=mobile_view, chart_type="bar")
                    st.plotly_chart(fig_gender_rank, use_container_width=True, config={"displayModeBar": False})

            else: # عرض سطح المكتب
                col1, col2 = st.columns([1, 1])
                with col1:
                    fig_rank_pie = px.pie(rank_distribution, values="العدد", names="الرتبة", title="توزيع الرتب الأكاديمية", color_discrete_sequence=px.colors.qualitative.Pastel)
                    fig_rank_pie = prepare_chart_layout(fig_rank_pie, "توزيع الرتب الأكاديمية", is_mobile=mobile_view, chart_type="pie")
                    st.plotly_chart(fig_rank_pie, use_container_width=True, config={"displayModeBar": False})
                with col2:
                    if "الجنس" in faculty_data.columns:
                        gender_rank_df = pd.crosstab(faculty_data['الرتبة'], faculty_data['الجنس'])
                        fig_gender_rank = px.bar(gender_rank_df, barmode='group', title="توزيع الرتب حسب الجنس", labels={"value": "العدد", "الجنس": "الجنس", "الرتبة": "الرتبة"}, color_discrete_sequence=["#1e88e5", "#E83E8C"])
                        fig_gender_rank = prepare_chart_layout(fig_gender_rank, "توزيع الرتب حسب الجنس", is_mobile=mobile_view, chart_type="bar")
                        st.plotly_chart(fig_gender_rank, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("لا تتوفر بيانات كافية لعرض توزيع الرتب.")

    # التبويب 2: التخصصات
    with tabs[1]:
        if specialization_distribution is not None and not specialization_distribution.empty:
            if mobile_view:
                 # رسم دائري لتوزيع التخصصات
                fig_spec_pie = px.pie(specialization_distribution, values="العدد", names="التخصص", title="توزيع التخصصات الدقيقة", color_discrete_sequence=px.colors.qualitative.Set2)
                fig_spec_pie = prepare_chart_layout(fig_spec_pie, "توزيع التخصصات", is_mobile=mobile_view, chart_type="pie")
                st.plotly_chart(fig_spec_pie, use_container_width=True, config={"displayModeBar": False})

                st.markdown("---")

                # رسم توزيع التخصصات حسب الجنس (عمودي في الجوال)
                if "الجنس" in faculty_data.columns:
                    spec_gender_df = pd.crosstab(faculty_data['التخصص'], faculty_data['الجنس'])
                    fig_spec_gender = px.bar(spec_gender_df, barmode='group', title="التخصصات حسب الجنس", labels={"value": "العدد", "الجنس": "الجنس", "التخصص": "التخصص"}, color_discrete_sequence=["#1e88e5", "#E83E8C"])
                    fig_spec_gender = prepare_chart_layout(fig_spec_gender, "التخصصات حسب الجنس", is_mobile=mobile_view, chart_type="bar")
                    st.plotly_chart(fig_spec_gender, use_container_width=True, config={"displayModeBar": False})
            else: # عرض سطح المكتب
                col1, col2 = st.columns([1, 1])
                with col1:
                    fig_spec_pie = px.pie(specialization_distribution, values="العدد", names="التخصص", title="توزيع التخصصات الدقيقة", color_discrete_sequence=px.colors.qualitative.Set2)
                    fig_spec_pie = prepare_chart_layout(fig_spec_pie, "توزيع التخصصات", is_mobile=mobile_view, chart_type="pie")
                    st.plotly_chart(fig_spec_pie, use_container_width=True, config={"displayModeBar": False})
                with col2:
                    if "الجنس" in faculty_data.columns:
                        spec_gender_df = pd.crosstab(faculty_data['التخصص'], faculty_data['الجنس'])
                        fig_spec_gender = px.bar(spec_gender_df, barmode='group', title="التخصصات حسب الجنس", labels={"value": "العدد", "الجنس": "الجنس", "التخصص": "التخصص"}, color_discrete_sequence=["#1e88e5", "#E83E8C"])
                        fig_spec_gender = prepare_chart_layout(fig_spec_gender, "التخصصات حسب الجنس", is_mobile=mobile_view, chart_type="bar")
                        st.plotly_chart(fig_spec_gender, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("لا تتوفر بيانات كافية لعرض توزيع التخصصات.")

    # التبويب 3: حالة الموظف
    with tabs[2]:
        if status_distribution is not None and not status_distribution.empty:
            if mobile_view:
                # رسم شريطي عمودي لتوزيع الأعضاء حسب حالة الموظف في الجوال
                fig_status_bar = px.bar(
                    status_distribution.sort_values("العدد", ascending=False),
                    x="حالة الموظف",
                    y="العدد",
                    title="توزيع الأعضاء حسب حالة الموظف",
                    color="العدد",
                    color_continuous_scale="Blues"
                )
                fig_status_bar = prepare_chart_layout(fig_status_bar, "توزيع الأعضاء حسب حالة الموظف", is_mobile=mobile_view, chart_type="bar")
                st.plotly_chart(fig_status_bar, use_container_width=True, config={"displayModeBar": False})

                st.markdown("---")

                # رسم توزيع الرتب في كل حالة موظف (عمودي مكدس في الجوال)
                if rank_distribution is not None:
                    status_rank_df = pd.crosstab(faculty_data['حالة الموظف'], faculty_data['الرتبة'])
                    fig_status_rank = px.bar(
                        status_rank_df,
                        barmode='stack',
                        title="الرتب الأكاديمية حسب حالة الموظف",
                        labels={"value": "العدد", "الرتبة": "الرتبة", "حالة الموظف": "حالة الموظف"},
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig_status_rank = prepare_chart_layout(fig_status_rank, "الرتب حسب حالة الموظف", is_mobile=mobile_view, chart_type="bar")
                    st.plotly_chart(fig_status_rank, use_container_width=True, config={"displayModeBar": False})

            else: # عرض سطح المكتب
                col1, col2 = st.columns([1, 1])
                with col1:
                    # رسم شريطي أفقي لتوزيع الأعضاء حسب حالة الموظف
                    fig_status_bar = px.bar(status_distribution.sort_values("العدد", ascending=True), y="حالة الموظف", x="العدد", title="توزيع الأعضاء حسب حالة الموظف", color="العدد", orientation='h', color_continuous_scale="Blues")
                    fig_status_bar = prepare_chart_layout(fig_status_bar, "توزيع الأعضاء حسب حالة الموظف", is_mobile=mobile_view, chart_type="bar")
                    st.plotly_chart(fig_status_bar, use_container_width=True, config={"displayModeBar": False})
                with col2:
                     # رسم توزيع الرتب في كل حالة موظف
                    if rank_distribution is not None:
                        status_rank_df = pd.crosstab(faculty_data['حالة الموظف'], faculty_data['الرتبة'])
                        fig_status_rank = px.bar(status_rank_df, barmode='stack', title="الرتب الأكاديمية حسب حالة الموظف", labels={"value": "العدد", "الرتبة": "الرتبة", "حالة الموظف": "حالة الموظف"}, color_discrete_sequence=px.colors.qualitative.Pastel)
                        fig_status_rank = prepare_chart_layout(fig_status_rank, "الرتب حسب حالة الموظف", is_mobile=mobile_view, chart_type="bar")
                        st.plotly_chart(fig_status_rank, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("لا تتوفر بيانات كافية لعرض توزيع حالة الموظف.")

    # التبويب 4: توزيع البحوث
    with tabs[3]:
        if "عدد البحوث" in faculty_data.columns:
            if mobile_view:
                 # رسم شريطي عمودي لمتوسط البحوث حسب الرتبة في الجوال
                research_by_rank = faculty_data.groupby("الرتبة")["عدد البحوث"].mean().reset_index()
                research_by_rank.columns = ["الرتبة", "متوسط عدد البحوث"]
                fig_research_rank = px.bar(research_by_rank.sort_values("متوسط عدد البحوث", ascending=False), x="الرتبة", y="متوسط عدد البحوث", title="متوسط البحوث حسب الرتبة", color="متوسط عدد البحوث", color_continuous_scale="Greens")
                fig_research_rank = prepare_chart_layout(fig_research_rank, "متوسط البحوث حسب الرتبة", is_mobile=mobile_view, chart_type="bar")
                st.plotly_chart(fig_research_rank, use_container_width=True, config={"displayModeBar": False})

                st.markdown("---")

                # رسم شريطي عمودي لإجمالي البحوث حسب الجنس في الجوال
                research_by_gender = faculty_data.groupby("الجنس")["عدد البحوث"].sum().reset_index()
                research_by_gender.columns = ["الجنس", "إجمالي البحوث"]
                fig_research_gender = px.bar(research_by_gender, x="الجنس", y="إجمالي البحوث", title="إجمالي البحوث حسب الجنس", color="إجمالي البحوث", color_continuous_scale="Greens")
                fig_research_gender = prepare_chart_layout(fig_research_gender, "إجمالي البحوث حسب الجنس", is_mobile=mobile_view, chart_type="bar")
                st.plotly_chart(fig_research_gender, use_container_width=True, config={"displayModeBar": False})

                st.markdown("---")

                 # رسم توزيع حجم البحوث (الهستوجرام)
                fig_research_hist = px.histogram(faculty_data, x="عدد البحوث", title="توزيع عدد البحوث للأعضاء", color_discrete_sequence=["#1e88e5"])
                fig_research_hist.update_layout(bargap=0.2)
                fig_research_hist = prepare_chart_layout(fig_research_hist, "توزيع عدد البحوث", is_mobile=mobile_view, chart_type="bar")
                st.plotly_chart(fig_research_hist, use_container_width=True, config={"displayModeBar": False})

            else: # عرض سطح المكتب
                col1, col2 = st.columns([1, 1])
                with col1:
                    # رسم شريطي لمتوسط البحوث حسب الرتبة
                    research_by_rank = faculty_data.groupby("الرتبة")["عدد البحوث"].mean().reset_index()
                    research_by_rank.columns = ["الرتبة", "متوسط عدد البحوث"]
                    fig_research_rank = px.bar(research_by_rank.sort_values("متوسط عدد البحوث", ascending=True), y="الرتبة", x="متوسط عدد البحوث", title="متوسط البحوث حسب الرتبة", color="متوسط عدد البحوث", orientation='h', color_continuous_scale="Greens")
                    fig_research_rank = prepare_chart_layout(fig_research_rank, "متوسط البحوث حسب الرتبة", is_mobile=mobile_view, chart_type="bar")
                    st.plotly_chart(fig_research_rank, use_container_width=True, config={"displayModeBar": False})
                with col2:
                    # رسم شريطي لإجمالي البحوث حسب الجنس
                    research_by_gender = faculty_data.groupby("الجنس")["عدد البحوث"].sum().reset_index()
                    research_by_gender.columns = ["الجنس", "إجمالي البحوث"]
                    fig_research_gender = px.bar(research_by_gender, y="الجنس", x="إجمالي البحوث", title="إجمالي البحوث حسب الجنس", color="إجمالي البحوث", orientation='h', color_continuous_scale="Greens")
                    fig_research_gender = prepare_chart_layout(fig_research_gender, "إجمالي البحوث حسب الجنس", is_mobile=mobile_view, chart_type="bar")
                    st.plotly_chart(fig_research_gender, use_container_width=True, config={"displayModeBar": False})

                # رسم توزيع حجم البحوث (الهستوجرام) تحت الأعمدة
                fig_research_hist = px.histogram(faculty_data, x="عدد البحوث", title="توزيع عدد البحوث للأعضاء", color_discrete_sequence=["#1e88e5"])
                fig_research_hist.update_layout(bargap=0.2)
                fig_research_hist = prepare_chart_layout(fig_research_hist, "توزيع عدد البحوث", is_mobile=mobile_view, chart_type="bar")
                st.plotly_chart(fig_research_hist, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("لا تتوفر بيانات كافية لعرض توزيع البحوث.")

    # --- فلاتر البحث عن أعضاء هيئة التدريس ---
    st.subheader("بحث وتصفية أعضاء هيئة التدريس")

    # إنشاء صف للفلاتر (أو عمود في الجوال)
    if mobile_view:
        filter_container = st.container()
        with filter_container:
            if "حالة الموظف" in faculty_data.columns:
                all_statuses = ["الكل"] + sorted(faculty_data["حالة الموظف"].unique().tolist())
                selected_status = st.selectbox("حالة الموظف", all_statuses, key="status_mobile")
            else: selected_status = "الكل"

            if "الرتبة" in faculty_data.columns:
                all_ranks = ["الكل"] + sorted(faculty_data["الرتبة"].unique().tolist())
                selected_rank = st.selectbox("الرتبة", all_ranks, key="rank_mobile")
            else: selected_rank = "الكل"

            if "التخصص" in faculty_data.columns:
                all_specs = ["الكل"] + sorted(faculty_data["التخصص"].unique().tolist())
                selected_spec = st.selectbox("التخصص", all_specs, key="spec_mobile")
            else: selected_spec = "الكل"

            if "الجنس" in faculty_data.columns:
                all_genders = ["الكل", "ذكر", "أنثى"]
                selected_gender = st.selectbox("الجنس", all_genders, key="gender_mobile")
            else: selected_gender = "الكل"
    else: # عرض سطح المكتب
        filter_cols = st.columns([1, 1, 1, 1])
        with filter_cols[0]:
            if "حالة الموظف" in faculty_data.columns:
                all_statuses = ["الكل"] + sorted(faculty_data["حالة الموظف"].unique().tolist())
                selected_status = st.selectbox("حالة الموظف", all_statuses, key="status_desktop")
            else: selected_status = "الكل"
        with filter_cols[1]:
            if "الرتبة" in faculty_data.columns:
                all_ranks = ["الكل"] + sorted(faculty_data["الرتبة"].unique().tolist())
                selected_rank = st.selectbox("الرتبة", all_ranks, key="rank_desktop")
            else: selected_rank = "الكل"
        with filter_cols[2]:
            if "التخصص" in faculty_data.columns:
                all_specs = ["الكل"] + sorted(faculty_data["التخصص"].unique().tolist())
                selected_spec = st.selectbox("التخصص", all_specs, key="spec_desktop")
            else: selected_spec = "الكل"
        with filter_cols[3]:
            if "الجنس" in faculty_data.columns:
                all_genders = ["الكل", "ذكر", "أنثى"]
                selected_gender = st.selectbox("الجنس", all_genders, key="gender_desktop")
            else: selected_gender = "الكل"

    # تطبيق الفلاتر
    filtered_data = faculty_data.copy()

    if selected_status != "الكل" and "حالة الموظف" in filtered_data.columns:
        filtered_data = filtered_data[filtered_data["حالة الموظف"] == selected_status]

    if selected_rank != "الكل" and "الرتبة" in filtered_data.columns:
        filtered_data = filtered_data[filtered_data["الرتبة"] == selected_rank]

    if selected_spec != "الكل" and "التخصص" in filtered_data.columns:
        filtered_data = filtered_data[filtered_data["التخصص"] == selected_spec]

    if selected_gender != "الكل" and "الجنس" in filtered_data.columns:
        filtered_data = filtered_data[filtered_data["الجنس"] == selected_gender]

    # فلتر البحث بالنص (الاسم)
    search_query = st.text_input("البحث بالاسم", placeholder="ادخل اسم عضو هيئة التدريس...")
    if search_query and "الاسم" in filtered_data.columns:
        filtered_data = filtered_data[filtered_data["الاسم"].str.contains(search_query, case=False, na=False)]

    # --- عرض قائمة أعضاء هيئة التدريس ---
    if len(filtered_data) > 0:
        st.subheader(f"قائمة الأعضاء ({len(filtered_data)})")

        # معاملات تقييم النشاط البحثي
        filtered_data["تصنيف_البحوث"] = ""
        if "عدد البحوث" in filtered_data.columns:
            # التأكد من أن العمود رقمي قبل المقارنة
            filtered_data["عدد البحوث"] = pd.to_numeric(filtered_data["عدد البحوث"], errors='coerce').fillna(0)
            filtered_data.loc[filtered_data["عدد البحوث"] >= 15, "تصنيف_البحوث"] = "نشط جداً"
            filtered_data.loc[(filtered_data["عدد البحوث"] >= 10) & (filtered_data["عدد البحوث"] < 15), "تصنيف_البحوث"] = "نشط"
            filtered_data.loc[(filtered_data["عدد البحوث"] >= 5) & (filtered_data["عدد البحوث"] < 10), "تصنيف_البحوث"] = "متوسط"
            filtered_data.loc[filtered_data["عدد البحوث"] < 5, "تصنيف_البحوث"] = "محدود"

            # قاموس الشارات لكل تصنيف
            badge_map = {
                "نشط جداً": "badge-green",
                "نشط": "badge-blue",
                "متوسط": "badge-orange",
                "محدود": "badge-red"
            }

        # حساب نقاط الإنجازات لكل عضو من جدول الإنجازات إذا كان متاحًا
        has_achievements = False
        if not faculty_achievements.empty and "العضو" in faculty_achievements.columns and "النقاط" in faculty_achievements.columns:
            has_achievements = True
            # التأكد من أن عمود النقاط رقمي
            faculty_achievements["النقاط"] = pd.to_numeric(faculty_achievements["النقاط"], errors='coerce').fillna(0)
            faculty_points = faculty_achievements.groupby("العضو")["النقاط"].sum().reset_index()
            faculty_points.columns = ["الاسم", "نقاط_الإنجازات"]

            # دمج البيانات مع بيانات الأعضاء المفلترة
            filtered_data = pd.merge(filtered_data, faculty_points, on="الاسم", how="left")
            filtered_data["نقاط_الإنجازات"] = filtered_data["نقاط_الإنجازات"].fillna(0)

        # عرض بطاقات الأعضاء
        for i, row in filtered_data.iterrows():
            name = row.get("الاسم", "غير متوفر")
            gender = row.get("الجنس", "")
            rank = row.get("الرتبة", "")
            spec = row.get("التخصص", "")
            nationality = row.get("الجنسية", "")
            email = row.get("البريد الإلكتروني", "")
            status = row.get("حالة الموظف", "")
            research_count = int(row.get("عدد البحوث", 0))
            research_classification = row.get("تصنيف_البحوث", "")
            badge_class = badge_map.get(research_classification, "badge-blue") if "تصنيف_البحوث" in row and row["تصنيف_البحوث"] != "" else ""

            # الحصول على نقاط الإنجازات إذا كانت متاحة
            achievement_points = int(row.get("نقاط_الإنجازات", 0)) if has_achievements else 0

            # إضافة تمييز للأعضاء الجدد
            is_new_member = new_members_data is not None and name in new_members_data["الاسم"].values
            new_member_tag = '<span class="badge badge-green">جديد</span>' if is_new_member else ''

            # إضافة تمييز للأعضاء المُرقين
            is_promoted = promotions is not None and any(p["الاسم"] == name for p in promotions)
            promoted_tag = '<span class="badge badge-blue">ترقية</span>' if is_promoted else ''

            # عرض بطاقة العضو (تم تطبيق التنسيقات عبر CSS)
            st.markdown(f"""
            <div class="faculty-profile-card">
                <div class="profile-avatar">
                    {get_avatar_placeholder(name)}
                </div>
                <div class="profile-info">
                    <div class="profile-name">{name} {new_member_tag} {promoted_tag}</div>
                    <div class="profile-title">{rank} - {spec}</div>
                    <div class="profile-details">
                        <span class="profile-detail-item">{"👨" if gender == "ذكر" else "👩"} {gender}</span>
                        <span class="profile-detail-item">🌍 {nationality}</span>
                        <span class="profile-detail-item">📧 {email}</span>
                        <span class="profile-detail-item">👤 {status}</span>
                        {f'<span class="profile-detail-item badge {badge_class}">{research_classification}</span>' if research_classification else ''}
                    </div>
                    <div class="profile-metrics">
                        <div class="profile-metric">
                            <div class="profile-metric-value">{research_count}</div>
                            <div class="profile-metric-label">البحوث</div>
                        </div>
                        {f'''
                        <div class="profile-metric">
                            <div class="profile-metric-value">{achievement_points}</div>
                            <div class="profile-metric-label">نقاط الإنجاز</div>
                        </div>
                        ''' if has_achievements else ''}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("لا توجد بيانات مطابقة للفلاتر المختارة. يرجى تعديل الفلاتر للحصول على نتائج.")

    # --- نصائح للاستخدام ---
    with st.expander("💡 نصائح للاستخدام", expanded=False):
        st.markdown("""
        - **منتقي السنة:** يمكنك اختيار السنة لعرض بيانات أعضاء هيئة التدريس لتلك السنة.
        - **مؤشرات المقارنة:** الأسهم بجانب الأرقام توضح التغيير مقارنة بالسنة السابقة (زيادة أو نقصان).
        - **تفاصيل التغييرات:** انقر على "عرض تفاصيل التغييرات عن العام السابق" لمشاهدة معلومات عن الأعضاء الجدد والمغادرين والترقيات.
        - **شريط التنقل العلوي:** يعرض الأقسام الرئيسية والبرامج الأكاديمية مباشرة بشكل أفقي على الشاشات الكبيرة.
        - **على الجوال:** تظهر نفس القائمة بشكل رأسي عند النقر على أيقونة القائمة (☰).
        - **الفلاتر المتعددة:** يمكنك تطبيق أكثر من فلتر في نفس الوقت للوصول إلى بيانات محددة.
        - **البحث بالاسم:** يمكنك البحث عن عضو معين بكتابة جزء من اسمه.
        - **الرسوم البيانية تفاعلية:** مرر الفأرة فوقها لرؤية التفاصيل.
        - **التبويبات:** انقر على التبويبات المختلفة لعرض طرق متنوعة لتحليل البيانات.
        - **تصنيف النشاط البحثي:**
            - <span class="badge badge-green">نشط جداً</span>: 15 بحث أو أكثر
            - <span class="badge badge-blue">نشط</span>: 10-14 بحث
            - <span class="badge badge-orange">متوسط</span>: 5-9 بحوث
            - <span class="badge badge-red">محدود</span>: أقل من 5 بحوث
        """, unsafe_allow_html=True)

# --- إضافة نص تذييل الصفحة ---
st.markdown("""
<div style="margin-top: 50px; text-align: center; color: #888; font-size: 0.75em;">
    © قسم القراءات - جامعة الطائف {0}
</div>
""".format(datetime.now().year), unsafe_allow_html=True)
