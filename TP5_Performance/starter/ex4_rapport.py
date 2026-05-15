"""
TP5 - Exercice 4 : Rapport de recommandation
Tableau de decision et analyse
"""

import json
from typing import Dict, List


class RecommendationReport:
    
    def __init__(self):
        self.results = {
            'write': self._load_results('results/write_benchmark.json'),
            'read': self._load_results('results/read_benchmark.json'),
            'load': self._load_results('results/load_test.json')
        }
        
    def _load_results(self, filename: str) -> List[Dict]:
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def generate_table(self) -> str:
        """Genere le tableau de decision"""
        
        # Extraire les metriques
        metrics = {}
        for db in ['Redis', 'MongoDB', 'Cassandra', 'Neo4j']:
            metrics[db] = {
                'write_throughput': self._get_write_throughput(db),
                'read_p50': self._get_read_latency(db, 'point_lookup'),
                'range_p50': self._get_read_latency(db, 'range_query'),
                'complex_p50': self._get_read_latency(db, 'complex_query'),
                'concurrent_ops': self._get_concurrent_throughput(db),
                'use_case': self._get_use_case(db)
            }
            
        table = """
╔══════════════╦═════════╦═════════╦═════════╦═════════╗
║ CRITERE      ║ Redis   ║ MongoDB ║Cassandra║ Neo4j   ║
╠══════════════╬═════════╬═════════╬═════════╬═════════╣
"""
        
        rows = [
            ('Ecriture (rec/s)', 'write_throughput', 'rec/s'),
            ('Lecture point (ms)', 'read_p50', 'ms'),
            ('Range query (ms)', 'range_p50', 'ms'),
            ('Complex query (ms)', 'complex_p50', 'ms'),
            ('Concurrent (ops/s)', 'concurrent_ops', 'ops/s'),
            ('Scalabilite', 'scalability', ''),
            ('Structure', 'structure', ''),
            ('Use case ideal', 'use_case', '')
        ]
        
        for row_name, metric, unit in rows:
            line = f"║ {row_name:<12} ║"
            for db in ['Redis', 'MongoDB', 'Cassandra', 'Neo4j']:
                val = metrics[db].get(metric, 'N/A')
                if isinstance(val, (int, float)):
                    if metric == 'write_throughput':
                        val_str = f"{val:,.0f}"
                    else:
                        val_str = f"{val:.2f}"
                    if unit:
                        val_str += unit
                else:
                    val_str = str(val)[:12]
                line += f" {val_str:<12}║"
            table += line + "\n"
            
        table += "╚══════════════╩═════════════╩═════════════╩═════════════╩═════════════╝"
        
        return table
    
    def _get_write_throughput(self, db: str) -> float:
        for r in self.results.get('write', []):
            if r.get('database') == db:
                return r.get('throughput_records_sec', 0)
        return 0
    
    def _get_read_latency(self, db: str, query_type: str) -> float:
        for r in self.results.get('read', []):
            if r.get('database') == db and r.get('query_type') == query_type:
                return r.get('p50_ms', 0)
        return 0
    
    def _get_concurrent_throughput(self, db: str) -> float:
        for r in self.results.get('load', []):
            if r.get('database') == db:
                return r.get('throughput_ops_sec', 0)
        return 0
    
    def _get_use_case(self, db: str) -> str:
        use_cases = {
            'Redis': 'Cache, Sessions, Compteurs',
            'MongoDB': 'Documents, CMS, Logs',
            'Cassandra': 'IoT, Time Series, Write-heavy',
            'Neo4j': 'Reseaux sociaux, Recommendations'
        }
        return use_cases.get(db, '')
    
    def generate_recommendation(self) -> str:
        """Genere la recommandation finale"""
        
        rec = """
# RAPPORT DE RECOMMANDATION

## Resume des performances

"""
        
        # Analyse des resultats
        best_write = max(self.results.get('write', []), key=lambda x: x.get('throughput_records_sec', 0))
        best_read = min(self.results.get('read', []), key=lambda x: x.get('p50_ms', float('inf')) if x.get('query_type') == 'point_lookup' else float('inf'))
        
        rec += f"""
### Meilleures performances
- **Ecriture**: {best_write.get('database')} - {best_write.get('throughput_records_sec', 0):.0f} rec/s
- **Lecture point**: {best_read.get('database')} - {best_read.get('p50_ms', 0):.2f} ms

### Recommandations par use case

| Use case | Base recommandee | Justification |
|----------|-----------------|---------------|
| Cache / Sessions | Redis | Latence <1ms, TTL natif |
| Catalogue produits | MongoDB | Schema flexible, requetes riches |
| IoT / Logs | Cassandra | Ecriture massive, scaling lineaire |
| Reseau social | Neo4j | Traversales rapides |

### Decision finale

**Pour le produit e-commerce:**
- **Cache**: Redis (produits populaires, sessions)
- **Stockage principal**: MongoDB (catalogue, commandes)
- **Analyse ventes**: Optionnel, export vers Cassandra

**Pour une application de reseau social:**
- **Neo4j** uniquement (tout en un)

**Pour une plateforme IoT:**
- **Cassandra** pour l'ingestion
- **Redis** pour le cache temps reel
"""
        return rec


def generate_final_report():
    """Genere le rapport complet"""
    
    print("\n" + "#"*60)
    print("# RAPPORT DE RECOMMANDATION")
    print("#"*60)
    
    report = RecommendationReport()
    
    print("\n" + report.generate_table())
    print("\n" + report.generate_recommendation())
    
    # Sauvegarde
    with open('results/final_report.md', 'w') as f:
        f.write("# TP5 - Benchmark NoSQL\n\n")
        f.write(report.generate_table())
        f.write("\n\n")
        f.write(report.generate_recommendation())


if __name__ == "__main__":
    generate_final_report()
