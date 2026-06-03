import os
# Professional Fix: Force pure Python implementation of protobuf globally
# This must be set before any module importing protobuf is loaded.
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

# Logic package for LPU Chatbot
