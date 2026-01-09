use colored::*;
use std::fmt;

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ErrorSeverity {
    Faible,
    Moyenne,
    Forte,
}

impl ErrorSeverity {
    pub fn emoji(&self) -> &str {
        match self {
            ErrorSeverity::Faible => "😺",
            ErrorSeverity::Moyenne => "😾",
            ErrorSeverity::Forte => "🙀",
        }
    }
    
    pub fn label(&self) -> &str {
        match self {
            ErrorSeverity::Faible => "FAIBLE",
            ErrorSeverity::Moyenne => "MOYENNE",
            ErrorSeverity::Forte => "FORTE",
        }
    }
}

#[derive(Debug, Clone)]
pub struct ErrorDefinition {
    pub code: &'static str,
    pub name: &'static str,
    pub message_tech: &'static str,
    pub message_meow: &'static str,
    pub severity: ErrorSeverity,
    pub mood: &'static str,
    pub suggestion: &'static str,
    pub example: &'static str,
}

#[derive(Debug)]
pub struct MeowLangError {
    pub error_def: ErrorDefinition,
    pub file: String,
    pub line: usize,
    pub column: usize,
    pub instruction: String,
    pub context_lines: Vec<String>,
    pub extra_info: Vec<(String, String)>,
}

impl MeowLangError {
    pub fn new(error_def: ErrorDefinition, file: String, line: usize, column: usize) -> Self {
        MeowLangError {
            error_def,
            file,
            line,
            column,
            instruction: String::new(),
            context_lines: Vec::new(),
            extra_info: Vec::new(),
        }
    }
    
    pub fn with_instruction(mut self, instruction: String) -> Self {
        self.instruction = instruction;
        self
    }
    
    pub fn with_context(mut self, source_lines: &[String]) -> Self {
        self.context_lines = extract_context(source_lines, self.line);
        self
    }
    
    pub fn with_extra(mut self, key: String, value: String) -> Self {
        self.extra_info.push((key, value));
        self
    }
    
    fn format_message(&self, template: &str) -> String {
        let mut message = template.to_string();
        for (key, value) in &self.extra_info {
            message = message.replace(&format!("{{{}}}", key), value);
        }
        message
    }
}

impl fmt::Display for MeowLangError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let emoji = self.error_def.severity.emoji();
        let severity = self.error_def.severity.label();
        
        writeln!(f)?;
        writeln!(f, "{} ERREUR MEOWLANG [{}] — GRIFFURE {}", emoji, self.error_def.code.yellow().bold(), severity.red().bold())?;
        writeln!(f)?;
        writeln!(f, "Fichier      : {}", self.file.cyan())?;
        writeln!(f, "Ligne        : {}", self.line.to_string().cyan())?;
        writeln!(f, "Colonne      : {}", self.column.to_string().cyan())?;
        
        if !self.instruction.is_empty() {
            writeln!(f, "Instruction  : {}", self.instruction.yellow())?;
        }
        
        writeln!(f)?;
        writeln!(f, "Type         : {}", self.error_def.name.red().bold())?;
        writeln!(f)?;
        writeln!(f, "Message technique :")?;
        writeln!(f, "{}", self.format_message(self.error_def.message_tech))?;
        writeln!(f)?;
        writeln!(f, "Message MeowLang 🐱 :")?;
        writeln!(f, "{}", self.format_message(self.error_def.message_meow))?;
        
        if !self.context_lines.is_empty() {
            writeln!(f)?;
            writeln!(f, "Contexte :")?;
            for line_text in &self.context_lines {
                writeln!(f, "{}", line_text)?;
            }
        }
        
        writeln!(f)?;
        writeln!(f, "État du chat :")?;
        writeln!(f, "{}", self.error_def.mood)?;
        
        if !self.error_def.suggestion.is_empty() {
            writeln!(f)?;
            writeln!(f, "Suggestion du chat 💡 :")?;
            writeln!(f, "{}", self.format_message(self.error_def.suggestion).green())?;
        }
        
        if !self.error_def.example.is_empty() {
            writeln!(f)?;
            writeln!(f, "Exemple recommandé :")?;
            writeln!(f, "{}", self.format_message(self.error_def.example).bright_blue())?;
        }
        
        writeln!(f)?;
        writeln!(f, "Fin du jugement.")?;
        writeln!(f, "Le chat te surveille.")?;
        writeln!(f)?;
        
        Ok(())
    }
}

impl std::error::Error for MeowLangError {}

fn extract_context(source_lines: &[String], error_line: usize) -> Vec<String> {
    let context_size = 2;
    let start = error_line.saturating_sub(context_size).max(1);
    let end = (error_line + context_size).min(source_lines.len());
    
    let mut context = Vec::new();
    for line_no in start..=end {
        if line_no > 0 && line_no <= source_lines.len() {
            let prefix = if line_no == error_line { "> " } else { "  " };
            let line_text = &source_lines[line_no - 1];
            context.push(format!("{}  {:3} | {}", prefix, line_no, line_text));
        }
    }
    context
}

