"""
MongoDB Client Utility
Handles MongoDB connections and query execution
"""
from typing import Dict, List, Any, Optional
import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import logging

logger = logging.getLogger(__name__)


class MongoDBClient:
    """MongoDB client for Text-to-NoSQL system"""
    
    def __init__(self, uri: str = "mongodb://localhost:27017/", 
                 database_name: str = "tend_db",
                 timeout_ms: int = 5000):
        """
        Initialize MongoDB client
        
        Args:
            uri: MongoDB connection URI
            database_name: Default database name
            timeout_ms: Connection timeout in milliseconds
        """
        self.uri = uri
        self.database_name = database_name
        self.timeout_ms = timeout_ms
        self.client: Optional[MongoClient] = None
        self.db = None
        
    def connect(self) -> bool:
        """
        Connect to MongoDB
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.client = MongoClient(
                self.uri,
                serverSelectionTimeoutMS=self.timeout_ms
            )
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            logger.info(f"Successfully connected to MongoDB at {self.uri}")
            return True
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    def execute_query(self, query_str: str, collection_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a MongoDB query string
        
        Args:
            query_str: MongoDB query string (e.g., "db.collection.find({...})")
            collection_name: Optional collection name if not in query
            
        Returns:
            Dict with 'success', 'results', and optional 'error' keys
        """
        try:
            # Parse and execute the query
            # MongoDB queries can be in different formats:
            # 1. db.collection.find({...})
            # 2. db.collection.aggregate([...])
            # 3. db.collection.countDocuments({...})
            
            results = self._parse_and_execute(query_str)
            
            return {
                "success": True,
                "results": results,
                "count": len(results) if isinstance(results, list) else None
            }
            
        except OperationFailure as e:
            logger.error(f"Query execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": "OperationFailure"
            }
        except Exception as e:
            logger.error(f"Unexpected error executing query: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def _parse_and_execute(self, query_str: str) -> List[Dict]:
        """
        Parse and execute MongoDB query string
        
        Args:
            query_str: MongoDB query string
            
        Returns:
            List of result documents
        """
        import re
        
        # Remove trailing semicolon if present
        query_str = query_str.strip().rstrip(';')
        
        # Extract collection name
        collection_match = re.search(r'db\.(\w+)\.', query_str)
        if not collection_match:
            raise ValueError("Could not extract collection name from query")
        
        collection_name = collection_match.group(1)
        collection = self.db[collection_name]
        
        # Determine query type and execute
        if '.find(' in query_str:
            return self._execute_find(query_str, collection)
        elif '.aggregate(' in query_str:
            return self._execute_aggregate(query_str, collection)
        elif '.countDocuments(' in query_str:
            return self._execute_count(query_str, collection)
        elif '.distinct(' in query_str:
            return self._execute_distinct(query_str, collection)
        else:
            raise ValueError(f"Unsupported query type: {query_str}")
    
    def _execute_find(self, query_str: str, collection) -> List[Dict]:
        """Execute find() query"""
        import re
        
        # Extract find parameters: db.collection.find(filter, projection)
        find_match = re.search(r'\.find\((.*?)\)', query_str)
        if not find_match:
            raise ValueError("Invalid find query format")
        
        params = find_match.group(1)
        
        # Parse filter and projection
        filter_dict, projection_dict = self._parse_find_params(params)
        
        # Execute query
        cursor = collection.find(filter_dict, projection_dict)
        
        # Check for sort, limit, skip
        if '.sort(' in query_str:
            sort_match = re.search(r'\.sort\((.*?)\)', query_str)
            if sort_match:
                sort_params = eval(sort_match.group(1))
                cursor = cursor.sort(sort_params)
        
        if '.limit(' in query_str:
            limit_match = re.search(r'\.limit\((\d+)\)', query_str)
            if limit_match:
                cursor = cursor.limit(int(limit_match.group(1)))
        
        return list(cursor)
    
    def _execute_aggregate(self, query_str: str, collection) -> List[Dict]:
        """Execute aggregate() query"""
        import re
        
        # Extract aggregation pipeline
        agg_match = re.search(r'\.aggregate\((.*)\)', query_str, re.DOTALL)
        if not agg_match:
            raise ValueError("Invalid aggregate query format")
        
        pipeline_str = agg_match.group(1)
        
        # Parse pipeline (it's a JSON array)
        pipeline = eval(pipeline_str)
        
        # Execute aggregation
        cursor = collection.aggregate(pipeline)
        return list(cursor)
    
    def _execute_count(self, query_str: str, collection) -> List[Dict]:
        """Execute countDocuments() query"""
        import re
        
        count_match = re.search(r'\.countDocuments\((.*?)\)', query_str)
        if not count_match:
            raise ValueError("Invalid countDocuments query format")
        
        filter_str = count_match.group(1)
        filter_dict = eval(filter_str) if filter_str else {}
        
        count = collection.count_documents(filter_dict)
        return [{"count": count}]
    
    def _execute_distinct(self, query_str: str, collection) -> List[Dict]:
        """Execute distinct() query"""
        import re
        
        distinct_match = re.search(r'\.distinct\("([^"]+)"(?:,\s*(.*?))?\)', query_str)
        if not distinct_match:
            raise ValueError("Invalid distinct query format")
        
        field = distinct_match.group(1)
        filter_str = distinct_match.group(2)
        filter_dict = eval(filter_str) if filter_str else {}
        
        values = collection.distinct(field, filter_dict)
        return [{"values": values}]
    
    def _parse_find_params(self, params: str) -> tuple:
        """
        Parse find() parameters into filter and projection
        
        Args:
            params: Parameter string from find()
            
        Returns:
            Tuple of (filter_dict, projection_dict)
        """
        if not params or params.strip() == '':
            return {}, {}
        
        # Split by comma, but respect nested braces
        parts = []
        current = ""
        brace_count = 0
        
        for char in params:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
            elif char == ',' and brace_count == 0:
                parts.append(current.strip())
                current = ""
                continue
            current += char
        
        if current.strip():
            parts.append(current.strip())
        
        filter_dict = eval(parts[0]) if parts else {}
        projection_dict = eval(parts[1]) if len(parts) > 1 else {}
        
        return filter_dict, projection_dict
    
    def create_collection(self, collection_name: str, documents: List[Dict]):
        """
        Create a collection and insert documents
        
        Args:
            collection_name: Name of the collection
            documents: List of documents to insert
        """
        try:
            collection = self.db[collection_name]
            
            # Drop if exists
            collection.drop()
            
            # Insert documents
            if documents:
                collection.insert_many(documents)
                logger.info(f"Created collection '{collection_name}' with {len(documents)} documents")
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise
    
    def list_collections(self) -> List[str]:
        """List all collections in the database"""
        return self.db.list_collection_names()
    
    def get_collection_schema(self, collection_name: str) -> Dict[str, Any]:
        """
        Get schema information for a collection
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dict with collection schema information
        """
        collection = self.db[collection_name]
        
        # Sample a few documents to infer schema
        sample_docs = list(collection.find().limit(10))
        
        if not sample_docs:
            return {"collection": collection_name, "fields": []}
        
        # Collect all field names
        fields = set()
        for doc in sample_docs:
            fields.update(self._get_all_fields(doc))
        
        return {
            "collection": collection_name,
            "fields": sorted(list(fields))
        }
    
    def _get_all_fields(self, doc: Dict, prefix: str = "") -> List[str]:
        """Recursively get all field paths from a document"""
        fields = []
        
        for key, value in doc.items():
            field_path = f"{prefix}.{key}" if prefix else key
            fields.append(field_path)
            
            if isinstance(value, dict):
                fields.extend(self._get_all_fields(value, field_path))
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                fields.extend(self._get_all_fields(value[0], field_path))
        
        return fields
