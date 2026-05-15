// TP4 - Exercice 1 : Creation du graphe UniConnect DZ
// Effacer la base pour partir propre
MATCH (n) DETACH DELETE n;

// ─── 1.1 : Contraintes d'unicite ─────────────────────────────────────────────
CREATE CONSTRAINT etudiant_id IF NOT EXISTS FOR (e:Etudiant) REQUIRE e.id IS UNIQUE;
CREATE CONSTRAINT cours_code IF NOT EXISTS FOR (c:Cours) REQUIRE c.code IS UNIQUE;
CREATE CONSTRAINT competence_nom IF NOT EXISTS FOR (c:Competence) REQUIRE c.nom IS UNIQUE;
CREATE CONSTRAINT club_nom IF NOT EXISTS FOR (c:Club) REQUIRE c.nom IS UNIQUE;
CREATE CONSTRAINT entreprise_nom IF NOT EXISTS FOR (e:Entreprise) REQUIRE e.nom IS UNIQUE;

// ─── 1.2 : Creer les competences ──────────────────────────────────────────────
UNWIND [
  {nom: "Python", categorie: "Programmation"},
  {nom: "Java", categorie: "Programmation"},
  {nom: "SQL", categorie: "Bases de Donnees"},
  {nom: "NoSQL", categorie: "Bases de Donnees"},
  {nom: "Machine Learning", categorie: "IA"},
  {nom: "Deep Learning", categorie: "IA"},
  {nom: "React", categorie: "Web"},
  {nom: "Angular", categorie: "Web"},
  {nom: "Docker", categorie: "DevOps"},
  {nom: "Kubernetes", categorie: "DevOps"},
  {nom: "Linux", categorie: "Systemes"},
  {nom: "Reseaux", categorie: "Infrastructure"},
  {nom: "C++", categorie: "Programmation"},
  {nom: "JavaScript", categorie: "Web"},
  {nom: "TypeScript", categorie: "Web"}
] AS comp
MERGE (:Competence {nom: comp.nom, categorie: comp.categorie});

// ─── 1.3 : Creer les cours ────────────────────────────────────────────────────
UNWIND [
  {code: "INFO401", intitule: "Bases de Donnees Avancees", credits: 6, dept: "Informatique"},
  {code: "INFO402", intitule: "Intelligence Artificielle", credits: 6, dept: "Informatique"},
  {code: "INFO403", intitule: "Developpement Web", credits: 4, dept: "Informatique"},
  {code: "INFO404", intitule: "Systemes Distribues", credits: 5, dept: "Informatique"},
  {code: "INFO405", intitule: "Cloud Computing", credits: 4, dept: "Informatique"},
  {code: "INFO406", intitule: "Algorithmique Avancee", credits: 5, dept: "Informatique"},
  {code: "MATH301", intitule: "Statistiques", credits: 4, dept: "Mathematiques"},
  {code: "ELT201", intitule: "Circuits Electroniques", credits: 5, dept: "Electronique"},
  {code: "TLC301", intitule: "Telecoms Mobiles", credits: 4, dept: "Telecoms"},
  {code: "GL401", intitule: "Genie Logiciel", credits: 5, dept: "GL"}
] AS cours
MERGE (:Cours {code: cours.code, intitule: cours.intitule, 
               credits: cours.credits, departement: cours.dept});

// ─── 1.4 : Creer les clubs ────────────────────────────────────────────────────
UNWIND [
  {nom: "Club IA USTHB", universite: "USTHB", domaine: "Intelligence Artificielle"},
  {nom: "GDG Algiers", universite: "USTHB", domaine: "Tech"},
  {nom: "Robotics Club UMBB", universite: "UMBB", domaine: "Robotique"},
  {nom: "Enactus USTO", universite: "USTO", domaine: "Entrepreneuriat"},
  {nom: "IEEE UMC", universite: "UMC", domaine: "Electronique"},
  {nom: "DevClub USTHB", universite: "USTHB", domaine: "Developpement"},
  {nom: "CyberSec DZ", universite: "USTO", domaine: "Securite"},
  {nom: "AI Hub Annaba", universite: "UBMA", domaine: "Intelligence Artificielle"}
] AS club
MERGE (:Club {nom: club.nom, universite: club.universite, domaine: club.domaine});

// ─── 1.5 : Creer les entreprises ──────────────────────────────────────────────
UNWIND [
  {nom: "Sonatrach", secteur: "Petrole", ville: "Alger"},
  {nom: "Djezzy", secteur: "Telecom", ville: "Alger"},
  {nom: "Air Algerie", secteur: "Transport", ville: "Alger"},
  {nom: "Microsoft Algeria", secteur: "Tech", ville: "Alger"},
  {nom: "Ooredoo", secteur: "Telecom", ville: "Alger"},
  {nom: "IBM Algeria", secteur: "Tech", ville: "Alger"},
  {nom: "Oracle Algeria", secteur: "Tech", ville: "Alger"},
  {nom: "Groupe CEVITAL", secteur: "Agroalimentaire", ville: "Alger"}
] AS entreprise
MERGE (:Entreprise {nom: entreprise.nom, secteur: entreprise.secteur, ville: entreprise.ville});

