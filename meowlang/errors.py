"""
Système d'erreurs MeowLang avec messages personnalisés et emojis félins.
"""

from typing import Optional, Tuple, Dict, Any
from enum import Enum


class ErrorSeverity(Enum):
    FAIBLE = "FAIBLE"
    MOYENNE = "MOYENNE"
    FORTE = "FORTE"


class ErrorDefinition:
    def __init__(
        self,
        code: str,
        name: str,
        message_meow: str,
        message_tech: str,
        severity: ErrorSeverity,
        mood: str,
        suggestion: str = "",
        example: str = ""
    ):
        self.code = code
        self.name = name
        self.message_meow = message_meow
        self.message_tech = message_tech
        self.severity = severity
        self.mood = mood
        self.suggestion = suggestion
        self.example = example


class MeowLangError(Exception):
    def __init__(
        self,
        error_def: ErrorDefinition,
        file: str = "<script>",
        line: int = 1,
        column: int = 1,
        instruction: str = "",
        context_lines: Optional[list] = None,
        python_error: Optional[str] = None,
        **kwargs
    ):
        self.error_def = error_def
        self.file = file
        self.line = line
        self.column = column
        self.instruction = instruction
        self.context_lines = context_lines or []
        self.python_error = python_error
        self.extra_vars = kwargs
        
        super().__init__(self.format())
    
    def format(self) -> str:
        severity_emoji = {
            ErrorSeverity.FAIBLE: "😺",
            ErrorSeverity.MOYENNE: "😾",
            ErrorSeverity.FORTE: "🙀"
        }
        
        emoji = severity_emoji.get(self.error_def.severity, "😾")
        
        output = []
        output.append(f"\n{emoji} ERREUR MEOWLANG [{self.error_def.code}] — GRIFFURE {self.error_def.severity.value}\n")
        output.append(f"Fichier      : {self.file}")
        output.append(f"Ligne        : {self.line}")
        output.append(f"Colonne      : {self.column}")
        if self.instruction:
            output.append(f"Instruction  : {self.instruction}")
        output.append("")
        output.append(f"Type         : {self.error_def.name}")
        if self.python_error:
            output.append(f"Code interne : {self.python_error}")
        output.append("")
        output.append("Message technique :")
        
        message_tech = self.error_def.message_tech
        for key, value in self.extra_vars.items():
            message_tech = message_tech.replace(f"{{{key}}}", str(value))
        output.append(message_tech)
        
        output.append("")
        output.append("Message MeowLang 🐱 :")
        
        message_meow = self.error_def.message_meow
        for key, value in self.extra_vars.items():
            message_meow = message_meow.replace(f"{{{key}}}", str(value))
        output.append(message_meow)
        
        if self.context_lines:
            output.append("")
            output.append("Contexte :")
            for ctx_line_no, ctx_line_text, is_error_line in self.context_lines:
                prefix = "> " if is_error_line else "  "
                output.append(f"{prefix}{ctx_line_no:3} | {ctx_line_text}")
                if is_error_line and self.column > 1:
                    pointer = " " * (7 + self.column - 1) + "^" * max(1, len(self.instruction))
                    output.append(pointer)
        
        output.append("")
        output.append("État du chat :")
        output.append(self.error_def.mood)
        
        if self.error_def.suggestion:
            output.append("")
            output.append("Suggestion du chat 💡 :")
            suggestion = self.error_def.suggestion
            for key, value in self.extra_vars.items():
                suggestion = suggestion.replace(f"{{{key}}}", str(value))
            output.append(suggestion)
        
        if self.error_def.example:
            output.append("")
            output.append("Exemple recommandé :")
            example = self.error_def.example
            for key, value in self.extra_vars.items():
                example = example.replace(f"{{{key}}}", str(value))
            output.append(example)
        
        output.append("")
        output.append("Fin du jugement.")
        output.append("Le chat te surveille.")
        output.append("")
        
        return "\n".join(output)


