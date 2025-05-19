import pandas as pd
import streamlit as st
import altair as alt

# ---- PAGE CONFIG ----
st.set_page_config(page_title="Organic Search Country Dashboard", layout="wide")

# ---- HEADER ----
st.title("🌍 Organic Google Search Impressions by Country")
st.markdown("Upload your data and analyze total impressions by country.")

# ---- FILE UPLOAD ----
uploaded_file = st.file_uploader("📤 Upload your Excel file", type=["xlsx", "csv"])

if uploaded_file:
    try:
        # Load file (support Excel or CSV)
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)

        df.columns = df.columns.str.strip()  # Clean column names

        # Validate required columns
        required_cols = {'Country', 'Organic Google Search impressions'}
        if not required_cols.issubset(set(df.columns)):
            st.error(f"Missing columns: {required_cols - set(df.columns)}")
            st.stop()

        # Filter rows with impressions > 0
        filtered_df = df[df['Organic Google Search impressions'] > 0]

        # Group by Country and sum impressions
        grouped_df = (
            filtered_df
            .groupby('Country')[['Organic Google Search impressions']]
            .sum()
            .reset_index()
            .sort_values(by='Organic Google Search impressions', ascending=False)
        )

        # Optionally filter countries via multiselect
        countries = grouped_df['Country'].tolist()
        selected_countries = st.multiselect(
            "Select Countries to display",
            options=countries,
            default=countries[:10]  # default top 10 countries
        )

        display_df = grouped_df[grouped_df['Country'].isin(selected_countries)]

        # SUMMARY METRICS
        st.subheader("📊 Summary Metrics")
        total_impressions = display_df['Organic Google Search impressions'].sum()
        st.metric("Total Impressions (Selected Countries)", f"{total_impressions:,}")

        # BAR CHART
        st.subheader("📈 Impressions by Country")
        if not display_df.empty:
            pie_chart = alt.Chart(display_df).mark_arc().encode(
            theta=alt.Theta(field="Organic Google Search impressions", type="quantitative"),
            color=alt.Color(field="Country", type="nominal"),
            tooltip=["Country", "Organic Google Search impressions"]
            ).properties(width=600, height=600)

            st.altair_chart(pie_chart, use_container_width=True)
        else:
            st.info("No data to display for selected countries.")


        # DATA TABLE
        st.subheader("🔍 Data Table")
        st.dataframe(display_df, use_container_width=True)

        # DOWNLOAD OPTIONS
        csv_data = display_df.to_csv(index=False).encode('utf-8')
        html_data = display_df.to_html(index=False).encode('utf-8')

        st.download_button("📥 Download CSV", csv_data, "filtered_impressions.csv", "text/csv")
        st.download_button("📥 Download HTML", html_data, "filtered_impressions.html", "text/html")

    except Exception as e:
        st.error(f"⚠️ Error processing file: {e}")

else:
    st.info("📎 Please upload an Excel (.xlsx) or CSV file to begin.")