// ─── 1.6 : Creer les etudiants ────────────────────────────────────────────────
UNWIND [
  // USTHB - Alger (Informatique)
  {id: "E001", prenom: "Ahmed", nom: "Bensalem", universite: "USTHB", filiere: "Informatique", annee: 3, ville: "Alger"},
  {id: "E002", prenom: "Fatima", nom: "Ouali", universite: "USTHB", filiere: "Informatique", annee: 3, ville: "Alger"},
  {id: "E003", prenom: "Mohamed", nom: "Mehdi", universite: "USTHB", filiere: "Informatique", annee: 2, ville: "Alger"},
  {id: "E004", prenom: "Nassima", nom: "Touati", universite: "USTHB", filiere: "GL", annee: 3, ville: "Alger"},
  {id: "E005", prenom: "Karim", nom: "Ferhat", universite: "USTHB", filiere: "Informatique", annee: 1, ville: "Alger"},
  {id: "E006", prenom: "Sofia", nom: "Boukhelifa", universite: "USTHB", filiere: "GL", annee: 2, ville: "Alger"},
  {id: "E007", prenom: "Yacine", nom: "Mansouri", universite: "USTHB", filiere: "Mathematiques", annee: 3, ville: "Alger"},
  {id: "E008", prenom: "Amira", nom: "Boudiaf", universite: "USTHB", filiere: "Informatique", annee: 2, ville: "Alger"},
  {id: "E009", prenom: "Rachid", nom: "Slimani", universite: "USTHB", filiere: "Electronique", annee: 3, ville: "Alger"},
  {id: "E010", prenom: "Leila", nom: "Cherif", universite: "USTHB", filiere: "Informatique", annee: 1, ville: "Alger"},
  {id: "E011", prenom: "Hakim", nom: "Zidane", universite: "USTHB", filiere: "Telecoms", annee: 2, ville: "Alger"},
  {id: "E012", prenom: "Nadia", nom: "Kaci", universite: "USTHB", filiere: "Informatique", annee: 3, ville: "Alger"},
  {id: "E013", prenom: "Samir", nom: "Hadjadj", universite: "USTHB", filiere: "GL", annee: 1, ville: "Alger"},
  {id: "E014", prenom: "Karima", nom: "Bouderbala", universite: "USTHB", filiere: "Informatique", annee: 2, ville: "Alger"},
  {id: "E015", prenom: "Fouad", nom: "Ait Yahia", universite: "USTHB", filiere: "Telecoms", annee: 3, ville: "Alger"},
  
  // UMBB - Boumerdes
  {id: "E016", prenom: "Yasmina", nom: "Ali", universite: "UMBB", filiere: "Informatique", annee: 3, ville: "Boumerdes"},
  {id: "E017", prenom: "Samir", nom: "Bouaziz", universite: "UMBB", filiere: "GL", annee: 2, ville: "Boumerdes"},
  {id: "E018", prenom: "Nadia", nom: "Hamidi", universite: "UMBB", filiere: "Electronique", annee: 3, ville: "Boumerdes"},
  {id: "E019", prenom: "Hichem", nom: "Mebarki", universite: "UMBB", filiere: "Informatique", annee: 1, ville: "Boumerdes"},
  {id: "E020", prenom: "Wassila", nom: "Gherbi", universite: "UMBB", filiere: "Telecoms", annee: 2, ville: "Boumerdes"},
  {id: "E021", prenom: "Rafik", nom: "Mokhtari", universite: "UMBB", filiere: "Informatique", annee: 3, ville: "Boumerdes"},
  {id: "E022", prenom: "Djamila", nom: "Said", universite: "UMBB", filiere: "Mathematiques", annee: 2, ville: "Boumerdes"},
  {id: "E023", prenom: "Tahar", nom: "Belkacem", universite: "UMBB", filiere: "GL", annee: 3, ville: "Boumerdes"},
  {id: "E024", prenom: "Zohra", nom: "Boukhedimi", universite: "UMBB", filiere: "Informatique", annee: 1, ville: "Boumerdes"},
  {id: "E025", prenom: "Abdenour", nom: "Khelifi", universite: "UMBB", filiere: "Telecoms", annee: 3, ville: "Boumerdes"},
  
  // USTO - Oran
  {id: "E026", prenom: "Omar", nom: "Belkacem", universite: "USTO", filiere: "Informatique", annee: 3, ville: "Oran"},
  {id: "E027", prenom: "Zahra", nom: "Medjber", universite: "USTO", filiere: "Electronique", annee: 2, ville: "Oran"},
  {id: "E028", prenom: "Abdel", nom: "Khaldi", universite: "USTO", filiere: "GL", annee: 3, ville: "Oran"},
  {id: "E029", prenom: "Meriem", nom: "Benziane", universite: "USTO", filiere: "Informatique", annee: 1, ville: "Oran"},
  {id: "E030", prenom: "Fouad", nom: "Zerrouki", universite: "USTO", filiere: "Telecoms", annee: 2, ville: "Oran"},
  {id: "E031", prenom: "Latifa", nom: "Mansouri", universite: "USTO", filiere: "Informatique", annee: 3, ville: "Oran"},
  {id: "E032", prenom: "Mokhtar", nom: "Guechi", universite: "USTO", filiere: "Mathematiques", annee: 2, ville: "Oran"},
  {id: "E033", prenom: "Assia", nom: "Boutaleb", universite: "USTO", filiere: "GL", annee: 1, ville: "Oran"},
  {id: "E034", prenom: "Kamal", nom: "Benyahia", universite: "USTO", filiere: "Informatique", ann