class ErrorCatalog:
    _errors: Dict[str, ErrorDefinition] = {}
    
    @classmethod
    def register(cls, error_def: ErrorDefinition):
        cls._errors[error_def.code] = error_def
    
    @classmethod
    def get(cls, code: str) -> ErrorDefinition:
        return cls._errors.get(code)
    
    @classmethod
    def raise_error(
        cls,
        code: str,
        file: str = "<script>",
        line: int = 1,
        column: int = 1,
        instruction: str = "",
        source_lines: Optional[list] = None,
        python_error: Optional[str] = None,
        **kwargs
    ):
        error_def = cls.get(code)
        if not error_def:
            raise ValueError(f"Code d'erreur inconnu: {code}")
        
        context_lines = []
        if source_lines:
            context_lines = extract_context(source_lines, line)
        
        raise MeowLangError(
            error_def=error_def,
            file=file,
            line=line,
            column=column,
            instruction=instruction,
            context_lines=context_lines,
            python_error=python_error,
            **kwargs
        )


def extract_context(source_lines: list, error_line: int, context_size: int = 2) -> list:
    context = []
    start = max(1, error_line - context_size)
    end = min(len(source_lines), error_line + context_size)
    
    for line_no in range(start, end + 1):
        if 1 <= line_no <= len(source_lines):
            line_text = source_lines[line_no - 1].rstrip()
            is_error_line = (line_no == error_line)
            context.append((line_no, line_text, is_error_line))
    
    return context


ErrorCatalog.register(ErrorDefinition(
    code="E000",
    name="ScriptSansMiaou",
    message_tech="Le script doit commencer par 'miaou'.",
    message_meow="😾 Le chat refuse d'entrer sans un \"miaou\" au début.",
    severity=ErrorSeverity.FORTE,
    mood="😾 En colère, refuse d'entrer.",
    suggestion="✔ Ajoute 'miaou' au tout début du fichier",
    example="  miaou\n  ecrire \"Hello!\"\n  meow"
))

ErrorCatalog.register(ErrorDefinition(
    code="E001",
    name="ScriptSansMeow",
    message_tech="Le script doit se terminer par 'meow'.",
    message_meow="💤 Le chat s'est endormi avant le \"meow\" final.",
    severity=ErrorSeverity.FORTE,
    mood="💤 Endormi, perdu dans ses rêves.",
    suggestion="✔ Ajoute 'meow' à la toute fin du fichier",
    example="  miaou\n  ecrire \"Hello!\"\n  meow"
))

ErrorCatalog.register(ErrorDefinition(
    code="E002",
    name="MeowPremature",
    message_tech="Le mot-clé 'meow' apparaît avant la fin du script.",
    message_meow="🪟 Le chat est sorti trop tôt par la fenêtre.",
    severity=ErrorSeverity.MOYENNE,
    mood="😼 Pressé, déjà dehors.",
    suggestion="✔ Place 'meow' uniquement à la fin du script",
    example="  miaou\n  # ton code ici\n  meow"
))

ErrorCatalog.register(ErrorDefinition(
    code="E003",
    name="OrdreInterdit",
    message_tech="Structure invalide du script.",
    message_meow="😼 Les croquettes ne se servent pas avant le bol.",
    severity=ErrorSeverity.MOYENNE,
    mood="😼 Confus, sourcils froncés.",
    suggestion="✔ Vérifie l'ordre des instructions"
))

ErrorCatalog.register(ErrorDefinition(
    code="E004",
    name="FichierVide",
    message_tech="Le fichier est vide.",
    message_meow="😿 Le carton est vide.",
    severity=ErrorSeverity.MOYENNE,
    mood="😿 Déçu et triste.",
    suggestion="✔ Ajoute du code dans le fichier"
))

ErrorCatalog.register(ErrorDefinition(
    code="E100",
    name="InstructionInconnue",
    message_tech="Instruction ou mot-clé non reconnu.",
    message_meow="😿 Le chat ne comprend pas ce mot.",
    severity=ErrorSeverity.MOYENNE,
    mood="😿 Perplexe, tête penchée.",
    suggestion="✔ Vérifie l'orthographe de l'instruction\n✔ Consulte la liste des mots-clés valides"
))

