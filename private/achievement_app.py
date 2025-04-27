# -*- coding: utf-8 -*-
import streamlit as st, pandas as pd, requests, base64, io, uuid
from datetime import datetime
from github import Github

# -------------------------------------------------------------------------
# أسرار التطبيق (ضعها في .streamlit/secrets.toml)
GITHUB_TOKEN   = st.secrets["github_token"]
MASTER_PASS    = st.secrets["master_password"]
DEESEEK_KEY    = st.secrets["deepseek_key"]

REPO_NAME      = "ORG/taif-quran-readings-dashboard"

# -------------------------------------------------------------------------
# الفئات (لن تُعرَض للمستخدم)
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
# أدوات GitHub ------------------------------------------------------------
def gh_repo():
    return Github(GITHUB_TOKEN).get_repo(REPO_NAME)

def load_csv(path:str):
    repo = gh_repo()
    try:
        file = repo.get_contents(path)
        data = base64.b64decode(file.content).decode("utf-8-sig")
        return pd.read_csv(io.StringIO(data)), file.sha
    except Exception:
        return pd.DataFrame(), None

def save_csv(path:str, df:pd.DataFrame, sha:str|None, msg:str):
    repo = gh_repo()
    content = df.to_csv(index=False, line_terminator="\n", encoding="utf-8-sig")
    if sha:
        repo.update_file(path, msg, content, sha)
    else:
        repo.create_file(path, msg, content)

def year_path(y:int):         # مسار ملف الإنجازات للسنة
    return f"data/department/{y}/achievements_{y}.csv"

# -------------------------------------------------------------------------
# DeepSeek (التصنيف + النقاط) --------------------------------------------
def deepseek_eval(text:str)->dict:
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
        headers={"Authorization":f"Bearer {DEESEEK_KEY}"},
        json=prompt, timeout=25
    )
    return r.json()["choices"][0]["message"]["function_call"]["arguments"]

# -------------------------------------------------------------------------
# تهيئة الواجهة -----------------------------------------------------------
st.set_page_config("لوحة الإنجازات", layout="centered")

if "auth" not in st.session_state:
    st.session_state.auth = False
if not st.session_state.auth:
    pw = st.text_input("كلمة المرور العامة", type="password")
    if st.button("دخول"):
        st.session_state.auth = (pw == MASTER_PASS)
        st.experimental_rerun()
    st.stop()

# -------------------------------------------------------------------------
# بيانات المستخدم ---------------------------------------------------------
with st.sidebar:
    st.header("بيانات المستخدم")
    member = st.text_input("الاسم الثلاثي")
    year   = st.number_input("السنة", 2010, datetime.now().year,
                             datetime.now().year, step=1)
if not member.strip():
    st.info("اكتب اسمك أولًا.")
    st.stop()

# -------------------------------------------------------------------------
# ### NEW – تحميل/إدارة المهام الرئيسية ------------------------------------
main_df, main_sha = load_csv("data/main_tasks.csv")
if main_df.empty:
    main_df = pd.DataFrame(columns=["id","title","descr"])

titles = main_df["title"].tolist()
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
        save_csv("data/main_tasks.csv", main_df, main_sha,
                 f"add main task {new_title}")
        st.success("تمت إضافة المهمة الرئيسية.")
        st.experimental_rerun()
elif choice.startswith("—"):
    st.warning("اختر مهمة رئيسية أو أضف واحدة.")
    st.stop()
else:
    main_id = main_df.loc[main_df["title"]==choice,"id"].iloc[0]

# -------------------------------------------------------------------------
# تحميل مهام السنة لهذا العضو ---------------------------------------------
df, sha = load_csv(year_path(year))
if df.empty:
    df = pd.DataFrame(columns=[
        "العضو","الإنجاز","التاريخ","النقاط",
        "الفئة","الساعات الافتراضية","main_id"
    ])

my = df[df["العضو"]==member].reset_index(drop=True)

st.subheader(f"مهامك في {year}")
if my.empty:
    st.caption("لا مهام حتى الآن.")
else:
    for i in my.index:
        col1,col2 = st.columns([8,1])
        with col1:
            st.markdown(f"**{my.loc[i,'الإنجاز']}**  \n{my.loc[i,'التاريخ']}")
        with col2:
            if st.button("🗑️", key=f"del-{i}"):
                df.drop(my.index[i], inplace=True)
                save_csv(year_path(year), df, sha,
                         f"delete achievement by {member}")
                st.experimental_rerun()

# -------------------------------------------------------------------------
# ### NEW – نموذج إدخال “مخفي التفاصيل” -----------------------------------
st.markdown("---")
st.subheader("إضافة مهمة جزئية")

with st.form("add_task", clear_on_submit=True):
    date = st.date_input("التاريخ")
    desc = st.text_area("وصف المهمة", height=120)
    ok   = st.form_submit_button("إرســــال")

if ok:
    if not desc.strip():
        st.error("الوصف مطلوب.")
        st.stop()
    with st.spinner("يتم الحفظ..."):
        eva = deepseek_eval(desc)      # التصنيف + النقاط خلف الستار
        new_row = pd.Series({
            "العضو": member,
            "الإنجاز": desc,
            "التاريخ": date.isoformat(),
            "النقاط": eva["points"],
            "الفئة":  eva["category_label"],
            "الساعات الافتراضية": eva["virtual_hours"],
            "main_id": main_id
        })
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_csv(year_path(year), df, sha,
                 f"add achievement by {member} ({date})")
    st.success("تمت إضافة المهمة.")
    st.experimental_rerun()
