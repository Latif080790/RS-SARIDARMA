"""
Production Logger for Auto Volume Calculator
Structured logging with file rotation, audit trail, and error tracking
"""

import logging
import logging.handlers
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path


class ProductionLogger:
    """
    Production-grade logging system with:
    - Configurable log levels
    - File rotation (max 10MB, keep 5 backups)
    - JSON-formatted audit trail
    - Error tracking and categorization
    - Console and file output
    """
    
    def __init__(
        self,
        name: str = "AutoVolumeCalculator",
        log_dir: str = "logs",
        log_level: str = "INFO",
        enable_console: bool = True,
        enable_file: bool = True,
        enable_audit: bool = True
    ):
        """
        Initialize production logger
        
        Args:
            name: Logger name
            log_dir: Directory for log files
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            enable_console: Enable console output
            enable_file: Enable file logging
            enable_audit: Enable JSON audit trail
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.enable_audit = enable_audit
        
        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize loggers
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.log_level)
        self.logger.handlers = []  # Clear existing handlers
        
        # Setup handlers
        self._setup_console_handler()
        self._setup_file_handler()
        self._setup_audit_handler()
        
        # Error tracking
        self.error_count = 0
        self.warning_count = 0
        self.errors_by_category = {}
    
    def _setup_console_handler(self):
        """Setup console output handler"""
        if not self.enable_console:
            return
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        
        # Format: [2026-01-20 15:30:45] INFO: Message
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def _setup_file_handler(self):
        """Setup rotating file handler"""
        if not self.enable_file:
            return
        
        log_file = self.log_dir / f"{self.name}.log"
        
        # Rotating file handler: max 10MB, keep 5 backups
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # Log everything to file
        
        # Detailed format for file
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def _setup_audit_handler(self):
        """Setup JSON audit trail handler"""
        if not self.enable_audit:
            return
        
        audit_file = self.log_dir / f"{self.name}_audit.jsonl"
        
        # Custom handler for JSON audit trail
        self.audit_file = open(audit_file, 'a', encoding='utf-8')
    
    def _write_audit(self, level: str, message: str, extra: Optional[Dict[str, Any]] = None):
        """Write to JSON audit trail"""
        if not self.enable_audit:
            return
        
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'logger': self.name,
            'message': message
        }
        
        if extra:
            audit_entry.update(extra)
        
        try:
            self.audit_file.write(json.dumps(audit_entry) + '\n')
            self.audit_file.flush()
        except Exception as e:
            self.logger.error(f"Failed to write audit log: {e}")
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message)
        self._write_audit('DEBUG', message, kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message)
        self._write_audit('INFO', message, kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message)
        self.warning_count += 1
        self._write_audit('WARNING', message, kwargs)
    
    def error(self, message: str, category: str = "general", **kwargs):
        """
        Log error message with categorization
        
        Args:
            message: Error message
            category: Error category (file_io, parsing, validation, calculation, etc.)
            **kwargs: Additional context for audit trail
        """
        self.logger.error(message)
        self.error_count += 1
        
        # Track by category
        self.errors_by_category[category] = self.errors_by_category.get(category, 0) + 1
        
        kwargs['category'] = category
        self._write_audit('ERROR', message, kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical error message"""
        self.logger.critical(message)
        self.error_count += 1
        self._write_audit('CRITICAL', message, kwargs)
    
    def log_operation(
        self,
        operation: str,
        status: str,
        duration_ms: Optional[float] = None,
        **kwargs
    ):
        """
        Log business operation with structured data
        
        Args:
            operation: Operation name (e.g., "grid_detection", "volume_calculation")
            status: Operation status ("started", "completed", "failed")
            duration_ms: Operation duration in milliseconds
            **kwargs: Additional operation context
        """
        message = f"Operation: {operation} | Status: {status}"
        if duration_ms:
            message += f" | Duration: {duration_ms:.2f}ms"
        
        self.info(message)
        
        # Enhanced audit entry
        audit_data = {
            'operation': operation,
            'status': status,
            'duration_ms': duration_ms
        }
        audit_data.update(kwargs)
        self._write_audit('OPERATION', message, audit_data)
    
    def log_file_processed(
        self,
        file_path: str,
        file_size: int,
        processing_time_ms: float,
        items_found: int,
        success: bool = True
    ):
        """
        Log file processing with metrics
        
        Args:
            file_path: Path to processed file
            file_size: File size in bytes
            processing_time_ms: Processing time in milliseconds
            items_found: Number of items extracted
            success: Whether processing succeeded
        """
        status = "SUCCESS" if success else "FAILED"
        message = f"File processed: {Path(file_path).name} | {status} | {items_found} items | {processing_time_ms:.0f}ms"
        
        if success:
            self.info(message)
        else:
            self.error(message, category="file_processing")
        
        # Detailed audit
        self._write_audit('FILE_PROCESSED', message, {
            'file_path': file_path,
            'file_size_bytes': file_size,
            'file_size_mb': round(file_size / (1024 * 1024), 2),
            'processing_time_ms': processing_time_ms,
            'items_found': items_found,
            'success': success
        })
    
    def log_validation_error(
        self,
        validator: str,
        error_type: str,
        details: str,
        file_path: Optional[str] = None
    ):
        """
        Log validation error with details
        
        Args:
            validator: Name of validator that failed
            error_type: Type of validation error
            details: Detailed error description
            file_path: File being validated (optional)
        """
        message = f"Validation failed: {validator} | {error_type} | {details}"
        if file_path:
            message += f" | File: {Path(file_path).name}"
        
        self.error(message, category="validation", validator=validator, error_type=error_type, details=details)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error and warning summary"""
        return {
            'total_errors': self.error_count,
            'total_warnings': self.warning_count,
            'errors_by_category': self.errors_by_category
        }
    
    def print_summary(self):
        """Print error/warning summary"""
        if self.error_count > 0 or self.warning_count > 0:
            print(f"\n{'='*70}")
            print("LOGGING SUMMARY")
            print(f"{'='*70}")
            print(f"Warnings: {self.warning_count}")
            print(f"Errors: {self.error_count}")
            
            if self.errors_by_category:
                print("\nErrors by category:")
                for category, count in sorted(self.errors_by_category.items(), key=lambda x: -x[1]):
                    print(f"  - {category}: {count}")
            
            print(f"{'='*70}\n")
    
    def close(self):
        """Close logger and cleanup resources"""
        if hasattr(self, 'audit_file'):
            self.audit_file.close()
        
        # Remove all handlers
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if exc_type:
            self.critical(f"Unhandled exception: {exc_type.__name__}: {exc_val}")
        self.close()
        return False


# Convenience function for quick logger creation
def create_logger(
    name: str = "AutoVolumeCalculator",
    log_dir: str = "logs",
    log_level: str = "INFO"
) -> ProductionLogger:
    """
    Create a production logger with default settings
    
    Example:
        logger = create_logger("MyApp", log_level="DEBUG")
        logger.info("Starting application")
        logger.log_operation("data_processing", "completed", duration_ms=1234.5)
        logger.close()
    """
    return ProductionLogger(name=name, log_dir=log_dir, log_level=log_level)


if __name__ == '__main__':
    # Demo usage
    print("Testing Production Logger...")
    
    with create_logger("TestApp", log_level="DEBUG") as logger:
        logger.info("Application started")
        logger.debug("Debug information")
        logger.warning("This is a warning")
        logger.error("File not found", category="file_io", file_path="/test/file.dxf")
        logger.log_operation("grid_detection", "completed", duration_ms=123.45, grids_found=63)
        logger.log_file_processed("test.dxf", 5242880, 2500, 150, success=True)
        logger.log_validation_error("DXFValidator", "invalid_format", "Missing required layer", "test.dxf")
        logger.print_summary()
    
    print("\n✓ Logs written to logs/ directory")
    print("  - TestApp.log (rotating file log)")
    print("  - TestApp_audit.jsonl (JSON audit trail)")
