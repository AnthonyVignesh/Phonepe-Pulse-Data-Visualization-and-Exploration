import os
import json
import pandas as pd
import psycopg2
import streamlit as st
import plotly.express as px
import numpy as np
import requests

# Connecting the PostgreSQL
mydb = psycopg2.connect(
    host="localhost",
    user="postgres",
    password="Hannah$2686",
    database="phonepe",
    port="5432"
)

cursor = mydb.cursor()

# streamlit creation

# Setting page configuration
st.set_page_config(page_title="Phonepe Pulse Data Visualization", layout="wide", page_icon="point_right")
st.header("Phonepe Pulse Data Visualization and Exploration", divider='rainbow')
st.sidebar.header(":wave: :violet[Hello! Welcome to the Visualization dashboard]")

with st.sidebar:
    buttons=st.radio("Please select below options",["Home","Aggregated","Mapped","Top Transactions","Top Users", "Questions"])

# query for store all state names in single variable
query_states = """SELECT DISTINCT states FROM mapped_transactions
                    order by states"""
cursor.execute(query_states)  # Execute the query
mydb.commit()
t1 = cursor.fetchall()        
all_states = pd.DataFrame(t1, columns=["states"])

def aggregated():
    def agg_trans():
        col1, col2 = st.columns(2)
        with col1:
            selected_quarters1 = st.selectbox(
                'Please select a Quarter for aggregated_transaction', ('1', '2', '3', '4'))
        with col2:
            selected_years1 = st.selectbox(
                'Please select a Year for aggregated_transaction', (2018, 2019, 2020, 2021, 2022, 2023))
            
        # Constructing the SQL query based on selected quarters and years
        if selected_quarters1 and selected_years1:
            quarters_filter1 = selected_quarters1
            years_filter1 = selected_years1

            query1 = f"""SELECT states, years, quarters, transaction_type,  SUM(transaction_count) / 100000 AS trxn_CNT_in_lakhs, SUM(transaction_amount) / 100000 AS trxn_AMT_in_lakhs
                        FROM aggregated_transactions
                        WHERE quarters IN ({quarters_filter1}) AND years IN ({years_filter1})
                        GROUP BY states, years, quarters, transaction_type
                        ORDER BY states"""

            cursor.execute(query1)  # Execute the query
            mydb.commit()
            t1 = cursor.fetchall()        
            df1 = pd.DataFrame(t1, columns=["states", "years", "quarters", "transaction_type", "trxn_CNT_in_lakhs", "trxn_AMT_in_lakhs"])
            fig1 = px.choropleth(
                df1,
                geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
                featureidkey='properties.ST_NM',
                locations='states',
                color='states',
                hover_data=['states', "years", "quarters", "transaction_type", 'trxn_CNT_in_lakhs', "trxn_AMT_in_lakhs"],
                title="Aggregated_transaction",
                color_continuous_scale='blues',
                height=600,
                width=1100)
            fig1.update_geos(fitbounds="locations", visible=False)
            st.plotly_chart(fig1)

        selected_state = st.selectbox('Please select a State for aggregated transaction', (all_states))
        if selected_state:
            state_filter = selected_state
        
            query11 = f"""select states, years, quarters, transaction_type, SUM(transaction_count) / 100000 AS trnx_count_in_lakhs, SUM(transaction_amount) / 100000 AS trnx_AMT_in_lakhs
                from aggregated_transactions
                WHERE states = '{state_filter}' AND quarters IN ({quarters_filter1}) AND years IN ({years_filter1})
                group by states, years, quarters, transaction_type
                ORDER BY states"""
            cursor.execute(query11)  # Execute the query
            mydb.commit()
            t11 = cursor.fetchall()
            df11 = pd.DataFrame(t11, columns=["States", "Years", "Quarters", "Transaction type", "Trnx_count_in_lakhs", "Trnx_AMT_in_lakhs"])
            fig11=px.pie(df11,
                    title="Transactions type wise",
                    values="Trnx_AMT_in_lakhs",
                    hover_name="States",
                    hover_data="Trnx_count_in_lakhs",
                    names="Transaction type",
                    height=600,
                    width=1000,
                    hole=.3)

            st.plotly_chart(fig11)


    def agg_users():
        col1, col2 = st.columns(2)
        with col1:
            selected_quarters2 = st.selectbox('Please select a Quarter for aggregated user', ('1', '2', '3', '4'))          
        with col2:
            selected_years2 = st.selectbox(
                'Please select a Year for aggregated user', (2018, 2019, 2020, 2021, 2022, 2023))
            
        # Constructing the SQL query based on selected quarters and years
        if selected_quarters2 and selected_years2:
            quarters_filter2 = selected_quarters2
            years_filter2 = selected_years2

            query2 = f"""select states, years, quarters, brands, SUM(transaction_count) AS transaction_count, percentage
                        from aggregated_users
                        WHERE quarters IN ({quarters_filter2}) AND years IN ({years_filter2})
                        group by states, years, quarters, brands, percentage
                        ORDER BY states"""

            cursor.execute(query2)  # Execute the query
            mydb.commit()
            t2 = cursor.fetchall()        
            df2 = pd.DataFrame(t2, columns=["States", "Years", "Quarters", "Brands", "Transaction count","Percentage"])
            fig2 = px.choropleth(
                df2,
                geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
                featureidkey='properties.ST_NM',
                locations='States',
                color='States',
                hover_data=["States", "Years", "Quarters", "Brands","Transaction count","Percentage"],
                title="Aggregated_Users",
                color_continuous_scale='blues',
               height=600,
                width=1100
            )

            fig2.update_geos(fitbounds="locations", visible=False)
            st.plotly_chart(fig2, use_container_width=False)
            
        selected_state = st.selectbox('Please select a State for aggregated user', (all_states))
        if selected_state:
            state_filter = selected_state
        
            query21 = f"""select states, years, quarters, brands, SUM(transaction_count) AS transaction_count, percentage
                from aggregated_users
                WHERE states = '{state_filter}' AND quarters IN ({quarters_filter2}) AND years IN ({years_filter2})
                group by states, years, quarters, brands, percentage
                ORDER BY states"""
            cursor.execute(query21)  # Execute the query
            mydb.commit()
            t21 = cursor.fetchall()
            df21 = pd.DataFrame(t21, columns=["States", "Years", "Quarters", "Brands", "Transaction count","Percentage"])
            fig21=px.pie(df21,
                    title="Brand wise Registered users",
                    values="Transaction count",
                    hover_name="Brands",
                    # hover_data="Quarters",
                    names="Brands",
                    height=600,
                    width=1000,
                    hole=.3)

            st.plotly_chart(fig21)

    tab1, tab2 = st.tabs(["Aggregated transations", "Aggregated users"])
    with tab1:
        agg_trans()
    with tab2:
        agg_users()

