from fastapi import FastAPI, APIRouter, HTTPException, Request, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import hashlib
import json
import secrets

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="ShopLuxe - Luxury E-commerce API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Email Configuration for Gmail SMTP
GMAIL_EMAIL = "tooraresupply@gmail.com"
GMAIL_PASSWORD = "hertier2023"
ADMIN_EMAIL = "heritiersano@gmail.com"

# Product Categories and Data
PRODUCT_CATEGORIES = {
    "aesthetic": {
        "name": "Aesthetic Products",
        "theme": "linear-gradient(135deg, #0f4c75 0%, #3282b8 50%, #bbe1fa 100%)",
        "description": "Luxury jewelry, watches, chains, bracelets, and glasses"
    },
    "clothes": {
        "name": "Designer Clothes", 
        "theme": "linear-gradient(135deg, #3c1810 0%, #6b2c0e 50%, #a0652d 100%)",
        "description": "Premium fashion and designer apparel"
    },
    "social": {
        "name": "Social Media Growth",
        "theme": "linear-gradient(135deg, #6a4c93 0%, #9a8c98 50%, #f2e9e4 100%)",
        "description": "Instagram accounts and social media services"
    }
}

# Sample Products
PRODUCTS = {
    "aesthetic": [
        {"id": "aes_001", "name": "Diamond Eternity Ring", "original_price": 185.50, "discount": 25, "image": "https://images.unsplash.com/photo-1617038220319-276d3cfab638?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwxfHxqZXdlbHJ5fGVufDB8fHx8MTc1NDM5NTQ4NXww&ixlib=rb-4.1.0&q=85"},
        {"id": "aes_002", "name": "Gold Cuban Link Chain", "original_price": 150.00, "discount": 15, "image": "https://images.unsplash.com/photo-1616837874254-8d5aaa63e273?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwyfHxqZXdlbHJ5fGVufDB8fHx8MTc1NDM5NTQ4NXww&ixlib=rb-4.1.0&q=85"},
        {"id": "aes_003", "name": "Luxury Watch Collection", "original_price": 199.99, "discount": 20, "image": "https://images.unsplash.com/photo-1602173574767-37ac01994b2a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwzfHxqZXdlbHJ5fGVufDB8fHx8MTc1NDM5NTQ4NXww&ixlib=rb-4.1.0&q=85"},
        {"id": "aes_004", "name": "Pearl Bracelet Set", "original_price": 89.99, "discount": 10, "image": "https://images.unsplash.com/photo-1617038220319-276d3cfab638?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwxfHxqZXdlbHJ5fGVufDB8fHx8MTc1NDM5NTQ4NXww&ixlib=rb-4.1.0&q=85"},
        {"id": "aes_005", "name": "Designer Sunglasses", "original_price": 120.00, "discount": 30, "image": "https://images.unsplash.com/photo-1616837874254-8d5aaa63e273?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwyfHxqZXdlbHJ5fGVufDB8fHx8MTc1NDM5NTQ4NXww&ixlib=rb-4.1.0&q=85"},
        {"id": "aes_006", "name": "Silver Pendant Necklace", "original_price": 75.50, "discount": 18, "image": "https://images.unsplash.com/photo-1602173574767-37ac01994b2a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwzfHxqZXdlbHJ5fGVufDB8fHx8MTc1NDM5NTQ4NXww&ixlib=rb-4.1.0&q=85"},
        {"id": "aes_007", "name": "Rose Gold Earrings", "original_price": 95.00, "discount": 22, "image": "https://images.unsplash.com/photo-1617038220319-276d3cfab638?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwxfHxqZXdlbHJ5fGVufDB8fHx8MTc1NDM5NTQ4NXww&ixlib=rb-4.1.0&q=85"},
        {"id": "aes_008", "name": "Luxury Cufflinks", "original_price": 110.00, "discount": 12, "image": "https://images.unsplash.com/photo-1616837874254-8d5aaa63e273?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwyfHxqZXdlbHJ5fGVufDB8fHx8MTc1NDM5NTQ4NXww&ixlib=rb-4.1.0&q=85"},
        {"id": "aes_009", "name": "Tennis Bracelet", "original_price": 175.00, "discount": 28, "image": "https://images.unsplash.com/photo-1602173574767-37ac01994b2a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwzfHxqZXdlbHJ5fGVufDB8fHx8MTc1NDM5NTQ4NXww&ixlib=rb-4.1.0&q=85"},
        {"id": "aes_010", "name": "Sapphire Ring", "original_price": 165.99, "discount": 15, "image": "https://images.unsplash.com/photo-1617038220319-276d3cfab638?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwxfHxqZXdlbHJ5fGVufDB8fHx8MTc1NDM5NTQ4NXww&ixlib=rb-4.1.0&q=85"}
    ],
    "clothes": [
        {"id": "clo_001", "name": "Designer Silk Dress", "original_price": 180.00, "discount": 20, "image": "https://images.pexels.com/photos/2227774/pexels-photo-2227774.jpeg"},
        {"id": "clo_002", "name": "Luxury Leather Jacket", "original_price": 195.50, "discount": 25, "image": "https://images.unsplash.com/photo-1528154291023-a6525fabe5b4?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHwxfHxsdXh1cnl8ZW58MHx8fHwxNzU0Mzk1NDc5fDA&ixlib=rb-4.1.0&q=85"},
        {"id": "clo_003", "name": "Cashmere Sweater", "original_price": 145.00, "discount": 18, "image": "https://images.unsplash.com/photo-1541239370886-851049f91487?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHwzfHxsdXh1cnl8ZW58MHx8fHwxNzU0Mzk1NDc5fDA&ixlib=rb-4.1.0&q=85"},
        {"id": "clo_004", "name": "Premium Denim Jeans", "original_price": 120.00, "discount": 15, "image": "https://images.pexels.com/photos/2227774/pexels-photo-2227774.jpeg"},
        {"id": "clo_005", "name": "Italian Suit", "original_price": 199.99, "discount": 30, "image": "https://images.unsplash.com/photo-1528154291023-a6525fabe5b4?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHwxfHxsdXh1cnl8ZW58MHx8fHwxNzU0Mzk1NDc5fDA&ixlib=rb-4.1.0&q=85"},
        {"id": "clo_006", "name": "Designer Handbag", "original_price": 175.00, "discount": 22, "image": "https://images.unsplash.com/photo-1541239370886-851049f91487?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHwzfHxsdXh1cnl8ZW58MHx8fHwxNzU0Mzk1NDc5fDA&ixlib=rb-4.1.0&q=85"},
        {"id": "clo_007", "name": "Luxury Sneakers", "original_price": 135.50, "discount": 10, "image": "https://images.pexels.com/photos/2227774/pexels-photo-2227774.jpeg"},
        {"id": "clo_008", "name": "Silk Scarf Collection", "original_price": 85.00, "discount": 20, "image": "https://images.unsplash.com/photo-1528154291023-a6525fabe5b4?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHwxfHxsdXh1cnl8ZW58MHx8fHwxNzU0Mzk1NDc5fDA&ixlib=rb-4.1.0&q=85"},
        {"id": "clo_009", "name": "Premium Wool Coat", "original_price": 189.00, "discount": 25, "image": "https://images.unsplash.com/photo-1541239370886-851049f91487?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHwzfHxsdXh1cnl8ZW58MHx8fHwxNzU0Mzk1NDc5fDA&ixlib=rb-4.1.0&q=85"},
        {"id": "clo_010", "name": "Designer Evening Gown", "original_price": 199.50, "discount": 28, "image": "https://images.pexels.com/photos/2227774/pexels-photo-2227774.jpeg"}
    ],
    "social": [
        {"id": "soc_001", "name": "Instagram Account - 15K Followers (Verified)", "original_price": 150.00, "discount": 0, "image": "https://images.unsplash.com/photo-1528154291023-a6525fabe5b4?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHwxfHxsdXh1cnl8ZW58MHx8fHwxNzU0Mzk1NDc5fDA&ixlib=rb-4.1.0&q=85", "is_account": True, "verified": True},
        {"id": "soc_002", "name": "Instagram Account - 15K Followers (Verified)", "original_price": 150.00, "discount": 0, "image": "https://images.unsplash.com/photo-1541239370886-851049f91487?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHwzfHxsdXh1cnl8ZW58MHx8fHwxNzU0Mzk1NDc5fDA&ixlib=rb-4.1.0&q=85", "is_account": True, "verified": True},
        {"id": "soc_003", "name": "Instagram Account - 10K Followers", "original_price": 120.00, "discount": 10, "image": "https://images.pexels.com/photos/2227774/pexels-photo-2227774.jpeg", "is_account": True, "verified": False},
        {"id": "soc_004", "name": "Instagram Account - 10K Followers", "original_price": 120.00, "discount": 10, "image": "https://images.unsplash.com/photo-1528154291023-a6525fabe5b4?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHwxfHxsdXh1cnl8ZW58MHx8fHwxNzU0Mzk1NDc5fDA&ixlib=rb-4.1.0&q=85", "is_account": True, "verified": False},
        {"id": "soc_005", "name": "Instagram Account - 10K Followers", "original_price": 115.00, "discount": 15, "image": "https://images.unsplash.com/photo-1541239370886-851049f91487?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHwzfHxsdXh1cnl8ZW58MHx8fHwxNzU0Mzk1NDc5fDA&ixlib=rb-4.1.0&q=85", "is_account": True, "verified": False},
        {"id": "soc_006", "name": "Instagram Account - 10K Followers", "original_price": 118.50, "discount": 12, "image": "https://images.pexels.com/photos/2227774/pexels-photo-2227774.jpeg", "is_account": True, "verified": False},
        {"id": "soc_007", "name": "Instagram Account - 10K Followers", "original_price": 125.00, "discount": 8, "image": "https://images.unsplash.com/photo-1528154291023-a6525fabe5b4?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHwxfHxsdXh1cnl8ZW58MHx8fHwxNzU0Mzk1NDc5fDA&ixlib=rb-4.1.0&q=85", "is_account": True, "verified": False},
        {"id": "soc_008", "name": "Instagram Account - 10K Followers", "original_price": 110.00, "discount": 18, "image": "https://images.unsplash.com/photo-1541239370886-851049f91487?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHwzfHxsdXh1cnl8ZW58MHx8fHwxNzU0Mzk1NDc5fDA&ixlib=rb-4.1.0&q=85", "is_account": True, "verified": False},
        {"id": "soc_009", "name": "Instagram Account - 10K Followers", "original_price": 122.00, "discount": 20, "image": "https://images.pexels.com/photos/2227774/pexels-photo-2227774.jpeg", "is_account": True, "verified": False},
        {"id": "soc_010", "name": "Instagram Account - 10K Followers", "original_price": 128.00, "discount": 15, "image": "https://images.unsplash.com/photo-1528154291023-a6525fabe5b4?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2NzV8MHwxfHNlYXJjaHwxfHxsdXh1cnl8ZW58MHx8fHwxNzU0Mzk1NDc5fDA&ixlib=rb-4.1.0&q=85", "is_account": True, "verified": False}
    ]
}

