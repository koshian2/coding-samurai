import pandas as pd
import streamlit as st

def select_category(df, pref_df, category_name):
    if category_name != "全体":
        filter_df = df.query("category == @category_name")
    else:
        filter_df = df
    kokudaka = filter_df.groupby("pref_code")["kokudaka_1"].sum()
    pref_sub = pref_df[pref_df["pref_id"].isin(kokudaka.index)]
    total = pd.merge(pref_sub, kokudaka, left_on="pref_id", right_index=True)
    scale = max(total["kokudaka_1"].max()/100000, 4)
    total["kokudaka_vis"] = total["kokudaka_1"] / scale
    total = total.style.format(precision=0, thousands=",", decimal=".")
    return total

def main():
    kokudaka_df = pd.read_csv("kokudaka.csv")
    kokudaka_df["pref_code"] = kokudaka_df["city_code"].astype(str).apply(
        lambda x: int(x[:2]) if len(x) == 5 else int(x[:1])) # prefecture id
    pref_df = pd.read_csv("pref.csv")

    st.title("石高マップ")
    category_name = st.selectbox("カテゴリーを選択",
                                 ["全体"]+kokudaka_df["category"].unique().tolist())

    if category_name:
        total = select_category(kokudaka_df, pref_df, category_name)
        st.map(total, latitude="lat", longitude="lng", size="kokudaka_vis")
        st.sidebar.dataframe(total, column_order=["pref", "kokudaka_1"], height=800, column_config={
            "pref": st.column_config.TextColumn("現在の都道府県"),
            "kokudaka_1": st.column_config.NumberColumn("旧高", format="%.0f")
        })

if __name__ == "__main__":
    main()