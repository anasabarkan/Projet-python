import streamlit as st
import pandas as pd
from io import StringIO
import csv
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import numpy as np
from urllib.parse import urlparse
import ssl
import io


# Fonction pour lire les données en fonction du type de fichier
def read_file(file_type, file_content, separator):
    if file_type == "CSV" :
        df = pd.read_csv(file_content, sep=separator)
    
    elif file_type == "Excel":
        df = pd.read_excel(file_content)
    elif file_type == "Link":
        response = requests.get(file_content)
        df = pd.read_csv(io.StringIO(response.text), sep=separator)
    elif uploaded_file.name.lower().endswith('.txt'):
        df = pd.read_fwf(uploaded_file, header=None)

    else:
        df = pd.DataFrame()
    return df  
def calculate_statistics(df, selected_columns, operation_type):
    non_numeric_columns = df[selected_columns].select_dtypes(exclude=['number']).columns
    if len(non_numeric_columns) > 0:
        st.error(f"Calculs non pris en charge pour les colonnes non numériques : {non_numeric_columns.tolist()}. Veuillez choisir des colonnes numériques.")
        return

    if operation_type == "Moyenne":
        result = df[selected_columns].mean()
    elif operation_type == "Mode":
        result = df[selected_columns].mode().iloc[0]  # Mode can have multiple values, we take the first one
    elif operation_type == "Mediane":
        result = df[selected_columns].median()
    elif operation_type == "Variance":
        result = df[selected_columns].var()
    elif operation_type == "Ecart type":
        result = df[selected_columns].std()
    elif operation_type == "Min":
        result = df[selected_columns].min()
    elif operation_type == "Max":
        result = df[selected_columns].max()
    elif operation_type == "Etendu":
        result = df[selected_columns].max() - df[selected_columns].min()
    st.write(result.astype(str))


