module versioncontrol::simple_repo {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;
    use sui::transfer;
    
    /// A very basic repository structure  
    struct SimpleRepo has key {
        id: UID,
        name: vector<u8>,
    }
    
    /// Create a basic repo
    public entry fun create_simple_repo(name: vector<u8>, ctx: &mut TxContext) {
        let repo = SimpleRepo {
            id: object::new(ctx),
            name,
        };
        transfer::share_object(repo);
    }
}