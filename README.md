# Who'll Be Lunch

Who’ll Be Lunch is een educatieve webapplicatie met een knipoog. Wanneer je de applicatie opent, zie je een interface die lijkt op een bekende bezorgdienst met gerechten. Al snel wordt duidelijk dat je niet bent ingelogd als een mens, maar als een dier. De gerechten die je ziet zijn geen maaltijden voor mensen, maar datgene wat het gekozen dier in de natuur zou eten.

Eten bezorgen, maar dan voor dieren. De applicatie gebruikt de herkenbare structuur van een eten-bestelwebsite, zonder dat je daadwerkelijk iets bestelt. In plaats daarvan kies je een gerecht en krijg je uitleg over wat een dier eet, waarom het dit eet en hoe dit past binnen zijn dieet. Zo zou een leeuw een zebra “bestellen”, een walvis plankton, een giraffe bladeren en een wrattenzwijn zowel planten als kleine dieren.

De applicatie is opgezet als een educatief project, waarbij op een speelse manier kennis wordt overgebracht over voedselketens, diëten en ecosystemen. Naast carnivoren en herbivoren komen ook minder bekende voedingsstrategieën aan bod, zoals omnivoren en zelfs chemoautotrofe organismen. Bij zowel dieren als gerechten worden extra feitjes en beschrijvingen getoond om de leerwaarde te vergroten.

Bij het openen van de applicatie is de gebruiker automatisch gekoppeld aan een willekeurig dier. Via het profiel-icoon kan eenvoudig een ander dier worden gekozen. Zodra dit gebeurt, past het menu zich direct aan en verschijnen de bijbehorende gerechten. Door op een gerecht te klikken, krijgt de gebruiker meer informatie over dit voedsel en de relatie met het gekozen dier.

Daarnaast bevat de applicatie een Food Web-weergave, waarin visueel wordt weergegeven hoe dieren en hun voedsel met elkaar verbonden zijn. Dit laat zien dat voedselketens geen simpele lijnen zijn, maar onderdeel van een groter en complexer ecosysteem.

Gebruikers kunnen ook nieuwe dieren en gerechten inzenden via een formulier. Deze inzendingen worden niet direct zichtbaar, maar eerst gecontroleerd in een admin panel. In dit admin panel kan een beheerder nieuwe content goedkeuren, bewerken of verwijderen, zodat de kwaliteit en juistheid van de informatie gewaarborgd blijft.

Technisch gezien is Who’ll Be Lunch een Python-applicatie met een webinterface, gebouwd met Flask. De applicatie combineert educatie, interactie en een herkenbaar design om op een laagdrempelige manier inzicht te geven in hoe dieren eten en hoe ecosystemen in elkaar zitten.


# Hoe werkt het? In stappen:

    1. Startpagina
    
    De gebruiker opent de website en komt terecht op de startpagina van Who’ll Be Lunch? De website is vormgegeven als een bezorgdienst, maar in plaats van mensen staan dieren centraal. Met de knop “Check het nu!” ga je verder naar de applicatie.


    2. Menu
    
    De gebruiker is automatisch “ingelogd” als een willekeurig dier. Bovenaan zie je welk dier actief is en wat voor dieet het heeft (bijv. carnivoor, herbivoor, omnivoor, chemoautotroof). Links onderin staat een kaart met het geseleteerde dier, vanuit hier kun je ook naar de Food Web.


    3. Dier selecteren 
    
    Rechtsboven kan de gebruiker een ander dier kiezen of een random dier oproepen via het profiel-icoon. Er is een zoekfunctie én een optie om een willekeurig dier te selecteren. 
    Zodra een ander dier wordt gekozen, verandert het menu direct.


    4. Menu bekijken (gerechten) 
    
    In het midden van de pagina zie je de “gerechten” die bij het dier horen. Gerechten zijn bijvoorbeeld andere dieren, planten of organismen.
    Elk gerecht heeft een label (zoals Vlees, Fruit, Symbiotisch).


    5. Detailpagina van een gerecht
    
    Door op een gerecht te klikken, ga je naar een detailpagina. Hier zie je: Een afbeelding, een korte uitleg Wat het gerecht is en waarom het gegeten wordt als dit is ingevult


    6. Food Web (voedselketen) 
    
    In de Food Web-weergave zie je visueel: Welk dier wat eet, waar het voedsel zelf weer vandaan komt, de verbindingen laten de ecologische relaties zien.
    Je kunt inzoomen, uitzoomen en de voedsel keten doorgaan om te zien waar de voedsel keten eindigd.


    7. Nieuw dier of gerecht inzenden
    
    Via de plusknop kan een gebruiker een nieuw dier of gerecht voorstellen. De gebruiker vult in: Naam, beschrijving, dieet, bijbehorende gerechten en optioneel een nieuw gerecht met de invul velden: naam gerecht, type, beschrijving. De inzending wordt niet direct zichtbaar, maar eerst gecontroleerd in het admin panel. De admin panel staat in de submit form maar in een eind product zou dit beveiligd moeten zijn.


    8. Admin panel

    In het admin panel kan een beheerder: Nieuwe dieren goedkeuren of afkeuren, nieuwe gerechten goedkeuren of afkeuren bestaande dieren en gerechten bewerken of verwijderen.
    Alleen goedgekeurde content verschijnt in de app.


# Technische opzet

Frontend
De frontend bestaat uit HTML-templates (Jinja2) en CSS voor de visuele presentatie. De interface is opgebouwd als een herkenbare bezorgdienst, met kaarten voor dieren en gerechten. Daarnaast wordt JavaScript gebruikt voor interactieve onderdelen zoals het Food Web, zoom-functionaliteit en dynamische updates van de weergave.

Backend
De backend is geschreven in Python met het Flask-framework. Deze laag verzorgt de applicatielogica, route-afhandeling en validatie van gebruikersinvoer. De backend bepaalt op basis van het geselecteerde dier welke gerechten, informatie en visualisaties worden getoond.

Data-opslag
Alle data wordt opgeslagen in JSON-bestanden. Dit omvat dieren, gerechten, diëten en relaties tussen dieren en voedsel. Er is onderscheid tussen goedgekeurde data en ingezonden (pending) data, zodat nieuwe inzendingen eerst gecontroleerd kunnen worden via het admin panel.

Architectuur & services
De applicatie is modulair opgezet. Logica voor dieren, gerechten en afbeeldingen is ondergebracht in aparte services, waardoor de code overzichtelijk blijft en eenvoudig uitbreidbaar is. Deze opzet maakt het mogelijk om later nieuwe dieetvormen, organismen of visualisaties toe te voegen zonder grote aanpassingen aan de kern van de applicatie.

Beheer & beveiliging
De applicatie bevat een admin panel voor het beheren van dieren en gerechten. Om misbruik te voorkomen is er input-validatie, normalisatie van namen en rate limiting toegepast op inzend-routes. Hierdoor fungeert de frontend als eerste filter, terwijl de backend de definitieve controle uitvoert.