import os
import runpy


ROOT_STREAMLIT_APP = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "streamlit_app.py")
)

runpy.run_path(ROOT_STREAMLIT_APP, run_name="__main__")
