import random
from typing import Optional, Iterable, Callable, Any
import json
import hashlib


################################################################################
# Exceptions
################################################################################


class InvalidGroupError(Exception):
    """Exception levée lorsqu'un numéro de groupe invalide est demandé."""
    pass


class InvalidExerciseError(Exception):
    """Exception levée lorsqu'un numéro d'exercice invalide est demandé."""
    pass


class ExerciseVariablesNotEnabledError(Exception):
    """Exception levée lorsque l'accès aux variables des exercices est tenté sans que cette option soit activée."""
    pass


################################################################################
# Fonctions de vérification
################################################################################


def checkGroupNb(groupNb: int) -> None:
    """
    Vérifie si le numéro de groupe spécifié est valide.

    Args:
        groupNb (int): Le numéro de groupe à vérifier.

    Raises:
        InvalidGroupError: Si le numéro de groupe spécifié n'est pas valide.
    """
    if str(groupNb) not in exerciseGroups:
        raise InvalidGroupError(f"Le numéro de groupe {groupNb} est invalide.")
    

def checkExerciseNb(groupNb: int, exerciseNb: int) -> None:
    """
    Vérifie si le numéro d'exercice spécifié est valide.

    Args:
        groupNb (int): Le numéro de groupe (index) de l'exercice.
        exerciseNb (int): Le numéro d'exercice (index) à vérifier.

    Raises:
        InvalidGroupError: Si le numéro de groupe spécifié n'est pas valide.
        InvalidExerciseError: Si le numéro d'exercice spécifié n'est pas valide.
    """
    checkGroupNb(groupNb)

    exercises = exerciseGroups[str(groupNb)]["exercises"]
    
    if exerciseNb < 0 or exerciseNb >= len(exercises):
        raise InvalidExerciseError(f"Le numéro d'exercice {exerciseNb} est invalide.")
    

def CheckExerciseVariables() -> None:
    """
    Vérifie si l'accès aux variables des exercices est activé.

    Raises:
        ExerciseVariablesNotEnabledError: Si l'accès aux variables des exercices n'est pas activé.
    """
    if not exercisesVariables:
        raise ExerciseVariablesNotEnabledError("L'accès aux variables des exercices n'est pas activé.")


################################################################################
# Fonctions pour la gestion de l'activité
################################################################################


def playExercise(exerciseId: str, params: Optional[dict] = None) -> None:
    """
    Démarre l'exécution d'un exercice en fonction de son ID et stoppe l'exécution du next.
    
    Args:
        exerciseId (str): L'ID de l'exercice à jouer.
        params (Optional[dict]): Paramètres supplémentaires pour l'exercice. Default: None.
    
    Raises:
        StopExec: Exception levée pour arrêter l'exécution du next.
    """
    global nextExerciseId
    global nextParams
    nextExerciseId = exerciseId
    if params:
        nextParams = params
    raise StopExec()


def stopActivity() -> None:
    """
    Termine l'activité en cours et stoppe l'exécution du next.
    
    Raises:
        StopExec: Exception levée pour arrêter l'exécution du next.
    """
    navigation["terminated"] = True
    nextExerciseId = ""
    raise StopExec()


def getExerciseId(groupNb: int = 0, exerciseNb: int = 0) -> str:
    """
    Récupère l'ID de l'exercice à partir d'un groupe et d'un numéro d'exercice spécifiés.
    
    Args:
        groupNb (int): Le numéro du groupe (index). Par défaut, 0.
        exerciseNb (int): Le numéro de l'exercice (index) dans le groupe. Par défaut, 0.

    Returns:
        str: L'ID de l'exercice sélectionné.
    
    Raises:
        InvalidGroupError: Si le numéro de groupe est invalide.
        InvalidExerciseError: Si le numéro d'exercice est invalide.
    """
    checkGroupNb(groupNb)
    checkExerciseNb(groupNb, exerciseNb)

    exercises = exerciseGroups[str(groupNb)]["exercises"]

    return exercises[exerciseNb]["id"]


def getExerciseAttempts(exerciseId: str) -> int:
    """
    Renvoie le nombre de tentatives effectuées pour un exercice donné par son ID.
    
    Args:
        exerciseId (str): L'ID de l'exercice.

    Returns:
        int: Le nombre de tentatives pour l'exercice spécifié.
    """
    return exercisesMeta[exerciseId]["attempts"]