# Fonction pour afficher le type de visualisation choisi
def show_visualization(df, visualization_type):
    if visualization_type == "Histogramme":
        st.subheader("Histogramme")
        selected_column = st.selectbox("Sélectionnez la colonne pour l'histogramme", df.columns)
        if pd.api.types.is_numeric_dtype(df[selected_column]):
            fig, ax = plt.subplots()
            ax.hist(df[selected_column].dropna(), bins=20, density=True, alpha=0.9)
            df[selected_column].plot(kind='kde', ax=ax, secondary_y=True)
            st.pyplot(fig)
        else:
            st.error("Erreur : La colonne sélectionnée n'est pas numérique.")
        
    elif visualization_type == "Pie Plot":
        st.subheader("Pie Plot")
        selected_column_pie = st.selectbox("Sélectionnez la colonne pour le Pie Plot", df.columns)
        if pd.api.types.is_numeric_dtype(df[selected_column_pie]):
            st.error("Erreur : La colonne sélectionnée doit être catégorique pour le Pie Plot.")
        else:
            pie_data = df[selected_column_pie].value_counts()
            fig_pie, ax_pie = plt.subplots()
            ax_pie.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=90)
            ax_pie.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            st.pyplot(fig_pie)


    elif visualization_type == "Scatter Plot":
        st.subheader("Scatter Plot")
        x_axis = st.selectbox("Sélectionnez la colonne pour l'axe X", df.columns)
        y_axis = st.selectbox("Sélectionnez la colonne pour l'axe Y", df.columns)

        # Créer le nuage de points sans régression linéaire
        fig_no_trendline = px.scatter(df, x=x_axis, y=y_axis, title="Scatter Plot (Sans régression linéaire)")
        st.plotly_chart(fig_no_trendline)

        # Vérifier si la colonne des x et y sont de type numérique avant de créer la régression linéaire
        if not pd.api.types.is_numeric_dtype(df[x_axis]):
            st.error(f"La colonne pour l'axe X '{x_axis}' ne contient pas de données numériques. Veuillez sélectionner une colonne numérique.")
        elif not pd.api.types.is_numeric_dtype(df[y_axis]):
            st.error(f"La colonne pour l'axe Y '{y_axis}' ne contient pas de données numériques. Veuillez sélectionner une colonne numérique.")
        else:
            # Créer le nuage de points avec une régression linéaire
            fig_with_trendline = px.scatter(df, x=x_axis, y=y_axis, title="Scatter Plot (Avec régression linéaire)", trendline="ols")
            st.plotly_chart(fig_with_trendline)



    elif visualization_type == "Box Plot":
        st.subheader("Box Plot")
        selected_column = st.selectbox("Sélectionnez la colonne pour Box Plot", df.columns)
        if pd.api.types.is_numeric_dtype(df[selected_column]):
            fig = px.box(df, y=selected_column)
            st.plotly_chart(fig)
        else:
            st.error("Erreur : La colonne sélectionnée n'est pas numérique.")

    elif visualization_type == "Line Plot":
        st.subheader("Line Plot")
        x_column_line = st.selectbox("Sélectionnez la colonne pour l'axe X", df.columns)
        y_column_line = st.selectbox("Sélectionnez la colonne pour l'axe Y", df.columns)

        if pd.api.types.is_numeric_dtype(df[x_column_line]) and pd.api.types.is_numeric_dtype(df[y_column_line]):
            fig = px.line(df, x=x_column_line, y=y_column_line, title="Line Plot")
            st.plotly_chart(fig)
        else:
            st.error("Erreur : Les colonnes sélectionnées ne sont pas numériques.")
    
    elif visualization_type == "KDE Plot":
        st.subheader("KDE Plot")
        selected_column = st.selectbox("Sélectionnez la colonne pour le KDE plot", df.columns)
        if pd.api.types.is_numeric_dtype(df[selected_column]):
            fig, ax = plt.subplots()
            sns.kdeplot(df[selected_column])
            st.plotly_chart(fig)
        else:
            st.error("Erreur : La colonne sélectionnée n'est pas numérique.")
            
    elif visualization_type == "Violin Plot":
        st.subheader("Violin Plot")
        x_column = st.selectbox("Sélectionnez la colonne pour l'axe X", df.columns)
        y_column = st.selectbox("Sélectionnez la colonne pour l'axe Y", df.columns)

        if pd.api.types.is_numeric_dtype(df[x_column]) and pd.api.types.is_numeric_dtype(df[y_column]):
            
            fig = px.violin(df, x=x_column, y=y_column, box=True, points="all", title="Violin Plot")
            st.plotly_chart(fig)
        else:
            st.error("Erreur : Les colonnes sélectionnées ne sont pas numériques.")
            
    elif visualization_type == "Bar Plot":
        st.subheader("Bar Plot")
        x_column = st.selectbox("Sélectionnez la colonne pour l'axe X", df.columns)
        y_column = st.selectbox("Sélectionnez la colonne pour l'axe Y", df.columns)

        if not pd.api.types.is_numeric_dtype(df[x_column]):
            st.error(f"La colonne pour l'axe X '{x_column}' ne contient pas de données numériques. Veuillez sélectionner une colonne numérique.")
        elif not pd.api.types.is_numeric_dtype(df[y_column]):
            st.error(f"La colonne pour l'axe Y '{y_column}' ne contient pas de données numériques. Veuillez sélectionner une colonne numérique.")
        else:
            fig = px.bar(df, x=x_column, y=y_column, title="Bar Plot")
            st.plotly_chart(fig)

    
    elif visualization_type == "Heatmap":
        st.subheader("Heatmap")

    # Exclure les colonnes non numériques
        numeric_df = df.select_dtypes(include='number')

        if not numeric_df.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', fmt='.2f', ax=ax)
            st.pyplot(fig)
        else:
            st.write("Aucune colonne numérique disponible pour créer la heatmap.")



# Titre de l'application
st.title("Traitement de données")

# Sélection du type de fichier
file_type = st.radio("Sélectionnez le type de fichier", ("CSV", "Excel", "TXT", "Link"))

# Affichage des données
df = None  # Initialisation de df en dehors des blocs conditionnels

def get_file_extension(file):
    return file.split(".")[-1]

