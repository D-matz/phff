#uvicorn potatoemr:app
#uvicorn potatoemr:app --reload

from app import app
from pages import calendar, index, lists, registerPatient, settings
from pages.patient import allergy, demographics, immunizations, overview, photo