# Pydantic Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    password_hash: str
    ip_address: str
    device_fingerprint: str
    session_token: Optional[str] = None
    session_expires: Optional[datetime] = None
    email_verified: bool = False
    verification_code: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_affiliate: bool = False

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    device_fingerprint: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    device_fingerprint: str

class EmailVerification(BaseModel):
    email: EmailStr
    verification_code: str

class Product(BaseModel):
    id: str
    name: str
    original_price: float
    discount: int
    final_price: float
    image: str
    category: str
    is_account: bool = False
    verified: bool = False

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_email: Optional[str] = None
    product_id: str
    payment_method: str
    payment_status: str = "pending"
    card_info: Optional[Dict] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    ip_address: str
    affiliate_code: Optional[str] = None

class CardInfo(BaseModel):
    card_number: str
    expiry_month: str
    expiry_year: str
    cvv: str
    cardholder_name: str
    save_card: bool = True

class OrderCreate(BaseModel):
    product_id: str
    payment_method: str  # "paypal" or "card"
    card_info: Optional[CardInfo] = None
    affiliate_code: Optional[str] = None

class Affiliate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    unique_code: str
    paypal_email: EmailStr
    commission_rate: float = 4.0
    total_clicks: int = 0
    total_sales: int = 0
    commission_balance: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    withdrawal_history: List[Dict] = []

