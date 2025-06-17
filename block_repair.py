#!/usr/bin/env python3
"""
Block Repair Functionality for DGLA Blockchain
"""

import logging
import datetime
from typing import List, Dict, Tuple
from key_fix import FixedKeyStore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - Rogers5G-Repair - %(levelname)s - %(message)s'
)
logger = logging.getLogger('Rogers5G-Repair')

class SelfHealingBlockchain(FixedKeyStore):
    """Blockchain with self-healing capabilities"""
    
    def __init__(self):
        """Initialize with fixed keys"""
        super().__init__()
        self.repair_history = []
        
    def detect_tampered_blocks(self) -> List[int]:
        """Find blocks that have been tampered with"""
        tampered_blocks = []
        
        # Skip genesis block (index 0)
        for i in range(1, len(self.blockchain.chain)):
            block = self.blockchain.chain[i]
            prev_block = self.blockchain.chain[i-1]
            
            # Check block hash
            if block.hash != block.calculate_hash():
                tampered_blocks.append(i)
                continue
                
            # Check link to previous block
            if block.previous_hash != prev_block.hash:
                tampered_blocks.append(i)
                
        return tampered_blocks
            
    def repair_blockchain(self) -> Tuple[bool, str, List[int]]:
        """Repair tampered blocks by recalculating hashes"""
        tampered_blocks = self.detect_tampered_blocks()
        
        if not tampered_blocks:
            return True, "No repairs needed", []
            
        # Start repair at earliest tampered block
        start_idx = min(tampered_blocks) 
        repaired = []
        
        # Repair each block and subsequent ones to maintain chain
        for i in range(start_idx, len(self.blockchain.chain)):
            if i == 0:  # Skip genesis
                continue
                
            block = self.blockchain.chain[i]
            prev_block = self.blockchain.chain[i-1]
            
            # Update previous hash
            block.previous_hash = prev_block.hash
            
            # Recalculate hash and mine to difficulty
            block.hash = block.calculate_hash()
            block.mine_block(self.blockchain.difficulty)
            
            repaired.append(i)
            logger.info(f"Repaired block {i}, new hash: {block.hash[:10]}...")
            
        # Log the repair
        self.repair_history.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "blocks_repaired": repaired
        })
        
        return True, f"Successfully repaired {len(repaired)} blocks", repaired
            
    def get_repair_history(self) -> List[Dict]:
        """Get history of blockchain repairs"""
        return self.repair_history

def test_block_repair():
    """Demo the block repair functionality"""
    print("\n🔧 Testing DGLA Blockchain Auto-Repair")
    print("===================================\n")
    
    # Create self-healing store
    store = SelfHealingBlockchain()
    
    # Add test data
    print("1. Creating network slices...")
    store.store_network_slice({"slice_id": "emergency-1", "priority": 100})
    store.store_network_slice({"slice_id": "consumer-1", "priority": 50})
    print("  ✓ Added slices to blockchain\n")
    
    # Initial verification
    print("2. Verifying initial blockchain...")
    valid, message = store.verify_integrity()
    print(f"  {'✓' if valid else '✗'} Initial state: {message}\n")
    
    # Tamper with a block
    print("3. Simulating attack by tampering with block 1...")
    store.blockchain.chain[1].data["entries"][0]["content"]["priority"] = 30
    valid, message = store.verify_integrity()
    print(f"  {'✓' if valid else '✗'} Post-attack: {message}\n")
    
    # Repair the chain
    print("4. Auto-repairing the blockchain...")
    success, repair_msg, blocks = store.repair_blockchain()
    print(f"  {'✓' if success else '✗'} {repair_msg}")
    if blocks:
        print(f"  ✓ Repaired blocks: {blocks}\n")
    
    # Verify repair fixed the issue
    print("5. Verifying blockchain after repair...")
    valid, message = store.verify_integrity()
    print(f"  {'✓' if valid else '✗'} Post-repair: {message}\n")
    
    # Show repair history
    history = store.get_repair_history()
    if history:
        print("6. Repair history:")
        for entry in history:
            blocks = entry["blocks_repaired"]
            time = entry["timestamp"]
            print(f"  - {time}: Repaired {len(blocks)} block(s)")
    
if __name__ == "__main__":
    test_block_repair()
