"""
TP1 - Exercice 1 : Structures de données Redis
Use Case : ShopFast - Gestion des produits, paniers et navigation
"""
import redis
import json

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


def store_product(r, product_id, product_data: dict):
    """
    Stocker un produit comme Hash Redis
    Clé : "product:{product_id}"
    Champs : name, price, category, stock
    
    >>> store_product(r, 1, {"name": "Samsung A54", "price": 65000, "category": "phones", "stock": 15})
    """
    # Créer la clé unique pour ce produit
    key = f"product:{product_id}"
    
    # HSET: stocke un dictionnaire dans un hash Redis
    r.hset(key, mapping=product_data)
    
    # Optionnel: ajouter un TTL (expiration après 1 heure)
    r.expire(key, 3600)


def get_product(r, product_id):
    """
    Récupérer un produit par son ID
    Retourner None si le produit n'existe pas
    """
    key = f"product:{product_id}"
    
    # HGETALL: récupère tout le hash
    product = r.hgetall(key)
    
    # Retourne le produit ou None si pas trouvé
    return product if product else None


def add_to_cart(r, user_id, product_id, quantity: int = 1):
    """
    Ajouter/incrémenter un produit dans le panier
    Clé : "cart:{user_id}"
    Champ : product_id → quantité
    """
    key = f"cart:{user_id}"
    
    # HINCRBY: incrémente atomiquement la quantité
    # Si le champ n'existe pas, il est créé avec valeur = quantity
    r.hincrby(key, product_id, quantity)
    
    # TTL: le panier expire après 2 heures (7200 secondes)
    r.expire(key, 7200)


def get_cart(r, user_id):
    """
    Récupérer tout le contenu du panier d'un utilisateur
    Retourner un dict {product_id: quantity}
    """
    key = f"cart:{user_id}"
    
    # HGETALL: retourne tous les produits du panier
    cart = r.hgetall(key)
    
    # Convertir les quantités de string vers int
    return {prod_id: int(qty) for prod_id, qty in cart.items()}


def record_view(r, user_id, product_id, max_history: int = 10):
    """
    Enregistrer un produit vu par l'utilisateur
    Clé : "history:{user_id}" (List)
    Garder seulement les max_history derniers produits
    Astuce : LPUSH + LTRIM
    """
    key = f"history:{user_id}"
    
    # LPUSH: ajoute le produit au DÉBUT de la liste
    # Les produits récents sont donc en première position
    r.lpush(key, product_id)
    
    # LTRIM: garde seulement les N premiers éléments (les plus récents)
    # 0 à max_history-1 = les max_history derniers produits
    r.ltrim(key, 0, max_history - 1)
    
    # TTL: l'historique expire après 7 jours
    r.expire(key, 604800)


def get_history(r, user_id):
    """Récupérer l'historique de navigation"""
    key = f"history:{user_id}"
    
    # LRANGE 0, -1 récupère TOUS les éléments
    # Retourne une liste du plus récent au plus ancien
    return r.lrange(key, 0, -1)


def add_product_to_category(r, category: str, product_id):
    """
    Associer un produit à une catégorie
    Clé : "category:{category}" (Set)
    """
    key = f"category:{category}"
    
    # SADD: ajoute le produit au set
    # Si le produit existe déjà, pas de doublon
    r.sadd(key, product_id)
    
    # TTL: la catégorie expire après 24 heures
    r.expire(key, 86400)


def get_products_in_categories(r, *categories):
    """
    Récupérer les produits appartenant à TOUTES les catégories données
    Ex: produits qui sont à la fois "electronics" ET "promo"
    Astuce : SINTER
    """
    # Construire les clés pour chaque catégorie
    keys = [f"category:{cat}" for cat in categories]
    
    # SINTER: intersection des sets
    # Retourne les produits présents dans TOUTES les catégories
    if keys:
        return r.sinter(keys)
    return set()


if __name__ == "__main__":
    # Test manuel
    r.flushdb()  # Nettoyer pour les tests
    
    print("=== TEST EXERCICE 1 ===\n")
    
    # 1. Stocker quelques produits
    print("1. Stockage des produits:")
    store_product(r, 1, {"name": "Samsung A54", "price": "65000", "category": "phones", "stock": "15"})
    store_product(r, 2, {"name": "Laptop HP", "price": "120000", "category": "laptops", "stock": "8"})
    store_product(r, 3, {"name": "iPhone 15", "price": "150000", "category": "phones", "stock": "5"})
    print("   ✓ 3 produits stockés\n")
    
    # 2. Récupérer un produit
    print("2. Récupération d'un produit:")
    product = get_product(r, 1)
    print(f"   Produit 1: {product}\n")
    
    # 3. Tester le panier
    print("3. Gestion du panier:")
    add_to_cart(r, "user:42", 1, 2)  # 2 x Samsung A54
    add_to_cart(r, "user:42", 2, 1)  # 1 x Laptop HP
    add_to_cart(r, "user:42", 1, 1)  # +1 Samsung A54 (total 3)
    cart = get_cart(r, "user:42")
    print(f"   Panier: {cart}\n")
    
    # 4. Tester l'historique
    print("4. Historique de navigation:")
    views = [1, 2, 3, 1, 2, 3, 3, 1, 2]  # Produits visités dans l'ordre
    for pid in views:
        record_view(r, "user:42", pid)
    history = get_history(r, "user:42")
    print(f"   Derniers produits vus: {history}\n")
    
    # 5. Tester les catégories
    print("5. Catégories:")
    add_product_to_category(r, "phones", 1)
    add_product_to_category(r, "phones", 3)
    add_product_to_category(r, "laptops", 2)
    add_product_to_category(r, "promo", 1)  # Samsung en promo
    
    # Produits dans "phones"
    phones = r.smembers("category:phones")
    print(f"   Produits dans 'phones': {phones}")
    
    # Intersection: produits dans phones ET promo
    common = get_products_in_categories(r, "phones", "promo")
    print(f"   Produits dans 'phones' ET 'promo': {common}\n")
    
    print("=== FIN DU TEST ===")