def getGroupsCount() -> int:
    """
    Récupère le nombre total de groupes d'exercices disponibles.

    Returns:
        int: Le nombre de groupes. Si le groupe "Exercices générés" est présent, il est exclu du compte.
    """
    if "-1" in exerciseGroups:
        return len(exerciseGroups) - 1
    return len(exerciseGroups)


def getGroupExercisesCount(groupNb: int) -> int:
    """
    Récupère le nombre d'exercices dans un groupe spécifique.

    Args:
        groupNb (int): Le numéro du groupe (index).

    Returns:
        int: Le nombre d'exercices dans le groupe spécifié.
    
    Raises:
        InvalidGroupError: Si le numéro de groupe spécifié n'existe pas.
    """
    checkGroupNb(groupNb)

    return len(exerciseGroups[str(groupNb)]["exercises"])


def getPreviousExerciseId() -> Optional[str]:
    """
    Récupère l'ID du dernier exercice joué.

    Returns:
        Optional[str]: L'ID du dernier exercice joué, ou None si aucun exercice n'a été joué.
    """
    if not navigation.get("current"):
        return None
    return navigation["current"]["id"]


def isAllExercisesPlayed() -> bool:
    """
    Vérifie si tous les exercices ont été joués au moins une fois.

    Returns:
        bool: True si tous les exercices ont été tentés, False sinon.
    """
    for exercise in exercisesMeta.values():
        if exercise["attempts"] == 0:
            return False
    return True


def getRandomGroupNb() -> int:
    """
    Sélectionne un numéro de groupe aléatoire.

    Returns:
        int: Un numéro de groupe choisi aléatoirement (index).
    """
    return random.randint(0, getGroupsCount() - 1)


def getRandomGroupExerciseNb(groupNb: int) -> int:
    """
    Sélectionne un numéro d'exercice aléatoire au sein d'un groupe spécifié.

    Args:
        groupNb (int): Le numéro du groupe (index).

    Returns:
        int: Un numéro d'exercice choisi aléatoirement au sein du groupe spécifié.
    
    Raises:
        InvalidGroupError: Si le numéro de groupe spécifié n'existe pas.
    """
    checkGroupNb(groupNb)

    return random.randint(0, getGroupExercisesCount(groupNb) - 1)


def getRandomExercise() -> str:
    """
    Sélectionne un exercice aléatoire dans un groupe choisi aléatoirement.

    Returns:
        str: L'ID de l'exercice choisi aléatoirement.
    """
    groupNb = getRandomGroupNb()
    exerciseNb = getRandomGroupExerciseNb(groupNb)
    return getExerciseId(groupNb, exerciseNb)


def getRandomExerciseFromGroup(groupNb: int) -> str:
    """
    Sélectionne un exercice aléatoire dans un groupe spécifié.

    Args:
        groupNb (int): Le numéro du groupe (index) dont on veut sélectionner un exercice aléatoire.

    Returns:
        str: L'ID de l'exercice aléatoire choisi dans le groupe.

    Raises:
        InvalidGroupError: Si le numéro de groupe spécifié n'existe pas.
    """
    checkGroupNb(groupNb)
    
    return getExerciseId(groupNb, getRandomGroupExerciseNb(groupNb))


def getRandomUnplayedExerciseId() -> Optional[str]:
    """
    Sélectionne un exercice aléatoire qui n'a pas encore été joué.

    Returns:
        Optional[str]: L'ID de l'exercice choisi aléatoirement qui n'a pas été joué.
    """
    unplayed_exercises = [ex_id for ex_id, meta in exercisesMeta.items() if meta["attempts"] == 0]
    
    if not unplayed_exercises:
        return None
    
    return random.choice(unplayed_exercises)


def playPrevious() -> None:
    """
    Joue le dernier exercice lancé, s'il existe.

    Si aucun exercice n'a été lancé, aucune action n'est effectuée.
    """
    previousId = getPreviousExerciseId()
    if previousId:
        playExercise(previousId)


def playPreviousIfUnplayed() -> None:
    """
    Joue l'exercice précédent s'il n'a pas encore été tenté.
    
    Si l'exercice précédent a déjà été tenté, aucune action n'est effectuée.
    """
    previousId = getPreviousExerciseId()
    if previousId and getExerciseAttempts(previousId) == 0:
        playExercise(previousId)


def getExerciseGrades(exerciseId: str) -> Iterable[int]:
    """
    Récupère toutes les notes attribuées à un exercice spécifique.

    Args:
        exerciseId (str): L'ID de l'exercice dont on souhaite obtenir les notes.

    Returns:
        Iterable[int]: Une liste des notes attribuées à cet exercice.
    """
    return exercisesMeta[exerciseId]["grades"]


