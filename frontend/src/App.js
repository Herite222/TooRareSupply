import React, { useState, useEffect, createContext, useContext } from 'react';
import './App.css';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [sessionToken, setSessionToken] = useState(localStorage.getItem('session_token'));

  useEffect(() => {
    if (sessionToken) {
      setUser({ sessionToken });
    }
  }, [sessionToken]);

  const login = (token) => {
    localStorage.setItem('session_token', token);
    setSessionToken(token);
    setUser({ sessionToken: token });
  };

  const logout = () => {
    localStorage.removeItem('session_token');
    setSessionToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => useContext(AuthContext);

// Device Fingerprinting
const generateDeviceFingerprint = () => {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  ctx.textBaseline = 'top';
  ctx.font = '14px Arial';
  ctx.fillText('Device fingerprint', 2, 2);
  
  const fingerprint = [
    navigator.userAgent,
    navigator.language,
    screen.width + 'x' + screen.height,
    new Date().getTimezoneOffset(),
    canvas.toDataURL()
  ].join('|');
  
  return btoa(fingerprint).substring(0, 32);
};

// Components
const LandingPage = () => {
  const { user } = useAuth();
  const [categories, setCategories] = useState({});

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API}/categories`);
      setCategories(response.data);
    } catch (error) {
      console.error('Failed to fetch categories:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-300 via-gray-400 to-gray-500">
      {/* Header */}
      <header className="flex justify-between items-center p-6">
        <div className="text-3xl font-bold text-white">
          ShopLuxe
        </div>
        {!user ? (
          <AuthModal />
        ) : (
          <div className="text-white">Welcome back</div>
        )}
      </header>

      {/* Hero Section */}
      <div className="text-center py-20">
        <h1 className="text-6xl font-bold text-white mb-6">
          Luxury Redefined
        </h1>
        <p className="text-xl text-gray-200 mb-12 max-w-2xl mx-auto">
          Discover exclusive collections of premium products, designer fashion, and social media growth services
        </p>
      </div>

      {/* Product Categories */}
      <div className="max-w-7xl mx-auto px-6 pb-20">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {Object.entries(categories).map(([key, category]) => (
            <CategoryCard key={key} categoryKey={key} category={category} />
          ))}
        </div>
      </div>

      {/* Footer */}
      <Footer />
    </div>
  );
};

const CategoryCard = ({ categoryKey, category }) => {
  const [showProducts, setShowProducts] = useState(false);

  return (
    <div
      className="relative rounded-3xl overflow-hidden h-96 cursor-pointer transform hover:scale-105 transition-all duration-300 shadow-2xl"
      style={{ background: category.theme }}
      onClick={() => setShowProducts(true)}
    >
      <div className="absolute inset-0 bg-black bg-opacity-30" />
      <div className="relative z-10 p-8 h-full flex flex-col justify-end">
        <h3 className="text-3xl font-bold text-white mb-2">{category.name}</h3>
        <p className="text-gray-200 text-lg">{category.description}</p>
        <button className="mt-4 bg-white text-black px-6 py-3 rounded-full font-semibold hover:bg-gray-100 transition-colors">
          Explore Collection
        </button>
      </div>
      
      {showProducts && (
        <ProductModal categoryKey={categoryKey} onClose={() => setShowProducts(false)} />
      )}
    </div>
  );
};

const ProductModal = ({ categoryKey, onClose }) => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await axios.get(`${API}/products/${categoryKey}`);
      setProducts(response.data);
    } catch (error) {
      console.error('Failed to fetch products:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b flex justify-between items-center sticky top-0 bg-white">
          <h2 className="text-2xl font-bold">Products</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>
        
        {loading ? (
          <div className="p-8 text-center">Loading products...</div>
        ) : (
          <div className="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const ProductCard = ({ product }) => {
  const [showCheckout, setShowCheckout] = useState(false);

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
      <img
        src={product.image}
        alt={product.name}
        className="w-full h-48 object-cover"
      />
      <div className="p-4">
        <h3 className="font-bold text-lg mb-2">{product.name}</h3>
        <div className="flex items-center justify-between mb-4">
          <div>
            <span className="text-2xl font-bold text-green-600">
              ${product.final_price}
            </span>
            {product.discount > 0 && (
              <span className="text-gray-500 line-through ml-2">
                ${product.original_price}
              </span>
            )}
          </div>
          {product.discount > 0 && (
            <span className="bg-red-500 text-white px-2 py-1 rounded-full text-sm">
              {product.discount}% OFF
            </span>
          )}
        </div>
        {product.verified && (
          <div className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs inline-block mb-2">
            ✓ Verified Account
          </div>
        )}
        <button
          onClick={() => setShowCheckout(true)}
          className="w-full bg-black text-white py-3 rounded-lg font-semibold hover:bg-gray-800 transition-colors"
        >
          Buy Now
        </button>
      </div>
      
      {showCheckout && (
        <CheckoutModal
          product={product}
          onClose={() => setShowCheckout(false)}
        />
      )}
    </div>
  );
};

const CheckoutModal = ({ product, onClose }) => {
  const [paymentMethod, setPaymentMethod] = useState('card');
  const [cardInfo, setCardInfo] = useState({
    card_number: '',
    expiry_month: '',
    expiry_year: '',
    cvv: '',
    cardholder_name: '',
    save_card: true
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const orderData = {
        product_id: product.id,
        payment_method: paymentMethod,
        card_info: paymentMethod === 'card' ? cardInfo : null
      };

      const response = await axios.post(`${API}/order`, orderData);
      
      if (response.data.success) {
        setMessage('Order placed successfully! You will receive confirmation shortly.');
        if (product.is_account) {
          setMessage(prev => prev + ' Check your email within 10 minutes for account credentials.');
        }
      }
    } catch (error) {
      setMessage('Transaction failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold">Checkout</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700 text-2xl">×</button>
        </div>

        <div className="mb-4">
          <h3 className="font-semibold">{product.name}</h3>
          <p className="text-2xl font-bold text-green-600">${product.final_price}</p>
        </div>

        {message && (
          <div className={`p-3 rounded mb-4 ${message.includes('failed') ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
            {message}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Payment Method</label>
            <div className="flex space-x-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  value="card"
                  checked={paymentMethod === 'card'}
                  onChange={(e) => setPaymentMethod(e.target.value)}
                  className="mr-2"
                />
                Credit Card
              </label>
              {product.id === 'aes_002' && (
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="paypal"
                    checked={paymentMethod === 'paypal'}
                    onChange={(e) => setPaymentMethod(e.target.value)}
                    className="mr-2"
                  />
                  PayPal
                </label>
              )}
            </div>
          </div>

          {paymentMethod === 'paypal' && product.id === 'aes_002' ? (
            <div className="mb-4">
              <div id="paypal-container-BXKHDQEVHPVNC"></div>
              <script 
                src="https://www.paypal.com/sdk/js?client-id=BAAg1n9aB94U3n9jboHwjCR9R59zKGCUhjhYx25JZ9ILR1mEjHS6QyUO3MuV22QQfix7sM_Vi_WypvhyEc&components=hosted-buttons&disable-funding=venmo&currency=USD"
                onLoad={() => {
                  if (window.paypal) {
                    window.paypal.HostedButtons({
                      hostedButtonId: "BXKHDQEVHPVNC",
                    }).render("#paypal-container-BXKHDQEVHPVNC");
                  }
                }}
              />
            </div>
          ) : (
            <div className="space-y-4">
              <input
                type="text"
                placeholder="Card Number"
                value={cardInfo.card_number}
                onChange={(e) => setCardInfo({...cardInfo, card_number: e.target.value})}
                className="w-full p-3 border rounded-lg"
                required
              />
              <div className="grid grid-cols-2 gap-4">
                <input
                  type="text"
                  placeholder="MM"
                  value={cardInfo.expiry_month}
                  onChange={(e) => setCardInfo({...cardInfo, expiry_month: e.target.value})}
                  className="p-3 border rounded-lg"
                  required
                />
                <input
                  type="text"
                  placeholder="YY"
                  value={cardInfo.expiry_year}
                  onChange={(e) => setCardInfo({...cardInfo, expiry_year: e.target.value})}
                  className="p-3 border rounded-lg"
                  required
                />
              </div>
              <input
                type="text"
                placeholder="CVV"
                value={cardInfo.cvv}
                onChange={(e) => setCardInfo({...cardInfo, cvv: e.target.value})}
                className="w-full p-3 border rounded-lg"
                required
              />
              <input
                type="text"
                placeholder="Cardholder Name"
                value={cardInfo.cardholder_name}
                onChange={(e) => setCardInfo({...cardInfo, cardholder_name: e.target.value})}
                className="w-full p-3 border rounded-lg"
                required
              />
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={cardInfo.save_card}
                  onChange={(e) => setCardInfo({...cardInfo, save_card: e.target.checked})}
                  className="mr-2"
                />
                Save card for future purchases
              </label>
            </div>
          )}

          {paymentMethod === 'card' && (
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-black text-white py-3 rounded-lg font-semibold hover:bg-gray-800 transition-colors mt-6"
            >
              {loading ? 'Processing...' : `Pay $${product.final_price}`}
            </button>
          )}
        </form>
      </div>
    </div>
  );
};

