"""THROWAWAY review test: a court module with a bug."""
from deck import tokens as T
def build():
    return {"jade": [f'<path d="M200 300h100v100h-100z" fill="{T.JADE}"/>']} | undefined_name  # NameError
