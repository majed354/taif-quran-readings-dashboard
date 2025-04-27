import streamlit as st
import pandas as pd
import requests
import base64
import io
import uuid
from datetime import datetime
import traceback
import time
import json
import os

# -------------------------------------------------------------------------
# الفئات
CATEGORIES = {
    "CURR": "تطوير المناهج",
    "TEAC": "التعليم والتقويم",
    "QUAL": "الاعتماد والجودة",
    "RESR": "بحث علمي ونشر",
    "EVNT": "فعاليات وخدمة مجتمع",
    "STUD": "دعم وخدمات طلابية",
    "ADMN": "مهام إدارية",
    "PDVL": "تطوير مهني"
}

# -------------------------------------------------------------------------
# تهيئة الواجهة -----------------------------------------------------------
st.set_page_config("لوحة الإنجازات", layout="centered")

# CSS للواجهة العربية
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    
    * {
        font-family: 'Tajawal', sans-serif !important;
    }
    body, .stApp {
        direction: rtl;
        text-align: right;
    }
    button, input, select, textarea {
        text-align: right;
    }
    .stTabs [data-baseweb="tab-list"] {
        direction: rtl;
    }
    h1, h2, h3, h4, h5, h6 {
        text-align: right;
    }
    .stButton>button {
        background-color: #1e88e5;
        color: white;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #1565c0;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# معالجة الأخطاء ---------------------------------------------------------
def show_error(error_msg, details=None):
    st.error(f"حدث خطأ: {error_msg}")
    if details:
        with st.expander("تفاصيل الخطأ (للمطورين)"):
            st.code(details)

# -------------------------------------------------------------------------
# التحقق من المتغيرات المطلوبة --------------------------------------------
def check_environment():
    try:
        # تحقق من وجود المتغيرات الضرورية
        required_vars = ["GITHUB_TOKEN", "REPO_NAME", "MASTER_PASS", "DEESEEK_KEY"]
        missing_vars = []

        for var in required_vars:
            if var not in st.secrets:
                missing_vars.append(var)

        if missing_vars:
            show_error(
                f"بعض المتغيرات المطلوبة غير موجودة في ملف الأسرار: {', '.join(missing_vars)}",
                "يجب إضافة هذه المتغيرات إلى ملف .streamlit/secrets.toml"
            )
            return False
        return True
    except Exception as e:
        show_error("خطأ في التحقق من المتغيرات البيئية", str(e))
        return False

# -------------------------------------------------------------------------
# أدوات GitHub ------------------------------------------------------------
def gh_repo():
    try:
        from github import Github
        return Github(st.secrets["GITHUB_TOKEN"]).get_repo(st.secrets["REPO_NAME"])
    except Exception as e:
        show_error("خطأ في الاتصال بمستودع GitHub", traceback.format_exc())
        return None

def load_csv(path:str):
    try:
        repo = gh_repo()
        if not repo:
            return pd.DataFrame(), None
            
        try:
            file = repo.get_contents(path)
            data = base64.b64decode(file.content).decode("utf-8-sig")
            return pd.read_csv(io.StringIO(data)), file.sha
        except Exception as e:
            st.warning(f"لم يتم العثور على الملف: {path} - سيتم إنشاؤه عند الحفظ.")
            return pd.DataFrame(), None
    except Exception as e:
        show_error(f"خطأ في تحميل الملف: {path}", traceback.format_exc())
        return pd.DataFrame(), None

def save_csv(path:str, df:pd.DataFrame, sha:str|None, msg:str):
    try:
        repo = gh_repo()
        if not repo:
            return False
            
        content = df.to_csv(index=False, line_terminator="\n", encoding="utf-8-sig")
        try:
            if sha:
                repo.update_file(path, msg, content, sha)
            else:
                # تأكد من وجود المجلد
                folder_path = '/'.join(path.split('/')[:-1])
                try:
                    repo.get_contents(folder_path)
                except:
                    # المجلد غير موجود، ننشئه
                    parts = folder_path.split('/')
                    current_path = ""
                    for part in parts:
                        if not part:
                            continue
                        current_path += part + "/"
                        try:
                            repo.get_contents(current_path)
                        except:
                            repo.create_file(current_path + ".gitkeep", f"إنشاء مجلد {current_path}", "")
                
                repo.create_file(path, msg, content)
            return True
        except Exception as e:
            show_error(f"خطأ في حفظ الملف: {path}", traceback.format_exc())
            return False
    except Exception as e:
        show_error("خطأ في الاتصال بـ GitHub", traceback.format_exc())
        return False

def year_path(y:int):         # مسار ملف الإنجازات للسنة
    return f"data/department/{y}/achievements_{y}.csv"

# -------------------------------------------------------------------------
# تصنيف المهام (وظيفة احتياطية في حالة فشل DeepSeek) ----------------------
def fallback_classification(text:str)->dict:
    # تصنيف بسيط بناءً على الكلمات المفتاحية
    text_lower = text.lower()
    if any(word in text_lower for word in ["بحث", "نشر", "مقالة", "مؤتمر", "مجلة"]):
        category_code = "RESR"
    elif any(word in text_lower for word in ["مقرر", "منهج", "تطوير", "مادة"]):
        category_code = "CURR"
    elif any(word in text_lower for word in ["تعليم", "تدريس", "محاضر", "تقويم"]):
        category_code = "TEAC"
    elif any(word in text_lower for word in ["جودة", "اعتماد", "تقييم"]):
        category_code = "QUAL"
    elif any(word in text_lower for word in ["خدمة", "مجتمع", "فعالية", "نشاط"]):
        category_code = "EVNT"
    elif any(word in text_lower for word in ["طلاب", "طالب", "إرشاد"]):
        category_code = "STUD"
    elif any(word in text_lower for word in ["إدارة", "لجنة", "اجتماع"]):
        category_code = "ADMN"
    else:
        category_code = "PDVL"  # افتراضي: تطوير مهني
    
    # تقدير النقاط والساعات
    word_count = len(text.split())
    virtual_hours = max(5, min(30, word_count // 10))  # بين 5 و 30 ساعة
    points = virtual_hours * 2  # تقريبًا ضعف الساعات
    
    return {
        "points": points,
        "virtual_hours": virtual_hours,
        "category_code": category_code,
        "category_label": CATEGORIES[category_code]
    }

# -------------------------------------------------------------------------
# DeepSeek (التصنيف + النقاط) --------------------------------------------
def deepseek_eval(text:str)->dict:
    try:
        # أولاً نحاول استخدام DeepSeek API
        prompt = {
            "model":"deepseek-chat",
            "messages":[
                {"role":"system","content":(
                    "أنت مساعد يقيّم إنجازات أكاديمية. اختر أنسب فئة من القائمة التالية:"
                    + "، ".join(f"{k}:{v}" for k,v in CATEGORIES.items())
                    + ". أعد JSON يحوي: points, virtual_hours, category_code, category_label.")},
                {"role":"user","content":text}
            ],
            "functions":[{
                "name":"score_achievement",
                "parameters":{
                    "type":"object",
                    "properties":{
                        "points":{"type":"integer"},
                        "virtual_hours":{"type":"integer"},
                        "category_code":{"type":"string"},
                        "category_label":{"type":"string"}
                    },
                    "required":["points","virtual_hours","category_code","category_label"]
                }
            }]
        }
        
        r = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization":f"Bearer {st.secrets['DEESEEK_KEY']}"},
            json=prompt, timeout=25
        )
        
        response = r.json()
        
        # التحقق من وجود خطأ في استجابة API
        if "error" in response:
            st.warning(f"خطأ في استجابة DeepSeek: {response['error']['message']}. استخدام التصنيف الاحتياطي.")
            return fallback_classification(text)
            
        return json.loads(response["choices"][0]["message"]["function_call"]["arguments"])
        
    except Exception as e:
        st.warning("فشل في استدعاء DeepSeek API. استخدام التصنيف الاحتياطي.")
        return fallback_classification(text)

# -------------------------------------------------------------------------
# الصفحة الرئيسية ---------------------------------------------------------

if "auth" not in st.session_state:
    st.session_state.auth = False

# التحقق من المتغيرات البيئية
env_check = check_environment()

if not env_check:
    st.warning("يرجى إصلاح مشكلات الإعداد قبل المتابعة.")
    st.stop()

# نموذج تسجيل الدخول
if not st.session_state.auth:
    st.title("نظام إدخال المهام")
    pw = st.text_input("كلمة المرور العامة", type="password")
    if st.button("دخول"):
        if pw == st.secrets["MASTER_PASS"]:
            st.session_state.auth = True
            st.success("تم تسجيل الدخول بنجاح!")
            time.sleep(1)  # تأخير قصير لعرض رسالة النجاح
            st.experimental_rerun()
        else:
            st.error("كلمة المرور غير صحيحة!")
    st.stop()

# -------------------------------------------------------------------------
# صفحة إدخال المهام (بعد تسجيل الدخول) -----------------------------------
st.title("نظام إدخال مهام وإنجازات قسم القراءات")

# بيانات المستخدم ---------------------------------------------------------
with st.sidebar:
    st.header("بيانات المستخدم")
    member = st.text_input("الاسم الثلاثي")
    year = st.number_input("السنة", 2010, datetime.now().year,
                         datetime.now().year, step=1)
    
    if st.button("تسجيل الخروج"):
        st.session_state.auth = False
        st.experimental_rerun()
        
if not member.strip():
    st.info("👈 الرجاء إدخال اسمك الثلاثي في القائمة الجانبية")
    st.stop()

# -------------------------------------------------------------------------
# تحميل/إدارة المهام الرئيسية --------------------------------------------
try:
    main_df, main_sha = load_csv("data/main_tasks.csv")
    if main_df.empty:
        main_df = pd.DataFrame(columns=["id","title","descr"])

    titles = main_df["title"].tolist() if "title" in main_df.columns else []
    options = ["— اختر المهمة الرئيسية —"] + titles + ["➕ إضافة مهمة رئيسية…"]
    choice = st.selectbox("المهمة الرئيسية", options, key="main_task")

    if choice == "➕ إضافة مهمة رئيسية…":
        with st.form("add_main"):
            new_title = st.text_input("عنوان المهمة الرئيسية")
            new_descr = st.text_area("وصف مختصر")
            s = st.form_submit_button("حفظ")
        if s and new_title.strip():
            new_id = str(uuid.uuid4())[:8]
            main_df.loc[len(main_df)] = [new_id, new_title, new_descr]
            if save_csv("data/main_tasks.csv", main_df, main_sha,
                     f"add main task {new_title}"):
                st.success("تمت إضافة المهمة الرئيسية.")
                time.sleep(1)  # تأخير قصير لعرض رسالة النجاح
                st.experimental_rerun()
            else:
                st.error("حدث خطأ في حفظ المهمة الرئيسية.")
    elif choice.startswith("—"):
        st.warning("اختر مهمة رئيسية أو أضف واحدة.")
        st.stop()
    else:
        main_id = main_df.loc[main_df["title"]==choice,"id"].iloc[0]
except Exception as e:
    show_error("خطأ في تحميل/إدارة المهام الرئيسية", traceback.format_exc())
    st.stop()

# -------------------------------------------------------------------------
# تحميل مهام السنة لهذا العضو ---------------------------------------------
try:
    df, sha = load_csv(year_path(year))
    if df.empty:
        df = pd.DataFrame(columns=[
            "العضو","الإنجاز","التاريخ","النقاط",
            "الفئة","الساعات الافتراضية","main_id"
        ])

    # استخدم فلتر آمن للمهام الخاصة بالعضو
    my_tasks = df[df["العضو"] == member] if "العضو" in df.columns else pd.DataFrame()
    my = my_tasks.reset_index(drop=True) if not my_tasks.empty else pd.DataFrame()

    st.subheader(f"مهامك في {year}")
    if my.empty:
        st.caption("لا توجد مهام حتى الآن.")
    else:
        for i in my.index:
            col1,col2 = st.columns([8,1])
            with col1:
                achievement = my.loc[i,'الإنجاز'] if 'الإنجاز' in my.columns else ""
                date = my.loc[i,'التاريخ'] if 'التاريخ' in my.columns else ""
                st.markdown(f"**{achievement}**  \n{date}")
            with col2:
                if st.button("🗑️", key=f"del-{i}"):
                    # التأكد من وجود الصف قبل الحذف
                    if i < len(df):
                        df = df.drop(my.index[i])
                        if save_csv(year_path(year), df, sha,
                                 f"delete achievement by {member}"):
                            st.success("تم حذف المهمة بنجاح.")
                            time.sleep(1)  # تأخير قصير لعرض رسالة النجاح
                            st.experimental_rerun()
                        else:
                            st.error("حدث خطأ في حذف المهمة.")
except Exception as e:
    show_error("خطأ في تحميل مهام الأعضاء", traceback.format_exc())

# -------------------------------------------------------------------------
# نموذج إدخال "مخفي التفاصيل" -------------------------------------------
st.markdown("---")
st.subheader("إضافة مهمة جزئية")

with st.form("add_task", clear_on_submit=True):
    date = st.date_input("التاريخ")
    desc = st.text_area("وصف المهمة", height=120)
    ok = st.form_submit_button("إرســــال")

if ok:
    if not desc.strip():
        st.error("الوصف مطلوب.")
        st.stop()
    
    with st.spinner("جاري التصنيف وحفظ المهمة..."):
        try:
            # محاولة تصنيف المهمة باستخدام DeepSeek أو الطريقة الاحتياطية
            eva = deepseek_eval(desc)
            
            # إنشاء صف جديد للمهمة
            new_row = pd.Series({
                "العضو": member,
                "الإنجاز": desc,
                "التاريخ": date.isoformat(),
                "النقاط": eva["points"],
                "الفئة": eva["category_label"],
                "الساعات الافتراضية": eva["virtual_hours"],
                "main_id": main_id
            })
            
            # إضافة الصف الجديد للإطار
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            
            # حفظ الملف المحدث
            if save_csv(year_path(year), df, sha, f"add achievement by {member} ({date})"):
                st.success(f"تمت إضافة المهمة بنجاح! ({eva['points']} نقطة، {eva['virtual_hours']} ساعة، {eva['category_label']})")
                time.sleep(1)  # تأخير قصير لعرض رسالة النجاح
                st.experimental_rerun()
            else:
                st.error("حدث خطأ في حفظ المهمة.")
                
        except Exception as e:
            show_error("خطأ في إضافة المهمة", traceback.format_exc())
