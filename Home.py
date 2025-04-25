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
    page_title="الرئيسية | قسم القراءات",
    page_icon="🏠",
    layout="wide"
)

# --- CSS و HTML للقائمة العلوية المتجاوبة (RTL) - مأخوذ من الكود القديم ---
# يتضمن هذا الجزء تنسيقات CSS لقائمة التنقل (سطح المكتب والجوال)
# بالإضافة إلى JavaScript لزر العودة للأعلى وقائمة الجوال.
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
    .faculty-card { background: linear-gradient(135deg, #f5f7fa 0%, #e3e6f0 100%); border-radius: 8px; padding: 12px; margin-bottom: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08); }
    .achievement-item { padding: 8px; border-right: 3px solid #1e88e5; margin-bottom: 8px; background-color: rgba(30, 136, 229, 0.05); }
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

    /* --- قواعد Media Query للتبديل بين القائمتين وتحسين عرض الجوال --- */
    @media only screen and (max-width: 768px) {
        .top-navbar { display: none; }
        .mobile-menu-trigger { display: block; }
        .main .block-container { padding-right: 0.8rem !important; padding-left: 0.8rem !important; padding-top: 40px !important; } /* تقليل الحشو أكثر */

        /* تصغير الخطوط والهوامش للعناوين في الجوال */
        h1 { font-size: 1.3rem; margin-bottom: 15px; padding-bottom: 8px; }
        h2 { font-size: 1.1rem; margin-top: 20px; margin-bottom: 10px; }
        h3 { font-size: 1.0rem; margin-top: 18px; margin-bottom: 8px; }

        /* تصغير خطوط المقاييس في الجوال */
        [data-testid="stMetricValue"] { font-size: 1.3rem !important; }
        [data-testid="stMetricLabel"] { font-size: 0.8rem !important; }
        .metric-card { padding: 10px; margin-bottom: 10px;} /* تقليل حشو وهوامش بطاقات المقاييس */

        /* تصغير خطوط بطاقات هيئة التدريس والإنجازات في الجوال */
        .faculty-card h5 { font-size: 0.9rem !important; margin-bottom: 2px !important; }
        .faculty-card p { font-size: 0.8em !important; }
        .achievement-item p:first-of-type { font-size: 0.85em !important; margin-bottom: 1px !important; }
        .achievement-item p:nth-of-type(2) { font-size: 0.8em !important; margin-bottom: 1px !important; }
        .achievement-item p:last-of-type { font-size: 0.7em !important; }

        /* جعل أعمدة هيئة التدريس والإنجازات عمودًا واحدًا */
        /* هذا يتطلب تعديل كود Python لاستخدام st.container بدلاً من st.columns في الجوال */
        /* سنقوم بتطبيق هذا التعديل لاحقًا في كود Python */

         /* تصغير خطوط التبويبات */
        button[data-baseweb="tab"] {
            font-size: 0.85rem !important;
            padding-top: 8px !important;
            padding-bottom: 8px !important;
        }
         /* تصغير خط منتقي السنة */
        .stSelectbox label { font-size: 0.9rem !important; }
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

# --- العنوان الرئيسي للصفحة (تم التعديل) ---
st.markdown("<h1>🏠 الرئيسية</h1>", unsafe_allow_html=True) # تغيير النص وتصغير الخط عبر CSS

# --- دوال مساعدة ---
def is_mobile():
    """التحقق من كون العرض الحالي محتملاً أن يكون جهاز محمول"""
    # ملاحظة: هذه الدالة تحتاج إلى طريقة لتحديد عرض الشاشة بشكل فعلي.
    # يمكنك استخدام مكون مثل streamlit_js_eval أو اختبار العرض يدويًا بتغيير حجم المتصفح.
    # حاليًا، ستُرجع False دائمًا.
    # يمكنك تغييرها إلى True مؤقتًا لاختبار تنسيقات الجوال.
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
                fig.update_xaxes(tickangle=0, tickfont={"size": 6}) # تصغير خط المحور السيني
                fig.update_yaxes(tickfont={"size": 6}) # تصغير خط المحور الصادي
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

        fig.update_layout(**layout_settings)
    except Exception as e:
        st.warning(f"تعذر تطبيق إعدادات التخطيط للرسم '{title}': {e}")

    return fig

# --- تحديد قاموس رموز البرامج ---
PROGRAM_MAP = {
    "بكالوريوس في القرآن وعلومه": "bachelor_quran",
    "بكالوريوس القراءات": "bachelor_readings",
    "ماجستير الدراسات القرآنية المعاصرة": "master_contemporary",
    "ماجستير القراءات": "master_readings",
    "دكتوراه علوم القرآن": "phd_quran",
    "دكتوراه القراءات": "phd_readings"
}
REVERSE_PROGRAM_MAP = {code: name for name, code in PROGRAM_MAP.items()}
SHORT_PROGRAM_MAP = {
    "بكالوريوس في القرآن وعلومه": "ب. قرآن",
    "بكالوريوس القراءات": "ب. قراءات",
    "ماجستير الدراسات القرآنية المعاصرة": "م. دراسات",
    "ماجستير القراءات": "م. قراءات",
    "دكتوراه علوم القرآن": "د. قرآن",
    "دكتوراه القراءات": "د. قراءات"
}

# --- دوال تحميل البيانات ---
@st.cache_data(ttl=3600)
def load_department_summary():
    """تحميل بيانات ملخص القسم الكلية"""
    try:
        file_path = "data/department/summary_latest.csv"
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
        else:
            data = {
                "البرنامج": list(PROGRAM_MAP.keys()),
                "عدد الطلاب": [210, 180, 150, 200, 120, 140],
                "أعضاء هيئة التدريس": [15, 12, 8, 10, 5, 6]
            }
            df = pd.DataFrame(data)
        return df
    except Exception as e:
        st.error(f"خطأ في تحميل ملخص القسم: {e}")
        return pd.DataFrame({"البرنامج": [], "عدد الطلاب": [], "أعضاء هيئة التدريس": []})

@st.cache_data(ttl=3600)
def load_yearly_data():
    """تحميل بيانات سنوية لجميع البرامج"""
    YEAR_LIST = list(range(2022, 2026))
    years = YEAR_LIST
    data = []
    for year in years:
        for program_name, program_code in PROGRAM_MAP.items():
            try:
                summary_file = f"data/{program_code}/{year}/summary_{year}.csv"
                if os.path.exists(summary_file):
                    df = pd.read_csv(summary_file)
                    success_rate = df.loc[df["الفئة"] == "نسبة النجاح", "النسبة"].values[0] if "نسبة النجاح" in df["الفئة"].values else None
                    satisfaction = df.loc[df["الفئة"] == "معدل الرضا", "النسبة"].values[0] if "معدل الرضا" in df["الفئة"].values else None
                    student_file = f"data/{program_code}/{year}/students_{year}.csv"
                    if os.path.exists(student_file):
                        student_df = pd.read_csv(student_file)
                        student_count = student_df["الإجمالي"].sum() if "الإجمالي" in student_df.columns else None
                    else:
                        student_count = None
                    data.append({
                        "العام": year, "البرنامج": program_name, "عدد الطلاب": student_count,
                        "نسبة النجاح": success_rate, "معدل الرضا": satisfaction
                    })
                else: # بيانات تجريبية إذا لم يوجد الملف
                    program_hash = int(hashlib.md5(program_name.encode()).hexdigest(), 16) % 100
                    data.append({
                        "العام": year, "البرنامج": program_name,
                        "عدد الطلاب": 100 + (year - 2020) * 10 + program_hash % 100,
                        "نسبة النجاح": min(95, 70 + (year - 2020) * 2 + program_hash % 10),
                        "معدل الرضا": min(90, 75 + (year - 2020) * 1.5 + (program_hash // 2) % 10)
                    })
            except Exception as e: # بيانات تجريبية عند الخطأ
                program_hash = int(hashlib.md5(program_name.encode()).hexdigest(), 16) % 100
                data.append({
                    "العام": year, "البرنامج": program_name,
                    "عدد الطلاب": 100 + (year - 2020) * 10 + program_hash % 100,
                    "نسبة النجاح": min(95, 70 + (year - 2020) * 2 + program_hash % 10),
                    "معدل الرضا": min(90, 75 + (year - 2020) * 1.5 + (program_hash // 2) % 10)
                })
    return pd.DataFrame(data)

@st.cache_data(ttl=3600)
def load_faculty_achievements():
    """تحميل بيانات إنجازات أعضاء هيئة التدريس"""
    try:
        file_path = "data/department/achievements_latest.csv"
        if os.path.exists(file_path):
            return pd.read_csv(file_path)
        else:
            achievements = [
                {"العضو": "د. محمد أحمد", "الإنجاز": "نشر بحث في مجلة عالمية", "التاريخ": "2025-04-15", "النقاط": 50, "البرنامج": "بكالوريوس في القرآن وعلومه"},
                {"العضو": "د. عائشة سعد", "الإنجاز": "إطلاق مبادرة تعليمية", "التاريخ": "2025-04-10", "النقاط": 40, "البرنامج": "دكتوراه علوم القرآن"},
                {"العضو": "د. عبدالله محمد", "الإنجاز": "المشاركة في مؤتمر دولي", "التاريخ": "2025-04-05", "النقاط": 35, "البرنامج": "بكالوريوس القراءات"},
                {"العضو": "د. فاطمة علي", "الإنجاز": "تطوير مقرر دراسي", "التاريخ": "2025-04-01", "النقاط": 30, "البرنامج": "ماجستير الدراسات القرآنية المعاصرة"},
                {"العضو": "د. خالد إبراهيم", "الإنجاز": "تقديم ورشة عمل", "التاريخ": "2025-03-25", "النقاط": 25, "البرنامج": "ماجستير القراءات"}
            ]
            return pd.DataFrame(achievements)
    except Exception as e:
        st.error(f"خطأ في تحميل بيانات الإنجازات: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_top_faculty():
    """تحميل بيانات أعضاء هيئة التدريس المتميزين"""
    try:
        file_path = "data/department/top_faculty_latest.csv"
        if os.path.exists(file_path):
            return pd.read_csv(file_path)
        else:
            top_faculty = [
                {"الاسم": "د. عائشة سعد", "اللقب": "العضو القمة", "الشارة": "👑", "النقاط": 320, "البرنامج": "دكتوراه علوم القرآن"},
                {"الاسم": "د. محمد أحمد", "اللقب": "العضو المميز", "الشارة": "🌟", "النقاط": 280, "البرنامج": "بكالوريوس في القرآن وعلومه"},
                {"الاسم": "د. عبدالله محمد", "اللقب": "العضو الفعال", "الشارة": "🔥", "النقاط": 210, "البرنامج": "بكالوريوس القراءات"}
            ]
            return pd.DataFrame(top_faculty)
    except Exception as e:
        st.error(f"خطأ في تحميل بيانات أعضاء هيئة التدريس المتميزين: {e}")
        return pd.DataFrame()

# --- محتوى لوحة المعلومات الرئيسية ---

# تحديد عرض الجوال
mobile_view = is_mobile()

# تطبيق المنتقي الزمني وفقًا لدليل المنظومة
YEAR_LIST = list(range(2022, 2026))
selected_year = st.selectbox("اختر السنة", YEAR_LIST[::-1]) # عرض السنوات بترتيب تنازلي

# تحميل البيانات (مع معالجة الأخطاء والبيانات التجريبية)
try:
    dept_data = load_department_summary()
    total_students = dept_data["عدد الطلاب"].sum() if "عدد الطلاب" in dept_data.columns else 0
    total_faculty = dept_data["أعضاء هيئة التدريس"].sum() if "أعضاء هيئة التدريس" in dept_data.columns else 0
    total_programs = len(dept_data) if not dept_data.empty else 6

    yearly_data = load_yearly_data()

    if "العام" in yearly_data.columns:
        latest_year_data = yearly_data[yearly_data["العام"] == selected_year].copy()
    else:
        latest_year_data = pd.DataFrame()

    faculty_achievements = load_faculty_achievements()
    top_faculty = load_top_faculty()

    if latest_year_data.empty and not dept_data.empty:
        st.info(f"لا توجد بيانات لعام {selected_year}. استخدام بيانات ملخص القسم للرسوم البيانية.")
        latest_year_data = dept_data.copy()
        latest_year_data["العام"] = selected_year

except Exception as e:
    st.error(f"خطأ في تحميل أو تهيئة البيانات: {e}")
    st.warning("استخدام بيانات تجريبية.")
    # إعداد بيانات تجريبية عند الخطأ
    total_students = 1000
    total_faculty = 56
    total_programs = 6
    dept_data = pd.DataFrame({
        "البرنامج": list(PROGRAM_MAP.keys()),
        "عدد الطلاب": [210, 180, 150, 200, 120, 140],
        "أعضاء هيئة التدريس": [15, 12, 8, 10, 5, 6]
    })
    latest_year_data = pd.DataFrame({
        "العام": [selected_year] * 6, "البرنامج": list(PROGRAM_MAP.keys()),
        "عدد الطلاب": [210, 180, 150, 200, 120, 140],
        "نسبة النجاح": [88, 85, 92, 90, 95, 87], "معدل الرضا": [90, 88, 93, 91, 94, 89]
    })
    yearly_data = pd.DataFrame()
    for year in range(2022, 2026):
        for idx, program in enumerate(PROGRAM_MAP.keys()):
            yearly_data = yearly_data._append({
                "العام": year, "البرنامج": program,
                "عدد الطلاب": 150 + (year - 2022) * 15 + idx * 10,
                "نسبة النجاح": 80 + (year - 2022) * 2 + idx,
                "معدل الرضا": 82 + (year - 2022) * 2 + idx
            }, ignore_index=True)
    faculty_achievements = pd.DataFrame({
        "العضو": ["د. محمد أحمد", "د. عائشة سعد", "د. عبدالله محمد"],
        "الإنجاز": ["نشر بحث في مجلة عالمية", "إطلاق مبادرة تعليمية", "المشاركة في مؤتمر دولي"],
        "التاريخ": ["2025-04-15", "2025-04-10", "2025-04-05"], "النقاط": [50, 40, 35],
        "البرنامج": ["بكالوريوس في القرآن وعلومه", "دكتوراه علوم القرآن", "بكالوريوس القراءات"]
    })
    top_faculty = pd.DataFrame({
        "الاسم": ["د. عائشة سعد", "د. محمد أحمد", "د. عبدالله محمد"],
        "اللقب": ["العضو القمة", "العضو المميز", "العضو الفعال"], "الشارة": ["👑", "🌟", "🔥"],
        "النقاط": [320, 280, 210],
        "البرنامج": ["دكتوراه علوم القرآن", "بكالوريوس في القرآن وعلومه", "بكالوريوس القراءات"]
    })

# --- المقاييس الرئيسية (تم تغيير العنوان الفرعي) ---
st.subheader("مؤشرات قسم القراءات") # تغيير النص هنا

# عرض المقاييس الرئيسية - تعديل لعرض الجوال (2x2)
# ملاحظة: هذا يتطلب التحقق من mobile_view. إذا كانت True، نستخدم شبكة 2x2.
if mobile_view:
    row1_cols = st.columns(2)
    row2_cols = st.columns(2)
    metric_cols = [row1_cols[0], row1_cols[1], row2_cols[0], row2_cols[1]]
else:
    metric_cols = st.columns(4)

with metric_cols[0]:
    st.metric("إجمالي الطلاب", f"{total_students:,}")
with metric_cols[1]:
    st.metric("أعضاء هيئة التدريس", f"{total_faculty:,}")
with metric_cols[2]:
    st.metric("البرامج الأكاديمية", f"{total_programs}")

# تحديد المؤشر الرابع وعرضه
indicators_to_plot = []
fourth_metric_available = False
if not latest_year_data.empty and "نسبة الاستبقاء" in latest_year_data.columns:
    avg_retention = latest_year_data["نسبة الاستبقاء"].mean()
    indicators_to_plot.append("نسبة الاستبقاء")
    with metric_cols[3]:
        st.metric("متوسط الاستبقاء", f"{avg_retention:.0f}%")
    fourth_metric_available = True
elif not latest_year_data.empty and "نسبة النجاح" in latest_year_data.columns:
    avg_success = latest_year_data["نسبة النجاح"].mean()
    indicators_to_plot.append("نسبة النجاح")
    with metric_cols[3]:
        st.metric("متوسط النجاح", f"{avg_success:.0f}%")
    fourth_metric_available = True

# إذا لم يكن هناك مؤشر رابع، يمكن ترك العمود فارغًا أو إضافة عنصر نائب
if not fourth_metric_available and len(metric_cols) > 3:
     with metric_cols[3]:
         pass # أو st.empty()

if not latest_year_data.empty:
    for column in ["معدل الرضا", "نسبة التوظيف"]:
        if column in latest_year_data.columns:
            indicators_to_plot.append(column)

# --- تحليل البرامج ---
if not latest_year_data.empty and "البرنامج" in latest_year_data.columns and "عدد الطلاب" in latest_year_data.columns:
    st.subheader("تحليل البرامج الأكاديمية")
    display_data = latest_year_data.copy()
    if "البرنامج" in display_data.columns:
        display_data["البرنامج_المختصر"] = display_data["البرنامج"].map(SHORT_PROGRAM_MAP).fillna(display_data["البرنامج"])
    else:
        display_data["البرنامج_المختصر"] = display_data["البرنامج"] # Fallback

    tab_labels = ["توزيع الطلاب", "مقارنة المؤشرات", "التطور السنوي"]
    tabs = st.tabs(tab_labels)

    with tabs[0]: # توزيع الطلاب
        # تعديل لعرض الجوال: عمود واحد بدلاً من اثنين
        if mobile_view:
            fig_pie = px.pie(display_data, values="عدد الطلاب", names="البرنامج_المختصر", title="توزيع الطلاب حسب البرامج", color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_pie = prepare_chart_layout(fig_pie, "توزيع الطلاب", is_mobile=mobile_view, chart_type="pie")
            st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

            st.markdown("---") # فاصل

            fig_bar = px.bar(display_data.sort_values("عدد الطلاب", ascending=False), x="البرنامج_المختصر", y="عدد الطلاب", title="عدد الطلاب لكل برنامج", color="عدد الطلاب", color_continuous_scale="Blues") # تغيير الاتجاه لعمودي في الجوال
            fig_bar = prepare_chart_layout(fig_bar, "عدد الطلاب لكل برنامج", is_mobile=mobile_view, chart_type="bar")
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
        else:
            col1_tab1, col2_tab1 = st.columns([1, 1])
            with col1_tab1:
                fig_pie = px.pie(display_data, values="عدد الطلاب", names="البرنامج_المختصر", title="توزيع الطلاب حسب البرامج", color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_pie = prepare_chart_layout(fig_pie, "توزيع الطلاب", is_mobile=mobile_view, chart_type="pie")
                st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
            with col2_tab1:
                fig_bar = px.bar(display_data.sort_values("عدد الطلاب", ascending=True), y="البرنامج_المختصر", x="عدد الطلاب", title="عدد الطلاب لكل برنامج", color="عدد الطلاب", orientation='h', color_continuous_scale="Blues")
                fig_bar = prepare_chart_layout(fig_bar, "عدد الطلاب لكل برنامج", is_mobile=mobile_view, chart_type="bar")
                st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})


    with tabs[1]: # مقارنة المؤشرات
        if indicators_to_plot:
            fig_indicators = px.bar(display_data, x="البرنامج_المختصر", y=indicators_to_plot, barmode="group", title="مقارنة المؤشرات بين البرامج", labels={"value": "النسبة المئوية", "variable": "المؤشر", "البرنامج_المختصر": "البرنامج"}, color_discrete_sequence=["#1e88e5", "#27AE60", "#E74C3C"][:len(indicators_to_plot)])
            fig_indicators = prepare_chart_layout(fig_indicators, "مقارنة المؤشرات", is_mobile=mobile_view, chart_type="bar")
            st.plotly_chart(fig_indicators, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("لا توجد بيانات مؤشرات لعرض المقارنة.")

    with tabs[2]: # التطور السنوي
        if not yearly_data.empty and "البرنامج" in yearly_data.columns:
            unique_programs_full = yearly_data["البرنامج"].unique()
            program_options_display = {SHORT_PROGRAM_MAP.get(p, p): p for p in unique_programs_full}
            selected_display_program = st.selectbox("اختر البرنامج لعرض تطوره:", options=list(program_options_display.keys()), key="trend_prog_select") # إضافة مفتاح فريد
            selected_program_full = program_options_display[selected_display_program]
            program_data = yearly_data[yearly_data["البرنامج"] == selected_program_full].copy()

            trend_indicators = []
            if "عدد الطلاب" in program_data.columns: trend_indicators.append("عدد الطلاب")
            for indicator in indicators_to_plot:
                if indicator in program_data.columns: trend_indicators.append(indicator)

            if trend_indicators and "العام" in program_data.columns:
                fig_trend = px.line(program_data, x="العام", y=trend_indicators, title=f"تطور مؤشرات: {selected_display_program}", labels={"value": "القيمة", "variable": "المؤشر", "العام": "السنة"}, markers=True)
                fig_trend = prepare_chart_layout(fig_trend, f"تطور: {selected_display_program}", is_mobile=mobile_view, chart_type="line")
                st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info(f"لا توجد بيانات كافية لعرض التطور السنوي لبرنامج {selected_display_program}.")
        else:
            st.info("لا توجد بيانات سنوية لعرض التطور.")
else:
    st.info("لا توجد بيانات كافية لعرض الرسوم البيانية للبرامج.")

# --- قسم أعضاء هيئة التدريس والإنجازات ---
st.subheader("أعضاء هيئة التدريس والإنجازات")

# تعديل لعرض الجوال: استخدام حاوية واحدة بدلاً من عمودين
faculty_container = st.container()

if not top_faculty.empty or not faculty_achievements.empty:
    # تحديد الأعمدة فقط إذا لم يكن عرض الجوال
    if not mobile_view:
        col1_faculty, col2_faculty = faculty_container.columns([1, 1])
    else:
        # في عرض الجوال، استخدم الحاوية مباشرة لكل قسم
        col1_faculty = faculty_container
        col2_faculty = faculty_container


    # أعضاء هيئة التدريس المتميزون
    with col1_faculty:
        # إضافة فاصل في الجوال قبل القسم الثاني إذا كان القسم الأول موجودًا
        if mobile_view and not top_faculty.empty:
             st.markdown("#### 🏆 المميزون")
        elif not mobile_view:
             st.markdown("#### 🏆 المميزون")

        if not top_faculty.empty:
            num_to_display = min(len(top_faculty), 3)
            for _, member in top_faculty.head(num_to_display).iterrows():
                name = member.get('الاسم', 'غير متوفر')
                badge = member.get('الشارة', '')
                title = member.get('اللقب', '')
                points = member.get('النقاط', '')
                # تصغير خطوط بطاقة العضو المميز (تم تطبيق CSS)
                st.markdown(f"""<div class='faculty-card'><h5 style="margin-bottom: 3px; font-size: 0.95rem;">{badge} {name}</h5><p style="font-size: 0.85em; margin: 2px 0;">{title} ({points} نقطة)</p></div>""", unsafe_allow_html=True)
            st.markdown("<a href='/هيئة_التدريس' target='_top' style='font-size: 0.85em;'>عرض الكل...</a>", unsafe_allow_html=True)
        else:
            st.info("لا توجد بيانات لأعضاء هيئة التدريس المتميزين.")
        # إضافة فاصل في الجوال بعد القسم الأول
        if mobile_view and not top_faculty.empty and not faculty_achievements.empty:
            st.markdown("---")


    # أحدث الإنجازات
    with col2_faculty:
        # التأكد من عدم تكرار العنوان في الجوال
        if mobile_view and not faculty_achievements.empty:
            st.markdown("#### 🌟 أحدث الإنجازات")
        elif not mobile_view:
            st.markdown("#### 🌟 أحدث الإنجازات")

        if not faculty_achievements.empty:
            num_to_display = min(len(faculty_achievements), 3)
            if 'التاريخ' in faculty_achievements.columns:
                faculty_achievements['التاريخ'] = pd.to_datetime(faculty_achievements['التاريخ'], errors='coerce')
                achievements_to_display = faculty_achievements.sort_values('التاريخ', ascending=False).head(num_to_display)
            else:
                achievements_to_display = faculty_achievements.head(num_to_display)
            for _, achievement in achievements_to_display.iterrows():
                member_name = achievement.get('العضو', 'غير معروف')
                desc = achievement.get('الإنجاز', 'لا يوجد وصف')
                date_str = achievement.get('التاريخ', None)
                formatted_date = date_str.strftime("%Y/%m/%d") if pd.notna(date_str) else ""
                # تصغير خطوط بطاقة الإنجاز (تم تطبيق CSS)
                st.markdown(f"""<div class='achievement-item'><p style="font-size: 0.9em; margin-bottom: 2px;"><strong>{member_name}</strong></p><p style="font-size: 0.85em; margin-bottom: 2px;">{desc}</p>{f'<p style="font-size: 0.75em; color: grey; margin-bottom: 0;">{formatted_date}</p>' if formatted_date else ''}</div>""", unsafe_allow_html=True)
            st.markdown("<a href='/إنجاز_المهام' target='_top' style='font-size: 0.85em;'>عرض الكل...</a>", unsafe_allow_html=True)
        else:
            # التأكد من عدم عرض الرسالة مرتين في الجوال
            if not mobile_view:
                st.info("لا توجد بيانات لأحدث الإنجازات.")

else:
    st.info("لا تتوفر بيانات أعضاء هيئة التدريس أو الإنجازات حاليًا.")

# --- عرض الخريطة الحرارية للمؤشرات ---
if not latest_year_data.empty and "البرنامج_المختصر" in display_data.columns and indicators_to_plot:
    st.subheader("نظرة عامة على المؤشرات")
    try:
        heatmap_plot_data = display_data[["البرنامج_المختصر"] + indicators_to_plot].set_index("البرنامج_المختصر")
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=heatmap_plot_data.values, x=heatmap_plot_data.columns, y=heatmap_plot_data.index,
            colorscale="Blues", text=heatmap_plot_data.values, texttemplate="%{text:.0f}",
            textfont={"size": 8 if mobile_view else 10}, # تصغير الخط للجوال
            hoverongaps=False
        ))
        fig_heatmap = prepare_chart_layout(fig_heatmap, "مقارنة المؤشرات الرئيسية", is_mobile=mobile_view, chart_type="heatmap")
        # تم نقل التعديلات الخاصة بالخطوط والهوامش إلى prepare_chart_layout
        st.plotly_chart(fig_heatmap, use_container_width=True, config={"displayModeBar": False})
    except Exception as heatmap_error:
        st.warning(f"لم يتمكن من إنشاء المخطط الحراري: {heatmap_error}")
elif not latest_year_data.empty:
    st.info("لا تتوفر بيانات مؤشرات كافية لإنشاء المخطط الحراري.")

# --- جدول خلاصة البرامج ---
if not dept_data.empty and "البرنامج" in dept_data.columns:
    st.subheader("خلاصة البرامج")
    summary_table = dept_data.copy()
    if "عدد الطلاب" in summary_table.columns:
        summary_table = summary_table.sort_values(by="عدد الطلاب", ascending=False)
    display_columns = ["البرنامج", "عدد الطلاب", "أعضاء هيئة التدريس"]
    additional_columns = ["نسبة النجاح", "نسبة الاستبقاء", "نسبة التوظيف"]
    for col in additional_columns:
        if col in summary_table.columns:
            display_columns.append(col)
    st.dataframe(
        summary_table[display_columns],
        hide_index=True,
        column_config={
            "البرنامج": st.column_config.TextColumn("البرنامج"),
            "عدد الطلاب": st.column_config.NumberColumn("عدد الطلاب", format="%d"),
            "أعضاء هيئة التدريس": st.column_config.NumberColumn("أعضاء هيئة التدريس", format="%d"),
            "نسبة النجاح": st.column_config.NumberColumn("نسبة النجاح", format="%.1f%%") if "نسبة النجاح" in summary_table.columns else None,
            "نسبة الاستبقاء": st.column_config.NumberColumn("نسبة الاستبقاء", format="%.1f%%") if "نسبة الاستبقاء" in summary_table.columns else None,
            "نسبة التوظيف": st.column_config.NumberColumn("نسبة التوظيف", format="%.1f%%") if "نسبة التوظيف" in summary_table.columns else None,
        },
        use_container_width=True
    )

# --- نصائح للاستخدام ---
with st.expander("💡 نصائح للاستخدام", expanded=False):
    st.markdown("""
    - **شريط التنقل العلوي:** يعرض الأقسام الرئيسية والبرامج الأكاديمية مباشرة بشكل أفقي على الشاشات الكبيرة.
    - **على الجوال:** تظهر نفس القائمة بشكل رأسي عند النقر على أيقونة القائمة (☰).
    - **منتقي السنة:** يمكنك اختيار السنة لعرض بيانات ذلك العام في جميع المخططات والبطاقات.
    - **الرسوم البيانية تفاعلية:** مرر الفأرة فوقها لرؤية التفاصيل.
    - **التبويبات:** انقر على التبويبات المختلفة لعرض طرق متنوعة لتحليل البيانات.
    - **زر العودة للأعلى:** انقر على زر السهم ↑ في أسفل الصفحة للعودة إلى أعلى الصفحة بسرعة.
    - **تصدير البيانات:** يمكنك النقر بزر الفأرة الأيمن على أي رسم بياني واختيار "تنزيل كصورة" للحصول على نسخة منه.
    """)

# --- إضافة نص تذييل الصفحة ---
st.markdown("""
<div style="margin-top: 40px; text-align: center; color: #888; font-size: 0.75em;"> © كلية القرآن الكريم والدراسات الإسلامية - جامعة الطائف {0}
</div>
""".format(datetime.now().year), unsafe_allow_html=True)

