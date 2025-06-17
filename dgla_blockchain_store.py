#!/usr/bin/env python3
"""
DGLA Blockchain Storage Implementation
-------------------------------------

This module demonstrates the internal workings of how the DGLA infrastructure 
stores and verifies data using blockchain technology for the Rogers 5G demos.
"""

import time
import hashlib
import json
import datetime
import uuid
import base64
from typing import Dict, List, Any, Tuple, Optional

class Block:
    """A single block in the DGLA blockchain"""
    
    def __init__(self, 
                 index: int, 
                 timestamp: str, 
                 data: Dict[str, Any], 
                 previous_hash: str,
                 nonce: int = 0):
        """Initialize a new block
        
        Args:
            index: Block position in the chain
            timestamp: ISO timestamp of block creation
            data: Payload data stored in the block
            previous_hash: Hash of the previous block
            nonce: Value used for mining/verification
        """
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()
        
    def calculate_hash(self) -> str:
        """Calculate cryptographic hash of this block
        
        Returns:
            str: SHA-256 hash of the block contents
        """
        block_contents = {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }
        block_string = json.dumps(block_contents, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int = 2) -> None:
        """Mine the block by finding a hash with leading zeros
        
        Args:
            difficulty: Number of leading zeros required
        """
        target = '0' * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary representation
        
        Returns:
            Dict: Block as a dictionary
        """
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash
        }

class DGLABlockchain:
    """Blockchain implementation for DGLA data storage"""
    
    def __init__(self, difficulty: int = 2):
        """Initialize a new DGLA blockchain
        
        Args:
            difficulty: Mining difficulty (leading zeros)
        """
        self.difficulty = difficulty
        self.chain: List[Block] = []
        self.pending_data: List[Dict[str, Any]] = []
        
        # Create genesis block
        self.create_genesis_block()
        
        # For demo: Use deterministic shared keys
        self.shared_keys = {
            "primary": "NB_KEY_5G_PRIMARY_12345",
            "secondary": "NB_KEY_5G_SECONDARY_67890",
            "verification": "NB_KEY_5G_VERIFY_ABCDE"
        }
    
    def create_genesis_block(self) -> None:
        """Create the first block in the chain"""
        genesis_block = Block(
            index=0,
            timestamp=datetime.datetime.now().isoformat(),
            data={"message": "DGLA Genesis Block", "source": "Rogers 5G Security System"},
            previous_hash="0"
        )
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)
    
    def get_latest_block(self) -> Block:
        """Get the most recent block in the chain
        
        Returns:
            Block: Latest block
        """
        return self.chain[-1]
    
    def add_data(self, data: Dict[str, Any]) -> str:
        """Add data to pending queue for next block
        
        Args:
            data: Data to store in blockchain
            
        Returns:
            str: Data ID
        """
        data_id = str(uuid.uuid4())
        data["data_id"] = data_id
        data["timestamp"] = datetime.datetime.now().isoformat()
        self.pending_data.append(data)
        return data_id
    
    def mine_pending_data(self) -> Optional[Block]:
        """Mine a new block with all pending data
        
        Returns:
            Block: Newly mined block or None if no pending data
        """
        if not self.pending_data:
            return None
            
        # Create combined data object with all pending items
        combined_data = {
            "entries": self.pending_data,
            "merkle_root": self._calculate_merkle_root(self.pending_data)
        }
        
        # Create and mine new block
        latest_block = self.get_latest_block()
        new_block = Block(
            index=latest_block.index + 1,
            timestamp=datetime.datetime.now().isoformat(),
            data=combined_data,
            previous_hash=latest_block.hash
        )
        new_block.mine_block(self.difficulty)
        
        # Add to chain and clear pending data
        self.chain.append(new_block)
        self.pending_data = []
        
        return new_block
    
    def verify_chain_integrity(self) -> Tuple[bool, str]:
        """Verify the integrity of the entire blockchain
        
        This is the correct verification method that was missing in the
        original implementation, replacing the non-existent verify_chain()
        
        Returns:
            tuple: (is_valid, message)
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # Verify current block hash
            if current_block.hash != current_block.calculate_hash():
                return (False, f"Block {i} hash invalid")
            
            # Verify connection to previous block
            if current_block.previous_hash != previous_block.hash:
                return (False, f"Block {i} not connected to previous block")
                
        # For demo, also verify the deterministic shared keys
        for key_name, key_value in self.shared_keys.items():
            expected_value = f"NB_KEY_5G_{key_name.upper()}_"
            if not key_value.startswith(expected_value):
                return (False, f"Shared key {key_name} has been tampered with")
        
        return (True, "Ledger verification successful")
    
    def get_data_by_id(self, data_id: str) -> Optional[Dict[str, Any]]:
        """Find data in the blockchain by its ID
        
        Args:
            data_id: ID of the data to find
            
        Returns:
            Dict: The data if found, None otherwise
        """
        # Search through all blocks
        for block in self.chain:
            if "entries" not in block.data:
                continue
                
            for entry in block.data["entries"]:
                if entry.get("data_id") == data_id:
                    return entry
        
        return None
    
    def _calculate_merkle_root(self, data_list: List[Dict[str, Any]]) -> str:
        """Calculate a merkle root hash for a list of data items
        
        Args:
            data_list: List of data dictionaries
            
        Returns:
            str: Merkle root hash
        """
        # Convert data items to strings and hash them
        hashes = [hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
                 for data in data_list]
                 
        # If odd number of hashes, duplicate the last one
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])
            
        # Combine hashes until we get a single root hash
        while len(hashes) > 1:
            new_hashes = []
            for i in range(0, len(hashes), 2):
                combined = hashes[i] + hashes[i+1]
                new_hash = hashlib.sha256(combined.encode()).hexdigest()
                new_hashes.append(new_hash)
            hashes = new_hashes
            
            # If odd number of hashes, duplicate the last one
            if len(hashes) % 2 == 1 and len(hashes) > 1:
                hashes.append(hashes[-1])
        
        return hashes[0]
    
    def get_chain_data(self) -> List[Dict[str, Any]]:
        """Get the entire blockchain as a list of dictionaries
        
        Returns:
            List[Dict]: The blockchain
        """
        return [block.to_dict() for block in self.chain]
        
    def tamper_with_block(self, index: int, new_data: Dict[str, Any]) -> bool:
        """Deliberately tamper with a block for demo purposes
        
        Args:
            index: Index of the block to tamper with
            new_data: New data to inject
            
        Returns:
            bool: True if tampering was successful
        """
        if index < 0 or index >= len(self.chain):
            return False
            
        # Modify the block data without updating its hash
        if "entries" in self.chain[index].data:
            if self.chain[index].data["entries"]:
                self.chain[index].data["entries"][0].update(new_data)
        else:
            self.chain[index].data.update(new_data)
            
        return True

