-- ============================================
-- EX1: Modelisation des tables
-- ============================================

-- 1.1 Keyspace pour SmartGrid DZ
CREATE KEYSPACE IF NOT EXISTS smartgrid
WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'datacenter1': 3
}
AND durable_writes = true;

USE smartgrid;

-- 1.2 Table mesures_par_capteur
-- Requete: mesures du capteur X entre T1 et T2
CREATE TABLE IF NOT EXISTS mesures_par_capteur (
    capteur_id UUID,
    date DATE,
    heure TIMESTAMP,
    wilaya TEXT,
    tension FLOAT,
    courant FLOAT,
    puissance FLOAT,
    alerte BOOLEAN,
    PRIMARY KEY ((capteur_id, date), heure)
) WITH CLUSTERING ORDER BY (heure DESC)
AND default_time_to_live = 7776000
AND compaction = {
    'class': 'TimeWindowCompactionStrategy',
    'compaction_window_unit': 'DAYS',
    'compaction_window_size': 1
};

-- 1.3 Table mesures_par_wilaya
-- Requete: toutes les mesures d'une wilaya sur une journee
CREATE TABLE IF NOT EXISTS mesures_par_wilaya (
    wilaya TEXT,
    date DATE,
    heure TIMESTAMP,
    capteur_id UUID,
    tension FLOAT,
    courant FLOAT,
    puissance FLOAT,
    alerte BOOLEAN,
    PRIMARY KEY ((wilaya, date), heure)
) WITH CLUSTERING ORDER BY (heure DESC)
AND default_time_to_live = 7776000
AND compaction = {
    'class': 'TimeWindowCompactionStrategy',
    'compaction_window_unit': 'DAYS',
    'compaction_window_size': 1
};

-- 1.4 Table alertes_par_wilaya
-- Requete: alertes d'une wilaya aujourd'hui
CREATE TABLE IF NOT EXISTS alertes_par_wilaya (
    wilaya TEXT,
    date DATE,
    heure TIMESTAMP,
    capteur_id UUID,
    tension FLOAT,
    courant FLOAT,
    puissance FLOAT,
    message TEXT,
    PRIMARY KEY ((wilaya, date), heure)
) WITH CLUSTERING ORDER BY (heure DESC)
AND default_time_to_live = 31536000
AND compaction = {
    'class': 'TimeWindowCompactionStrategy',
    'compaction_window_unit': 'DAYS',
    'compaction_window_size': 7
};

-- 1.5 Table agregats_horaires
-- Requete: consommation moyenne par heure (dashboard)
CREATE TABLE IF NOT EXISTS agregats_horaires (
    wilaya TEXT,
    annee_mois TEXT,
    heure INT,
    date_agregat DATE,
    puissance_moyenne FLOAT,
    puissance_max FLOAT,
    puissance_min FLOAT,
    nombre_mesures BIGINT,
    PRIMARY KEY ((wilaya, annee_mois), heure, date_agregat)
) WITH default_time_to_live = 157680000
AND compaction = {
    'class': 'TimeWindowCompactionStrategy',
    'compaction_window_unit': 'MONTHS',
    'compaction_window_size': 1
};

-- 1.6 Table capteurs_par_wilaya
-- Pour lister les capteurs actifs par wilaya
CREATE TABLE IF NOT EXISTS capteurs_par_wilaya (
    wilaya TEXT,
    capteur_id UUID,
    date_activation DATE,
    dernier_contact TIMESTAMP,
    adresse TEXT,
    PRIMARY KEY (wilaya, capteur_id)
);

-- Verification
DESCRIBE TABLES;
