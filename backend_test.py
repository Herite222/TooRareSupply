#!/usr/bin/env python3
"""
ShopLuxe Backend API Testing Suite
Tests all core functionality including authentication, products, orders, and affiliate system
"""

import requests
import json
import time
import random
import string
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')
BASE_URL = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BASE_URL}/api"

class ShopLuxeAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.test_email = f"test_{random.randint(1000, 9999)}@luxetest.com"
        self.test_password = "TestPassword123!"
        self.device_fingerprint = self.generate_device_fingerprint()
        self.session_token = None
        self.verification_code = None
        
    def generate_device_fingerprint(self):
        """Generate a unique device fingerprint for testing"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    
    def log_test(self, test_name, success, message, response_data=None):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'response_data': response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if response_data and not success:
            print(f"   Response: {response_data}")
    
    def test_health_check(self):
        """Test GET /api/ - Basic health check"""
        try:
            response = self.session.get(f"{API_BASE}/")
            if response.status_code == 200:
                data = response.json()
                if "ShopLuxe" in data.get("message", ""):
                    self.log_test("Health Check", True, "API is responding correctly", data)
                    return True
                else:
                    self.log_test("Health Check", False, "Unexpected response message", data)
                    return False
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_get_categories(self):
        """Test GET /api/categories - Fetch product categories"""
        try:
            response = self.session.get(f"{API_BASE}/categories")
            if response.status_code == 200:
                data = response.json()
                expected_categories = ["aesthetic", "clothes", "social"]
                
                if all(cat in data for cat in expected_categories):
                    # Check category structure
                    for cat in expected_categories:
                        if not all(key in data[cat] for key in ["name", "theme", "description"]):
                            self.log_test("Get Categories", False, f"Missing keys in {cat} category", data)
                            return False
                    
                    self.log_test("Get Categories", True, "All categories returned with correct structure", data)
                    return True
                else:
                    self.log_test("Get Categories", False, "Missing expected categories", data)
                    return False
            else:
                self.log_test("Get Categories", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Get Categories", False, f"Error: {str(e)}")
            return False
    
    def test_get_products_by_category(self):
        """Test GET /api/products/{category} - Get products for each category"""
        categories = ["aesthetic", "clothes", "social"]
        all_passed = True
        
        for category in categories:
            try:
                response = self.session.get(f"{API_BASE}/products/{category}")
                if response.status_code == 200:
                    data = response.json()
                    
                    if len(data) == 10:  # Should have 10 products each
                        # Check product structure
                        required_fields = ["id", "name", "original_price", "discount", "final_price", "image", "category"]
                        
                        for product in data:
                            if not all(field in product for field in required_fields):
                                self.log_test(f"Get Products - {category}", False, f"Missing fields in product", product)
                                all_passed = False
                                continue
                            
                            # Verify pricing calculation
                            expected_final = round(product["original_price"] * (1 - product["discount"] / 100), 2)
                            if abs(product["final_price"] - expected_final) > 0.01:
                                self.log_test(f"Get Products - {category}", False, f"Incorrect price calculation for {product['name']}", product)
                                all_passed = False
                                continue
                            
                            # Verify discount doesn't exceed 30%
                            if product["discount"] > 30:
                                self.log_test(f"Get Products - {category}", False, f"Discount exceeds 30% for {product['name']}", product)
                                all_passed = False
                                continue
                        
                        # Special checks for social category (Instagram accounts)
                        if category == "social":
                            verified_accounts = [p for p in data if p.get("verified", False)]
                            if len(verified_accounts) >= 2:
                                self.log_test(f"Get Products - {category}", True, f"Found {len(verified_accounts)} verified Instagram accounts")
                            else:
                                self.log_test(f"Get Products - {category}", False, f"Expected at least 2 verified accounts, found {len(verified_accounts)}")
                                all_passed = False
                        
                        if all_passed:
                            self.log_test(f"Get Products - {category}", True, f"All 10 products returned with correct structure and pricing")
                    else:
                        self.log_test(f"Get Products - {category}", False, f"Expected 10 products, got {len(data)}", data)
                        all_passed = False
                else:
                    self.log_test(f"Get Products - {category}", False, f"HTTP {response.status_code}", response.text)
                    all_passed = False
            except Exception as e:
                self.log_test(f"Get Products - {category}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_get_individual_product(self):
        """Test GET /api/product/{product_id} - Get individual product details"""
        test_products = ["aes_002", "clo_001", "soc_001"]  # Cuban Link Chain, Designer Silk Dress, Verified Instagram
        all_passed = True
        
        for product_id in test_products:
            try:
                response = self.session.get(f"{API_BASE}/product/{product_id}")
                if response.status_code == 200:
                    data = response.json()
                    
                    required_fields = ["id", "name", "original_price", "discount", "final_price", "image", "category"]
                    if all(field in data for field in required_fields):
                        # Verify pricing calculation
                        expected_final = round(data["original_price"] * (1 - data["discount"] / 100), 2)
                        if abs(data["final_price"] - expected_final) > 0.01:
                            self.log_test(f"Get Product - {product_id}", False, f"Incorrect price calculation", data)
                            all_passed = False
                        else:
                            # Special check for Cuban Link Chain (aes_002) - should support PayPal
                            if product_id == "aes_002" and "Cuban Link Chain" in data["name"]:
                                self.log_test(f"Get Product - {product_id}", True, f"Cuban Link Chain found: {data['name']}")
                            else:
                                self.log_test(f"Get Product - {product_id}", True, f"Product details correct: {data['name']}")
                    else:
                        self.log_test(f"Get Product - {product_id}", False, f"Missing required fields", data)
                        all_passed = False
                else:
                    self.log_test(f"Get Product - {product_id}", False, f"HTTP {response.status_code}", response.text)
                    all_passed = False
            except Exception as e:
                self.log_test(f"Get Product - {product_id}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_user_signup(self):
        """Test POST /api/signup - User registration"""
        try:
            payload = {
                "email": self.test_email,
                "password": self.test_password,
                "device_fingerprint": self.device_fingerprint
            }
            
            response = self.session.post(f"{API_BASE}/signup", json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "verification code" in data.get("message", "").lower():
                    self.log_test("User Signup", True, "User registered successfully, verification email sent", data)
                    return True
                else:
                    self.log_test("User Signup", False, "Unexpected response format", data)
                    return False
            else:
                self.log_test("User Signup", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("User Signup", False, f"Error: {str(e)}")
            return False
    
    def test_duplicate_signup(self):
        """Test duplicate email signup should fail"""
        try:
            payload = {
                "email": self.test_email,
                "password": self.test_password,
                "device_fingerprint": self.device_fingerprint
            }
            
            response = self.session.post(f"{API_BASE}/signup", json=payload)
            if response.status_code == 400:
                data = response.json()
                if "already registered" in data.get("detail", "").lower():
                    self.log_test("Duplicate Signup Prevention", True, "Correctly prevented duplicate registration", data)
                    return True
                else:
                    self.log_test("Duplicate Signup Prevention", False, "Wrong error message", data)
                    return False
            else:
                self.log_test("Duplicate Signup Prevention", False, f"Expected HTTP 400, got {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Duplicate Signup Prevention", False, f"Error: {str(e)}")
            return False
    
    def test_email_verification(self):
        """Test POST /api/verify-email - Email verification with 5-digit code"""
        # Since we can't access the actual email, we'll test with a mock code
        # In a real scenario, you'd extract the code from the email
        test_codes = ["12345", "54321", "99999"]  # Try common test codes
        
        for code in test_codes:
            try:
                payload = {
                    "email": self.test_email,
                    "verification_code": code
                }
                
                response = self.session.post(f"{API_BASE}/verify-email", json=payload)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success") and data.get("session_token"):
                        self.session_token = data["session_token"]
                        self.log_test("Email Verification", True, f"Email verified with code {code}, session token received", data)
                        return True
                elif response.status_code == 400:
                    # Invalid code, try next one
                    continue
                else:
                    self.log_test("Email Verification", False, f"HTTP {response.status_code}", response.text)
                    return False
            except Exception as e:
                self.log_test("Email Verification", False, f"Error: {str(e)}")
                return False
        
        # If no test codes work, we'll simulate success for testing purposes
        self.log_test("Email Verification", False, "Could not verify with test codes (expected in test environment)")
        return False
    
    def test_user_login(self):
        """Test POST /api/login - User login with IP-locking and session management"""
        try:
            payload = {
                "email": self.test_email,
                "password": self.test_password,
                "device_fingerprint": self.device_fingerprint
            }
            
            response = self.session.post(f"{API_BASE}/login", json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("session_token"):
                    self.session_token = data["session_token"]
                    self.log_test("User Login", True, "Login successful, session token received", data)
                    return True
                else:
                    self.log_test("User Login", False, "Missing session token in response", data)
                    return False
            elif response.status_code == 400:
                data = response.json()
                if "verify your email" in data.get("detail", "").lower():
                    self.log_test("User Login", True, "Correctly blocked unverified user login", data)
                    return True
                else:
                    self.log_test("User Login", False, f"Unexpected error: {data.get('detail')}", data)
                    return False
            else:
                self.log_test("User Login", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("User Login", False, f"Error: {str(e)}")
            return False
    
    def test_create_order_paypal(self):
        """Test POST /api/order - Order creation with PayPal"""
        try:
            payload = {
                "product_id": "aes_002",  # Cuban Link Chain - should support PayPal
                "payment_method": "paypal"
            }
            
            response = self.session.post(f"{API_BASE}/order", json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("order_id"):
                    self.log_test("Create Order - PayPal", True, f"PayPal order created successfully: {data['order_id']}", data)
                    return True
                else:
                    self.log_test("Create Order - PayPal", False, "Missing order_id in response", data)
                    return False
            else:
                self.log_test("Create Order - PayPal", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Create Order - PayPal", False, f"Error: {str(e)}")
            return False
    
    def test_create_order_card(self):
        """Test POST /api/order - Order creation with card info"""
        try:
            payload = {
                "product_id": "aes_001",  # Diamond Eternity Ring
                "payment_method": "card",
                "card_info": {
                    "card_number": "4532123456789012",
                    "expiry_month": "12",
                    "expiry_year": "2025",
                    "cvv": "123",
                    "cardholder_name": "John Doe",
                    "save_card": True
                }
            }
            
            response = self.session.post(f"{API_BASE}/order", json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("order_id"):
                    self.log_test("Create Order - Card", True, f"Card order created successfully: {data['order_id']}", data)
                    return True
                else:
                    self.log_test("Create Order - Card", False, "Missing order_id in response", data)
                    return False
            else:
                self.log_test("Create Order - Card", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Create Order - Card", False, f"Error: {str(e)}")
            return False
    
    def test_affiliate_signup(self):
        """Test POST /api/affiliate/signup - Affiliate program registration"""
        try:
            affiliate_email = f"affiliate_{random.randint(1000, 9999)}@luxetest.com"
            payload = {
                "email": affiliate_email,
                "paypal_email": f"paypal_{random.randint(1000, 9999)}@luxetest.com"
            }
            
            response = self.session.post(f"{API_BASE}/affiliate/signup", json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("affiliate_code"):
                    self.affiliate_code = data["affiliate_code"]
                    if self.affiliate_code.startswith("LUX"):
                        self.log_test("Affiliate Signup", True, f"Affiliate registered with code: {self.affiliate_code}", data)
                        return True
                    else:
                        self.log_test("Affiliate Signup", False, f"Invalid affiliate code format: {self.affiliate_code}", data)
                        return False
                else:
                    self.log_test("Affiliate Signup", False, "Missing affiliate_code in response", data)
                    return False
            else:
                self.log_test("Affiliate Signup", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Affiliate Signup", False, f"Error: {str(e)}")
            return False
    
    def test_affiliate_dashboard(self):
        """Test GET /api/affiliate/{affiliate_code} - Affiliate dashboard data"""
        if not hasattr(self, 'affiliate_code'):
            self.log_test("Affiliate Dashboard", False, "No affiliate code available from signup test")
            return False
        
        try:
            response = self.session.get(f"{API_BASE}/affiliate/{self.affiliate_code}")
            if response.status_code == 200:
                data = response.json()
                required_fields = ["affiliate_code", "total_clicks", "total_sales", "commission_balance", "current_commission_rate"]
                
                if all(field in data for field in required_fields):
                    # Verify commission rate calculation (4% base + 1% per 10 sales)
                    expected_rate = 4.0 + (data["total_sales"] // 10) * 1.0
                    if abs(data["current_commission_rate"] - expected_rate) < 0.01:
                        self.log_test("Affiliate Dashboard", True, f"Dashboard data correct, commission rate: {data['current_commission_rate']}%", data)
                        return True
                    else:
                        self.log_test("Affiliate Dashboard", False, f"Incorrect commission rate calculation", data)
                        return False
                else:
                    self.log_test("Affiliate Dashboard", False, "Missing required fields in dashboard", data)
                    return False
            else:
                self.log_test("Affiliate Dashboard", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Affiliate Dashboard", False, f"Error: {str(e)}")
            return False
    
    def test_order_with_affiliate(self):
        """Test order creation with affiliate code"""
        if not hasattr(self, 'affiliate_code'):
            self.log_test("Order with Affiliate", False, "No affiliate code available")
            return False
        
        try:
            payload = {
                "product_id": "soc_001",  # Instagram account
                "payment_method": "paypal",
                "affiliate_code": self.affiliate_code
            }
            
            response = self.session.post(f"{API_BASE}/order", json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("order_id"):
                    self.log_test("Order with Affiliate", True, f"Order with affiliate code created: {data['order_id']}", data)
                    return True
                else:
                    self.log_test("Order with Affiliate", False, "Missing order_id in response", data)
                    return False
            else:
                self.log_test("Order with Affiliate", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Order with Affiliate", False, f"Error: {str(e)}")
            return False
    
    def test_invalid_endpoints(self):
        """Test error handling for invalid endpoints"""
        test_cases = [
            (f"{API_BASE}/products/invalid_category", 404),
            (f"{API_BASE}/product/invalid_product", 404),
            (f"{API_BASE}/affiliate/INVALID123", 404)
        ]
        
        all_passed = True
        for endpoint, expected_status in test_cases:
            try:
                response = self.session.get(endpoint)
                if response.status_code == expected_status:
                    self.log_test(f"Error Handling - {endpoint.split('/')[-1]}", True, f"Correctly returned HTTP {expected_status}")
                else:
                    self.log_test(f"Error Handling - {endpoint.split('/')[-1]}", False, f"Expected {expected_status}, got {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_test(f"Error Handling - {endpoint.split('/')[-1]}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print(f"\n🚀 Starting ShopLuxe Backend API Tests")
        print(f"📍 Testing against: {API_BASE}")
        print(f"📧 Test email: {self.test_email}")
        print(f"🔑 Device fingerprint: {self.device_fingerprint[:16]}...")
        print("=" * 80)
        
        # Core API Tests
        print("\n📋 CORE API ENDPOINTS")
        self.test_health_check()
        self.test_get_categories()
        self.test_get_products_by_category()
        self.test_get_individual_product()
        
        # Authentication Tests
        print("\n🔐 AUTHENTICATION FLOW")
        self.test_user_signup()
        self.test_duplicate_signup()
        self.test_email_verification()
        self.test_user_login()
        
        # E-commerce Tests
        print("\n🛒 E-COMMERCE FEATURES")
        self.test_create_order_paypal()
        self.test_create_order_card()
        
        # Affiliate Tests
        print("\n💰 AFFILIATE SYSTEM")
        self.test_affiliate_signup()
        self.test_affiliate_dashboard()
        self.test_order_with_affiliate()
        
        # Error Handling Tests
        print("\n⚠️  ERROR HANDLING")
        self.test_invalid_endpoints()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {total - passed}")
        print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
        
        print("\n" + "=" * 80)
        return passed, total

if __name__ == "__main__":
    tester = ShopLuxeAPITester()
    passed, total = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if passed == total else 1)