class DGLADataStore:
    """Interface to DGLA data storage system using blockchain"""
    
    def __init__(self):
        """Initialize a new DGLA data store"""
        self.blockchain = DGLABlockchain()
        self.verification_state = None
        
    def store_network_slice(self, slice_data: Dict[str, Any]) -> str:
        """Store network slice in the blockchain
        
        Args:
            slice_data: Network slice configuration
            
        Returns:
            str: Data ID for the stored slice
        """
        # Add cryptographic signature
        signed_data = self._sign_data(slice_data)
        
        # Add to blockchain
        data_id = self.blockchain.add_data({
            "type": "network_slice",
            "content": signed_data,
            "metadata": {
                "source": "Rogers 5G Security System",
                "category": "network_configuration",
                "version": "1.0"
            }
        })
        
        # Mine the block
        self.blockchain.mine_pending_data()
        
        return data_id
        
    def retrieve_network_slice(self, slice_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a network slice by its ID
        
        Args:
            slice_id: ID of the slice
            
        Returns:
            Dict: The slice data if found
        """
        # Search for the slice in all blockchain data
        for block in self.blockchain.chain:
            if "entries" not in block.data:
                continue
                
            for entry in block.data["entries"]:
                if entry.get("type") != "network_slice":
                    continue
                    
                content = entry.get("content", {})
                if content.get("slice_id") == slice_id:
                    return self._verify_signed_data(content)
                    
        return None
        
    def verify_integrity(self) -> Tuple[bool, str]:
        """Verify the integrity of all stored data
        
        Returns:
            tuple: (is_valid, message)
        """
        # Set initial verification state to avoid UI issues on first load
        if self.verification_state is None:
            self.verification_state = True
            
        try:
            # Using correct verify_chain_integrity() method
            valid, message = self.blockchain.verify_chain_integrity()
            self.verification_state = valid
            return (valid, message)
        except Exception as e:
            # Proper error handling with detailed logging
            self.verification_state = False
            return (False, f"Error verifying ledger: {str(e)}")
        
    def _sign_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cryptographically sign data using shared keys
        
        Args:
            data: Data to sign
            
        Returns:
            Dict: Signed data
        """
        # Create a copy of the data
        signed_data = data.copy()
        
        # Create signature using verification key
        data_string = json.dumps(data, sort_keys=True)
        signature_data = data_string + self.blockchain.shared_keys["verification"]
        signature = hashlib.sha256(signature_data.encode()).hexdigest()
        
        # Add signature to data
        signed_data["signature"] = signature
        signed_data["signed_at"] = datetime.datetime.now().isoformat()
        
        return signed_data
        
    def _verify_signed_data(self, signed_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Verify the signature of data
        
        Args:
            signed_data: Data with signature
            
        Returns:
            Dict: The verified data or None if invalid
        """
        # Create a copy without signature and signed_at
        data_to_verify = {k: v for k, v in signed_data.items() 
                          if k not in ["signature", "signed_at"]}
                          
        # Recreate signature
        data_string = json.dumps(data_to_verify, sort_keys=True)
        signature_data = data_string + self.blockchain.shared_keys["verification"]
        expected_signature = hashlib.sha256(signature_data.encode()).hexdigest()
        
        # Verify signature
        if signed_data.get("signature") != expected_signature:
            return None
            
        return signed_data

# Example usage of the DGLA blockchain store
if __name__ == "__main__":
    # Create store
    store = DGLADataStore()
    
    # Store a network slice
    slice_id = store.store_network_slice({
        "slice_id": "emergency-12345",
        "type_name": "emergency",
        "priority": 100,
        "resources": {
            "bandwidth": 500,
            "latency": 5
        }
    })
    
    print(f"Stored network slice with ID: {slice_id}")
    
    # Verify integrity
    valid, message = store.verify_integrity()
    print(f"Blockchain integrity: {valid}, {message}")
    
    # Tamper with the blockchain
    store.blockchain.tamper_with_block(1, {"priority": 50})
    print("Tampered with blockchain data")
    
    # Verify integrity again
    valid, message = store.verify_integrity()
    print(f"Blockchain integrity after tampering: {valid}, {message}")
