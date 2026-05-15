"""
TP1 - Exercice 2 : Gestion des sessions utilisateur
Sliding expiration : 30 minutes
"""
import redis
import uuid
from datetime import datetime

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


def create_session(r, user_id, user_data=None):
    """
    Créer une nouvelle session avec TTL 30 minutes
    Retourner l'identifiant de session
    """
    session_id = str(uuid.uuid4())
    key = f"session:{session_id}"
    
    session_info = {
        'user_id': user_id,
        'created_at': str(datetime.now()),
        'last_access': str(datetime.now())
    }
    
    if user_data:
        session_info.update(user_data)
    
    # HSET - Stocke les données de session
    r.hset(key, mapping=session_info)
    # EXPIRE - TTL 30 minutes
    r.expire(key, 1800)
    
    return session_id


def get_session(r, session_id):
    """
    Récupérer les données d'une session
    Retourner None si la session n'existe pas ou est expirée
    """
    key = f"session:{session_id}"
    
    # Vérifie si la session existe
    if not r.exists(key):
        return None
    
    return r.hgetall(key)


def renew_session(r, session_id):
    """
    Renouveler le TTL d'une session (sliding expiration)
    Retourner True si réussi, False si session inexistante
    """
    key = f"session:{session_id}"
    
    if not r.exists(key):
        return False
    
    # Met à jour le timestamp
    r.hset(key, 'last_access', str(datetime.now()))
    # Remet le TTL à 30 minutes
    r.expire(key, 1800)
    return True


def delete_session(r, session_id):
    """Supprimer une session (déconnexion)"""
    key = f"session:{session_id}"
    return bool(r.delete(key))


def get_session_ttl(r, session_id):
    """Retourner le temps restant de la session en secondes"""
    key = f"session:{session_id}"
    ttl = r.ttl(key)
    return ttl if ttl > 0 else 0
