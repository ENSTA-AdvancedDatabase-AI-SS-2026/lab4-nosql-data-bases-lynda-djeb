// ============================================
// EX4: Requetes avancees
// ============================================

// 4.1 Trouver un tuteur
// "Etudiant en Master qui maitrise Python et a eu >14/20 en BDD"
MATCH (tuteur:Etudiant)-[:MAITRISE]->(comp:Competence {nom: "Python"})
MATCH (tuteur)-[:SUIT {note: note}]->(cours:Cours {code: "INFO401"})
WHERE tuteur.annee >= 4 AND note > 14
RETURN tuteur.prenom, tuteur.nom, tuteur.universite, note AS note_BDD
ORDER BY note DESC;

// 4.2 Reseau alumni dans une entreprise
// "Qui de mon reseau (jusqu'a 3 sauts) travaille chez Sonatrach ?"
MATCH (moi:Etudiant {prenom: "Ahmed", nom: "Bensalem"})
MATCH (moi)-[:CONNAIT*1..3]-(alumni:Etudiant)
MATCH (alumni)-[:A_STAGE_CHEZ]->(entreprise:Entreprise {nom: "Sonatrach"})
WHERE moi <> alumni
RETURN DISTINCT alumni.prenom, alumni.nom, alumni.universite, 
       SIZE([(alumni)-[:CONNAIT]-(autre) | autre]) AS nb_connexions
ORDER BY nb_connexions DESC;

// 4.3 Etudiants qui connectent des communautes isolees (Ponts)
// Trouver les etudiants qui sont le seul lien entre deux universites differentes
MATCH (e:Etudiant)-[:CONNAIT]-(autre:Etudiant)
WHERE e.universite <> autre.universite
WITH e, COUNT(DISTINCT autre.universite) AS universites_connectees
WHERE universites_connectees >= 2
MATCH (e)-[:CONNAIT]-(ami:Etudiant)
WITH e, COLLECT(DISTINCT ami.universite) AS reseau_universites
WHERE SIZE(reseau_universites) >= 2
RETURN e.prenom, e.nom, e.universite, reseau_universites,
       SIZE(reseau_universites) AS ponts_entre_universites
ORDER BY ponts_entre_universites DESC;

// Version alternative avec shortestPath
MATCH (e:Etudiant)
WHERE EXISTS {
    MATCH (e)-[:CONNAIT]-(u1:Etudiant)
    WHERE u1.universite <> e.universite
}
RETURN e.prenom, e.nom, e.universite,
       COUNT(DISTINCT u1.universite) AS connexions_externes
ORDER BY connexions_externes DESC
LIMIT 10;

// 4.4 Analyse temporelle - Evolution du reseau par mois
// Creer des relations avec dates si pas encore fait
MATCH (a:Etudiant), (b:Etudiant)
WHERE a.id < b.id AND a.universite = b.universite
CREATE (a)-[:CONNAIT {depuis: 2022, contexte: "universite"}]->(b);

// Croissance des connexions par annee
MATCH ()-[r:CONNAIT]-()
RETURN r.depuis AS annee, COUNT(r) AS nouvelles_connexions
ORDER BY annee;

// 4.5 Score de similarite - Coefficient de Jaccard
// Etudiants les plus similaires a Ahmed
MATCH (moi:Etudiant {prenom: "Ahmed", nom: "Bensalem"})
MATCH (moi)-[:SUIT]->(coursMoi:Cours)
MATCH (moi)-[:MAITRISE]->(compMoi:Competence)
MATCH (moi)-[:MEMBRE_DE]->(clubMoi:Club)

MATCH (autre:Etudiant)
WHERE autre.id <> moi.id

WITH moi, autre,
     SIZE(COLLECT(DISTINCT coursMoi)) AS moi_cours,
     SIZE(COLLECT(DISTINCT compMoi)) AS moi_comps,
     SIZE(COLLECT(DISTINCT clubMoi)) AS moi_clubs,
     SIZE([(autre)-[:SUIT]->(c: Cours) | c]) AS autre_cours,
     SIZE([(autre)-[:MAITRISE]->(c: Competence) | c]) AS autre_comps,
     SIZE([(autre)-[:MEMBRE_DE]->(c: Club) | c]) AS autre_clubs

