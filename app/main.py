from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from sqlalchemy import text  # Added for database testing
from . import models, schemas, auth
from .database import engine, get_db

# Create all tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Medical Resource Tracker")

# Configure CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development; change for production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Medical Resource Tracker API"}

# Updated test database connection
@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    try:
        # Use text() to properly declare the SQL expression
        db.execute(text("SELECT 1"))
        return {"message": "Database connection successful!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

# Authentication routes
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/hospital/register", response_model=schemas.User)
async def register_hospital(hospital: schemas.HospitalCreate, db: Session = Depends(get_db)):
    try:
        # Check if the hospital already exists by email
        db_hospital = db.query(models.Hospital).filter(models.Hospital.email == hospital.email).first()
        if db_hospital:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        
        # Create a new hospital with the provided details
        hashed_password = auth.get_password_hash(hospital.password)
        db_hospital = models.Hospital(
            name=hospital.name,
            hospital_type=hospital.hospital_type,
            admin_name=hospital.admin_name,
            position=hospital.position,
            email=hospital.email,
            contact_number=hospital.contact_number,
            password_hash=hashed_password,
            location=hospital.location,
            latitude=hospital.latitude,
            longitude=hospital.longitude,
            is_active=True
        )
        
        db.add(db_hospital)
        db.commit()
        db.refresh(db_hospital)
        
        return db_hospital
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while registering the hospital: {str(e)}"
        )

@router.post("/hospital/login", response_model=schemas.Token)
async def login_hospital(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Check hospital credentials using the email and password
    hospital = db.query(models.Hospital).filter(models.Hospital.email == form_data.username).first()
    if not hospital or not auth.verify_password(form_data.password, hospital.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate access token with expiration time
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": hospital.email, "type": "hospital"},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/government/login", response_model=schemas.Token)
async def login_government(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Check government official credentials
    user = db.query(models.User).filter(
        models.User.email == form_data.username,
        models.User.user_type == "government"
    ).first()
    
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate access token for government user
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email, "type": "government"},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Protected route example
@router.get("/protected")
async def protected_route(current_user = Depends(auth.get_current_user)):
    return {"message": f"Hello {current_user.email}, you have access to this protected route"}

# Include the authentication router in the FastAPI app
app.include_router(router)

# Additional routes can be added here