macro_rules! error_def {
    ($code:expr, $name:expr, $tech:expr, $meow:expr, $sev:expr, $mood:expr) => {
        ErrorDefinition {
            code: $code,
            name: $name,
            message_tech: $tech,
            message_meow: $meow,
            severity: $sev,
            mood: $mood,
            suggestion: "",
            example: "",
        }
    };
    ($code:expr, $name:expr, $tech:expr, $meow:expr, $sev:expr, $mood:expr, $sugg:expr) => {
        ErrorDefinition {
            code: $code,
            name: $name,
            message_tech: $tech,
            message_meow: $meow,
            severity: $sev,
            mood: $mood,
            suggestion: $sugg,
            example: "",
        }
    };
    ($code:expr, $name:expr, $tech:expr, $meow:expr, $sev:expr, $mood:expr, $sugg:expr, $ex:expr) => {
        ErrorDefinition {
            code: $code,
            name: $name,
            message_tech: $tech,
            message_meow: $meow,
            severity: $sev,
            mood: $mood,
            suggestion: $sugg,
            example: $ex,
        }
    };
}

pub struct ErrorCatalog;

impl ErrorCatalog {
    pub fn get(code: &str) -> ErrorDefinition {
        match code {
            "E000" => error_def!(
                "E000", "ScriptSansMiaou",
                "Le script doit commencer par 'miaou'.",
                "😾 Le chat refuse d'entrer sans un \"miaou\" au début.",
                ErrorSeverity::Forte,
                "😾 En colère, refuse d'entrer.",
                "✔ Ajoute 'miaou' au tout début du fichier",
                "  miaou\n  ecrire \"Hello!\"\n  meow"
            ),
            "E001" => error_def!(
                "E001", "ScriptSansMeow",
                "Le script doit se terminer par 'meow'.",
                "💤 Le chat s'est endormi avant le \"meow\" final.",
                ErrorSeverity::Forte,
                "💤 Endormi, perdu dans ses rêves.",
                "✔ Ajoute 'meow' à la toute fin du fichier",
                "  miaou\n  ecrire \"Hello!\"\n  meow"
            ),
            "E002" => error_def!(
                "E002", "MeowPremature",
                "Le mot-clé 'meow' apparaît avant la fin du script.",
                "🪟 Le chat est sorti trop tôt par la fenêtre.",
                ErrorSeverity::Moyenne,
                "😼 Pressé, déjà dehors.",
                "✔ Place 'meow' uniquement à la fin du script",
                "  miaou\n  # ton code ici\n  meow"
            ),
            "E004" => error_def!(
                "E004", "FichierVide",
                "Le fichier est vide.",
                "😿 Le carton est vide.",
                ErrorSeverity::Moyenne,
                "😿 Déçu et triste.",
                "✔ Ajoute du code dans le fichier"
            ),
            "E100" => error_def!(
                "E100", "InstructionInconnue",
                "Instruction ou mot-clé non reconnu.",
                "😿 Le chat ne comprend pas ce mot.",
                ErrorSeverity::Moyenne,
                "😿 Perplexe, tête penchée.",
                "✔ Vérifie l'orthographe de l'instruction\n✔ Consulte la liste des mots-clés valides"
            ),
            "E101" => error_def!(
                "E101", "GuillemetManquant",
                "Guillemet de fermeture manquant pour une chaîne de caractères.",
                "🧶 La pelote de laine n'est pas fermée (guillemet manquant).",
                ErrorSeverity::Moyenne,
                "🧶 Distrait, joue avec la pelote.",
                "✔ Ajoute un guillemet \" à la fin de la chaîne",
                "  texte = \"Bonjour le chat\""
            ),
            "E102" => error_def!(
                "E102", "ParentheseManquante",
                "Parenthèse manquante dans une expression.",
                "🐈 Une patte dépasse. Parenthèse manquante.",
                ErrorSeverity::Moyenne,
                "🐈 Inconfortable, une patte en l'air.",
                "✔ Vérifie que chaque '(' a son ')'",
                "  resultat = (3 + 5) * 2"
            ),
            "E103" => error_def!(
                "E103", "IndentationFautive",
                "Indentation incorrecte détectée.",
                "😾 Le chat n'aime pas les lignes mal alignées.",
                ErrorSeverity::Moyenne,
                "😾 Agacé par le désordre.",
                "✔ Utilise des espaces cohérents pour l'indentation\n✔ Évite de mélanger espaces et tabulations",
                "  si age > 10 alors:\n    ecrire \"OK\"  # 2 ou 4 espaces d'indentation"
            ),
            "E104" => error_def!(
                "E104", "MotCleManquant",
                "Mot-clé attendu manquant.",
                "🧐 Il manque un mot magique.",
                ErrorSeverity::Moyenne,
                "🧐 Attend quelque chose.",
                "✔ Vérifie la syntaxe complète de l'instruction"
            ),
            "E200" => error_def!(
                "E200", "VariableInexistante",
                "Variable '{var_name}' non définie.",
                "🐾 Ce chat '{var_name}' n'existe pas dans la maison.",
                ErrorSeverity::Moyenne,
                "🐾 Cherche partout, ne trouve rien.",
                "✔ Vérifie l'orthographe de la variable\n✔ Définis la variable avant de l'utiliser",
                "  {var_name} = 42\n  ecrire {var_name}"
            ),
            "E202" => error_def!(
                "E202", "TypeIncompatible",
                "Opération impossible entre types incompatibles : {type1} et {type2}.",
                "🐟 Mauvaise gamelle pour ce repas. Types {type1} et {type2} incompatibles.",
                ErrorSeverity::Moyenne,
                "😿 Dégoûté par la gamelle.",
                "✔ Vérifie les types de tes variables\n✔ Convertis si nécessaire"
            ),
            "E300" => error_def!(
                "E300", "ConditionInvalide",
                "La condition n'est pas valide ou est mal formée.",
                "🤨 Cette condition n'a aucun sens.",
                ErrorSeverity::Moyenne,
                "🤨 Sourcil levé, dubitatif.",
                "✔ Vérifie la syntaxe de la condition\n✔ Utilise des opérateurs valides : =, !=, <, >, <=, >=, et, ou"
            ),
            "E301" => error_def!(
                "E301", "SinonSansSi",
                "'sinon' ou 'sinon si' sans 'si' correspondant.",
                "😾 Le chat répond \"sinon\" sans qu'on lui ait posé de question.",
                ErrorSeverity::Moyenne,
                "😾 Confus et agacé.",
                "✔ Place 'sinon' après un bloc 'si'"
            ),
            "E500" => error_def!(
                "E500", "DivisionParZero",
                "Division par zéro impossible.",
                "🚫 Partager des croquettes entre zéro chat est strictement interdit.",
                ErrorSeverity::Moyenne,
                "😾 Agacé, oreilles en arrière, queue en fouet.",
                "✔ Vérifie que le diviseur est différent de 0\n✔ Ajoute une condition avant le calcul",
                "  si nombre != 0 alors:\n    ecrire 10 / nombre\n  sinon:\n    ecrire \"Même le chat ne peut pas faire ça.\""
            ),
            "E600" => error_def!(
                "E600", "FonctionInconnue",
                "La fonction '{func_name}' n'existe pas.",
                "😿 Ce tour félin '{func_name}' n'existe pas.",
                ErrorSeverity::Moyenne,
                "😿 Désolé, ne connaît pas ce tour.",
                "✔ Vérifie le nom de la fonction\n✔ Définis la fonction avant de l'appeler"
            ),
            "E601" => error_def!(
                "E601", "ArgumentsInvalides",
                "Nombre d'arguments incorrect : attendu {expected}, reçu {received}.",
                "🐾 Le chat attend {expected} caresse(s), pas {received}.",
                ErrorSeverity::Moyenne,
                "🐾 Insatisfait du nombre de caresses.",
                "✔ Vérifie le nombre d'arguments passés à la fonction"
            ),
            "E700" => error_def!(
                "E700", "IndexHorsLimite",
                "Index {index} hors limites pour liste de taille {size}.",
                "🐈 Tu cherches un chat qui n'est pas dans la portée (index {index}).",
                ErrorSeverity::Moyenne,
                "🐈 Cherche dans le vide.",
                "✔ Vérifie que l'index est entre 0 et {size_minus_one}",
                "  # Pour une liste de taille {size}, utilise index 0 à {size_minus_one}"
            ),
            "E800" => error_def!(
                "E800", "TempsNegatif",
                "La durée d'attente ne peut pas être négative : {duration}.",
                "🕰️ Le chat ne peut pas dormir dans le passé.",
                ErrorSeverity::Moyenne,
                "🕰️ Confus par le temps.",
                "✔ Utilise une durée positive pour 'attendre'"
            ),
            "E900" => error_def!(
                "E900", "FichierIntrouvable",
                "Le fichier '{filename}' est introuvable.",
                "😾 Le chat ne retrouve pas son script '{filename}'.",
                ErrorSeverity::Forte,
                "😾 Énervé, cherche partout.",
                "✔ Vérifie le chemin du fichier\n✔ Vérifie que le fichier existe"
            ),
            "E902" => error_def!(
                "E902", "CrashInterpreteur",
                "Erreur interne de l'interpréteur : {reason}.",
                "💥 Le chat a renversé l'interpréteur.",
                ErrorSeverity::Forte,
                "💥 Catastrophe totale.",
                "✔ Ceci est un bug de MeowLang\n✔ Rapporte ce problème avec ton code"
            ),
            "E999" => error_def!(
                "E999", "ChatAssisSurClavier",
                "Trop d'erreurs détectées. Arrêt du parsing.",
                "🐾 Le chat s'est assis sur le clavier. Redémarrage conseillé.",
                ErrorSeverity::Forte,
                "🐾 Confortablement installé sur les touches.",
                "✔ Corrige les erreurs précédentes\n✔ Prends une pause café avec le chat"
            ),
            _ => error_def!(
                "E902", "CrashInterpreteur",
                "Erreur interne de l'interpréteur.",
                "💥 Le chat a renversé l'interpréteur.",
                ErrorSeverity::Forte,
                "💥 Catastrophe totale.",
                "✔ Ceci est un bug de MeowLang"
            ),
        }
    }
}
