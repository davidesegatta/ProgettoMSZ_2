<template>
  <div id="app">
    
<!-- Titolo con logo -->
    <!-- "class" serve per lo style CSS, può essere pre-impostata da bootstrap/vue o personalizzata da noi nello style -->
    <header class="header-container"> 
      <img src="../assets/4chan-logo.png" alt="Logo">
      <h1>4chan hate speech detector</h1>
    </header>

<!-- Input di testo -->
    <div class="input-group mb-3 col-sm-6 margins" style="width: 94%;"> 
      <!-- " @keydown.enter.prevent="handleEnterKey" " permette l'utilizzo di "enter" per fare submit-->
      <input type="text" class="form-control" placeholder="Insert here a 4Chan link" v-model="url" @keydown.enter.prevent="handleEnterKey"> 
      <!-- ":disabled="!isValidLink"" disabilitato quando il link non è valido, abilitato quando lo è-->
      <button class="btn btn-outline-primary" type="button" id="button-addon2" @click="processURL" :disabled="!isValidLink"> 
        <!-- "v-if=loading"" serve per vedere se "loading" è true o false, nel primo caso ti da "Loading..." nel secondo "Submit" -->
        <span v-if="loading" class="spinner-border spinner-border-sm"></span>
        <span v-if="loading" role="status">Loading...</span> 
        <span v-else>Submit</span>
      </button>
    </div>
    
<!-- Tabella risultati -->
    <div class="table-responsive margins">
      <table class="table align-middle">
        <thead>
          <tr>
            <!-- "v-if="comments.length"" serve per vedere se la lista esiste, esisterà solo dopo aver inviato il link ed addestrato il modello -->
            <th v-if="comments.length">Comments</th> 
            <th v-if="model.length">Sentiment</th>
          </tr>
        </thead>
        <tbody>
          <!-- cicla la lista dei commenti e stampa l'elemento dell'indice -->
          <tr class="col with-border text-justify" v-if="comments.length || model.length" v-for="(comment, index) in comments" :key="index"> 
            <td>{{ comment }}</td> <!-- esegue un ciclo per stampare come tabella ogni commento -->

            <!-- "color red" e "color green" sono style che colorano rispettivamente "HATE" e "NO HATE" -->
            <td class="col with-border text-center" :class="{ 'color-red': model[index] === 'Hate', 'color-green': model[index] === 'No hate' }" v-if="model[index]">
            {{ model[index] }}</td> 
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>


<script>
import axios from 'axios';

export default {
  // Inizializzazione delle variabili
  data() {
    return {
      url: '',
      comments: [],
      model: [],
      loading: false,
    };
  },
  // Definizione delle proprietà calcolate
  computed: {
    isValidLink() {
      // Controlla se l'url inizia con 'https://boards.4chan.org/'
      return this.url.startsWith('https://boards.4chan.org/');
    },
  },
  methods: {
    // Controllo che impedisce di usare il tasto "Enter" se il link non è valido
    handleEnterKey() {
      if (this.isValidLink) {
        this.processURL();
      }
    },
    // Fa una chiamata asincrona per inviare il link al server e recuperare i dati dei commenti ed il loro stato
    async processURL() {
      try {
        this.loading = true;  // Imposta lo stato "loading" a true prima della richiesta
        // Invio del link
        const response = await fetch('http://localhost:5001/process_url', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ url: this.url }),
        });
        // Recupero dati
        const data = await response.json();
        this.comments = data.comments;
        this.model = data.model;
      } catch (error) {
        console.error('Error:', error);
      } finally {
        this.loading = false;  // Imposta lo stato "loading" a false dopo la risposta o in caso di errore
      }
    },
  },
};
</script>

<!-- Stili personalizzati -->
<style>

  .with-border{
     border: 1px solid #ddd; 
     padding: 10px;
  }
  
  .margins{
     margin-left: 3%;
     margin-right: 3%;
  }

  .color-red {
    color: red;
}

  .color-green {
    color: green;
}

  .header-container {
    display: flex;
    align-items: center;
    margin-bottom: 5%;
    margin-top: 3%;
    margin-left: 30%;
  }

  .header-container img {
    margin-right: 2%;
}
</style>