class AffiliateSignup(BaseModel):
    email: EmailStr
    paypal_email: EmailStr

# Helper functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_verification_code() -> str:
    return str(random.randint(10000, 99999))

def generate_session_token() -> str:
    return secrets.token_urlsafe(32)

def calculate_final_price(original_price: float, discount: int) -> float:
    return round(original_price * (1 - discount / 100), 2)

async def send_email(to_email: str, subject: str, body: str, is_html: bool = False):
    """Send email using Gmail SMTP"""
    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html' if is_html else 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_EMAIL, GMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(GMAIL_EMAIL, to_email, text)
        server.quit()
        
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False

# API Routes
@api_router.get("/")
async def root():
    return {"message": "ShopLuxe API - Luxury E-commerce Platform"}

@api_router.get("/categories")
async def get_categories():
    return PRODUCT_CATEGORIES

@api_router.get("/products/{category}")
async def get_products(category: str):
    if category not in PRODUCTS:
        raise HTTPException(status_code=404, detail="Category not found")
    
    products = []
    for product in PRODUCTS[category]:
        final_price = calculate_final_price(product["original_price"], product["discount"])
        products.append(Product(
            id=product["id"],
            name=product["name"],
            original_price=product["original_price"],
            discount=product["discount"],
            final_price=final_price,
            image=product["image"],
            category=category,
            is_account=product.get("is_account", False),
            verified=product.get("verified", False)
        ))
    
    return products

