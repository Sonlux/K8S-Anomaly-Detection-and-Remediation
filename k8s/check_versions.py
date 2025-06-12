import sys
import os

# Open a file to write the output
with open('d:\\kubernetes\\k8s\\version_info.txt', 'w') as f:
    f.write(f"Python version: {sys.version}\n")
    f.write(f"Python executable: {sys.executable}\n")

    try:
        import numpy as np
        f.write(f"NumPy version: {np.__version__}\n")
    except ImportError:
        f.write("NumPy is not installed\n")
    except Exception as e:
        f.write(f"Error importing NumPy: {e}\n")

    try:
        import pandas as pd
        f.write(f"Pandas version: {pd.__version__}\n")
    except ImportError:
        f.write("Pandas is not installed\n")
    except Exception as e:
        f.write(f"Error importing Pandas: {e}\n")

    try:
        import chromadb
        f.write(f"ChromaDB version: {chromadb.__version__}\n")
    except ImportError:
        f.write("ChromaDB is not installed\n")
    except Exception as e:
        f.write(f"Error importing ChromaDB: {e}\n")

    try:
        from sentence_transformers import SentenceTransformer
        f.write("Sentence-Transformers is installed\n")
    except ImportError:
        f.write("Sentence-Transformers is not installed\n")
    except Exception as e:
        f.write(f"Error importing Sentence-Transformers: {e}\n")

    f.write("\nInstalled packages:\n")
    # Get the list of installed packages and write to file
    import subprocess
    result = subprocess.run([sys.executable, '-m', 'pip', 'list'], capture_output=True, text=True)
    f.write(result.stdout)

print(f"Version information written to d:\\kubernetes\\k8s\\version_info.txt")