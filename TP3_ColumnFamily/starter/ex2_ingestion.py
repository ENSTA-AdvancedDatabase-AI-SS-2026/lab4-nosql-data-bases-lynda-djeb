"""
EX2: Ingestion massive de donnees IoT
10 000 capteurs, 5 minutes de mesures
"""

from cassandra.cluster import Cluster
from cassandra.query import BatchStatement, SimpleStatement
from cassandra import ConsistencyLevel
import uuid
import random
import time
from datetime import datetime, timedelta, date
from typing import List, Dict

class SmartGridIngester:
    def __init__(self, hosts=['127.0.0.1'], keyspace='smartgrid'):
        self.cluster = Cluster(hosts)
        self.session = self.cluster.connect()
        self.session.set_keyspace(keyspace)
        
        self.wilayas = ['Alger', 'Oran', 'Constantine', 'Annaba', 'Tizi Ouzou']
        self.prepare_statements()
        
    def prepare_statements(self):
        """Prepare les statements pour insertion rapide"""
        
        self.insert_mesure_capteur = self.session.prepare("""
            INSERT INTO mesures_par_capteur 
            (capteur_id, date, heure, wilaya, tension, courant, puissance, alerte)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """)
        
        self.insert_mesure_wilaya = self.session.prepare("""
            INSERT INTO mesures_par_wilaya 
            (wilaya, date, heure, capteur_id, tension, courant, puissance, alerte)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """)
        
        self.insert_alerte = self.session.prepare("""
            INSERT INTO alertes_par_wilaya 
            (wilaya, date, heure, capteur_id, tension, courant, puissance, message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """)
        
    def generate_capteurs(self, nb_capteurs: int = 10000) -> List[uuid.UUID]:
        """Genere des IDs de capteurs"""
        capteurs = []
        for i in range(nb_capteurs):
            capteur_id = uuid.uuid4()
            capteurs.append(capteur_id)
            
            wilaya = random.choice(self.wilayas)
            self.session.execute(
                "INSERT INTO capteurs_par_wilaya (wilaya, capteur_id, date_activation, dernier_contact) VALUES (%s, %s, %s, %s)",
                (wilaya, capteur_id, date.today(), datetime.now())
            )
        
        return capteurs
    
    def generer_mesure(self, capteur_id: uuid.UUID, timestamp: datetime, wilaya: str) -> Dict:
        """Genere une mesure aleatoire realiste"""
        
        base_tension = 220.0
        tension = base_tension + random.uniform(-15, 15)
        
        if random.random() < 0.05:
            tension = base_tension + random.uniform(-30, 30)
        
        courant = random.uniform(0.5, 50.0)
        puissance = tension * courant / 1000
        
        alerte = (tension < 200 or tension > 240 or puissance > 15)
        
        return {
            'capteur_id': capteur_id,
            'timestamp': timestamp,
            'wilaya': wilaya,
            'tension': round(tension, 1),
            'courant': round(courant, 2),
            'puissance': round(puissance, 2),
            'alerte': alerte
        }
    
    def inserer_mesure(self, mesure: Dict):
        """Insere une mesure dans les tables"""
        
        date_val = mesure['timestamp'].date()
        
        self.session.execute(
            self.insert_mesure_capteur,
            (mesure['capteur_id'], date_val, mesure['timestamp'], 
             mesure['wilaya'], mesure['tension'], mesure['courant'], 
             mesure['puissance'], mesure['alerte'])
        )
        
        self.session.execute(
            self.insert_mesure_wilaya,
            (mesure['wilaya'], date_val, mesure['timestamp'],
             mesure['capteur_id'], mesure['tension'], mesure['courant'],
             mesure['puissance'], mesure['alerte'])
        )
        
        if mesure['alerte']:
            message = f"Tension anormale: {mesure['tension']}V"
            self.session.execute(
                self.insert_alerte,
                (mesure['wilaya'], date_val, mesure['timestamp'],
                 mesure['capteur_id'], mesure['tension'], mesure['courant'],
                 mesure['puissance'], message)
            )
    
    def inserer_batch(self, mesures: List[Dict]):
        """Insere un lot de mesures avec BATCH"""
        
        batch = BatchStatement(consistency_level=ConsistencyLevel.ONE)
        
        for mesure in mesures:
            date_val = mesure['timestamp'].date()
            
            batch.add(self.insert_mesure_capteur, (
                mesure['capteur_id'], date_val, mesure['timestamp'],
                mesure['wilaya'], mesure['tension'], mesure['courant'],
                mesure['puissance'], mesure['alerte']
            ))
            
            batch.add(self.insert_mesure_wilaya, (
                mesure['wilaya'], date_val, mesure['timestamp'],
                mesure['capteur_id'], mesure['tension'], mesure['courant'],
                mesure['puissance'], mesure['alerte']
            ))
            
            if mesure['alerte']:
                message = f"Tension anormale: {mesure['tension']}V"
                batch.add(self.insert_alerte, (
                    mesure['wilaya'], date_val, mesure['timestamp'],
                    mesure['capteur_id'], mesure['tension'], mesure['courant'],
                    mesure['puissance'], message
                ))
        
        self.session.execute(batch)
    
    def generer_donnees_historique(self, capteurs: List[uuid.UUID], minutes: int = 5):
        """Genere et insere des donnees sur plusieurs minutes"""
        
        capteur_wilaya = {}
        for capteur_id in capteurs[:1000]:
            result = self.session.execute(
                "SELECT wilaya FROM capteurs_par_wilaya WHERE capteur_id = %s",
                (capteur_id,)
            )
            row = result.one()
            if row:
                capteur_wilaya[capteur_id] = row.wilaya
        
        start_time = datetime.now() - timedelta(minutes=minutes)
        
        total_mesures = 0
        start_ingest = time.time()
        
        for minute in range(minutes):
            timestamp = start_time + timedelta(minutes=minute)
            batch_mesures = []
            
            for capteur_id in list(capteur_wilaya.keys())[:1000]:
                wilaya = capteur_wilaya[capteur_id]
                mesure = self.generer_mesure(capteur_id, timestamp, wilaya)
                batch_mesures.append(mesure)
                
                if len(batch_mesures) >= 50:
                    self.inserer_batch(batch_mesures)
                    total_mesures += len(batch_mesures)
                    batch_mesures = []
            
            if batch_mesures:
                self.inserer_batch(batch_mesures)
                total_mesures += len(batch_mesures)
            
            print(f"Minute {minute+1}/{minutes}: {len(batch_mesures)} mesures inserees")
        
        elapsed = time.time() - start_ingest
        debit = total_mesures / elapsed
        
        print(f"\n=== STATISTIQUES INGESTION ===")
        print(f"Total mesures: {total_mesures}")
        print(f"Temps total: {elapsed:.2f} secondes")
        print(f"Debit: {debit:.0f} mesures/seconde")
        
        return total_mesures, elapsed, debit
    
    def executer(self, nb_capteurs: int = 1000, minutes: int = 5):
        """Execute l'ingestion complete"""
        
        print("=== SMARTGRID INGESTER ===")
        print(f"Generation de {nb_capteurs} capteurs...")
        capteurs = self.generate_capteurs(nb_capteurs)
        
        print(f"Ingestion sur {minutes} minutes...")
        total, temps, debit = self.generer_donnees_historique(capteurs, minutes)
        
        return {
            'capteurs': nb_capteurs,
            'mesures': total,
            'temps_sec': temps,
            'debit_mesures_sec': debit
        }

if __name__ == "__main__":
    ingester = SmartGridIngester()
    stats = ingester.executer(nb_capteurs=500, minutes=3)
