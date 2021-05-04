# MongoDB_ProjectExchange
Ho voluto creare un sito nel quale è possibile comprare e vendere bitcoin. Il sito è sviluppato con Djongo ovvero Django + MongoDB. L'utilizzo di un database non relazionale permette di aumentare l'efficienza del sito. 

All'interno del sito l'utente potrà:

- Registrarsi e loggarsi;
- Al momento della registrazione verranno assegnati all'utente da 1 a 10 bitcoin in modo randomico;
- Creare più ordini di acquisto o vendita simultaneamente;
- Se, nel momento in cui l'utente crea un ordine di acquisto specificando prezzo e quantità, è già presente un ordine di vendita con quelle caratteristiche, l'ordine viene registrato e vengono aggiornati i bilanci dei due utenti coinvolti nella transazione. Se non esiste un ordine di questo tipo, procede a creare un matching tra gli ordini valutando il rapporto prezzo quantità che deve essere in linea con la richiesta fatta dall'utente. Nel caso in cui la richiesta dell'utente non venga completamente evasa, con la rimanenza viene generato un nuovo ordine di acquisto. 
- Vedere tutti gli ordini che sono attivi in quel preciso momento
- Vedere i profitti o le perdite di tutti gli utenti
