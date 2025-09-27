module versioncontrol::repo {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;
    use sui::transfer;

    /// Simple repository object
    struct Repository has key {
        id: UID,
        name: vector<u8>,
        commit_count: u64,
    }

    /// Create a new repository
    public entry fun create_repo(
        name: vector<u8>,
        ctx: &mut TxContext
    ) {
        let repo = Repository {
            id: object::new(ctx),
            name,
            commit_count: 0,
        };
        transfer::share_object(repo);
    }

    /// Get the current commit count
    public fun get_commit_count(repo: &Repository): u64 {
        repo.commit_count
    }
}
