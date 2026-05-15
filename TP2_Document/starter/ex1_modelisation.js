// ============================================
// EX1: Modelisation et Insertion
// ============================================

db.createCollection("patients", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["cin", "nom", "prenom", "dateNaissance", "sexe", "adresse"],
      properties: {
        cin: {
          bsonType: "string",
          pattern: "^[0-9]{12}$"
        },
        nom: { bsonType: "string", minLength: 2 },
        prenom: { bsonType: "string", minLength: 2 },
        dateNaissance: { bsonType: "date" },
        sexe: { enum: ["M", "F"] },
        adresse: {
          bsonType: "object",
          required: ["wilaya", "commune"],
          properties: {
            wilaya: { bsonType: "string" },
            commune: { bsonType: "string" }
          }
        },
        groupeSanguin: {
          enum: ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
        },
        antecedents: { bsonType: "array" },
        allergies: { bsonType: "array" },
        consultations: { bsonType: "array" }
      }
    }
  }
});

db.createCollection("analyses", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["patient_id", "date", "type"],
      properties: {
        patient_id: { bsonType: "objectId" },
        date: { bsonType: "date" },
        type: { enum: ["Glycemie", "NFS", "Lipidogramme", "ECG"] },
        resultats: { bsonType: "object" },
        laboratoire: { bsonType: "string" },
        valide: { bsonType: "bool" }
      }
    }
  }
});

// 1.2 Insertion des patients
const patients = [
  {
    cin: "123456789012",
    nom: "Bensalem",
    prenom: "Ahmed",
    dateNaissance: new Date("1965-03-15"),
    sexe: "M",
    adresse: { wilaya: "Alger", commune: "Bab Ezzouar" },
    groupeSanguin: "O+",
    antecedents: ["Diabete type 2", "HTA"],
    allergies: ["Penicilline"],
    consultations: [
      {
        id: UUID(),
        date: new Date("2024-01-15"),
        medecin: { nom: "Dr. Mansouri", specialite: "Cardiologie" },
        diagnostic: "Hypertension arterielle",
        tension: { systolique: 145, diastolique: 92 },
        medicaments: [
          { nom: "Amlodipine", dosage: "5mg", duree: "30 jours" }
        ]
      },
      {
        id: UUID(),
        date: new Date("2024-03-20"),
        medecin: { nom: "Dr. Mansouri", specialite: "Cardiologie" },
        diagnostic: "Controle HTA",
        tension: { systolique: 135, diastolique: 85 },
        medicaments: [
          { nom: "Amlodipine", dosage: "5mg", duree: "60 jours" }
        ]
      }
    ]
  },
  {
    cin: "234567890123",
    nom: "Kadri",
    prenom: "Fatima",
    dateNaissance: new Date("1972-07-22"),
    sexe: "F",
    adresse: { wilaya: "Oran", commune: "Es Senia" },
    groupeSanguin: "A+",
    antecedents: ["Asthme"],
    allergies: ["Arachides"],
    consultations: [
      {
        id: UUID(),
        date: new Date("2024-02-10"),
        medecin: { nom: "Dr. Benali", specialite: "Pneumologie" },
        diagnostic: "Crise d'asthme",
        medicaments: [
          { nom: "Ventoline", dosage: "100mcg", duree: "7 jours" }
        ]
      }
    ]
  },
  {
    cin: "345678901234",
    nom: "Mehdi",
    prenom: "Sofiane",
    dateNaissance: new Date("1980-11-05"),
    sexe: "M",
    adresse: { wilaya: "Constantine", commune: "El Khroub" },
    groupeSanguin: "B+",
    antecedents: [],
    allergies: [],
    consultations: [
      {
        id: UUID(),
        date: new Date("2024-01-05"),
        medecin: { nom: "Dr. Cherif", specialite: "Generaliste" },
        diagnostic: "Grippe saisonniere",
        tension: { systolique: 120, diastolique: 80 },
        medicaments: [
          { nom: "Paracetamol", dosage: "500mg", duree: "5 jours" }
        ]
      },
      {
        id: UUID(),
        date: new Date("2024-02-18"),
        medecin: { nom: "Dr. Cherif", specialite: "Generaliste" },
        diagnostic: "Angine bacterienne",
        medicaments: [
          { nom: "Amoxicilline", dosage: "1g", duree: "7 jours" }
        ]
      },
      {
        id: UUID(),
        date: new Date("2024-03-25"),
        medecin: { nom: "Dr. Nouar", specialite: "ORL" },
        diagnostic: "Otite moyenne",
        medicaments: [
          { nom: "Augmentin", dosage: "1g", duree: "10 jours" }
        ]
      }
    ]
  },
  {
    cin: "456789012345",
    nom: "Touati",
    prenom: "Nassima",
    dateNaissance: new Date("1990-09-30"),
    sexe: "F",
    adresse: { wilaya: "Blida", commune: "Boufarik" },
    groupeSanguin: "AB+",
    antecedents: ["Migraine chronique"],
    allergies: [],
    consultations: [
      {
        id: UUID(),
        date: new Date("2024-01-20"),
        medecin: { nom: "Dr. Slimani", specialite: "Neurologie" },
        diagnostic: "Migraine avec aura",
        medicaments: [
          { nom: "Ibuprofene", dosage: "400mg", duree: "3 jours" }
        ]
      }
    ]
  },
  {
    cin: "567890123456",
    nom: "Ferhat",
    prenom: "Lyes",
    dateNaissance: new Date("1975-12-12"),
    sexe: "M",
    adresse: { wilaya: "Setif", commune: "El Eulma" },
    groupeSanguin: "O-",
    antecedents: ["Diabete type 2", "Cholesterol", "HTA"],
    allergies: ["Sulfamides"],
    consultations: [
      {
        id: UUID(),
        date: new Date("2024-01-10"),
        medecin: { nom: "Dr. Mansouri", specialite: "Cardiologie" },
        diagnostic: "Bilan cardiovasculaire",
        tension: { systolique: 150, diastolique: 95 },
        medicaments: [
          { nom: "Ramipril", dosage: "10mg", duree: "90 jours" },
          { nom: "Simvastatine", dosage: "20mg", duree: "90 jours" }
        ]
      },
      {
        id: UUID(),
        date: new Date("2024-02-25"),
        medecin: { nom: "Dr. Mansouri", specialite: "Cardiologie" },
        diagnostic: "Diabete desequilibre",
        tension: { systolique: 148, diastolique: 92 },
        medicaments: [
          { nom: "Metformine", dosage: "1000mg", duree: "60 jours" }
        ]
      },
      {
        id: UUID(),
        date: new Date("2024-04-05"),
        medecin: { nom: "Dr. Nouar", specialite: "Endocrinologie" },
        diagnostic: "Controle diabetique",
        tension: { systolique: 142, diastolique: 88 },
        medicaments: [
          { nom: "Metformine", dosage: "1000mg", duree: "90 jours" }
        ]
      }
    ]
  }
];