def getExerciseLastGrade(exerciseId: str) -> Optional[int]:
    """
    Récupère la dernière note attribuée à un exercice spécifique.

    Args:
        exerciseId (str): L'ID de l'exercice dont on souhaite obtenir la dernière note.

    Returns:
        Optional[int]: La dernière note attribuée à l'exercice, ou None si l'exercice n'a pas encore été noté.
    """
    grades = getExerciseGrades(exerciseId)
    return grades[-1] if grades else None


def getExerciseBestGrade(exerciseId: str) -> Optional[int]:
    """
    Récupère la meilleure note attribuée à un exercice spécifique.

    Args:
        exerciseId (str): L'ID de l'exercice dont on souhaite obtenir la meilleure note.

    Returns:
        Optional[int]: La meilleure note attribuée à l'exercice, ou None si l'exercice n'a pas encore été noté.
    """
    grades = getExerciseGrades(exerciseId)
    return max(grades) if grades else None


def getPreviousGrade() -> Optional[int]:
    """
    Récupère la note du dernier exercice lancé.

    Returns:
        Optional[int]: La note du dernier exercice joué, ou None s'il n'y a pas de note.
    """
    return navigation.get("current", {}).get("grade")


def isPlayed(exerciseId: str) -> bool:
    """
    Vérifie si un exercice a déjà été joué au moins une fois.

    Args:
        exerciseId (str): L'ID de l'exercice à vérifier.

    Returns:
        bool: True si l'exercice a été joué au moins une fois, False sinon.
    """
    return getExerciseAttempts(exerciseId) > 0


def playAnyFromGroup(groupNb: int) -> Optional[None]:
    """
    Vérifie si au moins un exercice dans le groupe spécifié a déjà été effectué.
    Si aucun exercice n'a été fait dans le groupe, lance un exercice aléatoire de ce groupe.

    Args:
        groupNb (int): Le numéro du groupe dont on souhaite vérifier les exercices.

    Returns:
        None: Si un exercice a déjà été joué dans le groupe

    Raises:
        InvalidGroupError: Si le numéro de groupe spécifié n'existe pas.
    """
    checkGroupNb(groupNb)

    exercises = exerciseGroups[str(groupNb)]["exercises"]
    
    for exercise in exercises:
        if isPlayed(exercise["id"]):
            return None 

    randomExerciseNb = getRandomGroupExerciseNb(groupNb)
    playExercise(exercises[randomExerciseNb]["id"])


def playAllFromGroup(groupNb: int, randomOrder: bool = False) -> Optional[None]:
    """
    Lance un exercice non joué du groupe spécifié. Si tous les exercices ont été joués,
    aucune action n'est effectuée. Si l'argument randomOrder est True, un exercice non joué 
    est sélectionné aléatoirement.

    Args:
        groupNb (int): Le numéro du groupe dont on souhaite lancer un exercice non joué.
        randomOrder (bool): Si True, un exercice non joué sera choisi aléatoirement. 
                            Si False, les exercices sont lancés dans l'ordre.

    Returns:
        None: Si tous les exercices du groupe ont déjà été joués.

    Raises:
        InvalidGroupError: Si le numéro de groupe spécifié n'existe pas.
    """
    checkGroupNb(groupNb)

    exercises = exerciseGroups[str(groupNb)]["exercises"]
    
    unplayed_exercises = [exercise for exercise in exercises if not isPlayed(exercise["id"])]
    
    if not unplayed_exercises:
        return None 

    if randomOrder:
        playExercise(random.choice(unplayed_exercises)["id"])
    else:
        playExercise(unplayed_exercises[0]["id"])


def playFirstUnplayedExercise() -> None:
    """
    Sélectionne le prochain exercice non joué, en commençant par le premier groupe 
    et en progressant séquentiellement.

    Returns:
        Optional[str]: L'ID du prochain exercice non joué, ou None si tous les exercices
                       ont été joués.
    """
    for groupNb in range(getGroupsCount()):
        exercises = exerciseGroups[str(groupNb)]["exercises"]
        for exercise in exercises:
            if not isPlayed(exercise["id"]):
                playExercise(exercise["id"])


