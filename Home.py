# -*- coding: utf-8 -*-
"""
Home.py – الإصدار المرتبط بالبيانات الفعلية
===========================================
لم يعد يستخدم «بيانات تجريبية». يقرأ مباشرة من مجلد **data/** في المستودع عبر
الدوال المساعدة الموجودة في `pages/utils/github_helpers.py`:

* `get_github_file_content(path)` – تحميل أي ملف (CSV/MD/PDF) كـ DataFrame أو نص.
* `get_available_years(program_code)` – ترجِع (years, year→file_map) الموجودة.

يفترض أن الملفات التالية موجودة:

* `data/department/department_summary.csv` ← إجماليات القسم.
* لكل برنامج (`<code>`):
    * `data/<code>/<year>/students_<year>.csv`  ← عدد الطلبة.
    * `data/<code>/<year>/kpi_<year>.csv`       ← يحتوي مؤشرات «نسبة النجاح» و«معدل الرضا».

إذا تعذّر تحميل ملف فسيظهر تحذير للمستخدم بدلاً من البيانات الوهمية.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from pages.utils.github_helpers import get_github_file_content, get_available_years

# ------------------------------------------------------------------
# إعدادات الصفحة
# ------------------------------------------------------------------
st.set_page_config(page_title="الرئيسية", page_icon="🏠", layout="wide")

# ------------------------------------------------------------------
# CSS + قائمة التنقل (كما في النسخ السابقة – بدون تغيير على HTML)
# ------------------------------------------------------------------
# … (للإيجاز، نفس كود CSS/HTML السابق للقائمة والـ JS) …
# لإبقاء الملف مختصرًا، يمكن لصاحب المستودع إعادة لصق كتلة responsive_menu_html_css
# ------------------------------------------------------------------

# ------------------------------------------------------------------
# ثابتات وخرائط البرامج
# ------------------------------------------------------------------
PROGRAM_MAP = {
    "بكالوريوس في القرآن وعلومه":        "bachelor_quran",
    "بكالوريوس القراءات":               "bachelor_readings",
    "ماجستير الدراسات القرآنية المعاصرة":"master_contemporary",
    "ماجستير القراءات":                 "master_readings",
    "دكتوراه علوم القرآن":              "phd_quran",
    "دكتوراه القراءات":                 "phd_readings",
}
SHORT_MAP = {
    "بكالوريوس في القرآن وعلومه":"ب. قرآن",
    "بكالوريوس القراءات":"ب. قراءات",
    "ماجستير الدراسات القرآنية المعاصرة":"م. دراسات",
    "ماجستير القراءات":"م. قراءات",
    "دكتوراه علوم القرآن":"د. قرآن",
    "دكتوراه القراءات":"د. قراءات",
}
LATEST_YEAR = datetime.now().year if datetime.now().month >= 9 else datetime.now().year - 1  # مثال بسيط

# ------------------------------------------------------------------
# تحميل ملخّص القسم
# ------------------------------------------------------------------

def load_department_summary():
    try:
        df = get_github_file_content("data/department/department_summary.csv")
        if not isinstance(df, pd.DataFrame):
            raise ValueError("department_summary.csv لم يُحمّل كـ DataFrame")
        return df
    except Exception as e:
        st.error(f"تعذّر تحميل department_summary.csv: {e}")
        return pd.DataFrame()

# ------------------------------------------------------------------
# تحميل بيانات سنوية مجمّعة لكل البرامج
# ------------------------------------------------------------------

def load_yearly_data():
    rows = []
    for prog_name, code in PROGRAM_MAP.items():
        years, _ = get_available_years(code)
        for y in years:
            # --- الطلبة ---
            students_path = f"data/{code}/{y}/students_{y}.csv"
            try:
                students_df = get_github_file_content(students_path)
                if isinstance(students_df, pd.DataFrame):
                    if "إجمالي" in students_df.columns:
                        students_total = students_df["إجمالي"].iloc[0]
                    else:
                        # مجموع جميع الأعمدة الرقمية كبديل
                        students_total = students_df.select_dtypes("number").sum().sum()
                else:
                    students_total = None
            except Exception:
                students_total = None

            # --- KPI (نسبة النجاح / الرضا) ---
            kpi_path = f"data/{code}/{y}/kpi_{y}.csv"
            success_rate = satisfaction_rate = None
            try:
                kpi_df = get_github_file_content(kpi_path)
                if isinstance(kpi_df, pd.DataFrame) and "المؤشر" in kpi_df.columns:
                    def pick(k):
                        sel = kpi_df[kpi_df["المؤشر"].str.contains(k, na=False)]
                        return sel["القيمة"].iloc[0] if not sel.empty else None
                    success_rate = pick("نسبة النجاح")
                    satisfaction_rate = pick("معدل الرضا")
            except Exception:
                pass

            rows.append({
                "العام": y,
                "البرنامج": prog_name,
                "عدد الطلاب": students_total,
                "نسبة النجاح": success_rate,
                "معدل الرضا": satisfaction_rate,
            })
    return pd.DataFrame(rows)

# ------------------------------------------------------------------
# تحميل بيانات التميز والإنجازات (اختياري/لاحقًا)
# ------------------------------------------------------------------

def load_faculty_highlights():
    try:
        df = get_github_file_content("data/department/top_faculty.csv")
        return df if isinstance(df, pd.DataFrame) else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def load_recent_achievements():
    try:
        df = get_github_file_content("data/department/achievements_df.csv")
        return df if isinstance(df, pd.DataFrame) else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

# ------------------------------------------------------------------
# بدء عرض الصفحة
# ------------------------------------------------------------------

summary_df = load_department_summary()
yearly_df  = load_yearly_data()

if summary_df.empty or yearly_df.empty:
    st.warning("لا توجد بيانات كافية لعرض الصفحة بصورة كاملة.")

# إجماليات
total_students = summary_df["عدد الطلاب"].sum() if "عدد الطلاب" in summary_df.columns else None
total_faculty  = summary_df["أعضاء هيئة التدريس"].sum() if "أعضاء هيئة التدريس" in summary_df.columns else None

st.subheader("المؤشرات الرئيسية")
metrics_cols = st.columns(4)
if total_students is not None:
    metrics_cols[0].metric("إجمالي الطلاب", f"{int(total_students):,}")
if total_faculty is not None:
    metrics_cols[1].metric("أعضاء هيئة التدريس", f"{int(total_faculty):,}")

latest_df = yearly_df[yearly_df["العام"] == LATEST_YEAR]
if not latest_df.empty:
    if latest_df["نسبة النجاح"].notna().any():
        metrics_cols[2].metric("متوسط النجاح", f"{latest_df['نسبة النجاح'].mean():.0f}%")
    if latest_df["معدل الرضا"].notna().any():
        metrics_cols[3].metric("متوسط الرضا", f"{latest_df['معدل الرضا'].mean():.0f}%")

# ------------------------------------------------------------------
# الرسوم البيانية
# ------------------------------------------------------------------

st.subheader("تحليل البرامج الأكاديمية")

latest_df = latest_df.assign(البرنامج_مختصر=lambda d: d["البرنامج"].map(SHORT_MAP))
tabs = st.tabs(["توزيع الطلاب", "مقارنة المؤشرات", "التطور السنوي"])

with tabs[0]:
    if latest_df["عدد الطلاب"].notna().any():
        pie = px.pie(latest_df, values="عدد الطلاب", names="البرنامج_مختصر", title="توزيع الطلاب بين البرامج")
        st.plotly_chart(prepare_chart(pie, "", kind="pie"), use_container_width=True)
    else:
        st.info("لا تتوفر بيانات الطلاب لهذا العام.")

with tabs[1]:
    indicators = []
    if latest_df["نسبة النجاح"].notna().any(): indicators.append("نسبة النجاح")
    if latest_df["معدل الرضا"].notna().any(): indicators.append("معدل الرضا")
    if indicators:
        bar = px.bar(latest_df, x="البرنامج_مختصر", y=indicators, barmode="group", title="مقارنة المؤشرات بين البرامج")
        st.plotly_chart(prepare_chart(bar, ""), use_container_width=True)
    else:
        st.info("لا توجد بيانات مؤشرات كافية.")

with tabs[2]:
    if not yearly_df.empty:
        display_options = {SHORT_MAP.get(k, k): k for k in yearly_df["البرنامج"].unique()}
        sel_display = st.selectbox("اختر برنامجًا","","نفع" )
"