db.patients.insertMany(patients);

// 1.3 Insertion des analyses
const patientList = db.patients.find({}).toArray();

const analyses = [
  {
    patient_id: patientList[0]._id,
    date: new Date("2024-01-16"),
    type: "Glycemie",
    resultats: { valeur: 1.45, unite: "g/L", normale: "0.70-1.10" },
    laboratoire: "Labo Central Alger",
    valide: true
  },
  {
    patient_id: patientList[0]._id,
    date: new Date("2024-03-21"),
    type: "Lipidogramme",
    resultats: { cholesterol: 2.2, triglycerides: 1.8, hdl: 0.45, ldl: 1.4 },
    laboratoire: "Labo Central Alger",
    valide: true
  },
  {
    patient_id: patientList[1]._id,
    date: new Date("2024-02-11"),
    type: "NFS",
    resultats: { globulesBlancs: 11.5, hematies: 4.2, plaquettes: 250 },
    laboratoire: "Labo Es Senia",
    valide: true
  },
  {
    patient_id: patientList[2]._id,
    date: new Date("2024-01-06"),
    type: "Glycemie",
    resultats: { valeur: 0.95, unite: "g/L", normale: "0.70-1.10" },
    laboratoire: "Labo El Khroub",
    valide: true
  },
  {
    patient_id: patientList[4]._id,
    date: new Date("2024-01-11"),
    type: "Glycemie",
    resultats: { valeur: 1.82, unite: "g/L", normale: "0.70-1.10" },
    laboratoire: "Labo Setif",
    valide: true
  },
  {
    patient_id: patientList[4]._id,
    date: new Date("2024-02-26"),
    type: "Lipidogramme",
    resultats: { cholesterol: 2.8, triglycerides: 2.2, hdl: 0.38, ldl: 1.9 },
    laboratoire: "Labo Setif",
    valide: true
  },
  {
    patient_id: patientList[4]._id,
    date: new Date("2024-04-06"),
    type: "Glycemie",
    resultats: { valeur: 1.68, unite: "g/L", normale: "0.70-1.10" },
    laboratoire: "Labo Setif",
    valide: false
  }
];

db.analyses.insertMany(analyses);

print("Base de donnees initialisee avec " + db.patients.countDocuments() + " patients");
print("et " + db.analyses.countDocuments() + " analyses");
