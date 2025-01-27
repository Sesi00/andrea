import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import bcrypt
import streamlit_authenticator as stauth
from sqlite_signup import  fetch_users, sign_up
import datetime

st.set_page_config(page_title="Travel data",
                   page_icon="✈",
                   layout="wide"
)


df = pd.read_csv('Travel_details.csv', delimiter=',', encoding='latin-1')


def login_user(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT username, password FROM users WHERE username=?", (username,))
    row = cursor.fetchone()

    if row is not None:
        stored_password = row[1]
        if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
            return True

    conn.close()
    return False



connection = sqlite3.connect('database.db')
cursor = connection.cursor()

def display_data(connection):
    st.header("All travel data")
    cursor = connection.cursor()
    query = "SELECT * FROM travel_details"
    df = pd.read_sql(query, connection)
    st.dataframe(df)


def add_data(connection):
    st.header("Add new data")
    new_data = {}
    for column in df.columns:
        if column != "Trip_ID":
            if column == "Start_date" or column == "End_date":
                new_date = st.date_input(column)
                new_data[column] = new_date.strftime("%d-%b-%y") if new_date else None
            elif column == "Traveler_age":
                new_value = st.number_input("Traveler Age", key=column, step=1)
                new_data[column] = int(new_value) if new_value is not None else None
            elif column == "Traveler_gender":
                gender_options = ["Male", "Female"]
                selected_gender = st.selectbox("Gender", gender_options)
                new_data[column] = selected_gender
            elif column == "Accommodation_type":
                accommodation_options = ["Hotel", "Resort", "Villa", "Airbnb", "Hostel", "Riad", "Vacation rental", "Guest house"]
                selected_accommodation = st.selectbox("Accommodation Type", accommodation_options)
                new_data[column] = selected_accommodation
            elif column == "Accommodation_cost":
                new_value = st.number_input("Accommodation cost (€)", key=column, step=1)
                new_data[column] = int(new_value) if new_value is not None else None
            elif column == "Transportation_type":
                transportation_options = ["AirPlane", "Train", "Bus", "Car", "Subway", "Ferry"]
                selected_transportation = st.selectbox("Transportation type", transportation_options)
                new_data[column] = selected_transportation
            elif column == "Transportation_cost":
                new_value = st.number_input("Transportation cost (€)", key=column, step=1)
                new_data[column] = int(new_value) if new_value is not None else None
            else:
                custom_label = " ".join([word.capitalize() for word in column.split("_")])
                new_data[column] = st.text_input(custom_label, key=column)

    if st.button("Add new data"):
        
        columns = ', '.join(new_data.keys())


        values = ', '.join([f"'{value}'" if value is not None else "NULL" for value in new_data.values()])
        insert_query = f"INSERT INTO travel_details ({columns}) VALUES ({values})"
        cursor = connection.cursor()
        cursor.execute(insert_query)
        connection.commit()  
        st.success("Podaci su uspešno dodati!")




def update_data(connection, all_data):
    st.header("Update Data")
    st.write("Select the data you want to update:")


    # Odabir redaka za ažuriranje
    rows_to_update = st.multiselect(
        "Select Rows to Update",
        options=[f"ID  {data[0]}" for data in all_data],
    )

    if rows_to_update:
        for row in rows_to_update:
            row_id = int(row.split()[1])
            selected_row = next((data for data in all_data if data[0] == row_id), None)

            if selected_row:
                st.write(f"Updating data for Row {row_id}:")
                new_data = {}
                for i, column in enumerate(df.columns):
                    if column != "Trip_ID" and column != "Duration_days":
                        if column == "Start_date" or column == "End_date":
                            new_date = st.date_input("Start Date" if column == "Start_date" else "End Date")
                            new_data[column] = new_date.strftime("%d-%b-%y") if new_date else None
                        elif column == "Traveler_age":
                            new_value = st.number_input("Traveler Age", key=column, step=1)
                            new_data[column] = int(new_value) if new_value is not None else None
                        elif column == "Traveler_gender":
                            gender_options = ["Male", "Female"]
                            selected_gender = st.selectbox("Gender", gender_options)
                            new_data[column] = selected_gender
                        elif column == "Accommodation_type":
                            accommodation_options = ["Hotel", "Resort", "Villa", "Airbnb", "Hostel", "Riad", "Vacation rental", "Guest house"]
                            selected_accommodation = st.selectbox("Accommodation type", accommodation_options)
                            new_data[column] = selected_accommodation
                        elif column == "Accommodation_cost":
                            new_value = st.number_input("Accommodation cost (€)", key=column, step=1)
                            new_data[column] = int(new_value) if new_value is not None else None
                        elif column == "Transportation_type":
                            transportation_options = ["AirPlane", "Train", "Bus", "Car", "Subway", "Ferry"]
                            selected_transportation = st.selectbox("Transportation type", transportation_options)
                            new_data[column] = selected_transportation
                        elif column == "Transportation_cost":
                            new_value = st.number_input("Transportation cost (€)", key=column, step=1)
                            new_data[column] = int(new_value) if new_value is not None else None
                        else:
                            custom_label = " ".join([word.capitalize() for word in column.split("_")])
                            new_value = st.text_input(custom_label, value=selected_row[i], key=column)
                            new_data[column] = new_value

                if st.button("Update Selected Row"):
                    start_date = datetime.datetime.strptime(new_data["Start_date"], "%d-%b-%y")
                    end_date = datetime.datetime.strptime(new_data["End_date"], "%d-%b-%y")
                    duration_days = (end_date - start_date).days
                    new_data["Duration_Days"] = duration_days

                    set_values = ', '.join([f"{key} = '{value}'" for key, value in new_data.items()])
                    update_query = f"UPDATE travel_details SET {set_values} WHERE Trip_ID = {row_id}"
                    cursor = connection.cursor()
                    cursor.execute(update_query)
                    connection.commit()
                    st.success("Selected row has been updated.")
            else:
                st.warning(f"No data found for Row {row_id}.")

def delete_data(connection):
    st.header("Delete Data")
    st.write("Select the data you want to delete:")

    # Izvlačenje svih podataka iz tablice travel_details
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM travel_details")
    all_data = cursor.fetchall()


    # Odabir redaka za brisanje
    rows_to_delete = st.multiselect(
        "Select Rows to Delete",
        options=[f"Row {data[0]}" for data in all_data],
    )

    if st.button("Delete Selected Rows"):
        cursor = connection.cursor()
        for row in rows_to_delete:
            row_id = int(row.split()[1])
            cursor.execute("DELETE FROM travel_details WHERE Trip_ID=?", (row_id,))
        connection.commit()
        st.success("Selected rows have been deleted.")



users = fetch_users()
usernames = []

for user in users:
    usernames.append(user['username'])

credentials = {'usernames': {}}
for index in range(len(users)):
    credentials['usernames'][users[index]['username']] = {
        'name': users[index]['username'], 'password': users[index]['password']

    }

Authenticator = stauth.Authenticate(credentials, cookie_name='Streamlit', key='abcdef', cookie_expiry_days=4)

email, authentication_status, username = Authenticator.login(':green[Login]', 'main')

info, info1 = st.columns(2)

if not authentication_status:
    sign_up()

if username:
    if username in usernames:
        if authentication_status:
            if username == "admin1":
                Authenticator.logout('Log Out', 'main')
                st.header(f'Welcome!')
                
                display_data(connection)
                
                admin_options = ["Add Data", "Update Data", "Delete Data"]
                selected_admin_option = st.selectbox("Select an admin option:", admin_options)

                if selected_admin_option == "Add Data":
                    add_data(connection)

                if selected_admin_option == "Update Data":

                    # Izvlačenje svih podataka iz tablice travel_details
                    cursor = connection.cursor()
                    cursor.execute("SELECT * FROM travel_details")
                    all_data = cursor.fetchall()

                    update_data(connection, all_data)

                if selected_admin_option == "Delete Data":
                    delete_data(connection)



            elif username == "korisnik":
                st.header(f'Welcome!')

                #-------------GRAF-WEB------------
                #gornji dio weba
                st.title("✈ Data analysis of travel")
                st.markdown("##")

                #ukupan broj troskova smjestaja
                total_accommodation_cost_query = "SELECT SUM(Accommodation_cost) FROM travel_details"
                cursor.execute(total_accommodation_cost_query)
                total_accommodation_cost = cursor.fetchone()[0]
                
                #ukupan broj troskova puta
                total_transportation_cost_query = "SELECT SUM(Transportation_cost) FROM travel_details"
                cursor.execute(total_transportation_cost_query)
                total_transportation_cost = cursor.fetchone()[0]

                #ukupni broj putovanja
                total_number_of_trips_query = "SELECT COUNT(*) FROM travel_details"
                cursor.execute(total_number_of_trips_query)
                total_number_of_trips = cursor.fetchone()[0]


                left_column, middle_column, right_column = st.columns(3)
                with left_column:
                    st.subheader("Total number of trips")
                    st.subheader(f"{total_number_of_trips}")
                    
                with middle_column:
                    st.subheader("Total accommodation cost")
                    st.subheader(f"€ {total_accommodation_cost:,}")
                    
                    
                with right_column:
                    st.subheader("Total transportation cost")
                    st.subheader((f"€ {total_transportation_cost:,}"))



                # Odabir prikaza
                view_options = ["Traveler Data", "Accommodation Data", "Transportation Data"]  
                selected_view = st.selectbox("Select a view:", view_options)

                if selected_view == "Traveler Data":

                    #-----------SIDEBAR--------
                    Authenticator.logout(':red[Logout]', 'sidebar')
                    st.sidebar.header("AGE FILTER:")

                    #Dohvati age value 
                    unique_ages = df["Traveler_age"].unique()

                    #Range slider za odabir godina
                    age_range = st.sidebar.slider(
                        "Select age range:",
                        min_value=int(min(unique_ages)),
                        max_value=int(max(unique_ages)),
                        value=(int(min(unique_ages)), int(max(unique_ages))),
                        step=1
                    )

                    #Filtriraj odabrane godine
                    filtered_df = df[
                        (df["Traveler_age"] >= age_range[0]) &
                        (df["Traveler_age"] <= age_range[1])
                    ]


                    st.sidebar.header("GENDER FILTER:")
                    traveler_gender = st.sidebar.multiselect(
                        "Select the gender:",
                        options=df["Traveler_gender"].unique(),
                        default=df["Traveler_gender"].unique()
                    )

                    st.sidebar.header("DESTINATION CITY FILTER:")
                    #Checkbox za prikaz svih gradova
                    show_all_cities = st.sidebar.checkbox("Show All cities", value=True)
                    if show_all_cities:
                        selected_cities = df["Destination_city"].unique()
                    else:
                        selected_cities = st.sidebar.multiselect(
                            "Select cities:",
                            options=df["Destination_city"].unique()
                        )


                    st.sidebar.header("DESTINATION COUNTRY FILTER:")
                    #Checkbox za prikaz svih drzava
                    show_all_countries = st.sidebar.checkbox("Show All countries", value=True)
                    if show_all_countries:
                        selected_countries = df["Destination_country"].unique()
                    else:
                        selected_countries= st.sidebar.multiselect(
                            "Select countries:",
                            options=df["Destination_country"].unique()
                        )


                    df_traveler = df.query(
                        "Traveler_gender == @traveler_gender"
                    )


                    # Izračunavanje broja putnika po dobi
                    age_counts = filtered_df['Traveler_age'].value_counts()
                    gender_counts = df_traveler['Traveler_gender'].value_counts()
                    city_counts= df['City_of_residence'].value_counts()
                    country_counts = df_traveler['Traveler_nationality'].value_counts()
                    destination_country_counts = df_traveler['Destination_country'].value_counts()
                    destination_city_counts = df['Destination_city'].value_counts()
                    filtered_df_cities = df[df["Destination_city"].isin(selected_cities)]
                    filtered_df_countries = df[df["Destination_country"].isin(selected_countries)]

                    

                #GRAFIKONI ZA TRAVELER DATA
                    #Definiranje raspona dobne skupine i odgovarajuće boje
                    age_ranges = [(20, 30), (30, 40), (40, 50), (50, 60)]  
                    color_palette = ["blue", "green", "orange", "yellow"]  



                    #GRAFIKON ZA DOBNU SKUPINU
                    fig_age = px.bar(
                        age_counts,
                        x=age_counts.index,
                        y=age_counts.values,
                        title="<b>Number of Travelers by Traveler Age</b>",
                        labels={'x': 'Age', 'y': 'Count'},
                        color_discrete_sequence=color_palette,
                        template="plotly_white"
                    )

                    #Promjena naziva osi X i Y
                    fig_age.update_xaxes(title_text="Age") 
                    fig_age.update_yaxes(title_text="Count")  

                    #Podešavanje boja za svaku dobnu skupinu
                    for i, (start_age, end_age) in enumerate(age_ranges):
                        fig_age.add_vrect(
                            x0=start_age,
                            x1=end_age,
                            fillcolor=color_palette[i],
                            opacity=0.2,  #intenzitet boje
                            layer="below",
                            line_width=0,
                        )
                    

                    # GRAFIKON ZA SPOL
                    # Definirajte boje za svaki spol
                    gender_colors = {"Male": "blue", "Female": "pink"} 
                    

                    fig_gender = px.bar(
                        gender_counts,
                        x=gender_counts.index,
                        y=gender_counts.values,
                        title="<b>Number of Travelers by Gender</b>",
                        labels={'x': 'Gender', 'y': 'Count'},
                        color=gender_counts.index,
                        color_discrete_map=gender_colors,
                        template="plotly_white"
                    )

                
                    fig_gender.update_xaxes(title_text="Gender")  
                    fig_gender.update_yaxes(title_text="Count") 

                    # Prikazivanje grafa za AGE i GENDER
                    left_column, right_column = st.columns(2)
                    left_column.plotly_chart(fig_age, use_container_width=True)
                    right_column.plotly_chart(fig_gender, use_container_width=True)
                                

                    # Groupby po GODINAMA i SPOLU putnika te kreiranje grupiranog bar grafikona
                    grouped_df = filtered_df.groupby(['Traveler_age', 'Traveler_gender']).size().reset_index(name='count')

                    fig_age_gender = px.bar(
                        grouped_df, 
                        x='Traveler_age', 
                        y='count', 
                        color='Traveler_gender',
                        title='Age Distribution of Travelers by Gender',
                        labels={'Traveler_age': 'Godine', 'Traveler_gender': 'Spol', 'count': 'Broj putnika'},
                        width=800, height=500
                    )  

                

                    #PODACI ZA HISTOGRAM O MJESECIMA PUTOVANJA I DOBI PUTNIKA
                    df["Start_date"] = pd.to_datetime(df["Start_date"], format="%d-%b-%y")
                    df['Month'] = df['Start_date'].dt.strftime('%b')
                    

                # Definiranje redoslijeda meseci
                    Month_Order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                # Dodavanje nove kolone sa redoslijedom mjeseci
                    df['Month_Order'] = pd.Categorical(df['Month'], categories=Month_Order, ordered=True)
                    

                # Sortiranje DataFrame-a po redoslijedu mjeseci
                    df_sorted = df.sort_values(by='Month_Order')
            
                #HISTOGRAM ZA MJESECE PUTOVANJA I DOBNIH RASPONA KORISNIKA
                    df_sorted['AgeRange'] = pd.cut(df_sorted['Traveler_age'], bins=[18, 25, 35, 45, np.inf], labels=['18-25', '25-35', '35-45', '45+'])
                    fig_age_month = px.histogram(
                        df_sorted,
                        x='Month_Order',
                        color='AgeRange',  
                        title="<b>Age Distribution of Travelers by Month</b>",
                        labels={'x': 'Month', 'y': 'Count'},
                        template="plotly_white",
                        width=800, height=500
        )
                    
                    # Postavljanje redoslijeda mjeseci na osi X
                    fig_age_month.update_xaxes(categoryorder='array', categoryarray=Month_Order)

    
                    fig_age_month.update_xaxes(title_text="Months") 
                    fig_age_month.update_yaxes(title_text="Count")  


                    # Prikazivanje grafa za AGE-GENDER i AGE-MONTHS
                    left_column, right_column = st.columns(2)
                    left_column.plotly_chart(fig_age_gender, use_container_width=True)
                    right_column.plotly_chart(fig_age_month, use_container_width=True)


                #SORTIRANJE GRADOVA I DRZAVA
                    # Izdvajanje prvih 10 GRADOVA
                    sorted_city_counts = city_counts.sort_values(ascending=False)
                    top_10_cities = sorted_city_counts.head(10)
                    # Izdvajanje top 10 DRZAVA
                    sorted_country_counts = country_counts.sort_values(ascending=False)
                    top_10_countries = sorted_country_counts.head(10)



                    nationality_counts = df_traveler['Traveler_nationality'].value_counts()
                # Sortiranje nacionalnosti po broju pojavljivanja
                    sorted_nationalities = nationality_counts.sort_values(ascending=False)
                # Izdvajanje prvih 10 nacionalnosti
                    top_10_nationalities = sorted_nationalities.head(10)

                    #GRAFIKON ZA TOP 10 NACIONALNOSTI
                    fig_age_nat = px.scatter(
                        df_traveler[df_traveler['Traveler_nationality'].isin(top_10_nationalities.index) & (df["Traveler_age"] >= age_range[0]) & (df["Traveler_age"] <= age_range[1])],  
                        x='Traveler_age',
                        y='Traveler_nationality', 
                        color='Traveler_nationality',
                        symbol='Traveler_nationality', 
                        title="<b>Distribution of Traveler Age to Nationality</b>",
                        labels={'x': 'Age', 'y': 'Nationality'},
                        template="plotly_white"
                    )

        
                    fig_age_nat.update_xaxes(title_text="Age")  
                    fig_age_nat.update_yaxes(title_text="Nationality")  

                    # prikazivanje grafa AGE-NATIONALITY
                    st.plotly_chart(fig_age_nat, use_container_width=True)


            
                # Sortiranje destinacija po broju pojavljivanja
                    sorted_destinations = destination_country_counts.sort_values(ascending=False)
                # Izdvajanje prvih 10 destinacija
                    top_10_destinations = sorted_destinations.head(10)

                #GRAFIKON ZA TOP 10 DESTINACIJA
                    fig_age_des_country = px.scatter(
                        filtered_df_countries[filtered_df_countries['Destination_country'].isin(top_10_destinations.index) & (df["Traveler_age"] >= age_range[0]) & (df["Traveler_age"] <= age_range[1])],
                        x='Traveler_age',
                        y='Destination_country',  
                        color='Destination_country',
                        symbol='Destination_country',
                        title="<b>Distribution of Traveler Age to Destination Country</b>",
                        labels={'x': 'Destination country', 'y': 'Age'},
                        template="plotly_white"
                    )

            
                    fig_age_des_country.update_xaxes(title_text="Age")  
                    fig_age_des_country.update_yaxes(title_text="Destination country")  

                    #prikazivanje grafa AGE-DESTINATION CITY
                    st.plotly_chart(fig_age_des_country, use_container_width=True)




                    # Sortiranje destinacija po broju pojavljivanja
                    sorted_destinations = destination_city_counts.sort_values(ascending=False)
                # Izdvajanje prvih 10 destinacija
                    top_10_destinations = sorted_destinations.head(10)

                #GRAFIKON ZA TOP 10 DESTINACIJA
                    fig_age_des_city = px.scatter(
                        filtered_df_cities[filtered_df_cities['Destination_city'].isin(top_10_destinations.index) & (df["Traveler_age"] >= age_range[0]) & (df["Traveler_age"] <= age_range[1])],
                        x='Traveler_age',
                        y='Destination_city',  
                        color='Destination_city',
                        symbol='Destination_city',
                        title="<b>Distribution of Traveler Age to Destination City</b>",
                        labels={'x': 'Destination city', 'y': 'Age'},
                        template="plotly_white"
                    )

                 
                    fig_age_des_city.update_xaxes(title_text="Age")  
                    fig_age_des_city.update_yaxes(title_text="Destination city")  

                    #prikazivanje grafa AGE-DESTINATION CITY
                    st.plotly_chart(fig_age_des_city, use_container_width=True)




                #GRAFIKON ZA NACIONALNOSTI    
                    fig_nationality = px.bar(
                        country_counts,
                        x=country_counts.index,
                        y=country_counts.values,
                        title="Number of Travelers by Nationality",
                        labels={'x': 'Nationality', 'y': 'Count'},
                        template="plotly_white"
                    )

               
                    fig_nationality.update_xaxes(title_text="Nationality")  
                    fig_nationality.update_yaxes(title_text="Count") 
                    
                    
                    #prikazivanje grafa NATIONALITY
                    st.plotly_chart(fig_nationality, use_container_width=True)


                #FUNKCIJE ZA GRAF GRADOVI-DRZAVE
                    st.subheader("Select a nationality")
                    
                    # Odabir nacionalnosti
                    selected_nationality = st.selectbox("Select a Nationality", df['Traveler_nationality'].unique())

                    # Filtriranje podataka za izabranu nacionalnost
                    selected_nationality_data = df[df['Traveler_nationality'] == selected_nationality]

                    # Izračunavanje broja ponavljanja svakog grada
                    city_counts = selected_nationality_data['City_of_residence'].value_counts()

                    # Pretvorba podataka o broju ponavljanja u novi DataFrame
                    city_counts_df = pd.DataFrame({'City_of_residence': city_counts.index, 'Count': city_counts.values})

                    # Kreiranje grafikona za gradove prebivališta povezane s izabranom nacionalnošću
                    fig_residence_cities = px.bar(
                        city_counts_df,
                        x='City_of_residence',
                        y='Count',
                        title=f"Number of Travelers by Residence City for {selected_nationality}"
                    )
                
                    fig_residence_cities.update_xaxes(title_text="City of residence") 
            

                    #prikazivanje grafa CITY OF RESIDENCE-NATIONALITY
                    st.plotly_chart(fig_residence_cities, use_container_width=True)



                    #MAPA S POSJECENIM DRZAVAMA
                    fig_visited_countries_map = px.scatter_geo(
                        df_traveler,
                        locations="Destination_country", 
                        title="<b>Visited Countries</b>",
                        template="plotly",
                        locationmode="country names",  # Način lociranja (države prema imenima država)
                        color="Destination_country",
                        width=1200, height=700
                    )
                    

                    # PRIKAZ MAPE S POSJECENIM DRZAVAMA
                    st.plotly_chart(fig_visited_countries_map, use_container_width=False, width=1000)
                    



                #KREIRANJE GRAFIKONA ZA SMJESTAJ
                elif selected_view == "Accommodation Data":


                    #-----------SIDEBAR--------
            
                    Authenticator.logout(':red[Logout]', 'sidebar')
                    st.sidebar.header("ACCOMMODATION TYPE FILTER:")
                    accommodation_type = st.sidebar.multiselect(
                        "Select the accommodation:",
                        options=df["Accommodation_type"].unique(),
                        default=df["Accommodation_type"].unique()
                    )

                    st.sidebar.header("ACCOMMODATION PRICE FILTER:")
                  
                    unique_cost = df["Accommodation_cost"].unique()

                    # Range slider za odabir cijena
                    cost_range = st.sidebar.slider(
                        "Select cost range:",
                        min_value=int(min(unique_cost)),
                        max_value=int(max(unique_cost)),
                        value=(int(min(unique_cost)), int(max(unique_cost))),
                        step=1
                    )

                    # Filtriranje podataka ovisno o odabiru cijena
                    filtered_df = df[
                        (df["Accommodation_cost"] >= cost_range[0]) &
                        (df["Accommodation_cost"] <= cost_range[1])
                    ]

                    st.sidebar.header("DESTINATION COUNTRY FILTER:")

                    # Checkbox za prikaz drzava
                    show_all_countries = st.sidebar.checkbox("Show All Countries", value=True)
                    if show_all_countries:
                        selected_countries = df["Destination_country"].unique()
                    else:
                        selected_countries = st.sidebar.multiselect(
                            "Select Countries:",
                            options=df["Destination_country"].unique()
                        )

                    st.sidebar.header("DESTINATION CITY FILTER:")
                    # Checkbox za prikaz gradova
                    show_all_cities = st.sidebar.checkbox("Show All cities", value=True)
                    if show_all_cities:
                        selected_cities = df["Destination_city"].unique()
                    else:
                        selected_cities = st.sidebar.multiselect(
                            "Select cities:",
                            options=df["Destination_city"].unique()
                        )

                    df_accommodation = df.query(
                        "Accommodation_type == @accommodation_type"
                    )


                    #izracunavanje podaci
                    accommodation_type_counts = df_accommodation['Accommodation_type'].value_counts()
                    accommodation_cost_counts = filtered_df['Accommodation_cost'].value_counts().sort_values(ascending=False)
                    filtered_df = df[df["Destination_country"].isin(selected_countries)]
                    filtered_df_cities = df[df["Destination_city"].isin(selected_cities)]
                    filtered_df_countries = df[df["Destination_country"].isin(selected_countries)]


                    # Kreiranje grafikona za vrstu smjestaja
                    fig_accomodation_type = px.pie(
                        accommodation_type_counts,
                        names=accommodation_type_counts.index,
                        values=accommodation_type_counts.values,
                        title="<b>Ratio & number of Accomodation by Type</b>",
                        labels={'names': 'Accommodation Type', 'values': 'Count'},
                        template="plotly_white"
                    )

                    st.plotly_chart(fig_accomodation_type, use_container_width=True)

                

                    # Izračun najčešćih cijena smještaja i njihovih brojeva pojavljivanja (samo cijene koje se pojavljuju više od 1 puta)
                    most_common_prices = accommodation_cost_counts[accommodation_cost_counts > 1]  

                    # Filtriranje DataFrame-a na temelju najčešćih cijena
                    df_common_prices = filtered_df[filtered_df['Accommodation_cost'].isin(most_common_prices.index)]

                    # Sortiranje DataFrame-a prema iznosima cijena
                    df_common_prices = df_common_prices.sort_values(by='Accommodation_cost', ascending=True)      

                    # Izrada histograma za cijene smjestaja
                    fig_accomm_price = px.histogram(
                        df_common_prices, 
                        x='Accommodation_type', 
                        color='Accommodation_cost',
                        title='Accommodation price by accommodation type', labels={'Accommodation_cost': 'Price'}
                    )
                    

                    fig_accomm_price.update_xaxes(title_text="Accommodation type")  
                    st.plotly_chart(fig_accomm_price, use_container_width=True)


                    # Izrada Box plota za cijenu smjestaja

                    # Filtriranje DataFrame-a za minimalno trajanje putovanja od 7 dana
                    df_duration_filtered = df[df['Duration_days'] == 7]
                    fig_box_accomm = px.box(
                        df_duration_filtered, 
                        x='Accommodation_type', 
                        y='Accommodation_cost', 
                        title='Box Plot shown Accommodation Price range for each Accommodation Type (7 days stays only)', 
                        labels={'Accommodation_cost': 'Accommodation cost'}
                    )

                    fig_box_accomm.update_xaxes(title_text='Accommodation type')
                    fig_box_accomm.update_yaxes(title_text='Price')
                    st.plotly_chart(fig_box_accomm, use_container_width=True)




                #VREMENSKI GRAFIKON, CIJENE TIPOVA SMJESTAJA OVISNO O MJESECIMA

                # Konverzija Start_date u datetime format i izvlačenje mjeseca
                    df['Start_date'] = pd.to_datetime(df['Start_date'], format='%d-%b-%y')
                    df['Month'] = df['Start_date'].dt.month

                # Filtriranje podataka na osnovu odabira tipova smještaja
                    filtered_df = df[df["Accommodation_type"].isin(accommodation_type)]

                # Izvlačenje mjeseci iz filtriranog DataFrame-a
                    months = filtered_df['Month'].unique()

                # Izrada vremenskog niza grafikona s više linija
                    fig_price_by_months, ax = plt.subplots(figsize=(6, 3)) 
                    sns.lineplot(
                        x='Month', 
                        y='Accommodation_cost', 
                        hue='Accommodation_type', 
                        data=filtered_df, 
                        marker='o', 
                        ax=ax
                    )
                    plt.title('Accommodation Cost of each Accommodation Type depending on Month of the year', fontsize=12)
                    plt.xlabel('Month', fontsize=10)
                    plt.ylabel('Accommodation Cost', fontsize=10)

                    # Dodavanje odabranih država u naslov
                    if show_all_countries:
                        selected_countries_str = "All"
                    else:
                        selected_countries_str = ', '.join(selected_countries)
                    title_text = f'Selected Country: {selected_countries_str}'
                    title_color = 'blue'  
                    plt.suptitle(title_text, fontsize=10, y=1.05, color=title_color)

                    # Povećanje veličine fontova u legendi
                    plt.legend(title='Accommodation Type', fontsize=8)

                    # Povećanje debljine linije
                    for line in ax.lines:
                        line.set_linewidth(1.5)

                    # Pomicanje legende izvan grafa
                    plt.legend(title='Accommodation Type', fontsize=8, loc='upper left', bbox_to_anchor=(1, 1))

                    # Prikaz grafa
                    st.pyplot(fig_price_by_months)

                    # Izrada scatter plota
                    fig_scatter_accomm = px.scatter(
                        filtered_df_cities,
                        x='Destination_city',
                        y='Accommodation_cost',
                        color='Accommodation_type',
                        title='Accommodation Prices by Accommodation Type and Destination City',
                        labels={'Accommodation_cost': 'Accommodation cost', 'Destination_city': 'Destination city'},
                        width=800,
                        height=400
                    )

                    fig_scatter_accomm.update_xaxes(title_text='Destination city')
                    fig_scatter_accomm.update_yaxes(title_text='Accommodation cost')

                    # Prikaz scatter plota unutar širine kontejnera stranice
                    st.plotly_chart(fig_scatter_accomm, use_container_width=True)


                    



                #KREIRANJE GRAFIKONA ZA TRANSPORT
                elif selected_view == "Transportation Data":

                    #-----------SIDEBAR--------

                    Authenticator.logout(':red[Logout]', 'sidebar')
                    st.sidebar.header("TRANSPORTATION TYPE FILTER:")
                    transportation_type = st.sidebar.multiselect(
                        "Select the accommodation:",
                        options=df["Transportation_type"].unique(),
                        default=df["Transportation_type"].unique()
                    )

                    st.sidebar.header("TRANSPORTATION PRICE FILTER:")
                    
                    unique_cost = df["Transportation_cost"].unique()

                  
                    cost_range = st.sidebar.slider(
                        "Select cost range:",
                        min_value=int(min(unique_cost)),
                        max_value=int(max(unique_cost)),
                        value=(int(min(unique_cost)), int(max(unique_cost))),
                        step=1
                    )

                 
                    filtered_df = df[
                        (df["Transportation_cost"] >= cost_range[0]) &
                        (df["Transportation_cost"] <= cost_range[1])
                    ]



                    df_transportation = df.query(
                        "Transportation_type == @transportation_type"
                    )


                    # Izracunavanje podaci
                    transportation_type_counts = df_transportation['Transportation_type'].value_counts()
                    transportation_cost_counts = filtered_df['Transportation_cost'].value_counts()


                    # Kreiranje grafikona za vrstu smjestaja
                    fig_transport_type = px.pie(
                        transportation_type_counts,
                        names=transportation_type_counts.index,
                        values=transportation_type_counts.values,
                        title="<b>Ratio & number of Transportation by Type</b>",
                        labels={'names': 'Transportation Type', 'values': 'Count'},
                        template="plotly_white"
                    )

                    st.plotly_chart(fig_transport_type, use_container_width=True)

                    # Izračun najčešćih cijena smještaja i njihovih brojeva pojavljivanja (samo cijene koje se pojavljuju više od 1 puta)
                    most_common_prices = transportation_cost_counts[transportation_cost_counts > 1]  

                    # Filtriranje DataFrame-a na temelju najčešćih cijena
                    df_common_prices = filtered_df[filtered_df['Transportation_cost'].isin(most_common_prices.index)]

                    # Sortiranje DataFrame-a prema iznosima cijena
                    df_common_prices = df_common_prices.sort_values(by='Transportation_cost', ascending=True)      

                    # Izrada histograma za cijene smjestaja
                    fig_accomm_price = px.histogram(
                        df_common_prices, 
                        x='Transportation_type', 
                        color='Transportation_cost',
                        title='Transportation price by Transportation type', labels={'Transportation_cost': 'Price'}
                    )

                    fig_accomm_price.update_xaxes(title_text="Transportation type")  
                    st.plotly_chart(fig_accomm_price, use_container_width=True)


                    fig_box_accomm = px.box(
                        df, 
                        x='Transportation_type', 
                        y='Transportation_cost', 
                        title='Box Plot shown Transportation Price range for each Transportation Type', 
                        labels={'Transportation_cost': 'Transportation cost'}
                    )

                    fig_box_accomm.update_xaxes(title_text='Transportation type')
                    fig_box_accomm.update_yaxes(title_text='Price')
                    st.plotly_chart(fig_box_accomm, use_container_width=True)





        else:
            password = info.text_input("Password", type="password")
            if info.button("Log In"):
                if login_user(username, password):
                    Authenticator.login_successful(username)
                    st.experimental_rerun()
                else:
                    st.warning("Invalid credentials")
    else:
        with info:
            st.warning('Username does not exist, Please Sign up')




if __name__ == "__main__":
    conn = sqlite3.connect('database.db')
    conn.close()