const AuthModal = () => {
  const [showAuth, setShowAuth] = useState(false);
  const [isLogin, setIsLogin] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    verification_code: ''
  });
  const [message, setMessage] = useState('');
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const deviceFingerprint = generateDeviceFingerprint();

    try {
      if (isVerifying) {
        const response = await axios.post(`${API}/verify-email`, {
          email: formData.email,
          verification_code: formData.verification_code
        });
        
        if (response.data.success) {
          login(response.data.session_token);
          setShowAuth(false);
        }
      } else if (isLogin) {
        const response = await axios.post(`${API}/login`, {
          email: formData.email,
          password: formData.password,
          device_fingerprint: deviceFingerprint
        });
        
        if (response.data.success) {
          login(response.data.session_token);
          setShowAuth(false);
        }
      } else {
        const response = await axios.post(`${API}/signup`, {
          email: formData.email,
          password: formData.password,
          device_fingerprint: deviceFingerprint
        });
        
        if (response.data.success) {
          setIsVerifying(true);
          setMessage('Check your email for verification code');
        }
      }
    } catch (error) {
      setMessage(error.response?.data?.detail || 'An error occurred');
    }
  };

  if (!showAuth) {
    return (
      <button
        onClick={() => setShowAuth(true)}
        className="bg-white text-black px-6 py-3 rounded-full font-semibold hover:bg-gray-100 transition-colors"
      >
        Get Started
      </button>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold">
            {isVerifying ? 'Verify Email' : isLogin ? 'Login' : 'Sign Up'}
          </h2>
          <button onClick={() => setShowAuth(false)} className="text-gray-500 hover:text-gray-700 text-2xl">×</button>
        </div>

        {message && (
          <div className="p-3 bg-blue-100 text-blue-800 rounded mb-4">
            {message}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isVerifying && (
            <>
              <input
                type="email"
                placeholder="Email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                className="w-full p-3 border rounded-lg"
                required
              />
              <input
                type="password"
                placeholder="Password"
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
                className="w-full p-3 border rounded-lg"
                required
              />
            </>
          )}
          
          {isVerifying && (
            <input
              type="text"
              placeholder="5-digit verification code"
              value={formData.verification_code}
              onChange={(e) => setFormData({...formData, verification_code: e.target.value})}
              className="w-full p-3 border rounded-lg"
              required
            />
          )}

          <button
            type="submit"
            className="w-full bg-black text-white py-3 rounded-lg font-semibold hover:bg-gray-800 transition-colors"
          >
            {isVerifying ? 'Verify' : isLogin ? 'Login' : 'Sign Up'}
          </button>
        </form>

        {!isVerifying && (
          <div className="mt-4 text-center">
            <button
              onClick={() => setIsLogin(!isLogin)}
              className="text-blue-600 hover:underline"
            >
              {isLogin ? 'Need an account? Sign up' : 'Already have an account? Login'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

const Footer = () => {
  const [showAffiliate, setShowAffiliate] = useState(false);

  return (
    <>
      <footer className="bg-black text-white py-12">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-xl font-bold mb-4">ShopLuxe</h3>
              <p className="text-gray-400">Luxury redefined for the modern lifestyle</p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Terms of Service</a></li>
                <li><a href="#" className="hover:text-white">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-white">Contact</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Partnerships</h4>
              <button
                onClick={() => setShowAffiliate(true)}
                className="text-yellow-400 hover:text-yellow-300 font-semibold"
              >
                Become an Affiliate
              </button>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Follow Us</h4>
              <div className="flex space-x-4 text-gray-400">
                <a href="#" className="hover:text-white">Instagram</a>
                <a href="#" className="hover:text-white">Twitter</a>
              </div>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2025 ShopLuxe. All rights reserved.</p>
          </div>
        </div>
      </footer>

      {showAffiliate && (
        <AffiliateModal onClose={() => setShowAffiliate(false)} />
      )}
    </>
  );
};

const AffiliateModal = ({ onClose }) => {
  const [formData, setFormData] = useState({
    email: '',
    paypal_email: ''
  });
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API}/affiliate/signup`, formData);
      if (response.data.success) {
        setMessage(`Success! Your affiliate code is: ${response.data.affiliate_code}`);
      }
    } catch (error) {
      setMessage(error.response?.data?.detail || 'An error occurred');
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold">Join Affiliate Program</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700 text-2xl">×</button>
        </div>

        {message && (
          <div className={`p-3 rounded mb-4 ${message.includes('Success') ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
            {message}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            placeholder="Your Email"
            value={formData.email}
            onChange={(e) => setFormData({...formData, email: e.target.value})}
            className="w-full p-3 border rounded-lg"
            required
          />
          <input
            type="email"
            placeholder="PayPal Email for Payouts"
            value={formData.paypal_email}
            onChange={(e) => setFormData({...formData, paypal_email: e.target.value})}
            className="w-full p-3 border rounded-lg"
            required
          />

          <div className="bg-blue-50 p-4 rounded-lg text-sm">
            <h4 className="font-semibold mb-2">Commission Structure:</h4>
            <ul className="text-gray-600 space-y-1">
              <li>• 4% base commission per sale</li>
              <li>• +1% bonus for every 10 confirmed sales</li>
              <li>• 30-day cookie tracking</li>
              <li>• Weekly payouts available</li>
            </ul>
          </div>

          <button
            type="submit"
            className="w-full bg-black text-white py-3 rounded-lg font-semibold hover:bg-gray-800 transition-colors"
          >
            Join Program
          </button>
        </form>
      </div>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <div className="App">
        <LandingPage />
      </div>
    </AuthProvider>
  );
}

export default App;