ErrorCatalog.register(ErrorDefinition(
    code="E101",
    name="GuillemetManquant",
    message_tech="Guillemet de fermeture manquant pour une chaîne de caractères.",
    message_meow="🧶 La pelote de laine n'est pas fermée (guillemet manquant).",
    severity=ErrorSeverity.MOYENNE,
    mood="🧶 Distrait, joue avec la pelote.",
    suggestion="✔ Ajoute un guillemet \" à la fin de la chaîne",
    example="  texte = \"Bonjour le chat\""
))

ErrorCatalog.register(ErrorDefinition(
    code="E102",
    name="ParentheseManquante",
    message_tech="Parenthèse manquante dans une expression.",
    message_meow="🐈 Une patte dépasse. Parenthèse manquante.",
    severity=ErrorSeverity.MOYENNE,
    mood="🐈 Inconfortable, une patte en l'air.",
    suggestion="✔ Vérifie que chaque '(' a son ')'",
    example="  resultat = (3 + 5) * 2"
))

ErrorCatalog.register(ErrorDefinition(
    code="E103",
    name="IndentationFautive",
    message_tech="Indentation incorrecte détectée.",
    message_meow="😾 Le chat n'aime pas les lignes mal alignées.",
    severity=ErrorSeverity.MOYENNE,
    mood="😾 Agacé par le désordre.",
    suggestion="✔ Utilise des espaces cohérents pour l'indentation\n✔ Évite de mélanger espaces et tabulations",
    example="  si age > 10 alors:\n    ecrire \"OK\"  # 2 ou 4 espaces d'indentation"
))

ErrorCatalog.register(ErrorDefinition(
    code="E104",
    name="MotCleManquant",
    message_tech="Mot-clé attendu manquant.",
    message_meow="🧐 Il manque un mot magique.",
    severity=ErrorSeverity.MOYENNE,
    mood="🧐 Attend quelque chose.",
    suggestion="✔ Vérifie la syntaxe complète de l'instruction"
))

ErrorCatalog.register(ErrorDefinition(
    code="E200",
    name="VariableInexistante",
    message_tech="Variable '{var_name}' non définie.",
    message_meow="🐾 Ce chat '{var_name}' n'existe pas dans la maison.",
    severity=ErrorSeverity.MOYENNE,
    mood="🐾 Cherche partout, ne trouve rien.",
    suggestion="✔ Vérifie l'orthographe de la variable\n✔ Définis la variable avant de l'utiliser",
    example="  {var_name} = 42\n  ecrire {var_name}"
))

ErrorCatalog.register(ErrorDefinition(
    code="E201",
    name="VariableNonInitialisee",
    message_tech="Variable utilisée avant d'être initialisée.",
    message_meow="😼 Tu appelles le chat avant de l'avoir adopté.",
    severity=ErrorSeverity.MOYENNE,
    mood="😼 Sceptique.",
    suggestion="✔ Assigne une valeur à la variable avant de l'utiliser"
))

ErrorCatalog.register(ErrorDefinition(
    code="E202",
    name="TypeIncompatible",
    message_tech="Opération impossible entre types incompatibles : {type1} et {type2}.",
    message_meow="🐟 Mauvaise gamelle pour ce repas. Types {type1} et {type2} incompatibles.",
    severity=ErrorSeverity.MOYENNE,
    mood="😿 Dégoûté par la gamelle.",
    suggestion="✔ Vérifie les types de tes variables\n✔ Convertis si nécessaire"
))

ErrorCatalog.register(ErrorDefinition(
    code="E203",
    name="ConversionImpossible",
    message_tech="Impossible de convertir '{value}' en {target_type}.",
    message_meow="😾 Impossible de transformer ça en {target_type}.",
    severity=ErrorSeverity.MOYENNE,
    mood="😾 Refuse catégoriquement.",
    suggestion="✔ Vérifie que la valeur peut être convertie"
))

ErrorCatalog.register(ErrorDefinition(
    code="E300",
    name="ConditionInvalide",
    message_tech="La condition n'est pas valide ou est mal formée.",
    message_meow="🤨 Cette condition n'a aucun sens.",
    severity=ErrorSeverity.MOYENNE,
    mood="🤨 Sourcil levé, dubitatif.",
    suggestion="✔ Vérifie la syntaxe de la condition\n✔ Utilise des opérateurs valides : =, !=, <, >, <=, >=, et, ou"
))

