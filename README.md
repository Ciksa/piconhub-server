# PiconHub server – Skylink 23.5°E TEST 5

Toto je prvý kontrolovaný serverový balík pre PiconHub by Warder.

Obsahuje 5 TEST piconov s reálnymi Service References z prijímača:
- Markiza HD
- TV JOJ HD
- RTVS SPORT HD
- Nova Sport 1 HD
- TA3 HD

PNG sú zámerne označené PICONHUB TEST. Nie sú to finálne logá. Slúžia iba na overenie celého reťazca server -> manifest -> SHA-256 -> prijímač.

## GitHub
1. Vytvor verejný repozitár, napr. `piconhub-server`.
2. Nahraj celý obsah tohto priečinka do koreňa repozitára.
3. Pred uploadom alebo po lokálnom rozbalení spusti:
   `python3 tools/configure_repo.py TVOJE_GITHUB_MENO piconhub-server`
4. Výsledná adresa katalógu bude:
   `https://raw.githubusercontent.com/TVOJE_GITHUB_MENO/piconhub-server/main/catalog.json`

Pošli túto adresu do chatu. Následne sa vytvorí testovacie IPK, ktoré ju použije ako catalog_url.

Dôležité: PiconHub má mať zapnuté zálohovanie existujúcich piconov počas testu.
