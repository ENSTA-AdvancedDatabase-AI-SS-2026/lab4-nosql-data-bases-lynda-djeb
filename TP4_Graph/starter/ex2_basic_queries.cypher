// ============================================
// EX2: Requetes de base
// ============================================

// 2.1 Trouver tous les amis d'Ahmed (1 saut)
MATCH (ahmed:Etudiant {prenom: "Ahmed", nom: "Bensalem"})-[:CONNAIT]-(ami:Etudiant)
RETURN ami.prenom, ami.nom, ami.universite, ami.filiere
ORDER BY ami.prenom;

// 2.2 Amis d'amis d'Ahmed qui ne sont pas deja ses amis
// Suggestions de connexions
MATCH (ahmed:Etudiant {prenom: "Ahmed", nom: "Bensalem"})-[:CONNAIT*2]-(suggestion:Etudiant)
WHERE NOT (ahmed)-[:CONNAIT]-(suggestion)
  AND ahmed <> suggestion
RETURN suggestion.prenom, suggestion.nom, suggestion.universite,
       COUNT(*) AS amis_communs
ORDER BY amis_communs DESC
LIMIT 10;

// 2.3 Etudiants qui suivent le meme cours que Fatima mais ne la connaissent pas
MATCH (fatima:Etudiant {prenom: "Fatima", nom: "Ouali"})-[:SUIT]->(cours:Cours)
MATCH (autre:Etudiant)-[:SUIT]->(cours)
WHERE autre <> fatima
  AND NOT (fatima)-[:CONNAIT]-(autre)
RETURN DISTINCT autre.prenom, autre.nom, autre.universite,
       cours.code AS cours_commun, cours.intitule
ORDER BY autre.universite, autre.prenom
LIMIT 20;

// 2.4 Clubs les plus populaires (par nombre de membres)
MATCH (club:Club)<-[:MEMBRE_DE]-(membre:Etudiant)
RETURN club.nom, club.universite, club.domaine,
       COUNT(membre) AS nb_membres
ORDER BY nb_membres DESC;

// 2.5 Profil complet d'un etudiant
// Amis, cours, competences, clubs, stages
MATCH (e:Etudiant {prenom: "Ahmed", nom: "Bensalem"})
OPTIONAL MATCH (e)-[:CONNAIT]-(ami:Etudiant)
OPTIONAL MATCH (e)-[:SUIT]->(cours:Cours)
OPTIONAL MATCH (e)-[:MAITRISE]->(comp:Competence)
OPTIONAL MATCH (e)-[:MEMBRE_DE]->(club:Club)
OPTIONAL MATCH (e)-[:A_STAGE_CHEZ]->(stage:Entreprise)
RETURN e.prenom, e.nom, e.universite, e.filiere, e.annee,
       COLLECT(DISTINCT ami.prenom + " " + ami.nom) AS amis,
       COLLECT(DISTINCT cours.code + ": " + cours.intitule) AS cours,
       COLLECT(DISTINCT comp.nom) AS competences,
       COLLECT(DISTINCT club.nom) AS clubs,
       COLLECT(DISTINCT stage.nom) AS stages;

// 2.6 Etudiants par universite
MATCH (e:Etudiant)-[:ETUDIE_A]->(u:Universite)
RETURN u.nom AS universite, COUNT(e) AS nb_etudiants
ORDER BY nb_etudiants DESC;

// 2.7 Les cours les plus populaires
MATCH (c:Cours)<-[:SUIT]-(e:Etudiant)
RETURN c.code, c.intitule, c.departement,
       COUNT(e) AS nb_etudiants,
       ROUND(AVG(e.note), 1) AS moyenne_notes
ORDER BY nb_etudiants DESC
LIMIT 10;

// 2.8 Competences les plus maitrisees
MATCH (comp:Competence)<-[:MAITRISE]-(e:Etudiant)
RETURN comp.nom, comp.categorie,
       COUNT(e) AS nb_etudiants,
       COLLECT(DISTINCT e.universite)[0..3] AS universites