# Affichage des données
if file_type == "CSV" :
    uploaded_file = st.file_uploader(f"Télécharger un fichier {file_type}", type=[file_type.lower()])
    if uploaded_file is not None:
        separator = st.text_input("Entrez le séparateur", value=",")
        df = read_file(file_type, uploaded_file, separator)
        st.write("Données du fichier :")
        st.write(df)
        
elif file_type == "Excel":
    uploaded_file = st.file_uploader("Télécharger un fichier Excel", type=["xls", "xlsx"])
    if uploaded_file is not None:
        st.write("File uploaded successfully!")
        if uploaded_file.name.endswith(('.xls', '.xlsx')):
            available_sheets = pd.ExcelFile(uploaded_file).sheet_names
            sheet_name = st.selectbox("Choose a sheet", available_sheets, index=0, key="sheet_selector")
            st.write(f"Sheet: {sheet_name}")
            df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
            st.write("Data from selected sheet:")
            st.write(df)
        else:
            st.write("Invalid file format. Please upload an Excel file.")

elif file_type == "Link":
    link = st.text_input("Entrez le lien du fichier")
    if link:
        separator = st.text_input("Entrez le séparateur (optionnel)", value=",")
        df = read_file(file_type, link, separator)
        st.write("Données du fichier à partir du lien :")
        st.write(df)

#reccuperer l'extention du fichier
elif file_type == "TXT":
    uploaded_file = st.file_uploader(f"Télécharger un fichier {file_type}", type=[file_type.lower()])
    if uploaded_file is not None:
        separator = st.text_input("Entrez le séparateur (optionnel)", value=",")
        try:
            if file_type == "TXT":
                if separator:
                    df = pd.read_csv(uploaded_file, sep=separator)
                else:
                    df = pd.read_csv(uploaded_file)
                st.write("Données du fichier :")
                st.write(df)
        # Ajouter des conditions pour d'autres types de fichiers si nécessaire
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier : {e}")
    else:
        st.info("Veuillez télécharger un fichier.")


# Boutons pour extraire des colonnes, des lignes ou des valeurs
if df is not None:  # Check if df is defined
    
    if st.checkbox("Afficher les options d'extraction"):
        option = st.selectbox("Sélectionnez une option", ("Colonne", "Ligne", "Valeur"))
        if option == "Colonne":
            selected_column = st.selectbox("Sélectionnez une colonne", df.columns)
            st.write("Colonne Extraite : ", df[selected_column])
        elif option == "Ligne":
            selected_index = st.selectbox("Sélectionnez une ligne", df.index)
            st.write("Ligne Extraite : ", df.loc[selected_index])
        elif option == "Valeur":
            selected_column = st.selectbox("Sélectionnez une colonne pour les valeurs", df.columns)
            selected_value = st.selectbox("Sélectionnez une valeur", df[selected_column].unique())
            st.write("Lignes avec la valeur sélectionnée : ", df[df[selected_column] == selected_value])


# Affichage des données
if df is not None:

    # Streamlit UI for statistics
    st.title("Calcul des statistiques")
    selected_columns = st.multiselect("Sélectionnez les colonnes", df.columns)

    # Check if at least one column is selected
    if selected_columns:
        #selection du type d'opération à effectuer
        operation_type = st.selectbox("Sélectionnez le type d'opération", ("Moyenne","Mode","Mediane","Variance","Ecart type","Min","Max","Etendu"))
        # affichage des opérations sélectionnées
        calculate_statistics(df, selected_columns, operation_type)
    else:
        st.warning("Sélectionnez au moins une colonne pour effectuer les calculs.")

    # Streamlit UI for visualizations
    st.title("Visualisations")
    # Sélection du type de visualisation
    visualization_type = st.selectbox("Sélectionnez le type de visualisation", (" ","Histogramme", "Pie Plot", "Scatter Plot", "Box Plot", "Line Plot", "KDE Plot", "Violin Plot", "Bar Plot","Heatmap"))

    # Check if at least one visualization type is selected
    if visualization_type != " ":
        # Affichage de la visualisation sélectionnée
        show_visualization(df, visualization_type)
    else:
        st.warning("Sélectionnez au moins un type de visualisation.")