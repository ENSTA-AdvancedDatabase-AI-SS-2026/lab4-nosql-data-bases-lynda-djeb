-- ============================================
-- EX4: Compaction et maintenance
-- ============================================

USE smartgrid;

-- 4.1 Verification des strategies actuelles
SELECT table_name, compaction 
FROM system_schema.tables 
WHERE keyspace_name = 'smartgrid';

-- 4.2 Configuration TWCS pour mesures_par_capteur
ALTER TABLE mesures_par_capteur
WITH compaction = {
    'class': 'TimeWindowCompactionStrategy',
    'compaction_window_unit': 'DAYS',
    'compaction_window_size': 1,
    'expired_sstable_check_frequency_seconds': 1800,
    'timestamp_resolution': 'MICROSECONDS'
};

-- 4.3 Configuration TWCS pour mesures_par_wilaya
ALTER TABLE mesures_par_wilaya
WITH compaction = {
    'class': 'TimeWindowCompactionStrategy',
    'compaction_window_unit': 'DAYS',
    'compaction_window_size': 1
};

-- 4.4 Configuration TWCS pour alertes (fenetre 7 jours)
ALTER TABLE alertes_par_wilaya
WITH compaction = {
    'class': 'TimeWindowCompactionStrategy',
    'compaction_window_unit': 'DAYS',
    'compaction_window_size': 7
};

-- 4.5 Configuration TWCS pour agregats (fenetre 1 mois)
ALTER TABLE agregats_horaires
WITH compaction = {
    'class': 'TimeWindowCompactionStrategy',
    'compaction_window_unit': 'MONTHS',
    'compaction_window_size': 1
};

-- 4.6 Verifier l'utilisation des TTL
SELECT ttl(tension) as ttl_restant, 
       writeTime(tension) as ecrit_le,
       capteur_id, heure
FROM mesures_par_capteur
LIMIT 10;

-- 4.7 Compaction manuelle (si necessaire)
ALTER TABLE mesures_par_capteur WITH compaction = {
    'class': 'TimeWindowCompactionStrategy',
    'compaction_window_unit': 'DAYS',
    'compaction_window_size': 1
};

-- 4.8 Nodetool commands (a executer dans terminal)
-- nodetool tablestats smartgrid.mesures_par_capteur
-- nodetool compact smartgrid mesures_par_capteur
-- nodetool garbagecollect smartgrid mesures_par_capteur

-- 4.9 Detection des hot partitions
SELECT partition_key, size_in_bytes
FROM system.size_estimates
WHERE keyspace_name = 'smartgrid'
  AND table_name = 'mesures_par_capteur'
ORDER BY size_in_bytes DESC
LIMIT 10;

-- 4.10 Reparer une hot partition avec bucket
CREATE TABLE mesures_par_capteur_bucketed (
    capteur_id UUID,
    annee_mois TEXT,
    jour INT,
    heure TIMESTAMP,
    tension FLOAT,
    courant FLOAT,
    puissance FLOAT,
    PRIMARY KEY ((capteur_id, annee_mois), jour, heure)
);

-- 4.11 Nettoyer les donnees expirees manuellement
SELECT COUNT(*) FROM mesures_par_capteur 
WHERE date < dateadd(day, -90, now());

-- Compaction forcee pour liberer l'espace
-- nodetool compact smartgrid mesures_par_capteur