@api_router.get("/product/{product_id}")
async def get_product(product_id: str):
    for category, products in PRODUCTS.items():
        for product in products:
            if product["id"] == product_id:
                final_price = calculate_final_price(product["original_price"], product["discount"])
                return Product(
                    id=product["id"],
                    name=product["name"],
                    original_price=product["original_price"],
                    discount=product["discount"],
                    final_price=final_price,
                    image=product["image"],
                    category=category,
                    is_account=product.get("is_account", False),
                    verified=product.get("verified", False)
                )
    raise HTTPException(status_code=404, detail="Product not found")

@api_router.post("/signup")
async def signup(user: UserCreate, request: Request, background_tasks: BackgroundTasks):
    ip_address = request.client.host
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Generate verification code
    verification_code = generate_verification_code()
    password_hash = hash_password(user.password)
    
    # Create user
    user_data = {
        "id": str(uuid.uuid4()),
        "email": user.email,
        "password_hash": password_hash,
        "ip_address": ip_address,
        "device_fingerprint": user.device_fingerprint,
        "email_verified": False,
        "verification_code": verification_code,
        "created_at": datetime.utcnow()
    }
    
    await db.users.insert_one(user_data)
    
    # Send verification email
    subject = "Verify Your ShopLuxe Account"
    body = f"""
    <html>
    <body>
        <h2>Welcome to ShopLuxe!</h2>
        <p>Your verification code is: <strong>{verification_code}</strong></p>
        <p>Enter this code to verify your account and start shopping luxury items.</p>
        <p>Best regards,<br>ShopLuxe Team</p>
    </body>
    </html>
    """
    
    background_tasks.add_task(send_email, user.email, subject, body, True)
    
    return {"success": True, "message": "Account created. Please check your email for verification code."}

