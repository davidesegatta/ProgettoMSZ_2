# Qui vengono importate le dipendenze necessarie per il progetto
from flask import Flask, jsonify, request
from flask_cors import CORS
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
import requests
import pandas as pd
import numpy as np
import random
import json


# Istanzia l'app
app = Flask(__name__)
app.config.from_object(__name__)

# Abilitazione CORS, impedisce che le richieste di risorse da un dominio diverso da quello dell'applicazione web vengano eseguite automaticamente.
CORS(app)

# Inizializzazione variabili globali
trained = False
vectorz = CountVectorizer()
clf = RandomForestClassifier()

# Viene eseguita quando il client fa una richiesta POST (quando invia il link)
@app.route('/process_url', methods=['POST'])
def process_url():

    # Dichiarazione variabili globali
    global trained, vectorz, clf
    
    # Prende il link che ho passato dal client
    data = request.json
    url = data.get('url')
    
    # Richiama la funzione per prendere i commenti
    comments = Scraper(url)

    # Controlla che il modello non sia già stato addestrato
    if(not trained):
        # Addestra il modello
        Training()
        trained = True
    
    # Vettorizza la lista dei commenti
    newvects = vectorz.transform(comments)
    # Predice i risultati dei commenti basandosi sul modello 
    model = clf.predict(newvects)

    # Converte la lista ndarray creata in una stringa per poi convertirla in una lista
    model_serializable_str = json.dumps(model, default=convert_to_json_serializable)
    model_serializable_list = json.loads(model_serializable_str)

    # Sostituisce nella lista i valori di 0 e 1 con "no hate" e "hate"
    for i, value in enumerate(model_serializable_list):
        if value == 0: model_serializable_list[i] = "No hate"
        if value == 1: model_serializable_list[i] = "Hate"
                   
    return jsonify({'comments': comments, 'model': model_serializable_list})


# Funzione per fare lo scraping del testo dall'html di 4chan
def Scraper(url):   
    # Richiesta all'URL
    source = requests.get(url).text
    soup = BeautifulSoup(source, "html.parser")
    comments = []
    
    # Prende ogni commento
    for tag in soup.find_all('blockquote', class_='postMessage'):
      # Elimina il codice di riferimento al commento a cui stanno rispondendo gli utenti
      for a_tag in tag.find_all('a', class_='quotelink'):
            a_tag.decompose()
      # Elimina gli spazi che dividerebbero le parole
      for wbr_tag in tag.find_all('wbr'):
            wbr_tag.decompose()
      # Prende la citazione di un altro commento e la mette come testo del commento
      for span_tag in tag.find_all('span', class_='quote'):
            span_text = span_tag.get_text()
            span_tag.replace_with(span_text)
      # Sostituisce i <br> con uno spazio 
      comment_text = ''.join([str(content) if content.name != 'br' else '' for content in tag.contents]) # "br" è l'elemento che manda a capo
      # Controlla che non ci siano spazi prima o dopo del elemento del vettore e se è vuoto non lo aggiunge alla lista
      if comment_text.strip():
        comments.append(comment_text)
              
    return comments

    
# Addestramento del modello 
def Training():    
    # Carica il file CSV utilizzando pandas e memorizza i dati in un DataFrame
    df = pd.read_csv('Ridotto_Final_data_Y_D.csv')
    # Estrae la colonna 'Content' dal DataFrame e crea una lista
    corpus = [i for i in df.Content]
    # Rimescola casualmente l'ordine degli elementi nella lista 
    random.shuffle(corpus)
    # Utilizza l'istanza del CountVectorizer per trasformare la lista di testi in una rappresentazione numerica. 
    # Questa rappresentazione conta le occorrenze delle parole nei documenti e crea una matrice sparsa, dove ogni riga rappresenta un documento e ogni colonna rappresenta una parola.
    m = vectorz.fit_transform(corpus)
    # Estrae la colonna 'Label' dal DataFrame e crea una lista y contenente le etichette associate ai documenti.
    # Queste etichette sono i target che il modello di machine learning cercherà di predire.
    y = [i for i in df['Label']]
    # Addestra il classificatore (clf), che è un modello di RandomForestClassifier, utilizzando la matrice m come dati di input e la lista y come target di addestramento. 
    # In altre parole, il modello viene addestrato a predire le etichette (y) basandosi sui dati rappresentati dalla matrice sparsa (m).
    clf.fit(m, y)
    
    return

# Converti l'ndarray in una stringa 
def convert_to_json_serializable(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()  
    raise TypeError(f"Type {type(obj)} not serializable")


if __name__ == '__main__':
    app.run()