ErrorCatalog.register(ErrorDefinition(
    code="E301",
    name="SinonSansSi",
    message_tech="'sinon' ou 'sinon si' sans 'si' correspondant.",
    message_meow="😾 Le chat répond \"sinon\" sans qu'on lui ait posé de question.",
    severity=ErrorSeverity.MOYENNE,
    mood="😾 Confus et agacé.",
    suggestion="✔ Place 'sinon' après un bloc 'si'"
))

ErrorCatalog.register(ErrorDefinition(
    code="E302",
    name="ComparaisonImpossible",
    message_tech="Impossible de comparer {type1} avec {type2}.",
    message_meow="🐈 Comparer un chat et un grille-pain est interdit.",
    severity=ErrorSeverity.MOYENNE,
    mood="🙀 Choqué par l'absurdité.",
    suggestion="✔ Compare des valeurs de types compatibles"
))

ErrorCatalog.register(ErrorDefinition(
    code="E400",
    name="BoucleInfinie",
    message_tech="Boucle infinie détectée (trop d'itérations).",
    message_meow="😵‍💫 Le chat tourne en rond avec le laser.",
    severity=ErrorSeverity.FORTE,
    mood="😵‍💫 Étourdi, ne peut plus s'arrêter.",
    suggestion="✔ Vérifie que la condition de sortie est atteignable\n✔ Ajoute un compteur de sécurité"
))

ErrorCatalog.register(ErrorDefinition(
    code="E401",
    name="SortieBoucleAbsente",
    message_tech="Boucle sans condition de sortie valide.",
    message_meow="🚪 Le chat ne trouve plus la sortie de la pièce.",
    severity=ErrorSeverity.FORTE,
    mood="🚪 Paniqué, cherche la sortie.",
    suggestion="✔ Ajoute une condition qui permet de sortir de la boucle"
))

ErrorCatalog.register(ErrorDefinition(
    code="E402",
    name="CompteurManquant",
    message_tech="Variable 'compteur' utilisée hors contexte de boucle 'repeter'.",
    message_meow="😿 Le chat a perdu le fil du compte.",
    severity=ErrorSeverity.MOYENNE,
    mood="😿 Perdu, ne sait plus compter.",
    suggestion="✔ Utilise 'compteur' uniquement dans une boucle 'repeter'"
))

ErrorCatalog.register(ErrorDefinition(
    code="E500",
    name="DivisionParZero",
    message_tech="Division par zéro impossible.",
    message_meow="🚫 Partager des croquettes entre zéro chat est strictement interdit.",
    severity=ErrorSeverity.MOYENNE,
    mood="😾 Agacé, oreilles en arrière, queue en fouet.",
    suggestion="✔ Vérifie que le diviseur est différent de 0\n✔ Ajoute une condition avant le calcul",
    example="  si nombre != 0 alors:\n    ecrire 10 / nombre\n  sinon:\n    ecrire \"Même le chat ne peut pas faire ça.\""
))

ErrorCatalog.register(ErrorDefinition(
    code="E501",
    name="DepassementValeur",
    message_tech="La valeur dépasse les limites supportées.",
    message_meow="🐟 Trop de croquettes pour ce bol.",
    severity=ErrorSeverity.MOYENNE,
    mood="😾 Débordé.",
    suggestion="✔ Utilise des valeurs plus petites"
))

ErrorCatalog.register(ErrorDefinition(
    code="E502",
    name="CalculImpossible",
    message_tech="Calcul mathématique impossible : {reason}.",
    message_meow="😿 Le chat abandonne ce calcul.",
    severity=ErrorSeverity.MOYENNE,
    mood="😿 Résigné.",
    suggestion="✔ Vérifie les valeurs utilisées dans le calcul"
))

ErrorCatalog.register(ErrorDefinition(
    code="E600",
    name="FonctionInconnue",
    message_tech="La fonction '{func_name}' n'existe pas.",
    message_meow="😿 Ce tour félin '{func_name}' n'existe pas.",
    severity=ErrorSeverity.MOYENNE,
    mood="😿 Désolé, ne connaît pas ce tour.",
    suggestion="✔ Vérifie le nom de la fonction\n✔ Définis la fonction avant de l'appeler"
))