WITH moi, autre,
     SIZE([(moi)-[:SUIT]->(c:Cours) WHERE (autre)-[:SUIT]->(c) | c]) AS cours_communs,
     SIZE([(moi)-[:MAITRISE]->(c:Competence) WHERE (autre)-[:MAITRISE]->(c) | c]) AS comps_communs,
     SIZE([(moi)-[:MEMBRE_DE]->(c:Club) WHERE (autre)-[:MEMBRE_DE]->(c) | c]) AS clubs_communs,
     moi_cours + autre_cours - SIZE([(moi)-[:SUIT]->(c:Cours) WHERE (autre)-[:SUIT]->(c) | c]) AS total_cours,
     moi_comps + autre_comps - SIZE([(moi)-[:MAITRISE]->(c:Competence) WHERE (autre)-[:MAITRISE]->(c) | c]) AS total_comps,
     moi_clubs + autre_clubs - SIZE([(moi)-[:MEMBRE_DE]->(c:Club) WHERE (autre)-[:MEMBRE_DE]->(c) | c]) AS total_clubs

WITH autre,
     (toFloat(cours_communs) / toFloat(CASE WHEN total_cours = 0 THEN 1 ELSE total_cours END)) AS jaccard_cours,
     (toFloat(comps_communs) / toFloat(CASE WHEN total_comps = 0 THEN 1 ELSE total_comps END)) AS jaccard_comps,
     (toFloat(clubs_communs) / toFloat(CASE WHEN total_clubs = 0 THEN 1 ELSE total_clubs END)) AS jaccard_clubs

WITH autre,
     (jaccard_cours + jaccard_comps + jaccard_clubs) / 3 AS score_similarite
WHERE score_similarite > 0
RETURN autre.prenom, autre.nom, autre.universite,
       ROUND(score_similarite * 100, 2) AS pourcentage_similarite
ORDER BY score_similarite DESC
LIMIT 10;

// 4.6 Chemin de competences
// "Quels cours dois-je suivre pour maitriser Deep Learning ?"
MATCH (cible:Competence {nom: "Deep Learning"})
MATCH (depart:Etudiant {prenom: "Ahmed", nom: "Bensalem"})
MATCH (depart)-[:MAITRISE]->(competenceActuelle:Competence)

// Trouver les cours qui enseignent les competences manquantes
MATCH (cours:Cours)-[:REQUIERT]->(competenceRequise:Competence)
WHERE NOT (depart)-[:MAITRISE]->(competenceRequise)

// Construire le chemin d'apprentissage
WITH DISTINCT competenceRequise, cours
MATCH (cours)-[:REQUIERT]->(autreComp:Competence)
WHERE NOT (depart)-[:MAITRISE]->(autreComp)

RETURN competenceRequise.nom AS competence_a_acquerir,
       cours.code AS cours_recommande,
       cours.intitule,
       [ (cours)-[:REQUIERT]->(c:Competence) | c.nom ] AS prerequis
ORDER BY SIZE([(cours)-[:REQUIERT]->(c:Competence) WHERE NOT (depart)-[:MAITRISE]->(c) | c]) ASC
LIMIT 10;

// 4.7 Centralite d'intermediation (Betweenness Centrality)
// Quels etudiants sont les plus importants pour la circulation de l'information ?
MATCH path = shortestPath((start:Etudiant)-[:CONNAIT*]-(end:Etudiant))
WHERE start.id < end.id
UNWIND nodes(path) AS noeud
WITH noeud, COUNT(path) AS chemins_passants
RETURN noeud.prenom, noeud.nom, noeud.universite, chemins_passants
ORDER BY chemins_passants DESC
LIMIT 10;

