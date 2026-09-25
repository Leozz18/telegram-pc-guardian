# Telegram PC Guardian

Utility Windows trasparente e **consensuale**: espone controlli limitati tramite un bot Telegram, esclusivamente per un Chat ID configurato. Non è uno strumento di sorveglianza e non esegue comandi arbitrari.

## Installazione

Richiede Python 3.11+ su Windows.

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[test]"
Copy-Item .env.example .env
```

In BotFather crea il bot e inserisci il token in `TELEGRAM_BOT_TOKEN` (meglio come variabile d'ambiente Windows, non in un file committato). Imposta `TELEGRAM_ALLOWED_CHAT_ID` con il tuo Chat ID numerico. Il bot ignora ogni altro Chat ID. Per sicurezza, proteggi il file di audit e la cartella di configurazione con permessi Windows minimi.

Esegui `telegram-pc-guardian`. Il programma mostra una notifica di avvio e registra eventi strutturati in JSON Lines. Per avviarlo con Windows, usa una voce **Utilità di pianificazione** visibile e documentata, con l'account utente dedicato e il minor privilegio possibile; il progetto non installa persistenza nascosta.

## Comandi e consenso

`/status` e `/help` sono disponibili al Chat ID autorizzato. `/stop`, `/shutdown`, `/restart`, `/lock` e `/screenshot` generano prima un codice temporaneo: l'azione avviene solo dopo `/confirm CODICE`. Ogni richiesta è registrata. Lo screenshot viene acquisito e inviato soltanto dopo quel comando esplicito autorizzato; non esistono acquisizioni periodiche.

Il meccanismo di emergenza locale è il file indicato da `GUARDIAN_STOP_FILE`: crealo per fermare il polling (`New-Item $env:ProgramData\TelegramPcGuardian\STOP`). Il file `audit.jsonl` documenta avvio, comandi, rate limiting ed esito delle azioni; token e codici non vengono registrati.

## Limitazioni e sicurezza

Le API Windows possono richiedere privilegi o policy specifiche per blocco, arresto e riavvio. Le notifiche sono sempre visibili. Il rate limiting limita le richieste; il polling richiede connettività verso Telegram. Il “risveglio remoto” non è implementato: Wake-on-LAN richiede hardware, BIOS, scheda di rete e configurazione della rete locale compatibili.

Non sono implementati persistenza occulta, furto di credenziali, esecuzione arbitraria, keylogging, monitoraggio nascosto o cattura di webcam/microfono. Il token è un segreto: revocalo da BotFather se esposto e non committarlo mai.

## Test

```powershell
pytest
```
