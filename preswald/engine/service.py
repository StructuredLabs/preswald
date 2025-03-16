"""
Modified service module that selects appropriate implementation
based on environment (server or browser)
"""

import logging
import sys


logger = logging.getLogger(__name__)

# Detect environment
IS_PYODIDE = "pyodide" in sys.modules

# Import appropriate implementation based on environment
if IS_PYODIDE:
    # In browser (Pyodide) environment
    from preswald.browser.virtual_service import VirtualPreswaldService as ServiceImpl

    logger.info("Using VirtualPreswaldService (Browser/Pyodide environment)")
else:
    # In regular Python environment with server capabilities
    from preswald.engine.server_service import ServerPreswaldService as ServiceImpl

    logger.info("Using ServerPreswaldService (Native Python environment)")


class PreswaldService:
    """
    Facade that forwards to the appropriate implementation based on environment.
    Maintains the same API regardless of environment.
    """

    @classmethod
    def initialize(cls, script_path=None):
        """Initialize the service"""
        return ServiceImpl.initialize(script_path)

    @classmethod
    def get_instance(cls):
        """Get the service instance"""
        return ServiceImpl.get_instance()