def mapped():
    def mapped_transactions():
        col1, col2 = st.columns(2)
        with col1:
            selected_quarters1 = st.selectbox(
                'Please select Quarter for mapped cases', ('1', '2', '3', '4'))
            
        with col2:
            selected_years1 = st.selectbox(
                'Please select Year for mapped cases', (2018, 2019, 2020, 2021, 2022, 2023))
            
        # Constructing the SQL query based on selected quarters and years
        if selected_quarters1 and selected_years1:
            quarters_filter1 = selected_quarters1
            years_filter1 = selected_years1
            query7 = f"""select states, sum(transaction_count) / 100000 as trxn_CNT_in_lakhs, sum(transaction_amount) / 100000 as trxn_AMT_in_lakhs 
                        from mapped_transactions
                        WHERE quarters IN ({quarters_filter1}) AND years IN ({years_filter1})
                        group by states
                        order by trxn_AMT_in_lakhs desc"""

            cursor.execute(query7)  # Execute the query
            mydb.commit()
            t7 = cursor.fetchall()        
            df7 = pd.DataFrame(t7, columns=["states", "trxn_CNT_in_lakhs", "trxn_AMT_in_lakhs"])
            fig7=px.bar(df7, x="states", y= "trxn_CNT_in_lakhs")


        if selected_quarters1 and selected_years1:
            quarters_filter1 = selected_quarters1
            years_filter1 = selected_years1
            query8 = f"""select states, sum(transaction_count) / 100000 as trxn_CNT_in_lakhs, sum(transaction_amount) / 100000 as trxn_AMT_in_lakhs 
                        from mapped_transactions
                        WHERE quarters IN ({quarters_filter1}) AND years IN ({years_filter1})
                        group by states
                        order by trxn_AMT_in_lakhs desc"""

            cursor.execute(query8)  # Execute the query
            mydb.commit()
            t8 = cursor.fetchall()        
            df8 = pd.DataFrame(t8, columns=["states", "trxn_CNT_in_lakhs", "trxn_AMT_in_lakhs"])
            fig8=px.bar(df8, x="states", y= "trxn_AMT_in_lakhs",)

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig7)
        with col2:
            st.plotly_chart(fig8)


    def mapped_users():
        col1, col2 = st.columns(2)
        years = st.slider("Select a year", 2018, 2023)
        if years:
            years_filter = years
        query9 = f"""select states, years, sum(registered_user) / 100000 as registered_user, sum(app_opens)/ 100000 as app_opens
                    from mapped_users
                    WHERE years IN ({years_filter})
                    group by states, years
                    order by app_opens desc"""

        cursor.execute(query9)  # Execute the query
        mydb.commit()
        t9 = cursor.fetchall()        
        df9 = pd.DataFrame(t9, columns=["states", "years", "registered_user", "app_opens"])
        fig91=px.histogram(df9, title="Application open count", x="states", y= "app_opens")
        fig92=px.histogram(df9, title="Registered users", x="states", y= "registered_user")


        col1,col2=st.columns(2)
        with col1:
            st.plotly_chart(fig91)
        with col2:
            st.plotly_chart(fig92)

    tab1, tab2 = st.tabs(["Mapped transactions", "Mapped users"])
    with tab1:
        mapped_transactions()
    with tab2:
        mapped_users()

