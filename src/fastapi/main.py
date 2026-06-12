import base64
import pandas as pd
from fastapi import FastAPI, HTTPException, Header
from typing import List, Optional
from pydantic import BaseModel
import os

# Initialize FastAPI app
app = FastAPI(
    title="Questions API",
    description="API pour générer des QCMs aléatoires",
    version="1.0.0"
)

# User credentials
USERS = {
    "alice": "wonderland",
    "bob": "builder",
    "clementine": "mandarine"
}

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "4dm1N"

# CSV file path
CSV_PATH = os.path.join(os.path.dirname(__file__), "questions.csv")

# Global dataframe
df = None


def load_questions_csv():
    """Charge le fichier CSV des questions."""
    global df
    df = pd.read_csv(CSV_PATH)
    return df


if df is None:
    load_questions_csv()


def authenticate_basic_auth(authorization: Optional[str] = Header(None)) -> str:
    """
    Vérifie l'authentification basique à partir du header Authorization.
    Retourne le username si valide, sinon lève une HTTPException 401.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    if not authorization.startswith("Basic "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    try:
        # Extraire la partie encodée en Base64
        encoded_credentials = authorization.split(" ")[1]
        # Décoder
        decoded = base64.b64decode(encoded_credentials).decode("utf-8")
        username, password = decoded.split(":", 1)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    # Vérifier les credentials
    if username not in USERS or USERS[username] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return username


def authenticate_admin(admin_username: str, admin_password: str) -> bool:
    """Vérifie les credentials admin."""
    return admin_username == ADMIN_USERNAME and admin_password == ADMIN_PASSWORD


# Pydantic models
class GenerateQuizRequest(BaseModel):
    test_type: str
    categories: List[str]
    number_of_questions: int


class CreateQuestionRequest(BaseModel):
    admin_username: str
    admin_password: str
    question: str
    subject: str
    correct: str  # Garder les lettres (A, B, C, D)
    use: str
    responseA: str
    responseB: str
    responseC: str
    responseD: Optional[str] = None


# Endpoints

@app.on_event("startup")
async def startup_event():
    """Charge le CSV au démarrage de l'application."""
    load_questions_csv()


@app.get("/verify")
async def verify():
    """Vérifie que l'API est fonctionnelle."""
    return {"message": "L'API est fonctionnelle."}


@app.post("/generate_quiz")
async def generate_quiz(
    request: GenerateQuizRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Génère un QCM basé sur les paramètres fournis.
    Nécessite l'authentification basique.
    """
    # Authentification
    username = authenticate_basic_auth(authorization)
    
    # Valider number_of_questions
    if request.number_of_questions not in [5, 10, 20]:
        raise HTTPException(
            status_code=400,
            detail="number_of_questions doit être 5, 10 ou 20"
        )
    
    # Filtrer les questions
    # Filtrer par test_type (colonne 'use')
    filtered = df[df['use'] == request.test_type]
    
    # Filtrer par catégories (colonne 'subject')
    filtered = filtered[filtered['subject'].isin(request.categories)]
    
    # Vérifier qu'il y a assez de questions
    if len(filtered) < request.number_of_questions:
        raise HTTPException(
            status_code=400,
            detail=f"Pas assez de questions disponibles. Demandé: {request.number_of_questions}, Disponible: {len(filtered)}"
        )
    
    # Sélectionner aléatoirement les questions
    selected = filtered.sample(n=request.number_of_questions, random_state=None)
    
    # Convertir en liste de dictionnaires
    questions = selected.to_dict('records')
    
    # Nettoyer les valeurs NaN (remplacer par None ou chaîne vide)
    for q in questions:
        for key, value in q.items():
            if pd.isna(value):
                q[key] = None
    
    return questions


@app.post("/create_question")
async def create_question(request: CreateQuestionRequest):
    """
    Crée une nouvelle question (admin uniquement).
    """
    # Vérifier les credentials admin
    if not authenticate_admin(request.admin_username, request.admin_password):
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    
    # Ajouter à la liste globale
    global df

    # Vérifier si la question existe déjà
    if any(df['question'].astype(str).str.strip().str.lower() == request.question.strip().lower()):
        raise HTTPException(status_code=400, detail="La question existe déjà")
    
    # Préparer la nouvelle ligne
    new_question = {
        "question": request.question,
        "subject": request.subject,
        "use": request.use,
        "correct": request.correct,
        "responseA": request.responseA,
        "responseB": request.responseB,
        "responseC": request.responseC,
        "responseD": request.responseD,
        "remark": ""  # Ajouter une colonne vide pour 'remark'
    }
    
    df = pd.concat([df, pd.DataFrame([new_question])], ignore_index=True)
    
    # Sauvegarder dans le CSV
    df.to_csv(CSV_PATH, index=False)
    
    return {"message": "Question créée avec succès."}