def playNextUnplayedExercise(loop: bool = False) -> None:
    """
    Joue le prochain exercice non joué après l'exercice précédent. 
    Si aucun exercice n'a été lancé ou si tous les exercices suivants ont déjà 
    été joués, elle parcourt la liste depuis le début pour trouver le premier exercice non joué.

    Raises:
        StopExec: Exception levée pour démarrer le prochain exercice non joué.
    """
    current_id = navigation.get("current", {}).get("id")
    found_current = False

    # Parcourt tous les groupes et exercices en cherchant le prochain exercice non joué après le current
    for groupNb in range(getGroupsCount()):
        exercises = exerciseGroups[str(groupNb)]["exercises"]
        for exercise in exercises:
            if found_current and not isPlayed(exercise["id"]):
                playExercise(exercise["id"])
            if exercise["id"] == current_id:
                found_current = True

    # Si aucun exercice suivant n'a été trouvé, recommence depuis le début
    if (loop):
        for groupNb in range(getGroupsCount()):
            exercises = exerciseGroups[str(groupNb)]["exercises"]
            for exercise in exercises:
                if not isPlayed(exercise["id"]):
                    playExercise(exercise["id"])


def getPreviousGroupNumber() -> Optional[int]:
    """
    Récupère le numéro du groupe du dernier exercice lancé, s'il existe.

    Returns:
        Optional[int]: Le numéro du groupe du dernier exercice lancé, ou None si aucun exercice
                       n'est en cours.
    """
    previous = navigation.get("current")
    if not previous:
        return None

    for groupNb, group in exerciseGroups.items():
        if any(ex["id"] == previous["id"] for ex in group["exercises"]):
            return int(groupNb)

    return None


def isAllExercisesFromGroupPlayed(groupNb: int = getPreviousGroupNumber()) -> bool:
    """
    Vérifie si tous les exercices d'un groupe spécifique ont été joués.

    Args:
        groupNb (int): Le numéro du groupe (index) à vérifier. Default : previous group

    Returns:
        bool: True si tous les exercices du groupe spécifié ont été joués, False sinon.
    
    Raises:
        InvalidGroupError: Si le numéro de groupe spécifié n'existe pas.
    """
    checkGroupNb(groupNb)
    
    exercises = exerciseGroups[str(groupNb)]["exercises"]
    return all(isPlayed(exercise["id"]) for exercise in exercises)


def playIfUnplayed(exerciseId: str, params: Optional[dict] = None) -> None:
    """
    Joue l'exercice spécifié s'il n'a pas encore été tenté.

    Args:
        exerciseId (str): L'ID de l'exercice à jouer.
        params (Optional[dict]): Paramètres supplémentaires pour l'exercice. Default: None.
    """
    if not isPlayed(exerciseId):
        playExercise(exerciseId, params)


def isOneExercisePlayed() -> bool:
    """
    Vérifie si au moins un exercice a déjà été joué.

    Returns:
        bool: True si au moins un exercice a été joué, False sinon.
    """
    return any(meta["attempts"] > 0 for meta in exercisesMeta.values())


def isOneExerciseFromGroupPlayed(groupNb: int) -> bool:
    """
    Vérifie si au moins un exercice du groupe spécifié a déjà été joué.

    Args:
        groupNb (int): Le numéro du groupe (index) à vérifier.

    Returns:
        bool: True si au moins un exercice du groupe a été joué, False sinon.
    
    Raises:
        InvalidGroupError: Si le numéro de groupe spécifié n'existe pas.
    """
    checkGroupNb(groupNb)

    exercises = exerciseGroups[str(groupNb)]["exercises"]
    return any(isPlayed(exercise["id"]) for exercise in exercises)



################################################################################
# Fonctions pour la gestion des notes
################################################################################


def setActivityGrade(grade_aggregation_strategy: Callable[[], int]) -> None:
    """
    Calcule la note totale de l'activité en agrégeant les notes de tous les exercices joués
    en utilisant une stratégie d'agrégation, et stocke cette note dans la navigation.

    Args:
        grade_aggregation_strategy (Callable[[], int]): Une fonction de stratégie qui ne prend 
                                                        aucun argument et retourne un entier représentant
                                                        la note finale.

    Raises:
        ValueError: Si aucun exercice n'a été joué ou si la note agrégée est invalide.
    """
    global activityGrade

    total_grade = grade_aggregation_strategy()
    
    if total_grade < 0 or total_grade > 100:
        raise ValueError("La note totale calculée est invalide. Elle doit être entre 0 et 100.")
    
    activityGrade = total_grade


# Strategies


