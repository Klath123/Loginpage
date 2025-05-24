import React,{useState,useContext,useEffect} from 'react'
import { useNavigate, Link}  from 'react-router-dom'
import { toast } from 'react-hot-toast'
import axios from 'axios'
import { AppContent } from '../context/appContext'

function EmailVerify() {
    const [otp, setOtp] = useState('')
    const navigate = useNavigate()
      const {backendUrl,getUserData,isLoggedin,userData} = useContext(AppContent)
  const onSubmitHandle = async (e)=>{
    e.preventDefault()
        try {
      const { data } = await axios.post(
        '/api/v1/auth/verify-email',
        { otp },
        { withCredentials: true }
      )
      getUserData()
       toast.success(data.message);
       navigate('/')
    }
    catch(error)
    {
        const message = error.response?.data?.detail || 'An unexpected error occurred';
                    toast.error(message);
                    console.log(message)
    }

  }
 
  useEffect(()=>{
    // isLoggedin && userData && userData.isAccountVerified && navigate('/')
  if (!isLoggedin || !userData) return;

  if (userData.isAccountVerified) {
    navigate('/');
  }
  },[isLoggedin,userData,navigate])

  return (
    <div>
      <div className="container mx-auto px-5 py-4 flex justify-between items-center   my-1 ">
          <Link
            to="/"
            className="text-3xl font-bold tracking-tight bg-clip-text"
          >
            QWI
          </Link>
    </div>
    <div className="mt-20 flex items-center justify-center bg-gray-50 px-4">
      <div className="bg-white border-2 border-black shadow-lg shadow-gray-300 rounded-2xl p-10 w-full max-w-md">
        <h1 className="text-3xl font-bold text-center mb-6">Enter Verification Code</h1>
        <p className="text-center text-gray-700 mb-6">
          We've sent a 6-digit code to your email. Please enter it below to verify your account.
        </p>
        <form className="space-y-5" onSubmit={onSubmitHandle}>
          <input
            type="text"
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
            maxLength={6}
            pattern="\d{6}"
            className="w-full px-4 py-2 text-center text-xl tracking-widest border-2 border-black rounded-xl focus:outline-none focus:ring-2"
            placeholder="••••••"
            required
          />
          <button
            type="submit"
            className="w-full bg-white hover:bg-black text-black hover:text-white font-semibold py-2 px-6 border-2 border-black rounded-xl transition duration-200"
          >
            Verify
          </button>
        </form>
      </div>
    </div>
 </div>
  )
}

export default EmailVerify
