#!/usr/bin/env python3
# coding: utf-8
"""
Module partagé pour le logging Platon.

Ce module permet d'utiliser platon_log depuis n'importe quelle librairie interne.
Les logs sont stockés en mémoire et récupérés par le runner à la fin de l'exécution.

Usage dans vos librairies:
    from platon_logger import platon_log
    platon_log("Message de debug")
    platon_log("Valeur:", ma_variable)

Usage dans le runner:
    from platon_logger import platon_log, get_logs, clear_logs
    # ... exécution du script ...
    variables['platon_logs'] = get_logs()
"""

from typing import List, Any
from datetime import datetime, timezone
import threading

# Liste thread-safe pour stocker les logs
_logs: List[str] = []
_lock = threading.Lock()


def platon_log(*args: Any, **kwargs: Any) -> None:
    """
    Log un message vers la console Platon.

    Cette fonction est similaire à print() mais les messages sont
    collectés et renvoyés à la plateforme Platon.

    Args:
        *args: Arguments à logger (convertis en string et joints par des espaces)
        **kwargs: Arguments nommés (actuellement ignorés, réservés pour usage futur)

    Examples:
        >>> platon_log("Hello World")
        >>> platon_log("x =", 42)
        >>> platon_log("Liste:", [1, 2, 3])
    """
    message = " ".join(map(str, args))
    with _lock:
        _logs.append(message)



def platon_log_exception(exception: Exception) -> None:
    """
    Loggue une exception vers la console Platon.

    L'exception est convertie en message lisible et stockée
    sans stacktrace brute.

    Args:
        exception (Exception): L'exception à logger.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    message = f"[{timestamp}] {type(exception).__name__}: {exception}"
    with _lock:
        _logs.append(message)


def get_logs() -> List[str]:
    """
    Récupère tous les logs enregistrés.

    Returns:
        List[str]: Liste des messages loggés dans l'ordre chronologique.

    Example:
        >>> platon_log("Message 1")
        >>> platon_log("Message 2")
        >>> get_logs()
        ['Message 1', 'Message 2']
    """
    with _lock:
        return _logs.copy()


def clear_logs() -> None:
    """
    Efface tous les logs enregistrés.

    Utile pour réinitialiser l'état entre plusieurs exécutions
    ou pour les tests.

    Example:
        >>> platon_log("Message")
        >>> clear_logs()
        >>> get_logs()
        []
    """
    with _lock:
        _logs.clear()


def log_count() -> int:
    """
    Retourne le nombre de logs enregistrés.

    Returns:
        int: Nombre de messages dans le buffer de logs.
    """
    with _lock:
        return len(_logs)


# Alias pour compatibilité et facilité d'utilisation
log = platon_log
