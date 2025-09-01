"""
PlatonLog.py

Une bibliothèque utilitaire pour le logging dans les sandboxes PLaTon.
Permet de logger des messages même en cas d'exceptions et d'erreurs dans la sandbox.

Changelog:
----------
v1.0.0 - Initial Release
- Implémentation de la classe `PlatonLog` avec toutes les fonctionnalités de logging
- Support du logging même en cas d'exceptions dans la sandbox
- Méthodes pour le débogage avancé et le logging d'activités PLaTon
"""
import os
from typing import Optional, Any
import traceback
from datetime import datetime, timezone

class PlatonLog:
    def __init__(self, log_file: str = ".log", include_timestamp: bool = True, timestamp_format: str = "%Y-%m-%d %H:%M:%S"):
        """
        Initialise une instance de PlatonLog.
        Args:
            log_file (str): Nom du fichier de log. Par défaut ".log".
            include_timestamp (bool): Si True, inclut un timestamp dans chaque log.
            timestamp_format (str): Format du timestamp.
        """
        self.log_file = log_file
        self.include_timestamp = include_timestamp
        self.timestamp_format = timestamp_format

    def _get_timestamp(self) -> str:
        """Génère un timestamp formaté."""
        if not self.include_timestamp:
            return ""
        return datetime.now(timezone.utc).strftime(self.timestamp_format)

    def _format_message(self, message: Any) -> str:
        """Formate un message avec timestamp optionnel."""
        str_message = str(message)
        if self.include_timestamp:
            timestamp = self._get_timestamp()
            return f"[{timestamp}] {str_message}"
        return str_message

    def maxlog(self, message: Any) -> None:
        """
        Remplace le nom du fichier de log par le message formaté.
        Note: Cette fonction ne fait PAS d'écriture dans un fichier.
        """
        formatted_message = self._format_message(message)
        self.log_file = formatted_message

    def maxlog_exception(self, exception: Exception, context: str = "") -> None:
        """
        Loggue une exception en remplaçant le nom du fichier par le message d'erreur.
        Args:
            exception (Exception): L'exception à logger.
            context (str): Contexte additionnel (non utilisé dans l'implémentation actuelle).
        """
        try:
            error_message = f"{type(exception).__name__}: {str(exception)}"
            self.maxlog(error_message)
        except Exception:
            pass

    def maxlog_debug(self, variable_name: str, variable_value: Any) -> None:
        """
        Loggue une variable de debug en remplaçant le nom du fichier.
        Args:
            variable_name (str): Le nom de la variable.
            variable_value (Any): La valeur de la variable.
        """
        try:
            self.maxlog(f"DEBUG - {variable_name} = {repr(variable_value)}")
        except Exception as e:
            self.maxlog(f"ERROR LOGGING DEBUG INFO: {str(e)}")

    def push2platonlog(self) -> Optional[str]:
        """
        Retourne le contenu actuel de self.log_file.
        Cette fonction ne lit PAS un fichier, elle retourne simplement
        la valeur stockée dans l'attribut log_file.
        Returns:
            Optional[str]: Le contenu de self.log_file, ou None en cas d'exception.
        """
        try:
            return self.log_file
        except Exception as e:
            return None




