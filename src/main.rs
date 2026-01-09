use meowlang::run_file;
use std::env;
use std::process;

fn main() {
    let args: Vec<String> = env::args().collect();
    
    if args.len() < 2 {
        eprintln!("🐱 MeowLang - Un langage élégant, félin et francophone");
        eprintln!();
        eprintln!("Usage: meowlang <fichier.miaou>");
        eprintln!();
        eprintln!("Exemple:");
        eprintln!("  meowlang hello.miaou");
        process::exit(1);
    }
    
    let filename = &args[1];
    
    if let Err(error) = run_file(filename) {
        eprintln!("{}", error);
        process::exit(1);
    }
}
