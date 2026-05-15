// ============================================
// EX2: Requetes de base
// ============================================

// 2.1 Patients diabetiques de plus de 50 ans à Alger
db.patients.find({
  antecedents: "Diabete type 2",
  dateNaissance: { $lte: new Date(new Date().setFullYear(new Date().getFullYear() - 50)) },
  "adresse.wilaya": "Alger"
}).pretty();

// 2.2 Patients allergiques à la Penicilline avec au moins 3 consultations
db.patients.find({
  allergies: "Penicilline",
  $expr: { $gte: [{ $size: "$consultations" }, 3] }
}).pretty();

// 2.3 Projection: nom, prenom, et derniere consultation seulement
db.patients.find({}, {
  nom: 1,
  prenom: 1,
  derniereConsultation: { $arrayElemAt: ["$consultations", -1] },
  _id: 0
}).pretty();

// 2.4 Patients sans antecedents avec tension systolique > 140 en derniere consultation
db.patients.find({
  antecedents: { $size: 0 },
  $expr: {
    $gt: [
      { $arrayElemAt: ["$consultations.tension.systolique", -1] },
      140
    ]
  }
}).pretty();

// 2.5 Index text sur les diagnostics
db.patients.createIndex({ "consultations.diagnostic": "text" });

db.patients.find({
  $text: { $search: "hypertension grippe" }
}, {
  score: { $meta: "textScore" },
  nom: 1,
  prenom: 1,
  "consultations.diagnostic": 1
}).sort({ score: { $meta: "textScore" } }).pretty();
