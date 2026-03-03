#!/usr/bin/env python3
# coding: utf-8
"""
Module partagé pour le logging Platon.

Ce module permet d'utiliser platon_log depuis n'importe quelle librairie interne.
Les logs sont stockés en mémoire sous forme de dictionnaires typés et récupérés
par le runner à la fin de l'exécution.

Structure d'un log:
    {"type": LogType, "message": str}

Usage dans vos librairies:
    from PlatonLogger import platon_log, LogType
    platon_log("Message de debug")
    platon_log("Attention", log_type=LogType.WARNING)
    platon_log("Erreur custom", log_type=LogType.ERROR)

Usage dans le runner:
    from PlatonLogger import platon_log, get_logs, clear_logs
    # ... exécution du script ...
    variables['platon_logs'] = get_logs()
"""

from typing import List, Any, Dict, Union
from datetime import datetime, timezone
from enum import Enum
import threading
import traceback


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

class LogType(str, Enum):
    """
    Type d'un message de log Platon.

    Les valeurs string sont alignées sur les conventions JavaScript/frontend
    (console.warn, winston, pino…) pour une sérialisation JSON cohérente.
    Les noms des membres suivent la convention Python (logging.WARNING).
    """
    DEBUG   = 'debug'
    INFO    = 'info'
    WARNING = 'warn' 
    ERROR   = 'error'



LogEntry = Dict[str, str] 


# ---------------------------------------------------------------------------
# Stockage interne (thread-safe)
# ---------------------------------------------------------------------------

_logs: List[LogEntry] = []
_lock = threading.Lock()

# Décalage introduit par with_try_clause dans runner.py ("try:\n    ...\n")
_WRAPPER_LINE_OFFSET: int = 2


# ---------------------------------------------------------------------------
# Helpers privés
# ---------------------------------------------------------------------------

def _coerce_level(level: Union[str, LogType]) -> LogType:
    """
    Accepte indifféremment une string ou un LogType.
    Gère les alias courants (ex. "warning" → LogType.WARNING).
    Lève ValueError si la valeur est inconnue.
    """
    if isinstance(level, LogType):
        return level

    _ALIASES: Dict[str, str] = {"warning": "warn"}

    normalized = _ALIASES.get(level.lower(), level.lower())
    try:
        return LogType(normalized)
    except ValueError:
        valid = ", ".join(f'"{t.value}"' for t in LogType)
        raise ValueError(f"level invalide : '{level}'. Valeurs acceptées : {valid}")


def _make_entry(level: LogType, message: str) -> LogEntry:
    """Construit un dictionnaire de log normalisé."""
    return {"type": level.value, "message": message}


def _resolve_script_line(exception: Exception) -> str:
    """
    Extrait le numéro de ligne dans le script utilisateur à partir
    de l'exception, en tenant compte du décalage du wrapper.

    Returns:
        str: Chaîne de la forme " (line N)" ou "" si non déterminable.
    """
    if isinstance(exception, SyntaxError):
        if exception.lineno is not None:
            return f" (line {exception.lineno - _WRAPPER_LINE_OFFSET})"
        return ""

    tb = exception.__traceback__
    if tb is None:
        return ""

    frames = traceback.extract_tb(tb)

    script_frames = [f for f in frames if f.filename == "<string>"]
    if script_frames:
        return f" (line {script_frames[-1].lineno - _WRAPPER_LINE_OFFSET})"

    if frames:
        return f" (line {frames[-1].lineno})"

    return ""


# ---------------------------------------------------------------------------
# API publique
# ---------------------------------------------------------------------------

def platon_log(*args: Any, level: Union[str, LogType] = LogType.INFO) -> None:
    """
    Enregistre un message dans la console Platon.

    Similaire à print(), mais les messages sont collectés et renvoyés
    à la plateforme Platon sous forme de dictionnaires typés.

    Args:
        *args:      Arguments à logger (convertis en str et joints par des espaces).
        level:   Type du message. Accepte une valeur LogType ou une string
                    équivalente ("info", "warning", "error", "debug").
                    Défaut : LogType.INFO.

    Examples:
        >>> platon_log("Hello World")
        >>> platon_log("x =", 42)
        >>> platon_log("Attention !", level=LogType.WARNING)
        >>> platon_log("Attention !", level="warning")   # équivalent
        >>> platon_log("Erreur custom", level=LogType.ERROR)
        >>> platon_log("Erreur custom", level="error")   # équivalent
    """
    message = " ".join(map(str, args))
    entry = _make_entry(_coerce_level(level), message)
    with _lock:
        _logs.append(entry)


def platon_log_exception(exception: Exception) -> None:
    """
    Enregistre une exception dans la console Platon (type ERROR).

    L'exception est convertie en message lisible avec horodatage et
    numéro de ligne dans le script utilisateur, sans stacktrace brute.

    Args:
        exception (Exception): L'exception à logger.

    Examples:
        >>> try:
        ...     1 / 0
        ... except Exception as e:
        ...     platon_log_exception(e)
    """
    location  = _resolve_script_line(exception)
    message   = f"{type(exception).__name__}{location}: {exception}"
    entry     = _make_entry(LogType.ERROR, message)
    with _lock:
        _logs.append(entry)


def get_logs() -> List[LogEntry]:
    """
    Retourne une copie de tous les logs enregistrés.

    Returns:
        List[LogEntry]: Liste de dictionnaires {"type": str, "message": str}.

    Example:
        >>> platon_log("Message 1")
        >>> platon_log("Attention", level=LogType.WARNING)
        >>> get_logs()
        [{"type": "info", "message": "Message 1"}, {"type": "warning", "message": "Attention"}]
    """
    with _lock:
        return list(_logs)


def clear_logs() -> None:
    """
    Efface tous les logs enregistrés.

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
        int: Nombre d'entrées dans le buffer de logs.
    """
    with _lock:
        return len(_logs)


# Alias pour compatibilité
log = platon_log
