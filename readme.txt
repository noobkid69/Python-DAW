Installation
  Kör pip install -r requirements.txt i projekt mappen för att installera alla (hoppas det är alla) libraries.

I global_stuff.py finns en variabel som heter BLOCKSIZE. Om man kör programmet på sin samsung smart fridge eller liknande kanske man behöver öka den.

Saker att tänka på:
  Ändra INTE bpm medan klippet spelas. 
  Gör inte heller något som fryser GUI-N (exempelvis importera en ny mapp i trädet) för vid båda dessa fall hamnar gui och ljud ur synk. Det beror på att ljudet är i sitt seperata thread och uppdaterar medan gui:t är fryst.


Kommandon
  Meny
    Hann inte med så alla knappar är visuella, förutom "stäng" knappen. 
  Träd
    Klicka mapp-knappen för att välja mapp. Klicka checkrutan för att ta bort/visa otillåtna filer. (mp3 och wav tillåts)
    Klicka och dra i ljudklipp till spellistan för att skapa ljudklipp.
    Om kanten på ljudklippet hamnar utanför spellistan måste man ta bort det eftersom det ej går att flytta då.
  Spellistan
    Ctrl+Scrollwheel: Zoom in/out
    Klicka + Dra ljudklipp för att flytta
    Dubbelklicka ljudklipp för att få upp meny med volym/pan/reverse knapp
    Vänsterklicka för att ta bort ljudklip
    Det går även att dubbelklicka på texten till vänster om varje rad för att ändra den.
  Top bar 
    Mixer knappen visar mixern.
    Snap-knappen visar hur precis avrundingen av klippens position. Lägsta är 1 takt. Högsta är 1/16 takt. 
    Bpm-ändring (dra eller dubbeklicka för att skriva) - maxbpm är 200 och minbpm är 40
    Spela-knapp. Tar ett litet tag att starta streamen.
    Penna - välja och rita ut grupperade klipp. Grupperade klipp delar allt förutom panning och individuell volym. (De delar mixerkanal, gemensam volymknapp och reverse)
    Hink - Välj färgen på den grupp du vill konvertera till och klicka på klipp för att byta dess grupp. Välj None eller klicka på penna för att avvälja hinken. 
    Notera att bågen för volymen inte hänger med uppdatteringar i grupperingen, men värdet är alltid synkroniserat.
    Slicer - klicka på ett klipp för att klippa av allt till höger (funkar endast på rektangeln eftersom texten kan vara till vänster om början på klippet.)
  Mixer
    Volym slider (ändrar volym duh)
    Klicka på en kanal för att ta upp effekt-lista.
    Distortion - man kanske behöver lägga till flera för att få ett riktigt distorted ljud.
  Sequencer
    Det var precis att jag inte hann med denna. Allt visuellt gjordes typ men hann inte med att göra ljud-delen. Jag tänkte göra AudioClip klassen till en mer abstakt Audio klass och ta bort allt som har med de fysiska klippen att göra. 
        Sedan tänkte jag göra en ny klass AudioClip(Audio) med super().__init__(file, ...)

