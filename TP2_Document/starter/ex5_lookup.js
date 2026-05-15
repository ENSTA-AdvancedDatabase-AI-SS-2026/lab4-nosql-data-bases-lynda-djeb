// ============================================
// EX5: $lookup et jointures
// ============================================

// 5.1 Dossier complet d'un patient avec ses analyses
const patientId = db.patients.findOne({ nom: "Ferhat" })._id;

db.patients.aggregate([
  { $match: { _id: patientId } },
  {
    $lookup: {
      from: "analyses",
      localField: "_id",
      foreignField: "patient_id",
      as: "analyses_completes"
    }
  },
  {
    $project: {
      nom: 1,
      prenom: 1,
      consultations: 1,
      analyses_completes: {
        $map: {
          input: "$analyses_completes",
          as: "a",
          in: {
            date: "$$a.date",
            type: "$$a.type",
            resultats: "$$a.resultats",
            valide: "$$a.valide"
          }
        }
      }
    }
  }
]).pretty();

// 5.2 Patients dont la glycemie depasse 1.26 g/L
db.analyses.aggregate([
  {
    $match: {
      type: "Glycemie",
      "resultats.valeur": { $gt: 1.26 }
    }
  },
  {
    $lookup: {
      from: "patients",
      localField: "patient_id",
      foreignField: "_id",
      as: "patient"
    }
  },
  { $unwind: "$patient" },
  {
    $project: {
      _id: 0,
      patient_nom: "$patient.nom",
      patient_prenom: "$patient.prenom",
      glycemie: "$resultats.valeur",
      date_analyse: "$date"
    }
  }
]).pretty();

// 5.3 Taux d'analyses anormales par wilaya
db.analyses.aggregate([
  {
    $lookup: {
      from: "patients",
      localField: "patient_id",
      foreignField: "_id",
      as: "patient"
    }
  },
  { $unwind: "$patient" },
  {
    $addFields: {
      anormale: {
        $cond: {
          if: {
            $or: [
              { $and: [
                { $eq: ["$type", "Glycemie"] },
                { $or: [
                  { $lt: ["$resultats.valeur", 0.70] },
                  { $gt: ["$resultats.valeur", 1.10] }
                ]}
              ]},
              { $and: [
                { $eq: ["$type", "Lipidogramme"] },
                { $gt: ["$resultats.cholesterol", 2.0] }
              ]}
            ]
          },
          then: 1,
          else: 0
        }
      }
    }
  },
  {
    $group: {
      _id: "$patient.adresse.wilaya",
      total_analyses: { $sum: 1 },
      analyses_anormales: { $sum: "$anormale" }
    }
  },
  {
    $project: {
      wilaya: "$_id",
      total_analyses: 1,
      analyses_anormales: 1,
      taux_anormalite: {
        $round: [
          { $multiply: [{ $divide: ["$analyses_anormales", "$total_analyses"] }, 100] },
          1
        ]
      },
      _id: 0
    }
  },
  { $sort: { taux_anormalite: -1 } }
]);
