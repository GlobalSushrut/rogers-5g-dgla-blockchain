#!/usr/bin/env python3
"""
Simple Key Verification Fix for DGLA Blockchain
"""

from dgla_blockchain_store import DGLABlockchain, DGLADataStore

class FixedKeyStore(DGLADataStore):
    def __init__(self):
        super().__init__()
        # Fix the shared keys with correct deterministic values
        self.blockchain.shared_keys = {
            "primary": "NB_KEY_5G_PRIMARY_12345",
            "secondary": "NB_KEY_5G_SECONDARY_67890",
            "verification": "NB_KEY_5G_VERIFICATION_ABCDE"  # Fixed key name
        }
        
    def verify_integrity(self):
        """Override with correct implementation"""
        try:
            valid, message = self.blockchain.verify_chain_integrity()
            self.verification_state = valid
            return valid, message
        except Exception as e:
            self.verification_state = False
            return False, f"Error verifying: {str(e)}"

def test_key_fix():
    """Test the key fix"""
    print("🔑 Testing DGLA Blockchain Key Fix")
    print("==============================\n")
    
    # Create fixed store
    store = FixedKeyStore()
    
    # Add data
    print("1. Adding network slice...")
    store.store_network_slice({"slice_id": "emergency-1", "priority": 100})
    
    # Verify integrity
    print("\n2. Verifying blockchain integrity...")
    valid, message = store.verify_integrity()
    print(f"  {'✓' if valid else '✗'} Chain integrity: {message}")

if __name__ == "__main__":
    test_key_fix()
