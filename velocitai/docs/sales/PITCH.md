# Pitch + copione demo (10 minuti)

## Struttura del pitch (8 punti)
1. **Aggancio** — «Quanti dei vostri verbali da autovelox vengono annullati o
   persi in ricorso? Ogni annullamento è costo e contenzioso.»
2. **Problema** — vizi formali, prove deboli, errori di calcolo, GDPR.
3. **Soluzione** — VelociTAI: ciclo completo, verbale **difendibile**.
4. **Differenziatore #1** — prova con catena di custodia **HMAC** verificabile +
   audit-log a prova di manomissione.
5. **Differenziatore #2** — sicurezza/GDPR by-design e affidabilità (niente doppie
   multe, auto-riparazione).
6. **Demo live** — vedi copione sotto.
7. **Prezzo & modelli** — SaaS / pay-per-verbale / chiavi in mano; MEPA/gara.
8. **Call to action** — pilota a basso rischio su una postazione.

## Copione demo (5 minuti, su laptop)

> Preparazione: `make install` (una volta). Avere un terminale pronto.

**1) Lo scenario completo (60s)**
```bash
python3 -m velocitai demo --show-verbale 3
```
«Cinque veicoli, limite 50. Il sistema rileva, misura, applica la tolleranza di
legge, classifica la sanzione e genera il verbale. Notate il comma 9, i punti, la
sospensione e — in fondo — l'**hash della prova**.»

**2) Dal VIDEO al verbale (90s)**
```bash
python3 examples/video_demo.py
```
«Qui processiamo un **video vero**: rileviamo il veicolo dai pixel, misuriamo la
velocità, **leggiamo la targa**, e produciamo la sanzione. Niente è inserito a
mano.»

**3) La prova regge (60s)**
```bash
python3 -m velocitai doctor          # tutto verde: prove integre, audit OK
# poi simuliamo una manomissione di un file-prova...
python3 -m velocitai doctor          # ora: "Prove compromesse" -> ATTENZIONE
```
«Se qualcuno altera la prova, il sistema **se ne accorge**. È questo che fa cadere
i ricorsi.»

**4) Console operatore (30s)**
```bash
python3 -m velocitai serve           # http://127.0.0.1:8080
```
«Esiti per veicolo, verbali, stato del sistema. C'è anche l'API per il vostro
gestionale.»

**5) Il prezzo, trasparente (30s)**
```bash
python3 -m velocitai quote --postazioni 5 --modello saas --anni 3
```
«Preventivo immediato. Per voi, con 5 postazioni, il TCO a 3 anni è questo.»

## Chiusura
«Possiamo partire con un **pilota** su una sola postazione, a risultato: voi
misurate il beneficio, noi avviamo in parallelo l'omologazione con il partner
hardware. Quando possiamo fissare il pilota?»
