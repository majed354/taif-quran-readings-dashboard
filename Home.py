# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import hashlib

# --- إعدادات الصفحة ---
st.set_page_config(
    page_title="الرئيسية", # Title shown in browser tab
    page_icon="🏠",
    layout="wide"
)

# --- CSS و HTML للقائمة العلوية المتجاوبة (مسطحة ومفصلة) ---
# ملاحظة: القائمة الآن أطول، قد تلتف على الشاشات المتوسطة.
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
        background-color: #f8f9fa; padding: 0.5rem 1rem; border-bottom: 1px solid #e7e7e7;
        width: 100%; box-sizing: border-box; display: none; /* Hidden by default on mobile */
    }
    .top-navbar ul {
        list-style: none; padding: 0; margin: 0; display: flex;
        justify-content: flex-start; align-items: center;
        flex-wrap: wrap; /* Allow wrapping on smaller desktop screens */
    }
    .top-navbar li {
        position: relative; margin-left: 1.2rem; /* Reduced margin */
        margin-bottom: 0.3rem; /* Add margin if wraps */
    }
    .top-navbar li:first-child { margin-right: 0; }
    .top-navbar a { text-decoration: none; color: #333; padding: 0.5rem 0.1rem; display: block; font-weight: 500; white-space: nowrap; /* Prevent wrapping within link */ }
    .top-navbar a:hover { color: #1e88e5; }
    /* Removed dropdown styles */

    /* --- تنسيق زر وقائمة البرجر (للجوال) --- */
    .mobile-menu-trigger {
        display: none; /* Hidden by default on desktop */
        position: fixed; top: 10px; right: 15px; z-index: 1001;
        cursor: pointer; background-color: #1e88e5; color: white;
        padding: 6px 10px; border-radius: 5px; font-size: 1.3rem; line-height: 1;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .mobile-menu-checkbox { display: none; }
    .mobile-menu {
        display: none; position: fixed; top: 0; right: 0;
        width: 250px; height: 100%; background-color: #f8f9fa;
        z-index: 1000; padding: 60px 20px 20px 20px;
        box-shadow: -2px 0 5px rgba(0,0,0,0.1);
        transition: transform 0.3s ease-in-out;
        transform: translateX(100%); overflow-y: auto;
    }
    .mobile-menu ul { list-style: none; padding: 0; margin: 0; }
    .mobile-menu li { margin-bottom: 0.5rem; }
    .mobile-menu a { text-decoration: none; color: #333; padding: 10px 5px; display: block; font-weight: 500; border-bottom: 1px solid #eee; }
    .mobile-menu a:hover { color: #1e88e5; background-color: #eee; }

    /* --- إظهار قائمة البرجر عند تفعيل الـ checkbox --- */
    .mobile-menu-checkbox:checked ~ .mobile-menu { display: block; transform: translateX(0); }
    .mobile-menu-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.4); z-index: 999; }
    .mobile-menu-checkbox:checked ~ .mobile-menu-overlay { display: block; }

    /* --- قواعد Media Query للتبديل بين القائمتين --- */
    @media only screen and (max-width: 768px) {
        .top-navbar { display: none; }
        .mobile-menu-trigger { display: block; }
        .main .block-container { padding-right: 1rem !important; padding-left: 1rem !important; padding-top: 55px !important; }
    }
    @media only screen and (min-width: 769px) {
        .top-navbar { display: block; }
        .mobile-menu-trigger, .mobile-menu, .mobile-menu-overlay, .mobile-menu-checkbox { display: none; }
    }

    /* --- تنسيقات عامة أخرى --- */
    h1,h2,h3 { color: #1e88e5; font-weight: 600; } /* Simplified */
    h1 { padding-bottom: 15px; border-bottom: 2px solid #1e88e5; margin-bottom: 30px; font-size: calc(1.2rem + 1vw); }
    h2 { margin-top: 30px; margin-bottom: 20px; font-size: calc(1rem + 0.5vw); }
    h3 { margin-top: 30px; margin-bottom: 20px; font-size: calc(1rem + 0.2vw); } /* Adjusted h3 size */
    .metric-card { background-color: white; border-radius: 10px; padding: 15px; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1); text-align: center; margin-bottom: 15px; }
    .chart-container { background-color: white; border-radius: 10px; padding: 10px; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1); margin-bottom: 20px; width: 100%; overflow: hidden; }
    .faculty-card { background: linear-gradient(135deg, #f5f7fa 0%, #e3e6f0 100%); border-radius: 10px; padding: 15px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); }
    .achievement-item { padding: 10px; border-right: 3px solid #1e88e5; margin-bottom: 10px; background-color: rgba(30, 136, 229, 0.05); }
    .stSelectbox label, .stMultiselect label { font-weight: 500; }
    .back-to-top { position: fixed; bottom: 20px; left: 20px; width: 40px; height: 40px; background-color: #1e88e5; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; z-index: 998; cursor: pointer; box-shadow: 0 2px 5px rgba(0,0,0,0.2); opacity: 0; transition: opacity 0.3s, transform 0.3s; transform: scale(0); }
    .back-to-top.visible { opacity: 1; transform: scale(1); }
    @media only screen and (min-width: 769px) and (max-width: 1024px) { h1 { font-size: 1.7rem; } h2, h3 { font-size: 1.2rem; } }

</style>

<nav class="top-navbar">
    <ul>
        <li><a href="/">الرئيسية</a></li>
        <li><a href="/هيئة_التدريس">هيئة التدريس</a></li>
        <li><a href="/إنجاز_المهام">إنجاز المهام</a></li>
        <li><a href="/program1">بكالوريوس قرآن وعلومه</a></li>
        <li><a href="/program2">بكالوريوس القراءات</a></li>
        <li><a href="/program3">ماجستير دراسات قرآنية</a></li>
        <li><a href="/program4">ماجستير القراءات</a></li>
        <li><a href="/program5">دكتوراه علوم قرآن</a></li>
        <li><a href="/program6">دكتوراه القراءات</a></li>
        </ul>
</nav>

<input type="checkbox" id="mobile-menu-toggle" class="mobile-menu-checkbox">
<label for="mobile-menu-toggle" class="mobile-menu-trigger">☰</label>
<label for="mobile-menu-toggle" class="mobile-menu-overlay"></label>
<div class="mobile-menu">
    <ul>
        <li><a href="/">الرئيسية</a></li>
        <li><a href="/هيئة_التدريس">هيئة التدريس</a></li>
        <li><a href="/إنجاز_المهام">إنجاز المهام</a></li>
        <li><a href="/program1">بكالوريوس قرآن وعلومه</a></li>
        <li><a href="/program2">بكالوريوس القراءات</a></li>
        <li><a href="/program3">ماجستير دراسات قرآنية</a></li>
        <li><a href="/program4">ماجستير القراءات</a></li>
        <li><a href="/program5">دكتوراه علوم قرآن</a></li>
        <li><a href="/program6">دكتوراه القراءات</a></li>
         </ul>
</div>


<div class="back-to-top" onclick="scrollToTop()">
    <span style="font-size: 1.2rem;">↑</span>
</div>
<script>
    // --- Scroll to Top Logic ---
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

    // Close mobile menu when a link is clicked (optional JS enhancement)
    try {
        document.querySelectorAll('.mobile-menu a').forEach(link => {
            link.addEventListener('click', () => {
                const checkbox = document.getElementById('mobile-menu-toggle');
                if (checkbox) {
                    checkbox.checked = false; // Uncheck the box to close the menu
                }
            });
        });
    } catch(e) { console.error("Error adding mobile link click listener:", e); }

</script>
"""
# تطبيق القائمة العلوية و CSS العام وزر العودة للأعلى
st.markdown(responsive_menu_html_css, unsafe_allow_html=True)


# --- العنوان الرئيسي والعنوان الفرعي (تم حذفها / التعليق عليها) ---
# st.title("🏠 الرئيسية")
# st.markdown("### كلية القرآن الكريم والدراسات الإسلامية") # Subtitle


# --- بقية محتوى الصفحة ---

# دوال مساعدة (تبقى كما هي)
def is_mobile():
    if 'IS_MOBILE' not in st.session_state: st.session_state.IS_MOBILE = False
    return st.session_state.IS_MOBILE

def prepare_chart_layout(fig, title, is_mobile=False, chart_type="bar"):
    try:
        fig.update_layout(dragmode=False)
        fig.update_xaxes(fixedrange=True)
        fig.update_yaxes(fixedrange=True)
        layout_settings = { "title": title, "font": {"family": "Tajawal"}, "plot_bgcolor": "rgba(240, 240, 240, 0.8)", "paper_bgcolor": "white", "legend": { "orientation": "h", "yanchor": "bottom", "xanchor": "center", "x": 0.5, } }
        if is_mobile:
            mobile_settings = { "height": 300 if chart_type != "heatmap" else 350, "margin": {"t": 40, "b": 100, "l": 10, "r": 10, "pad": 0}, "font": {"size": 10}, "title": {"font": {"size": 13}}, "legend": {"y": -0.4, "font": {"size": 9}} }
            layout_settings.update(mobile_settings)
            if chart_type == "pie": layout_settings["showlegend"] = False
            elif chart_type == "line": fig.update_traces(marker=dict(size=5))
            elif chart_type == "bar": fig.update_xaxes(tickangle=0, tickfont={"size": 8})
        else: # Desktop settings
            desktop_settings = { "height": 450 if chart_type != "heatmap" else 400, "margin": {"t": 50, "b": 90, "l": 30, "r": 30, "pad": 4}, "legend": {"y": -0.25, "font": {"size": 10}} }
            layout_settings.update(desktop_settings)
        fig.update_layout(**layout_settings)
    except Exception as e: st.warning(f"Could not apply layout settings for chart '{title}': {e}")
    return fig

# دوال تحميل البيانات (Dummy implementations - Kept as is)
def get_github_file_content(path):
     st.warning(f"Using dummy data for {path}. Implement `get_github_file_content`.")
     if "department_summary.csv" in path: data = { "البرنامج": ["بكالوريوس في القرآن وعلومه", "بكالوريوس القراءات", "ماجستير الدراسات القرآنية المعاصرة", "ماجستير القراءات", "دكتوراه علوم القرآن", "دكتوراه القراءات"], "عدد الطلاب": [210, 180, 150, 200, 120, 140], "أعضاء هيئة التدريس": [15, 12, 8, 10, 5, 6] }; return pd.DataFrame(data)
     return pd.DataFrame()
@st.cache_data(ttl=3600)
def load_department_summary():
    try: data = { "البرنامج": ["بكالوريوس في القرآن وعلومه", "بكالوريوس القراءات", "ماجستير الدراسات القرآنية المعاصرة", "ماجستير القراءات", "دكتوراه علوم القرآن", "دكتوراه القراءات"], "عدد الطلاب": [210, 180, 150, 200, 120, 140], "أعضاء هيئة التدريس": [15, 12, 8, 10, 5, 6] }; return pd.DataFrame(data)
    except Exception as e: st.error(f"Error loading department summary: {e}"); return pd.DataFrame({ "البرنامج": [], "عدد الطلاب": [], "أعضاء هيئة التدريس": [] })
@st.cache_data(ttl=3600)
def load_yearly_data():
    years = list(range(2020, 2025)); data = []; programs = ["بكالوريوس في القرآن وعلومه", "بكالوريوس القراءات", "ماجستير الدراسات القرآنية المعاصرة", "ماجستير القراءات", "دكتوراه علوم القرآن", "دكتوراه القراءات"]
    for year in years:
        for program in programs: program_hash = int(hashlib.md5(program.encode()).hexdigest(), 16) % 100; data.append({ "العام": year, "البرنامج": program, "عدد الطلاب": 100 + (year - 2020) * 10 + program_hash % 100, "نسبة النجاح": min(95, 70 + (year - 2020) * 2 + program_hash % 10), "معدل الرضا": min(90, 75 + (year - 2020) * 1.5 + (program_hash // 2) % 10) })
    return pd.DataFrame(data)
@st.cache_data(ttl=3600)
def load_faculty_achievements():
    achievements = [ {"العضو": "د. محمد أحمد", "الإنجاز": "نشر بحث في مجلة عالمية", "التاريخ": "2025-04-15", "النقاط": 50, "البرنامج": "بكالوريوس في القرآن وعلومه"}, {"العضو": "د. عائشة سعد", "الإنجاز": "إطلاق مبادرة تعليمية", "التاريخ": "2025-04-10", "النقاط": 40, "البرنامج": "دكتوراه علوم القرآن"}, {"العضو": "د. عبدالله محمد", "الإنجاز": "المشاركة في مؤتمر دولي", "التاريخ": "2025-04-05", "النقاط": 35, "البرنامج": "بكالوريوس القراءات"}, {"العضو": "د. فاطمة علي", "الإنجاز": "تطوير مقرر دراسي", "التاريخ": "2025-04-01", "النقاط": 30, "البرنامج": "ماجستير الدراسات القرآنية المعاصرة"}, {"العضو": "د. خالد إبراهيم", "الإنجاز": "تقديم ورشة عمل", "التاريخ": "2025-03-25", "النقاط": 25, "البرنامج": "ماجستير القراءات"} ]
    return pd.DataFrame(achievements)
@st.cache_data(ttl=3600)
def load_top_faculty():
    top_faculty = [ {"الاسم": "د. عائشة سعد", "اللقب": "العضو القمة", "الشارة": "👑", "النقاط": 320, "البرنامج": "دكتوراه علوم القرآن"}, {"الاسم": "د. محمد أحمد", "اللقب": "العضو المميز", "الشارة": "🌟", "النقاط": 280, "البرنامج": "بكالوريوس في القرآن وعلومه"}, {"الاسم": "د. عبدالله محمد", "اللقب": "العضو الفعال", "الشارة": "🔥", "النقاط": 210, "البرنامج": "بكالوريوس القراءات"} ]
    return pd.DataFrame(top_faculty)

# تحميل وعرض البيانات (تبقى كما هي)
mobile_view = is_mobile()
try:
    dept_data = load_department_summary(); total_students = dept_data["عدد الطلاب"].sum() if "عدد الطلاب" in dept_data.columns else 0; total_faculty = dept_data["أعضاء هيئة التدريس"].sum() if "أعضاء هيئة التدريس" in dept_data.columns else 0
    yearly_data = load_yearly_data()
    if "العام" in yearly_data.columns and 2024 in yearly_data["العام"].values: latest_year_data = yearly_data[yearly_data["العام"] == 2024].copy()
    else: st.warning("بيانات عام 2024 غير متوفرة."); latest_year_data = pd.DataFrame()
    faculty_achievements = load_faculty_achievements(); top_faculty = load_top_faculty()
    if latest_year_data.empty and not dept_data.empty: st.info("استخدام بيانات ملخص القسم للرسوم البيانية."); latest_year_data = dept_data
except Exception as e:
    st.error(f"خطأ في تحميل أو تهيئة البيانات: {e}"); st.warning("استخدام بيانات تجريبية.")
    total_students = 1000; total_faculty = 50
    dept_data = pd.DataFrame({"البرنامج": ["برنامج تجريبي"], "عدد الطلاب": [1000], "أعضاء هيئة التدريس": [50]})
    latest_year_data = pd.DataFrame({ "العام": [2024], "البرنامج": ["برنامج تجريبي"], "عدد الطلاب": [1000], "نسبة النجاح": [85], "معدل الرضا": [90] })
    yearly_data = latest_year_data.copy(); faculty_achievements = pd.DataFrame(); top_faculty = pd.DataFrame()

# عرض المقاييس والرسوم البيانية ... الخ (تبقى كما هي)
st.subheader("المؤشرات الرئيسية") # This is the remaining title/subheader
cols_metrics = st.columns(4)
with cols_metrics[0]: st.metric("إجمالي الطلاب", f"{total_students:,}")
with cols_metrics[1]: st.metric("أعضاء هيئة التدريس", f"{total_faculty:,}")
indicators_to_plot = []
if not latest_year_data.empty and "نسبة النجاح" in latest_year_data.columns: avg_success = latest_year_data["نسبة النجاح"].mean(); indicators_to_plot.append("نسبة النجاح"); cols_metrics[2].metric("متوسط النجاح", f"{avg_success:.0f}%")
if not latest_year_data.empty and "معدل الرضا" in latest_year_data.columns: avg_satisfaction = latest_year_data["معدل الرضا"].mean(); indicators_to_plot.append("معدل الرضا"); cols_metrics[3].metric("متوسط الرضا", f"{avg_satisfaction:.0f}%")

if not latest_year_data.empty and "البرنامج" in latest_year_data.columns and "عدد الطلاب" in latest_year_data.columns:
    st.subheader("تحليل البرامج الأكاديمية")
    program_mapping = { "بكالوريوس في القرآن وعلومه": "ب. قرآن", "بكالوريوس القراءات": "ب. قراءات", "ماجستير الدراسات القرآنية المعاصرة": "م. دراسات", "ماجستير القراءات": "م. قراءات", "دكتوراه علوم القرآن": "د. قرآن", "دكتوراه القراءات": "د. قراءات" }
    display_data = latest_year_data.copy()
    if "البرنامج" in display_data.columns: display_data["البرنامج_المختصر"] = display_data["البرنامج"].map(program_mapping).fillna(display_data["البرنامج"])
    else: display_data["البرنامج_المختصر"] = display_data["البرنامج"]
    tab_labels = ["توزيع الطلاب", "مقارنة المؤشرات", "التطور السنوي"]; tabs = st.tabs(tab_labels)
    with tabs[0]:
        col1_tab1, col2_tab1 = st.columns([1, 1])
        with col1_tab1: fig_pie = px.pie(display_data, values="عدد الطلاب", names="البرنامج_المختصر", title="توزيع الطلاب", color_discrete_sequence=px.colors.qualitative.Pastel); fig_pie = prepare_chart_layout(fig_pie, "توزيع الطلاب", is_mobile=mobile_view, chart_type="pie"); st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
        with col2_tab1: fig_bar = px.bar(display_data.sort_values("عدد الطلاب", ascending=True), y="البرنامج_المختصر", x="عدد الطلاب", title="عدد الطلاب لكل برنامج", color="عدد الطلاب", orientation='h', color_continuous_scale="Blues"); fig_bar = prepare_chart_layout(fig_bar, "عدد الطلاب لكل برنامج", is_mobile=mobile_view, chart_type="bar"); st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
    with tabs[1]:
         if indicators_to_plot: fig_indicators = px.bar(display_data, x="البرنامج_المختصر", y=indicators_to_plot, barmode="group", title="مقارنة المؤشرات", labels={"value": "النسبة المئوية", "variable": "المؤشر", "البرنامج_المختصر": "البرنامج"}, color_discrete_sequence=["#1e88e5", "#27AE60"]); fig_indicators = prepare_chart_layout(fig_indicators, "مقارنة المؤشرات", is_mobile=mobile_view, chart_type="bar"); st.plotly_chart(fig_indicators, use_container_width=True, config={"displayModeBar": False})
         else: st.info("لا توجد بيانات مؤشرات لعرض المقارنة.")
    with tabs[2]:
        if not yearly_data.empty and "البرنامج" in yearly_data.columns:
            unique_programs_full = yearly_data["البرنامج"].unique(); program_options_display = {program_mapping.get(p, p): p for p in unique_programs_full}
            selected_display_program = st.selectbox("اختر البرنامج لعرض تطوره:", options=list(program_options_display.keys())); selected_program_full = program_options_display[selected_display_program]
            program_data = yearly_data[yearly_data["البرنامج"] == selected_program_full].copy()
            trend_indicators = [];
            if "عدد الطلاب" in program_data.columns: trend_indicators.append("عدد الطلاب")
            if "نسبة النجاح" in program_data.columns: trend_indicators.append("نسبة النجاح")
            if "معدل الرضا" in program_data.columns: trend_indicators.append("معدل الرضا")
            if trend_indicators and "العام" in program_data.columns: fig_trend = px.line(program_data, x="العام", y=trend_indicators, title=f"تطور مؤشرات: {selected_display_program}", labels={"value": "القيمة", "variable": "المؤشر", "العام": "السنة"}, markers=True); fig_trend = prepare_chart_layout(fig_trend, f"تطور: {selected_display_program}", is_mobile=mobile_view, chart_type="line"); st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})
            else: st.info(f"لا توجد بيانات كافية لعرض التطور السنوي لبرنامج {selected_display_program}.")
        else: st.info("لا توجد بيانات سنوية لعرض التطور.")
else: st.info("لا توجد بيانات كافية لعرض الرسوم البيانية للبرامج.")

st.subheader("أعضاء هيئة التدريس والإنجازات")
if not top_faculty.empty or not faculty_achievements.empty:
    col1_faculty, col2_faculty = st.columns([1, 1])
    with col1_faculty:
        st.markdown("#### 🏆 المميزون")
        # ... (faculty display code remains the same) ...
        if not top_faculty.empty:
            num_to_display = min(len(top_faculty), 3)
            for _, member in top_faculty.head(num_to_display).iterrows(): name = member.get('الاسم', 'غير متوفر'); badge = member.get('الشارة', ''); title = member.get('اللقب', ''); points = member.get('النقاط', ''); st.markdown(f"""<div class='faculty-card'><h5 style="margin-bottom: 5px;">{badge} {name}</h5><p style="font-size: 0.9em; margin: 2px 0;">{title} ({points} نقطة)</p></div>""", unsafe_allow_html=True)
            st.markdown("<a href='/هيئة_التدريس' target='_top' style='font-size: 0.9em;'>عرض الكل...</a>", unsafe_allow_html=True)
        else: st.info("لا توجد بيانات لأعضاء هيئة التدريس المميزين.")
    with col2_faculty:
        st.markdown("#### 🌟 أحدث الإنجازات")
        # ... (achievements display code remains the same) ...
        if not faculty_achievements.empty:
            num_to_display = min(len(faculty_achievements), 3)
            if 'التاريخ' in faculty_achievements.columns: faculty_achievements['التاريخ'] = pd.to_datetime(faculty_achievements['التاريخ'], errors='coerce'); achievements_to_display = faculty_achievements.sort_values('التاريخ', ascending=False).head(num_to_display)
            else: achievements_to_display = faculty_achievements.head(num_to_display)
            for _, achievement in achievements_to_display.iterrows(): member_name = achievement.get('العضو', 'غير معروف'); desc = achievement.get('الإنجاز', 'لا يوجد وصف'); date_str = achievement.get('التاريخ', None); formatted_date = date_str.strftime("%Y/%m/%d") if pd.notna(date_str) else ""; st.markdown(f"""<div class='achievement-item'><p style="font-size: 0.95em; margin-bottom: 3px;"><strong>{member_name}</strong></p><p style="font-size: 0.9em; margin-bottom: 3px;">{desc}</p>{f'<p style="font-size: 0.8em; color: grey; margin-bottom: 0;">{formatted_date}</p>' if formatted_date else ''}</div>""", unsafe_allow_html=True)
            st.markdown("<a href='/لوحة_إنجاز_المهام' target='_top' style='font-size: 0.9em;'>عرض الكل...</a>", unsafe_allow_html=True)
        else: st.info("لا توجد بيانات لأحدث الإنجازات.")
else: st.info("لا تتوفر بيانات أعضاء هيئة التدريس أو الإنجازات حاليًا.")

# عرض الخريطة الحرارية (تبقى كما هي)
if not latest_year_data.empty and "البرنامج_المختصر" in display_data.columns and indicators_to_plot:
    st.subheader("نظرة عامة على المؤشرات")
    try:
        heatmap_plot_data = display_data[["البرنامج_المختصر"] + indicators_to_plot].set_index("البرنامج_المختصر")
        fig_heatmap = go.Figure(data=go.Heatmap(z=heatmap_plot_data.values, x=heatmap_plot_data.columns, y=heatmap_plot_data.index, colorscale="Blues", text=heatmap_plot_data.values, texttemplate="%{text:.0f}", textfont={"size": 10 if mobile_view else 12}, hoverongaps = False))
        fig_heatmap = prepare_chart_layout(fig_heatmap, "مقارنة المؤشرات الرئيسية", is_mobile=mobile_view, chart_type="heatmap")
        fig_heatmap.update_layout(xaxis_title="المؤشر", yaxis_title="البرنامج", yaxis=dict(tickfont=dict(size=9 if mobile_view else 10)), margin=dict(l=100))
        st.plotly_chart(fig_heatmap, use_container_width=True, config={"displayModeBar": False})
    except Exception as heatmap_error: st.warning(f"لم يتمكن من إنشاء المخطط الحراري: {heatmap_error}")
elif not latest_year_data.empty: st.info("لا تتوفر بيانات مؤشرات كافية لإنشاء المخطط الحراري.")

# عرض نصائح الاستخدام (تم التحديث ليعكس القائمة المسطحة)
with st.expander("💡 نصائح للاستخدام", expanded=False):
    st.markdown("""
    - **تم تعديل شريط التنقل العلوي:** يعرض الآن الأقسام الرئيسية والبرامج الأكاديمية مباشرة بشكل أفقي على الشاشات الكبيرة.
    - على الجوال، تظهر نفس القائمة بشكل رأسي عند النقر على أيقونة البرجر (☰).
    - **تم حذف "الاستطلاعات والتقييمات" و "لوحة التحكم" من القائمة.**
    - استخدم الروابط في القائمة العلوية أو قائمة الجوال للتنقل المباشر.
    - الرسوم البيانية تفاعلية، مرر الفأرة فوقها لرؤية التفاصيل.
    - **مفاتيح الرسوم البيانية تظهر الآن أسفلها لتوفير المساحة.**
    - انقر على زر السهم ↑ في الأسفل للعودة إلى أعلى الصفحة بسرعة.
    """)
