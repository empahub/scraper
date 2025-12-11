Mali Python alat koji automatski skuplja podatke o chip tuningu sa sajta dominanz.rs – sve marke, modele, generacije (godine) i motore – i snima ih u CSV fajl. Podaci su idealni za dalju obradu (Excel, Google Sheets, import u bazu ili korišćenje u web aplikacijama).

Šta skripta radi
Otvara stranicu /sr/services/tuning

Za svaku marku vozila čita:

naziv brenda

broj modela

broj motora sa mapiranjem i procenat dostupnosti

Za svaki model:

naziv modela

broj generacija / motora (informacija sa kartice)

broj motora sa mapiranjem i procenat

Za svaku generaciju/godinu:

oznaku (npr. 2001-2005, 2005 ->)

broj motora i procenat dostupnosti

Za svaki motor:

naziv motora (npr. 1.9 JTD 115hp)

fabričku i mapiranu snagu (HP)

fabrički i mapirani obrtni moment (Nm)

Sve se upisuje u jedan CSV fajl (npr. dominanz_tuning_all.csv).

Struktura CSV fajla
CSV ima sledeće kolone:

brand_name

brand_url

brand_models_count

brand_mapped

brand_total

brand_percent

model_name

model_url

model_info

model_mapped

model_total

model_percent

year_label

year_url

year_info

year_mapped

year_total

year_percent

engine_name

stock_hp

tuned_hp

stock_nm

tuned_nm

URL kolone su tu samo kao referenca i ne moraju se koristiti dalje u aplikacijama.
