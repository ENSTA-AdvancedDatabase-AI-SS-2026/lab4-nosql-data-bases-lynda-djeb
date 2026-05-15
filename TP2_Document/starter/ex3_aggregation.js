// ============================================
// EX3: Pipelines d'agregation
// ============================================

// 3.1 Distribution des diagnostics par wilaya
db.patients.aggregate([
  { $unwind: "$consultations" },
  {
    $group: {
      _id: {
        wilaya: "$adresse.wilaya",
        diagnostic: "$consultations.diagnostic"
      },
      count: { $sum: 1 }
    }
  },
  { $sort: { "_id.wilaya": 1, count: -1 } },
  {
    $group: {
      _id: "$_id.wilaya",
      diagnostics: {
        $push: {
          diagnostic: "$_id.diagnostic",
          count: "$count"
        }
      }
    }
  },
  { $project: { wilaya: "$_id", diagnostics: 1, _id: 0 } }
]);

// 3.2 Medicament le plus prescrit par specialite medicale
db.patients.aggregate([
  { $unwind: "$consultations" },
  { $unwind: "$consultations.medicaments" },
  {
    $group: {
      _id: {
        specialite: "$consultations.medecin.specialite",
        medicament: "$consultations.medicaments.nom"
      },
      count: { $sum: 1 }
    }
  },
  { $sort: { "_id.specialite": 1, count: -1 } },
  {
    $group: {
      _id: "$_id.specialite",
      top_medicament: { $first: "$_id.medicament" },
      prescriptions: { $first: "$count" }
    }
  },
  { $project: { specialite: "$_id", top_medicament: 1, prescriptions: 1, _id: 0 } }
]);

// 3.3 Evolution mensuelle des consultations sur 12 mois
db.patients.aggregate([
  { $unwind: "$consultations" },
  {
    $match: {
      "consultations.date": {
        $gte: new Date(new Date().setMonth(new Date().getMonth() - 11))
      }
    }
  },
  {
    $group: {
      _id: {
        annee: { $year: "$consultations.date" },
        mois: { $month: "$consultations.date" }
      },
      nombreConsultations: { $sum: 1 }
    }
  },
  { $sort: { "_id.annee": 1, "_id.mois": 1 } },
  {
    $project: {
      mois: {
        $concat: [
          { $toString: "$_id.annee" },
          "-",
          { $toString: "$_id.mois" }
        ]
      },
      nombreConsultations: 1,
      _id: 0
    }
  }
]);

// 3.4 Patients à risque: diabetiques + HTA + age > 60
db.patients.aggregate([
  {
    $match: {
      antecedents: { $all: ["Diabete type 2", "HTA"] },
      dateNaissance: { $lte: new Date(new Date().setFullYear(new Date().getFullYear() - 60)) }
    }
  },
  {
    $project: {
      nom: 1,
      prenom: 1,
      age: {
        $floor: {
          $divide: [
            { $subtract: [new Date(), "$dateNaissance"] },
            31536000000
          ]
        }
      },
      nbConsultations: { $size: "$consultations" }
    }
  },
  {
    $group: {
      _id: null,
      patients_risque: { $push: { nom: "$nom", prenom: "$prenom", age: "$age" } },
      consultations_moyennes: { $avg: "$nbConsultations" },
      total_patients: { $sum: 1 }
    }
  },
  {
    $project: {
      consultations_moyennes: { $round: ["$consultations_moyennes", 1] },
      patients_risque: 1,
      total_patients: 1,
      _id: 0
    }
  }
]);

// 3.5 Rapport: Top 5 medecins avec taux de re-consultation
db.patients.aggregate([
  { $unwind: "$consultations" },
  {
    $group: {
      _id: {
        medecin: "$consultations.medecin.nom",
        specialite: "$consultations.medecin.specialite",
        patient_id: "$_id"
      },
      visites: { $sum: 1 }
    }
  },
  {
    $group: {
      _id: {
        medecin: "$_id.medecin",
        specialite: "$_id.specialite"
      },
      total_consultations: { $sum: "$visites" },
      patients_uniques: { $sum: 1 },
      patients_avec_reconsultation: {
        $sum: { $cond: [{ $gt: ["$visites", 1] }, 1, 0] }
      }
    }
  },
  {
    $project: {
      medecin: "$_id.medecin",
      specialite: "$_id.specialite",
      total_consultations: 1,
      patients_uniques: 1,
      taux_reconsultation: {
        $multiply: [
          { $divide: ["$patients_avec_reconsultation", "$patients_uniques"] },
          100
        ]
      }
    }
  },
  { $sort: { total_consultations: -1 } },
  { $limit: 5 },
  { $project: { taux_reconsultation: { $round: ["$taux_reconsultation", 1] }, _id: 0 } }
]);