# complete code of top transactions
def top_transaction():
    col1, col2 = st.columns(2)

    with col1:
        selected_quarters1 = st.selectbox(
            'Please select transactions districts Quarter', ('1', '2', '3', '4'))
        
    with col2:
        selected_years1 = st.selectbox(
            'Please select transactions districts Year', (2018, 2019, 2020, 2021, 2022, 2023))


    # Constructing the SQL query based on selected quarters and years
    if selected_quarters1 and selected_years1:
        quarters_filter1 = selected_quarters1
        years_filter1 = selected_years1
        query3 = f"""select states, years, districts, sum(transaction_count) / 100000 as trxn_CNT_in_lakhs, sum(transaction_amount) / 100000 as trxn_AMT_in_lakhs
                    from top_transactions_districts
                    WHERE quarters IN ({quarters_filter1}) AND years IN ({years_filter1})
                    group by states, years, quarters, districts
                    order by trxn_AMT_in_lakhs desc limit 10"""

        cursor.execute(query3)  # Execute the query
        mydb.commit()
        t3 = cursor.fetchall()        
        df3 = pd.DataFrame(t3, columns=["States", "Years", "districts", "trxn_CNT_in_lakhs", "trxn_AMT_in_lakhs"])
        fig3=px.bar(df3,title="Top transactions districts wise",
                     x="districts",
                     y="trxn_AMT_in_lakhs",
                     hover_name="States",
                     hover_data="trxn_CNT_in_lakhs",
                     color_discrete_sequence=px.colors.sequential.Peach)

        
    # Constructing the SQL query based on selected quarters and years
    if selected_quarters1 and selected_years1:
        quarters_filter1 = selected_quarters1
        years_filter1 = selected_years1
        query4 = f"""select states, pincode, sum(transaction_count) / 100000 as trxn_CNT_in_lakhs, sum(transaction_amount) / 100000 as trxn_AMT_in_lakhs
                    from top_transactions_pincode
                    WHERE quarters IN ({quarters_filter1}) AND years IN ({years_filter1})
                    group by states, pincode
                    order by trxn_AMT_in_lakhs desc limit 10"""

        cursor.execute(query4)  # Execute the query
        mydb.commit()
        t4 = cursor.fetchall()        
        df4 = pd.DataFrame(t4, columns=["States", "Pincode", "trxn_CNT_in_lakhs", "trxn_AMT_in_lakhs"])
        fig4=px.pie(df4,
                    title="Top transactions pincode wise",
                    values="trxn_AMT_in_lakhs",
                    hover_name="States",
                    hover_data="Pincode",
                    names="Pincode",
                    height=500,
                    width=600,
                    hole=.4)

    if selected_quarters1 and selected_years1:
        quarters_filter1 = selected_quarters1
        years_filter1 = selected_years1
        query5 = f"""select states, districts, sum(transaction_count) as trxn_CNT, sum(transaction_amount) as trxn_AMT
                    from top_transactions_districts
                    WHERE quarters IN ({quarters_filter1}) AND years IN ({years_filter1})
                    group by states, years, quarters, districts
                    order by trxn_AMT limit 10"""

        cursor.execute(query5)  # Execute the query
        mydb.commit()
        t5 = cursor.fetchall()        
        df5 = pd.DataFrame(t5, columns=["States", "Districts", "trxn_CNT", "trxn_AMT"])
        fig5=px.bar(df5,title="Least transactions districts wise",
                x="Districts",
                y="trxn_AMT",
                hover_name="States",
                hover_data="trxn_CNT",
                color_discrete_sequence=px.colors.sequential.Reds_r)

        
    # Constructing the SQL query based on selected quarters and years
    if selected_quarters1 and selected_years1:
        quarters_filter1 = selected_quarters1
        years_filter1 = selected_years1
        query6 = f"""select states, pincode, sum(transaction_count) as transaction_count, sum(transaction_amount) as transaction_amount
                    from top_transactions_pincode
                    WHERE quarters IN ({quarters_filter1}) AND years IN ({years_filter1})
                    group by states, pincode
                    order by transaction_amount limit 10"""

        cursor.execute(query6)  # Execute the query
        mydb.commit()
        t6 = cursor.fetchall()        
        df6 = pd.DataFrame(t6, columns=["States", "Pincode", "Transaction count", "Transaction amount"])
        fig6=px.pie(df6,
                    title="Least transactions pincode wise",
                    values="Transaction amount",
                    hover_name="States",
                    hover_data="Pincode",
                    names="Pincode",
                    height=500,
                    width=600,
                    hole=.4)

    col1,col2=st.columns(2)
    with col1:
        st.plotly_chart(fig3)
    with col2:
        st.write(fig4)

    col1,col2=st.columns(2)
    with col1:
        st.plotly_chart(fig5)
    with col2:
        st.plotly_chart(fig6)


