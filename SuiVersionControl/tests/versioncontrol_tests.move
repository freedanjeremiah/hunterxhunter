#[test_only]
module versioncontrol::repo_tests {
    use versioncontrol::repo;
    use sui::test_scenario::{Self, Scenario};
    use sui::tx_context;
    use std::vector;

    const ADMIN: address = @0xA11CE;
    const USER: address = @0xB0B;

    #[test]
    fun test_create_repo() {
        let mut scenario = test_scenario::begin(ADMIN);
        let ctx = test_scenario::ctx(&mut scenario);
        
        // Create repository
        repo::create_repo(b"test-repo", ctx);
        
        test_scenario::end(scenario);
    }

    #[test]
    fun test_commit_functionality() {
        let mut scenario = test_scenario::begin(ADMIN);
        
        // First transaction: create repository
        test_scenario::next_tx(&mut scenario, ADMIN);
        {
            let ctx = test_scenario::ctx(&mut scenario);
            repo::create_repo(b"test-repo", ctx);
        };
        
        // Second transaction: test commit
        test_scenario::next_tx(&mut scenario, USER);
        {
            let mut repo_obj = test_scenario::take_shared<repo::Repository>(&scenario);
            let ctx = test_scenario::ctx(&mut scenario);
            
            // Check initial count
            assert!(repo::get_commit_count(&repo_obj) == 0, 0);
            
            // Make a commit
            repo::commit(&mut repo_obj, ctx);
            
            // Check updated count
            assert!(repo::get_commit_count(&repo_obj) == 1, 1);
            
            test_scenario::return_shared(repo_obj);
        };
        
        test_scenario::end(scenario);
    }

    #[test]
    fun test_commit_with_entry_and_history() {
        let mut scenario = test_scenario::begin(ADMIN);

        // Tx1: create repository
        test_scenario::next_tx(&mut scenario, ADMIN);
        {
            let ctx = test_scenario::ctx(&mut scenario);
            repo::create_repo(b"test-repo", ctx);
        };

        // Tx2: append first entry
        test_scenario::next_tx(&mut scenario, USER);
        {
            let mut repo_obj = test_scenario::take_shared<repo::Repository>(&scenario);
            let ctx = test_scenario::ctx(&mut scenario);

            // Initially, no entries
            assert!(repo::entries_len(&repo_obj) == 0, 10);

            // Commit with entry "blob1"
            repo::commit_with_entry(&mut repo_obj, b"blob1", ctx);
            assert!(repo::entries_len(&repo_obj) == 1, 11);
            assert!(repo::get_commit_count(&repo_obj) == 1, 12);

            // Verify last_entry == "blob1" (check a couple of bytes)
            let last = repo::last_entry(&repo_obj);
            assert!(vector::length(last) == 5, 13);
            assert!(*vector::borrow(last, 0) == b"b"[0], 14);
            assert!(*vector::borrow(last, 4) == b"1"[0], 15);

            test_scenario::return_shared(repo_obj);
        };

        // Tx3: append second entry and verify ordering
        test_scenario::next_tx(&mut scenario, USER);
        {
            let mut repo_obj = test_scenario::take_shared<repo::Repository>(&scenario);
            let ctx = test_scenario::ctx(&mut scenario);

            repo::commit_with_entry(&mut repo_obj, b"blob2", ctx);
            assert!(repo::entries_len(&repo_obj) == 2, 16);
            assert!(repo::get_commit_count(&repo_obj) == 2, 17);

            let last = repo::last_entry(&repo_obj);
            assert!(vector::length(last) == 5, 18);
            assert!(*vector::borrow(last, 4) == b"2"[0], 19);

            // entry_at(0) should be "blob1"
            let first = repo::entry_at(&repo_obj, 0);
            assert!(*vector::borrow(first, 4) == b"1"[0], 20);

            test_scenario::return_shared(repo_obj);
        };

        test_scenario::end(scenario);
    }
}