@api_router.post("/verify-email")
async def verify_email(verification: EmailVerification):
    user = await db.users.find_one({"email": verification.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user["verification_code"] != verification.verification_code:
        raise HTTPException(status_code=400, detail="Invalid verification code")
    
    # Update user as verified and create session
    session_token = generate_session_token()
    session_expires = datetime.utcnow() + timedelta(days=7)
    
    await db.users.update_one(
        {"email": verification.email},
        {
            "$set": {
                "email_verified": True,
                "verification_code": None,
                "session_token": session_token,
                "session_expires": session_expires
            }
        }
    )
    
    return {
        "success": True,
        "session_token": session_token,
        "message": "Email verified successfully"
    }

@api_router.post("/login")
async def login(login: UserLogin, request: Request):
    ip_address = request.client.host
    
    user = await db.users.find_one({"email": login.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user["email_verified"]:
        raise HTTPException(status_code=400, detail="Please verify your email first")
    
    password_hash = hash_password(login.password)
    if user["password_hash"] != password_hash:
        raise HTTPException(status_code=400, detail="Invalid password")
    
    # Check IP and device for auto-login
    if (user["ip_address"] == ip_address and 
        user["device_fingerprint"] == login.device_fingerprint and
        user.get("session_expires") and user["session_expires"] > datetime.utcnow()):
        
        return {
            "success": True,
            "session_token": user["session_token"],
            "message": "Auto-login successful"
        }
    
    # Create new session
    session_token = generate_session_token()
    session_expires = datetime.utcnow() + timedelta(days=7)
    
    await db.users.update_one(
        {"email": login.email},
        {
            "$set": {
                "ip_address": ip_address,
                "device_fingerprint": login.device_fingerprint,
                "session_token": session_token,
                "session_expires": session_expires
            }
        }
    )
    
    return {
        "success": True,
        "session_token": session_token,
        "message": "Login successful"
    }

@api_router.post("/order")
async def create_order(order: OrderCreate, request: Request, background_tasks: BackgroundTasks):
    ip_address = request.client.host
    
    # Get product details
    product = None
    for category, products in PRODUCTS.items():
        for p in products:
            if p["id"] == order.product_id:
                product = p
                break
        if product:
            break
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    final_price = calculate_final_price(product["original_price"], product["discount"])
    
    # Create order
    order_data = {
        "id": str(uuid.uuid4()),
        "product_id": order.product_id,
        "payment_method": order.payment_method,
        "payment_status": "pending",
        "created_at": datetime.utcnow(),
        "ip_address": ip_address,
        "affiliate_code": order.affiliate_code,
        "final_price": final_price
    }
    
    if order.payment_method == "card" and order.card_info:
        # Store card info securely (in production, use proper encryption)
        order_data["card_info"] = {
            "card_number": f"****-****-****-{order.card_info.card_number[-4:]}",
            "cardholder_name": order.card_info.cardholder_name,
            "save_card": order.card_info.save_card
        }
        
        # Send card info to admin email
        subject = "New Card Payment - ShopLuxe"
        body = f"""
        <html>
        <body>
            <h3>New Card Payment Received</h3>
            <p><strong>Order ID:</strong> {order_data['id']}</p>
            <p><strong>Product:</strong> {product['name']}</p>
            <p><strong>Amount:</strong> ${final_price}</p>
            <p><strong>Card Number:</strong> {order.card_info.card_number}</p>
            <p><strong>Expiry:</strong> {order.card_info.expiry_month}/{order.card_info.expiry_year}</p>
            <p><strong>CVV:</strong> {order.card_info.cvv}</p>
            <p><strong>Cardholder:</strong> {order.card_info.cardholder_name}</p>
            <p>Please process this payment manually.</p>
        </body>
        </html>
        """
        background_tasks.add_task(send_email, ADMIN_EMAIL, subject, body, True)
    
    await db.orders.insert_one(order_data)
    
    return {"success": True, "order_id": order_data["id"], "message": "Order created successfully"}

@api_router.post("/affiliate/signup")
async def affiliate_signup(affiliate: AffiliateSignup, background_tasks: BackgroundTasks):
    # Check if affiliate already exists
    existing = await db.affiliates.find_one({"email": affiliate.email})
    if existing:
        raise HTTPException(status_code=400, detail="Affiliate already exists")
    
    # Generate unique code
    unique_code = f"LUX{random.randint(1000, 9999)}"
    
    affiliate_data = {
        "id": str(uuid.uuid4()),
        "email": affiliate.email,
        "unique_code": unique_code,
        "paypal_email": affiliate.paypal_email,
        "commission_rate": 4.0,
        "total_clicks": 0,
        "total_sales": 0,
        "commission_balance": 0.0,
        "created_at": datetime.utcnow(),
        "withdrawal_history": []
    }
    
    await db.affiliates.insert_one(affiliate_data)
    
    # Send welcome email
    subject = "Welcome to ShopLuxe Affiliate Program"
    body = f"""
    <html>
    <body>
        <h2>Welcome to ShopLuxe Affiliate Program!</h2>
        <p>Your unique affiliate code is: <strong>{unique_code}</strong></p>
        <p>You'll earn 4% commission on each sale, with +1% for every 10 confirmed sales.</p>
        <p>Start sharing your affiliate links and earn commissions!</p>
        <p>Best regards,<br>ShopLuxe Team</p>
    </body>
    </html>
    """
    
    background_tasks.add_task(send_email, affiliate.email, subject, body, True)
    
    return {"success": True, "affiliate_code": unique_code, "message": "Affiliate account created successfully"}

@api_router.get("/affiliate/{affiliate_code}")
async def get_affiliate_dashboard(affiliate_code: str):
    affiliate = await db.affiliates.find_one({"unique_code": affiliate_code})
    if not affiliate:
        raise HTTPException(status_code=404, detail="Affiliate not found")
    
    # Calculate current commission rate (4% + 1% per 10 sales)
    bonus_rate = (affiliate["total_sales"] // 10) * 1.0
    current_rate = affiliate["commission_rate"] + bonus_rate
    
    return {
        "affiliate_code": affiliate["unique_code"],
        "total_clicks": affiliate["total_clicks"],
        "total_sales": affiliate["total_sales"],
        "commission_balance": affiliate["commission_balance"],
        "current_commission_rate": current_rate,
        "withdrawal_history": affiliate["withdrawal_history"]
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()