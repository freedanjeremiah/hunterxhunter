module versioncontrol::repo {
    use sui::object::{Self, UID};
    use sui::tx_context::TxContext;
    use sui::transfer;
    use std::vector;

    /// Repository object for version control
    struct Repository has key {
        id: UID,
        name: vector<u8>,
        commit_count: u64,
        owner: address,
        /// Ordered log of entries (e.g., Walrus blob IDs). Newest is at the end.
        entries: vector<vector<u8>>,
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
            owner: sui::tx_context::sender(ctx),
            entries: vector::empty<vector<u8>>()
        };
        transfer::share_object(repo);
    }

    /// Increment commit count (simulating a commit)
    public entry fun commit(repo: &mut Repository, _ctx: &mut TxContext) {
        repo.commit_count = repo.commit_count + 1;
    }

    /// Append a new entry to history (e.g., Walrus blob ID). This implicitly
    /// points to the previous entry by its index (len-2).
    public entry fun commit_with_entry(
        repo: &mut Repository,
        entry: vector<u8>,
        _ctx: &mut TxContext
    ) {
        vector::push_back(&mut repo.entries, entry);
        repo.commit_count = repo.commit_count + 1;
    }

    /// Get the current commit count
    public fun get_commit_count(repo: &Repository): u64 {
        repo.commit_count
    }

    /// Get repository owner
    public fun get_owner(repo: &Repository): address {
        repo.owner
    }

    /// Get the total number of entries stored
    public fun entries_len(repo: &Repository): u64 {
        vector::length(&repo.entries)
    }

    /// Borrow the last entry (fails if no entries exist)
    public fun last_entry(repo: &Repository): &vector<u8> {
        let len = vector::length(&repo.entries);
        assert!(len > 0, 0);
        vector::borrow(&repo.entries, len - 1)
    }

    /// Borrow an entry at a specific index (0-based)
    public fun entry_at(repo: &Repository, idx: u64): &vector<u8> {
        vector::borrow(&repo.entries, idx)
    }
}