def average_grade_strategy() -> int:
    """Stratégie qui retourne la moyenne des notes des exercices joués."""
    played_grades = [
        getExerciseLastGrade(ex_id)
        for ex_id in exercisesMeta if isPlayed(ex_id)
    ]
    played_grades = [grade for grade in played_grades if grade is not None]
    return sum(played_grades) // len(played_grades) if played_grades else 0


def best_grade_strategy() -> int:
    """Stratégie qui retourne la meilleure note obtenue parmi les exercices joués."""
    played_grades = [
        getExerciseLastGrade(ex_id)
        for ex_id in exercisesMeta if isPlayed(ex_id)
    ]
    played_grades = [grade for grade in played_grades if grade is not None]
    return max(played_grades) if played_grades else 0


################################################################################
# Fonction de gestion de la mémoire
################################################################################


def load(variableName: str, default: Any = None) -> Optional[Any]:
    """
    Charge une variable stockée en mémoire.

    Args:
        variableName (str): Le nom de la variable à charger.

    Returns:
        Optional[Any]: La valeur de la variable chargée, ou None si la variable n'existe pas.
    """
    return savedVariables.get(variableName, default)


def save(variableName: str, value: Any) -> None:
    """
    Stocke une variable en mémoire.

    Args:
        variableName (str): Le nom de la variable à stocker.
        value (Any): La valeur de la variable à stocker.
    """
    savedVariables[variableName] = value


def loadAll() -> dict:
    """
    Charge toutes les variables stockées en mémoire.

    Returns:
        dict: Un dictionnaire contenant toutes les variables stockées.
    """
    return savedVariables


################################################################################
# Fonctions pour accèder aux variables des exercices
# ATTENTION: Cette fonctionnalité doit être activée dans l'activité
################################################################################


def getExerciseVariable(exerciseId: str, variableName: str) -> Optional[Any]:
    """
    Récupère la valeur d'une variable spécifique pour un exercice donné.

    Args:
        exerciseId (str): L'ID de l'exercice.
        variableName (str): Le nom de la variable à récupérer.

    Returns:
        Optional[Any]: La valeur de la variable, ou None si la variable n'existe pas.

    Raises:
        ExerciseVariablesNotEnabledError: Si l'accès aux variables des exercices n'est pas activé.
    """
    CheckExerciseVariables()
    return exercisesVariables[exerciseId].get(variableName)


def getExerciseAllVariables(exerciseId: str) -> dict:
    """
    Récupère toutes les variables pour un exercice donné.

    Args:
        exerciseId (str): L'ID de l'exercice.

    Returns:
        dict: Un dictionnaire contenant toutes les variables de l'exercice.

    Raises:
        ExerciseVariablesNotEnabledError: Si l'accès aux variables des exercices n'est pas activé.
    """
    CheckExerciseVariables()
    return exercisesVariables[exerciseId]


################################################################################
# Fonctions pour la génération de nouveaux exercices
################################################################################


def hashParams(params: dict, exerciseId: str) -> str:
    """
    Génère un hash MD5 pour les paramètres donnés, incluant un ID d'exercice.

    Args:
        params (dict): Un dictionnaire contenant les paramètres à hasher.
        exerciseId (str): L'ID de l'exercice à inclure dans les paramètres.

    Returns:
        str: Le hash MD5 des paramètres sérialisés en JSON, incluant l'ID de l'exercice.
    """
    params_with_id = {**params, "idExo": exerciseId}
    params_str = json.dumps(params_with_id, sort_keys=True).encode('utf-8')
    return hashlib.md5(params_str).hexdigest()


def generateAndPlayExercise(exerciseId: str, params: dict = {}) -> Optional[str]:
    """
    Génère un exercice avec des paramètres donnés et le lance si cet exercice n'a pas déjà été généré.
    
    Args:
        exerciseId (str): L'ID de l'exercice à générer et à jouer.
        params (dict, optional): Paramètres supplémentaires pour l'exercice. Par défaut, un dictionnaire vide.
    
    Returns:
        Optional[str]: L'ID de l'exercice généré et joué si l'exercice vient d'être généré, None sinon.
    """
    global generatedExerciseHash
    exercice_hash = hashParams(params, exerciseId)
    if exercice_hash not in generatedExercises:
        generatedExerciseHash = exercice_hash
        playExercise(exerciseId, params)
    if getPreviousExerciseId() == generatedExercises[exercice_hash]:
        return generatedExercises[exercice_hash]
    return None
