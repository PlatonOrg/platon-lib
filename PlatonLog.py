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
        """Écrit un message dans le fichier .log."""
        try:
            formatted_message = self._format_message(message)
            
            with open(self.log_file, 'a', encoding='utf-8') as file:
                file.write(formatted_message + "\n")
                file.flush()
                
        except FileNotFoundError:
            try:
                formatted_message = self._format_message(message)
                
                with open(self.log_file, 'w', encoding='utf-8') as file:
                    file.write(formatted_message + "\n")
                    file.flush()
                    
            except Exception:
                raise KeyError("le fichier .log est inaccessible")
                
        except Exception:
            raise KeyError("le fichier .log est inaccessible")
        

    def maxlog_exception(self, exception: Exception, context: str = "") -> None:
        """
        Loggue une exception avec sa stack trace complète.
        
        Args:
            exception (Exception): L'exception à logger.
            context (str): Contexte additionnel pour l'exception.
        """
        try:
            error_message = f"EXCEPTION{' - ' + context if context else ''}: {type(exception).__name__}: {str(exception)}"
            self.maxlog(error_message)
            
            stack_trace = traceback.format_exc()
            self.maxlog(f"STACK TRACE:\n{stack_trace}")
            
        except Exception:
            try:
                with open(self.log_file, 'a') as f:
                    f.write(f"CRITICAL ERROR LOGGING EXCEPTION: {str(exception)}\n")
            except Exception:
                pass

    def maxlog_debug(self, variable_name: str, variable_value: Any) -> None:
        """
        Loggue une variable avec son nom et sa valeur pour le débogage.
        
        Args:
            variable_name (str): Le nom de la variable.
            variable_value (Any): La valeur de la variable.
        """
        try:
            self.maxlog(f"DEBUG - {variable_name} = {repr(variable_value)}")
        except Exception as e:
            self.maxlog(f"ERROR LOGGING DEBUG INFO: {str(e)}")


    def clear_log(self) -> None:
        """
        Efface le contenu du fichier .log.
        """
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'w') as file:
                    pass  # Fichier vidé
        except Exception as e:
            raise KeyError(f"Impossible d'effacer le fichier .log: {str(e)}")


    def push2platonlog(self) -> Optional[str]:
        """
        Transfère le contenu du fichier .log vers le système PLaTon.
        
        Cette fonction lit le fichier .log et prépare son contenu pour être
        affiché par le runner.py de PLaTon.
        
        Returns:
            Optional[str]: Le contenu du fichier .log s'il existe, None sinon.
        """
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as file:
                    log_content = file.read()
                    
                if log_content.strip():
                    return log_content
                else:
                    return ""
            else:
                return None
        except Exception as e:
            return None





