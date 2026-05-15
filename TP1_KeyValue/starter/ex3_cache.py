"""
TP1 - Exercice 3 : Pattern Cache-Aside avec TTL
Mesure des hits vs misses et invalidation
"""
import redis
import json
import time

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Statistiques globales
cache_stats = {'hits': 0, 'misses': 0}

# Simulation d'une base de données
fake_db = {
    '1': {'id': '1', 'name': 'Samsung A54', 'price': 65000, 'stock': 15},
    '2': {'id': '2', 'name': 'Laptop HP', 'price': 120000, 'stock': 8},
    '3': {'id': '3', 'name': 'iPhone 15', 'price': 150000, 'stock': 5},
}


def get_product_with_cache(r, product_id, ttl=3600):
    """
    Pattern Cache-Aside :
    1. Vérifier Redis
    2. Si présent (HIT) → retourner
    3. Si absent (MISS) → chercher DB → stocker → retourner
    """
    key = f"cache:product:{product_id}"
    
    # 1. Vérifier le cache
    cached = r.get(key)
    
    if cached:
        # CACHE HIT ✅
        cache_stats['hits'] += 1
        return json.loads(cached)
    
    # CACHE MISS ❌
    cache_stats['misses'] += 1
    
    # 2. Chercher en DB (simulée)
    time.sleep(0.1)  # Simule le temps de réponse DB
    product = fake_db.get(product_id)
    
    if product:
        # 3. Stocker dans Redis avec TTL
        r.setex(key, ttl, json.dumps(product))
    
    return product


def invalidate_cache(r, product_id):
    """Invalider le cache pour un produit"""
    key = f"cache:product:{product_id}"
    return bool(r.delete(key))


def update_product(r, product_id, product_data):
    """
    Mettre à jour un produit :
    1. Mettre à jour la DB
    2. Invalider le cache
    """
    # 1. Mettre à jour la DB
    fake_db[product_id] = product_data
    
    # 2. Invalider le cache
    invalidate_cache(r, product_id)
    return True


def get_cache_stats():
    """Retourner les statistiques cache hit/miss"""
    total = cache_stats['hits'] + cache_stats['misses']
    hit_rate = (cache_stats['hits'] / total * 100) if total > 0 else 0
    
    return {
        'hits': cache_stats['hits'],
        'misses': cache_stats['misses'],
        'total': total,
        'hit_rate': round(hit_rate, 2)
    }


def reset_cache_stats():
    """Réinitialiser les statistiques"""
    cache_stats['hits'] = 0
    cache_stats['misses'] = 0