ErrorCatalog.register(ErrorDefinition(
    code="E601",
    name="ArgumentsInvalides",
    message_tech="Nombre d'arguments incorrect : attendu {expected}, reçu {received}.",
    message_meow="🐾 Le chat attend {expected} caresse(s), pas {received}.",
    severity=ErrorSeverity.MOYENNE,
    mood="🐾 Insatisfait du nombre de caresses.",
    suggestion="✔ Vérifie le nombre d'arguments passés à la fonction"
))

ErrorCatalog.register(ErrorDefinition(
    code="E602",
    name="RetourManquant",
    message_tech="La fonction doit retourner une valeur.",
    message_meow="👋 Le chat est parti sans répondre (return manquant).",
    severity=ErrorSeverity.FAIBLE,
    mood="😼 Parti trop vite.",
    suggestion="✔ Ajoute 'retour valeur' dans ta fonction si nécessaire"
))

ErrorCatalog.register(ErrorDefinition(
    code="E700",
    name="IndexHorsLimite",
    message_tech="Index {index} hors limites pour liste de taille {size}.",
    message_meow="🐈 Tu cherches un chat qui n'est pas dans la portée (index {index}).",
    severity=ErrorSeverity.MOYENNE,
    mood="🐈 Cherche dans le vide.",
    suggestion="✔ Vérifie que l'index est entre 0 et {size_minus_one}",
    example="  # Pour une liste de taille {size}, utilise index 0 à {size_minus_one}"
))

ErrorCatalog.register(ErrorDefinition(
    code="E701",
    name="ListeVide",
    message_tech="Opération impossible sur liste vide.",
    message_meow="😿 La gamelle est vide.",
    severity=ErrorSeverity.FAIBLE,
    mood="😿 Triste et affamé.",
    suggestion="✔ Vérifie que la liste contient des éléments avant l'opération"
))

ErrorCatalog.register(ErrorDefinition(
    code="E800",
    name="TempsNegatif",
    message_tech="La durée d'attente ne peut pas être négative : {duration}.",
    message_meow="🕰️ Le chat ne peut pas dormir dans le passé.",
    severity=ErrorSeverity.MOYENNE,
    mood="🕰️ Confus par le temps.",
    suggestion="✔ Utilise une durée positive pour 'attendre'"
))

ErrorCatalog.register(ErrorDefinition(
    code="E900",
    name="FichierIntrouvable",
    message_tech="Le fichier '{filename}' est introuvable.",
    message_meow="😾 Le chat ne retrouve pas son script '{filename}'.",
    severity=ErrorSeverity.FORTE,
    mood="😾 Énervé, cherche partout.",
    suggestion="✔ Vérifie le chemin du fichier\n✔ Vérifie que le fichier existe"
))

ErrorCatalog.register(ErrorDefinition(
    code="E901",
    name="PermissionRefusee",
    message_tech="Permission refusée pour accéder à '{filename}'.",
    message_meow="🚪 Porte fermée. Le chat n'a pas la clé.",
    severity=ErrorSeverity.FORTE,
    mood="🚪 Bloqué dehors.",
    suggestion="✔ Vérifie les permissions du fichier"
))

ErrorCatalog.register(ErrorDefinition(
    code="E902",
    name="CrashInterpreteur",
    message_tech="Erreur interne de l'interpréteur : {reason}.",
    message_meow="💥 Le chat a renversé l'interpréteur.",
    severity=ErrorSeverity.FORTE,
    mood="💥 Catastrophe totale.",
    suggestion="✔ Ceci est un bug de MeowLang\n✔ Rapporte ce problème avec ton code"
))

ErrorCatalog.register(ErrorDefinition(
    code="E999",
    name="ChatAssisSurClavier",
    message_tech="Trop d'erreurs détectées. Arrêt du parsing.",
    message_meow="🐾 Le chat s'est assis sur le clavier. Redémarrage conseillé.",
    severity=ErrorSeverity.FORTE,
    mood="🐾 Confortablement installé sur les touches.",
    suggestion="✔ Corrige les erreurs précédentes\n✔ Prends une pause café avec le chat"
))
