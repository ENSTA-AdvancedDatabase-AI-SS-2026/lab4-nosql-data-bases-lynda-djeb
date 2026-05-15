-- ============================================
-- EX3: Requetes CQL
-- ============================================

USE smartgrid;

-- 3.1 Mesures d'un capteur sur les dernieres 6 heures
SELECT capteur_id, date, heure, tension, courant, puissance, alerte
FROM mesures_par_capteur
WHERE capteur_id = 123e4567-e89b-12d3-a456-426614174000
  AND date = '2024-01-15'
  AND heure >= '2024-01-15 18:00:00'
  AND heure <= '2024-01-16 00:00:00'
ORDER BY heure DESC;

-- 3.2 Derniere mesure de chaque capteur d'une wilaya
-- Table denormalisee pour cette requete
CREATE TABLE IF NOT EXISTS derniere_mesure_par_capteur (
    wilaya TEXT,
    capteur_id UUID,
    derniere_heure TIMESTAMP,
    derniere_tension FLOAT,
    dernier_courant FLOAT,
    derniere_puissance FLOAT,
    PRIMARY KEY (wilaya, derniere_heure, capteur_id)
) WITH CLUSTERING ORDER BY (derniere_heure DESC);

-- Requete
SELECT capteur_id, derniere_heure, derniere_tension, derniere_puissance
FROM derniere_mesure_par_capteur
WHERE wilaya = 'Alger'
LIMIT 100;

-- 3.3 Capteurs en alerte dans Alger aujourd'hui
SELECT wilaya, date, heure, capteur_id, tension, message
FROM alertes_par_wilaya
WHERE wilaya = 'Alger'
  AND date = '2024-01-15'
ALLOW FILTERING;

-- Version optimisee avec clustering sur alerte
CREATE TABLE IF NOT EXISTS alertes_par_jour (
    wilaya TEXT,
    date DATE,
    alerte BOOLEAN,
    heure TIMESTAMP,
    capteur_id UUID,
    tension FLOAT,
    message TEXT,
    PRIMARY KEY ((wilaya, date), alerte, heure)
);

SELECT COUNT(*) 
FROM alertes_par_jour
WHERE wilaya = 'Alger'
  AND date = '2024-01-15'
  AND alerte = true;

-- 3.4 Consommation totale par heure sur une journee
SELECT 
    wilaya,
    date,
    heure,
    SUM(puissance) as conso_totale,
    COUNT(*) as nb_mesures
FROM mesures_par_wilaya
WHERE wilaya = 'Alger'
  AND date = '2024-01-15'
GROUP BY wilaya, date, heure
ALLOW FILTERING;

-- Version avec table d'agregats
SELECT heure, puissance_moyenne, puissance_max, puissance_min
FROM agregats_horaires
WHERE wilaya = 'Alger'
  AND annee_mois = '2024-01'
ORDER BY heure ASC;

-- 3.5 Tension anormale dans les 30 dernieres minutes
SELECT wilaya, heure, capteur_id, tension
FROM mesures_par_wilaya
WHERE wilaya = 'Alger'
  AND date = '2024-01-15'
  AND heure >= '2024-01-15 23:30:00'
  AND tension < 200 OR tension > 240
ALLOW FILTERING;

-- 3.6 Top 10 capteurs les plus actifs cette semaine
SELECT capteur_id, COUNT(*) as nb_mesures
FROM mesures_par_capteur
WHERE date >= '2024-01-08'
  AND date <= '2024-01-15'
GROUP BY capteur_id
ORDER BY nb_mesures DESC
LIMIT 10
ALLOW FILTERING;

-- 3.7 ALLOW FILTERING - Explication
-- MAUVAISE REQUETE (scan complet)
SELECT * FROM mesures_par_capteur WHERE alerte = true ALLOW FILTERING;

-- BONNE REQUETE (table dediee)
SELECT * FROM alertes_par_jour WHERE alerte = true;

-- Demonstration de l'impact
TRACING ON;
SELECT * FROM mesures_par_capteur WHERE tension > 240 ALLOW FILTERING;
TRACING OFF;