def top_users():
    col1, col2 = st.columns(2)
    with col1:
        selected_quarters1 = st.selectbox(
            'Please select Quarter', ('1', '2', '3', '4'))
        
    with col2:
        selected_years1 = st.selectbox(
            'Please select Year', (2018, 2019, 2020, 2021, 2022, 2023))
        
    # Constructing the SQL query based on selected quarters and years
    if selected_quarters1 and selected_years1:
        quarters_filter1 = selected_quarters1
        years_filter1 = selected_years1
        query11 = f"""select states, years, quarters, pincodes, registered_user
                    from top_users_pincode
                    WHERE quarters IN ({quarters_filter1}) AND years IN ({years_filter1})
                    order by registered_user desc limit 10"""

        cursor.execute(query11)  # Execute the query
        mydb.commit()
        t11 = cursor.fetchall()        
        df11 = pd.DataFrame(t11, columns=["States", "Years", "Quarters", "Pincodes", "Registered user"])
        fig111=px.pie(df11,
                    title="Top Users Pincode",
                    values="Registered user",
                    hover_name="States",
                    hover_data="Pincodes",
                    names="Pincodes",
                    height=500,
                    width=550,
                    hole=.3)

    if selected_quarters1 and selected_years1:
        quarters_filter1 = selected_quarters1
        years_filter1 = selected_years1
        query12 = f"""select states, years, quarters, districts, registered_user
                    from top_users_districts
                    WHERE quarters IN ({quarters_filter1}) AND years IN ({years_filter1})
                    order by registered_user desc limit 10"""

        cursor.execute(query12)  # Execute the query
        mydb.commit()
        t12 = cursor.fetchall()        
        df12 = pd.DataFrame(t12, columns=["States", "Years", "Quarters", "Districts", "Registered user"])
        fig12=px.bar(df12,
                    title="Top Users Districts",
                    x="Districts",
                    y="Registered user",
                    hover_name="States",
                    hover_data="Districts",
                    height=500,
                    width=580,
                    color="Districts")
    col1,col2=st.columns(2)
    with col1:
        st.plotly_chart(fig12)
    with col2:
        st.plotly_chart(fig111)

    if selected_quarters1 and selected_years1:
        quarters_filter1 = selected_quarters1
        years_filter1 = selected_years1
        query13 = f"""select states, years, quarters, districts, registered_user
                    from top_users_districts
                    WHERE quarters IN ({quarters_filter1}) AND years IN ({years_filter1})
                    order by registered_user limit 10"""

        cursor.execute(query13)  # Execute the query
        mydb.commit()
        t13 = cursor.fetchall()        
        df13 = pd.DataFrame(t13, columns=["States", "Years", "Quarters", "Districts", "Registered user"])
        fig13=px.bar(df13,
                    title="Least Users Districts",
                    x="Districts",
                    y="Registered user",
                    hover_name="States",
                    hover_data="Districts",
                    height=500,
                    width=580,
                    color="Districts")

    if selected_quarters1 and selected_years1:
        quarters_filter1 = selected_quarters1
        years_filter1 = selected_years1
        query14 = f"""select states, years, quarters, pincodes, registered_user
                    from top_users_pincode
                    WHERE quarters IN ({quarters_filter1}) AND years IN ({years_filter1})
                    order by registered_user limit 10"""

        cursor.execute(query14)  # Execute the query
        mydb.commit()
        t14 = cursor.fetchall()        
        df14 = pd.DataFrame(t14, columns=["States", "Years", "Quarters", "Pincodes", "Registered user"])
        fig14 = px.pie(df14,
                    title="Least Users Pincodes",
                    values="Registered user",
                    hover_name="States",
                    hover_data="Pincodes",
                    names="Pincodes",
                    height=500,
                    width=550,
                    hole=.3)
    
    col1,col2=st.columns(2)
    with col1:
        st.plotly_chart(fig13)
    with col2:
        st.plotly_chart(fig14)

