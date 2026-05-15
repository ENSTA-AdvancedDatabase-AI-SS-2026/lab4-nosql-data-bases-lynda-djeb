// ============================================
// EX4: Index et optimisation
// ============================================

// 4.1 Creation des index

// Pour recherche par wilaya
db.patients.createIndex({ "adresse.wilaya": 1 });

// Pour recherche par antecedents
db.patients.createIndex({ antecedents: 1 });

// Pour recherche par age
db.patients.createIndex({ dateNaissance: -1 });

// Pour recherche textuelle sur diagnostics
db.patients.createIndex({ "consultations.diagnostic": "text" });

// Pour recherche par medecin
db.patients.createIndex({ "consultations.medecin.nom": 1 });

// Pour recherche par date de consultation
db.patients.createIndex({ "consultations.date": -1 });

// 4.2 Comparaison SANS index vs AVEC index

// SANS INDEX (desactiver l'index pour test)
print("=== REQUETE SANS INDEX ===");
db.patients.getIndexes().forEach(idx => {
  if (idx.name !== "_id_") db.patients.dropIndex(idx.name);
});

db.patients.find({
  "adresse.wilaya": "Alger",
  antecedents: "Diabete type 2"
}).explain("executionStats");

// AVEC INDEX
print("\n=== REQUETE AVEC INDEX ===");
db.patients.createIndex({ "adresse.wilaya": 1, antecedents: 1 });

db.patients.find({
  "adresse.wilaya": "Alger",
  antecedents: "Diabete type 2"
}).explain("executionStats");

// 4.3 Index compose pour requete complexe
db.patients.createIndex({
  "adresse.wilaya": 1,
  antecedents: 1,
  dateNaissance: -1
});

// 4.4 Index TTL pour archiver analyses de plus de 5 ans
db.analyses.createIndex(
  { date: 1 },
  { expireAfterSeconds: 157680000 }
);

print("\n=== INDEX ACTIFS ===");
db.patients.getIndexes().forEach(printjson);