// 4.8 Detection de cliques (groupes completement connectes)
// Trouver des groupes ou tout le monde connait tout le monde
MATCH (a:Etudiant)-[:CONNAIT]-(b:Etudiant)
MATCH (a)-[:CONNAIT]-(c:Etudiant)
MATCH (b)-[:CONNAIT]-(c)
WHERE a.id < b.id AND b.id < c.id
RETURN a.prenom + " " + a.nom AS personne1,
       b.prenom + " " + b.nom AS personne2,
       c.prenom + " " + c.nom AS personne3,
       a.universite
LIMIT 20;

// 4.9 Recommandation de stage basee sur le reseau
// "Les entreprises ou mes amis ont fait leur stage"
MATCH (moi:Etudiant {prenom: "Ahmed", nom: "Bensalem"})
MATCH (moi)-[:CONNAIT*1..2]-(ami:Etudiant)
MATCH (ami)-[:A_STAGE_CHEZ]->(entreprise:Entreprise)
WHERE NOT (moi)-[:A_STAGE_CHEZ]->(entreprise)
RETURN entreprise.nom, entreprise.secteur,
       COUNT(DISTINCT ami) AS nb_connaissances,
       COLLECT(DISTINCT ami.prenom + " " + ami.nom)[0..3] AS exemples
ORDER BY nb_connaissances DESC
LIMIT 5;

// 4.10 Evolution des competences par promotion
MATCH (e:Etudiant)-[:MAITRISE {niveau: "Expert"}]->(c:Competence)
RETURN e.annee AS promotion, c.nom AS competence, COUNT(e) AS nb_experts
ORDER BY promotion, nb_experts DESC;

// 4.11 Chemin le plus court avec proprietes
// "Chemin le plus court entre deux etudiants en passant par des amis communs"
MATCH p = shortestPath(
  (a:Etudiant {prenom: "Ahmed"})-[:CONNAIT*]-(b:Etudiant {prenom: "Yasmina"})
)
RETURN [n IN nodes(p) | n.prenom + " " + n.nom] AS chemin,
       length(p) AS distance,
       [r IN relationships(p) | r.contexte] AS contextes
LIMIT 5;

// 4.12 Propagation d'influence (BFS simple)
// "Tous les gens que Ahmed peut atteindre en 3 sauts"
MATCH (moi:Etudiant {prenom: "Ahmed", nom: "Bensalem"})
MATCH (moi)-[:CONNAIT*1..3]-(contact)
WHERE moi <> contact
RETURN contact.prenom, contact.nom, contact.universite,
       length(shortestPath((moi)-[:CONNAIT*]-(contact))) AS hops
ORDER BY hops, contact.universite;

// 4.13 Taux de clustering local
// "Mes amis sont-ils aussi amis entre eux ?"
MATCH (moi:Etudiant {prenom: "Ahmed", nom: "Bensalem"})
MATCH (moi)-[:CONNAIT]-(ami)
WITH moi, COLLECT(ami) AS amis
MATCH (a)-[:CONNAIT]-(b)
WHERE a IN amis AND b IN amis AND a.id < b.id
RETURN moi.prenom, moi.nom,
       SIZE(amis) AS nb_amis,
       COUNT(DISTINCT a) + COUNT(DISTINCT b) AS connexions_entre_amis,
       toFloat(COUNT(DISTINCT a) + COUNT(DISTINCT b)) / (SIZE(amis) * (SIZE(amis) - 1)) AS clustering_coeff;

// 4.14 Recommandation de projet
// "Formez des equipes pour un projet Data Science"
MATCH (e:Etudiant)
WHERE (e)-[:MAITRISE]->(:Competence {nom: "Python"})
  AND (e)-[:MAITRISE]->(:Competence {nom: "SQL"})
  AND (e)-[:SUIT]->(:Cours {code: "INFO402"})
WITH e, [ (e)-[:MAITRISE]->(c:Competence) | c.nom ] AS competences
WHERE SIZE(competences) >= 3
RETURN e.prenom, e.nom, e.universite, e.annee, competences
ORDER BY SIZE(competences) DESC
LIMIT 15;
