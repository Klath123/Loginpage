import React, { useState, useContext } from 'react'
import axios from 'axios'
import { toast } from 'react-hot-toast'
import { useNavigate, Link } from 'react-router-dom'
import { AppContent } from '../context/appContext'

function Login() {
  const [setup, setsetup] = useState('login') 
  const [otp, setOtp] = useState('')
  const [emailForOtp, setEmailForOtp] = useState('')
  const navigate = useNavigate()
  const [data, setData] = useState({
    email: '',
    password: ''
  })

  const { backendUrl, setLoggedIn, getUserData } = useContext(AppContent)

  async function loginUser(e) {
    e.preventDefault()
    try {
      const response = await axios.post('/api/v1/auth/login', data, {
        headers: {
          'Content-Type': 'application/json'
        },
        withCredentials: true
      });

      if (response.data.success) {
        toast.success(response.data.message)
        setEmailForOtp(data.email)
        setsetup('otp')
      }
    } catch (error) {
      const message =
        error.response?.data?.detail || 'An unexpected error occurred'
      toast.error(message)
    }
  }

  async function verifyOtp(e) {
    e.preventDefault()
    try {
      const response = await axios.post('/api/v1/auth/verify-login-otp', {
        email: emailForOtp,
        otp,
      }, {
        headers: {
          'Content-Type': 'application/json',
        },
        withCredentials: true,
      })

      if (response.data.success) {
        toast.success('OTP verified. Login successful!')
        setLoggedIn(true)
        getUserData()
        navigate('/')
      }
    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to verify OTP'
      toast.error(message)
    }
  }

  return (
    <div>
      <div className="container mx-auto px-5 py-4 flex justify-between items-center my-1">
        <Link to="/" className="text-3xl font-bold tracking-tight bg-clip-text">
          QWI
        </Link>
      </div>

      <div className="mt-15 flex items-center justify-center px-4">
        <div className="bg-white rounded-xl border-black border-3 shadow-xl shadow-gray-300 p-8 w-full max-w-md">
          <h2 className="text-3xl font-bold text-center text-black mb-6">
            Sign in to your account
          </h2>

          {setup === 'login' ? (
            <form onSubmit={loginUser} className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-black mb-1">
                  Email:
                </label>
                <input
                  type="email"
                  placeholder="you@example.com"
                  value={data.email}
                  onChange={(e) => setData({ ...data, email: e.target.value })}
                  required
                  className="w-full px-4 py-2 border-1 border-black rounded-xl"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-black mb-1">
                  Password:
                </label>
                <input
                  type="password"
                  placeholder="Enter your password"
                  value={data.password}
                  onChange={(e) => setData({ ...data, password: e.target.value })}
                  required
                  className="w-full px-4 py-2 border-1 border-black rounded-xl"
                />
                <p onClick={() => navigate('/reset-password')} className='text-xs mt-2 cursor-pointer'>
                  Forgot password?
                </p>
              </div>
              <button
                type="submit"
                className="w-full bg-white hover:bg-black text-black hover:text-white font-semibold py-2 px-7 border-2 border-black rounded-xl"
              >
                Login
              </button>
            </form>
          ) : (
            <form onSubmit={verifyOtp} className="space-y-5">
              <label className="block text-sm font-medium text-black mb-1">
                Enter OTP sent to your email:
              </label>
              <input
                type="text"
                placeholder="Enter OTP"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                required
                className="w-full px-4 py-2 border-1 border-black rounded-xl"
              />
              <button
                type="submit"
                className="w-full bg-white hover:bg-black text-black hover:text-white font-semibold py-2 px-7 border-2 border-black rounded-xl"
              >
                Verify OTP
              </button>
              <p onClick={() => setsetup('login')} className="text-xs mt-2 cursor-pointer text-blue-600 hover:underline">
                Back to Login
              </p>
            </form>
          )}

          <p className="mt-4 text-center text-sm text-gray-700">
            Don't have an account?{' '}
            <Link to="/register" className="text-gray-900 hover:underline">
              Register
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default Login
