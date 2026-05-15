"""
TP1 - Exercice 4 : Classement des ventes temps réel
Utilisation des Sorted Sets
"""
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


def record_sale(r, product_id, quantity=1):
    """
    Enregistrer une vente dans les classements
    Mettre à jour : daily, weekly, all_time
    """
    # ZINCRBY - Incrémente le score (nombre de ventes)
    r.zincrby("leaderboard:daily", quantity, product_id)
    r.zincrby("leaderboard:weekly", quantity, product_id)
    r.zincrby("leaderboard:all_time", quantity, product_id)
    
    # Expiration pour éviter accumulation
    r.expire("leaderboard:daily", 86400)   # 24h
    r.expire("leaderboard:weekly", 604800)  # 7 jours


def get_top_products(r, period, limit=10):
    """
    Récupérer le top N produits pour une période
    period: 'daily', 'weekly', 'all_time'
    Retourne liste de tuples (product_id, score)
    """
    key = f"leaderboard:{period}"
    # ZREVRANGE - Tri décroissant (plus haut score d'abord)
    return r.zrevrange(key, 0, limit - 1, withscores=True)


def get_product_rank(r, product_id, period):
    """
    Obtenir le rang d'un produit (1 = meilleur)
    Retourner None si produit non classé
    """
    key = f"leaderboard:{period}"
    # ZREVRANK - Position (0 = premier)
    rank = r.zrevrank(key, product_id)
    
    if rank is not None:
        return rank + 1  # +1 pour conversion 1-indexed
    return None


def get_product_score(r, product_id, period):
    """Obtenir le score (nombre de ventes) d'un produit"""
    key = f"leaderboard:{period}"
    score = r.zscore(key, product_id)
    return float(score) if score else 0.0


def get_category_leaderboard(r, category, limit=10):
    """
    Classement par catégorie
    """
    key = f"leaderboard:category:{category}"
    return r.zrevrange(key, 0, limit - 1, withscores=True)


def record_category_sale(r, category, product_id, quantity=1):
    """Enregistrer une vente dans une catégorie spécifique"""
    key = f"leaderboard:category:{category}"
    r.zincrby(key, quantity, product_id)
    r.expire(key, 2592000)  # 30 jours
