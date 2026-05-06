# Speaker Notes

## Folie 1: Titel

Sprecher A:

> Heute geht es um API Schema Design und REST. Wir schauen uns an, wie man APIs nicht nur implementiert, sondern als Vertrag zwischen Backend und Frontend gestaltet.

Sprecher B:

> Danach wechseln wir auf die Client-Seite und vergleichen `fetch` und `axios`. Unser VNB Atlas Projekt nutzen wir als Beispiel, aber die Konzepte gelten allgemein.

## Folie 2: Warum über API-Schema-Design sprechen?

Sprecher A:

> Eine API ist nicht nur eine Sammlung von URLs. Sie definiert, welche Daten ein System anbietet, welche Eingaben erlaubt sind und wie Fehler aussehen. Wenn dieser Vertrag unklar ist, entstehen Fehler oft erst im Frontend oder in der Integration.

## Folie 3: Was ist ein API-Schema?

Sprecher A:

> Ein Schema beschreibt die API maschinenlesbar. Das bedeutet: Tools können daraus Dokumentation, Tests oder sogar Client-Code ableiten. Wichtig ist aber, dass das Schema die echte API gut beschreibt und nicht nur zufällig aus dem Code entsteht.

## Folie 4: REST-Grundidee

Sprecher A:

> REST nutzt HTTP als Modell. Ressourcen stehen in der URL, Methoden beschreiben die Aktion. Für lesende Endpunkte sehen wir typischerweise `GET`. Filter werden häufig über Query-Parameter modelliert.

## Folie 5: Gutes REST-Design

Sprecher A:

> Gute REST-APIs sind vorhersehbar. Namen sollten domänennah sein, Fehler sollten konsistent aussehen, und Antwortmodelle sollten klar typisiert sein. Gerade bei größeren Datenmengen braucht man außerdem Limits oder Pagination.

## Folie 6: OpenAPI und Swagger UI

Sprecher A:

> OpenAPI ist der technische Vertrag. Swagger UI ist die sichtbare Oberfläche dafür. Das ist praktisch, weil man die API im Browser ausprobieren kann, ohne erst ein eigenes Tool oder Frontend zu bauen.

## Folie 7: Live-Interaktion mit REST

Sprecher A:

> Jetzt zeigen wir das konkret. Wir öffnen die Swagger UI des lokalen Backends, führen ein paar GET-Endpunkte aus und schauen uns danach das OpenAPI JSON an.

Live-Schritte stehen in `live-demo-plan.md`.

## Folie 8: Projekt als Showcase

Sprecher A:

> Am Projekt sieht man gut, was FastAPI automatisch liefert. Gleichzeitig sieht man auch eine typische Schwachstelle: Wenn ein Endpunkt nur `dict[str, Any]` zurückgibt, ist das Schema nicht besonders aussagekräftig. Das ist keine Katastrophe, aber ein guter Punkt für Verbesserung.

## Folie 9: Die Client-Perspektive

Sprecher B:

> Nach der API-Seite kommt die Frage: Wie konsumiert ein Frontend diese API? Wichtig ist, API-Aufrufe nicht überall im UI-Code zu verstreuen, sondern sie zentral zu kapseln.

## Folie 10: fetch

Sprecher B:

> `fetch` ist der Browser-Standard. Es ist schlank und überall verfügbar. Man muss aber wissen: Ein HTTP 404 oder 500 wird nicht automatisch als JavaScript-Fehler geworfen. Deshalb braucht man fast immer einen Wrapper.

## Folie 11: fetch im Projekt

Sprecher B:

> Genau das macht unser Projekt. `frontend/src/api-client.ts` enthält einen zentralen Wrapper. Dadurch steht die Fehlerbehandlung an einer Stelle, und Komponenten müssen nicht jedes Mal `response.ok` prüfen.

## Folie 12: axios

Sprecher B:

> axios ist komfortabler, sobald mehrere API-Aufrufe, Timeouts, Auth oder einheitliches Fehlerverhalten wichtig werden. Besonders Interceptors sind ein Grund, warum Teams axios einsetzen.

## Folie 13: axios-Beispiel

Sprecher B:

> Der Code ist kürzer, weil axios JSON direkt verarbeitet und Parameter sauber über `params` übernimmt. Auch der Rückgabewert ist klar: Die eigentlichen Daten liegen in `response.data`.

## Folie 14: fetch vs. axios

Sprecher B:

> Der Vergleich ist keine pauschale Empfehlung. Für kleine Projekte ist `fetch` oft ideal. Für größere Clients kann axios helfen, HTTP-Verhalten zentraler und konsistenter abzubilden.

## Folie 15: Live-Vergleich

Sprecher B:

> Wir nehmen einen realen fetch-Aufruf aus unserem Projekt und zeigen, wie derselbe Aufruf mit axios aussehen würde. Das hilft, die Unterschiede praktisch zu sehen.

## Folie 16: Gemeinsames Fazit

Sprecher A:

> API-Schema-Design sorgt dafür, dass APIs nicht nur funktionieren, sondern verständlich und überprüfbar bleiben.

Sprecher B:

> Und auf Client-Seite geht es darum, API-Zugriffe bewusst zu kapseln. Ob `fetch` oder axios besser passt, hängt von Größe und Anforderungen des Clients ab.