def questions():
    all_questions=st.selectbox("select below questions",
                    ("1. Which state has the highest transaction amount?",
                        "2. Which mobile brand has the highest transaction count in 2022?",
                        "3. Which mobile brand has the overall lowest transaction count?",
                        "4. In the third Quarter of the year 2021 which state has the highest number of transaction amount?",
                        "5. which state has the highest transaction amount in the year 2018 where the transaction type pertains to Financial services?",
                        "6. Which district has the lowest number of transaction in the year 2020 and what is the overall count?",
                        "7. Which district has the highest number of registered users?",
                        "8. What are the top 10 transactions in Kancheepuram district?",
                        "9. What are the least 10 transaction in Chennai district?",
                        "10. what are the top 10 pin codes have the highest number of transaction amount?",
                        "11 which state has the highest transaction amount in the third quarter of the year 2022 where the transaction type pertains to Recharge & bill ? present in bar chart",
                        "12. In the third quarter of  the year 2021 state Assam what are the highest transaction amount in transaction type wise? present in pie chart?"))
    
    # Execute SQL queries based on the selected question and display the results in a DataFrame
    if all_questions=="1. Which state has the highest transaction amount?":
        # SQL query 1
        question1= """ select states, years, quarters, transaction_type, sum(transaction_count) / 100000 as Trxn_CNT_in_lakhs, sum(transaction_amount) / 100000 as Trxn_AMT_in_lakhs
                        from aggregated_transactions
                        group by states, years, quarters, transaction_type
                        order by Trxn_AMT_in_lakhs desc limit 1"""
        cursor.execute(question1)
        mydb.commit()
        t1=cursor.fetchall()
        df1=pd.DataFrame(t1,columns=["States","Years","Quarters","Transaction type","Trxn_CNT_in_lakhs","Trxn_AMT_in_lakhs"])
        st.write(df1)

    elif all_questions=="2. Which mobile brand has the highest transaction count in 2022?":
        # SQL query 2
        question2= """ select states, years, quarters, brands, transaction_count
                        from aggregated_users
                        where years in ('2022')
                        order by transaction_count desc limit 1"""
        cursor.execute(question2)
        mydb.commit()
        t2=cursor.fetchall()
        df2=pd.DataFrame(t2,columns=["States","Years","Quarters","Brand","Transaction count"])
        st.write(df2)

    elif all_questions=="3. Which mobile brand has the overall lowest transaction count?":
    # SQL query 3
        question3= """ select states, years, quarters, brands, transaction_count
                        from aggregated_users
                        order by transaction_count limit 1"""
        cursor.execute(question3)
        mydb.commit()
        t3=cursor.fetchall()
        df3=pd.DataFrame(t3,columns=["States","Years","Quarters","Brand","Transaction count"])
        st.write(df3)

    elif all_questions=="4. In the third Quarter of the year 2021 which state has the highest number of transaction amount?":
    # SQL query 4
        question4= """ select states, years, quarters, transaction_type, sum(transaction_count) / 100000 as Trxn_CNT_in_lakhs, sum(transaction_amount) / 100000 as Trxn_AMT_in_lakhs
                        from aggregated_transactions
                        where years in (2021) and quarters in ('3')
                        group by states, years, quarters, transaction_type
                        order by Trxn_AMT_in_lakhs desc limit 1"""
        cursor.execute(question4)
        mydb.commit()
        t4=cursor.fetchall()
        df4=pd.DataFrame(t4,columns=["States","Years","Quarters","Transaction type","Trxn CNT in lakhs","Trxn AMT in lakhs"])
        st.write(df4)

    elif all_questions=="5. which state has the highest transaction amount in the year 2018 where the transaction type pertains to Financial services?":
    # SQL query 5
        question5= """ select states, years, quarters, transaction_type, sum(transaction_count) / 100000 as Trxn_CNT_in_lakhs, sum(transaction_amount) / 100000 as Trxn_AMT_in_lakhs
                        from aggregated_transactions
                        where transaction_type in ('Financial Services') and years in (2018)
                        group by states, years, quarters, transaction_type
                        order by Trxn_AMT_in_lakhs desc limit 1"""
        cursor.execute(question5)
        mydb.commit()
        t5=cursor.fetchall()
        df5=pd.DataFrame(t5,columns=["States","Years","Quarters","Transaction type","Trxn CNT in lakhs","Trxn AMT in lakhs"])
        st.write(df5)

    elif all_questions=="6. Which district has the lowest number of transaction in the year 2020 and what is the overall count?":
    # SQL query 6
        question6= """select states, years, quarters, districts, transaction_count
                        from mapped_transactions
                        where years in (2020)
                        order by transaction_count limit 1"""
        cursor.execute(question6)
        mydb.commit()
        t6=cursor.fetchall()
        df6=pd.DataFrame(t6,columns=["States","Years","Quarters","Districts","Transaction_count"])
        st.write(df6)

    elif all_questions=="7. Which district has the highest number of registered users?":
    # SQL query 7
        question7= """select states,years,quarters,districts,sum (registered_user) / 100000 as Register_users_in_lakhs
                    from mapped_users
                    group by states,years,quarters,districts
                    order by Register_users_in_lakhs desc limit 1"""
        cursor.execute(question7)
        mydb.commit()
        t7=cursor.fetchall()
        df7=pd.DataFrame(t7,columns=["States","Years","Quarters","Districts","Register_users_in_lakhs"])
        st.write(df7)

    elif all_questions=="8. What are the top 10 transactions in Kancheepuram district?":
    # SQL query 8
        question8= """select states, years, quarters, districts, sum(transaction_count) / 100000 as Trxn_CNT_in_lakhs, sum(transaction_amount) / 100000 as Trxn_AMT_in_lakhs
                    from mapped_transactions
                    where districts in ('kancheepuram district')
                    group by states, years, quarters, districts
                    order by Trxn_AMT_in_lakhs desc limit 10"""
        cursor.execute(question8)
        mydb.commit()
        t8=cursor.fetchall()
        df8=pd.DataFrame(t8,columns=["States","Years","Quarters","Districts","Trxn_CNT_in_lakhs","Trxn_AMT_in_lakhs"])
        st.write(df8)

    elif all_questions=="9. What are the least 10 transaction in Chennai district?":
    # SQL query 9
        question9= """select states, years, quarters, districts, sum(transaction_count) / 100000 as Trxn_CNT_in_lakhs, sum(transaction_amount) / 100000 as Trxn_AMT_in_lakhs
                    from mapped_transactions
                    where districts in ('chennai district')
                    group by states, years, quarters, districts
                    order by Trxn_AMT_in_lakhs limit 10"""
        cursor.execute(question9)
        mydb.commit()
        t9=cursor.fetchall()
        df9=pd.DataFrame(t9,columns=["States","Years","Quarters","Districts","Trxn_CNT_in_lakhs","Trxn_AMT_in_lakhs"])
        st.write(df9)

    elif all_questions=="10. what are the top 10 pin codes have the highest number of transaction amount?":
    # SQL query 10
        question10= """select states, years, quarters, pincode, sum(transaction_count) / 100000 as Trxn_CNT_in_lakhs, sum(transaction_amount) / 100000 as Trxn_AMT_in_lakhs
                        from top_transactionS_pincode
                        group by states, years, quarters, pincode
                        order by Trxn_AMT_in_lakhs desc limit 10"""
        cursor.execute(question10)
        mydb.commit()
        t10=cursor.fetchall()
        df10=pd.DataFrame(t10,columns=["States","Years","Quarters","Pincode","Trxn_CNT_in_lakhs","Trxn_AMT_in_lakhs"])
        st.write(df10)

    elif all_questions=="11 which state has the highest transaction amount in the third quarter of the year 2022 where the transaction type pertains to Recharge & bill ? present in bar chart":
    # SQL query 11
        question11= """select states, years, quarters, transaction_type, sum(transaction_count) / 100000 as Trxn_CNT_in_lakhs, sum(transaction_amount) / 100000 as Trxn_AMT_in_lakhs
                    from aggregated_transactions
                    where transaction_type in ('Recharge & bill payments') and years in (2022) and quarters in (3)
                    group by states, years, quarters, transaction_type
                    order by Trxn_AMT_in_lakhs desc"""
        cursor.execute(question11)
        mydb.commit()
        t11=cursor.fetchall()
        df11=pd.DataFrame(t11,columns=["States","Years","Quarters","Pincode","Trxn_CNT_in_lakhs","Trxn_AMT_in_lakhs"])
        st.write(df11)
        fig11=px.bar(df11,
                    x="States",
                    y="Trxn_AMT_in_lakhs",
                    color="States",
                    height=500,
                    width=1000)
        st.plotly_chart(fig11)



    elif all_questions=="12. In the third quarter of  the year 2021 state Assam what are the highest transaction amount in transaction type wise? present in pie chart?":
    # SQL query 12
        question12 = """select states, years, quarters, transaction_type, SUM(transaction_count) / 100000 AS trnx_count_in_lakhs, SUM(transaction_amount) / 100000 AS trnx_AMT_in_lakhs
                    from aggregated_transactions
                    WHERE states in ('Assam') AND quarters IN (3) AND years IN (2021)
                    group by states, years, quarters, transaction_type
                    ORDER BY Trnx_AMT_in_lakhs desc"""
        cursor.execute(question12)  # Execute the query
        mydb.commit()
        t12 = cursor.fetchall()
        df12 = pd.DataFrame(t12, columns=["States", "Years", "Quarters", "Transaction type", "Trnx_count_in_lakhs", "Trnx_AMT_in_lakhs"])
        fig12=px.pie(df12,
                title="Transactions type wise",
                values="Trnx_AMT_in_lakhs",
                hover_name="States",
                hover_data="Trnx_count_in_lakhs",
                names="Transaction type",
                height=500,
                width=1000,
                hole=.3)
        st.write(df12)
        st.plotly_chart(fig12)

# Show the output of top_transaction() only if the button is clicked
if buttons=="Aggregated":
    aggregated()
elif buttons=="Mapped":
    mapped()
elif buttons=="Top Transactions":
    top_transaction()
elif buttons=="Top Users":
    top_users()
elif buttons=="Questions":
    questions()