ORDER BY nb_etudiants DESC
LIMIT 10;

// 2.9 Reseau de connaissances d'Ahmed (graphique)
MATCH (ahmed:Etudiant {prenom: "Ahmed", nom: "Bensalem"})-[:CONNAIT*1..2]-(contact)
WHERE ahmed <> contact
RETURN ahmed.prenom AS source,
       contact.prenom AS cible,
       length(shortestPath((ahmed)-[:CONNAIT*]-(contact))) AS distance
ORDER BY distance, contact.prenom;

// 2.10 Etudiants par ville et filiere
MATCH (e:Etudiant)
RETURN e.ville, e.filiere, COUNT(e) AS effectif
ORDER BY e.ville, effectif DESC;

// 2.11 Taux de reussite par cours (note >= 10)
MATCH (c:Cours)<-[s:SUIT]-(e:Etudiant)
WITH c, 
     COUNT(s) AS total,
     SUM(CASE WHEN s.note >= 10 THEN 1 ELSE 0 END) AS reussis
RETURN c.code, c.intitule,
       total,
       reussis,
       ROUND(100.0 * reussis / total, 1) AS taux_reussite
ORDER BY taux_reussite DESC;

// 2.12 Etudiants qui peuvent etre tuteurs
// (M2 avec au moins 2 competences et moyenne > 15)
MATCH (e:Etudiant)
WHERE e.annee >= 4
WITH e, [(e)-[:MAITRISE]->(c) | c] AS comps, [(e)-[:SUIT]->(c) | c] AS cours
WHERE SIZE(comps) >= 2
WITH e, SIZE(comps) AS nb_comps,
     REDUCE(s = 0, c IN cours | s + c.note) / SIZE(cours) AS moyenne
WHERE moyenne > 15
RETURN e.prenom, e.nom, e.universite, e.filiere,
       nb_comps,
       ROUND(moyenne, 1) AS moyenne_generale
ORDER BY moyenne_generale DESC;

// 2.13 Suggestions de stage basees sur les competences
MATCH (e:Etudiant {prenom: "Ahmed", nom: "Bensalem"})-[:MAITRISE]->(comp:Competence)
MATCH (comp)<-[:REQUIERT]-(cours:Cours)
MATCH (autre:Etudiant)-[:SUIT]->(cours)
WHERE autre <> e
MATCH (autre)-[:A_STAGE_CHEZ]->(entreprise:Entreprise)
RETURN DISTINCT entreprise.nom AS entreprise,
       COUNT(DISTINCT autre) AS anciens_stagiaires,
       COLLECT(DISTINCT autre.prenom + " " + autre.nom)[0..3] AS exemples
ORDER BY anciens_stagiaires DESC
LIMIT 5;

// 2.14 Verifier que le graphe est connexe
// Compter les composantes connexes
MATCH (e:Etudiant)
OPTIONAL MATCH path = shortestPath((e)-[:CONNAIT*]-(autre))
WITH e, MIN(LENGTH(path)) AS min_dist
RETURN COUNT(DISTINCT e) AS total_etudiants,
       COUNT(DISTINCT CASE WHEN min_dist IS NULL THEN e END) AS isoles,
       COUNT(DISTINCT CASE WHEN min_dist IS NOT NULL THEN e END) AS connectes;

// 2.15 Les ponts entre universites
// Etudiants qui connaissent des gens d'autres univ
MATCH (e:Etudiant)-[:CONNAIT]-(autre:Etudiant)
WHERE e.universite <> autre.universite
RETURN e.universite AS univ_source,
       autre.universite AS univ_cible,
       COUNT(DISTINCT e) AS nb_connecteurs,
       COUNT(DISTINCT autre) AS nb_connectes
ORDER BY nb_connecteurs DESC;
