# VNBdigital Mesh TODO

## Spannungsebenen / Filter

Umgesetzte Filterwerte im VNBdigital-Client, Backend und Frontend:
- Niederspannung
- Mittelspannung
- Hochspannung

Noch fachlich zu klaeren bzw. gesondert abzubilden:
- Hoechstspannung
- TSO only

Hinweis: VNBdigital GraphQL hat `Höchstspannung`, `Hoechstspannung` und `TSO` im Feld `voltageTypes` bei Live-Tests abgelehnt. Falls TSO/Hoechstspannung gebraucht wird, muss vermutlich ein anderer API-Filter, `onlyNap`, Regionsdaten oder eine separate Datenquelle verwendet werden.
