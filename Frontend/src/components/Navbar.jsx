import React,{ useContext} from 'react'
import { Link } from 'react-router-dom'
import arrow from '../assets/arrow.svg'
import { useNavigate } from 'react-router-dom'
import { AppContent } from '../context/appContext'
import axios from 'axios'
import { toast } from 'react-hot-toast'


function Navbar() {
  const navigate = useNavigate()
  const { userData, setUserData, setLoggedIn } = useContext(AppContent)
  const sendVerificationOtp = async ()=>{
    try{

    const {data}= await axios.get('/api/v1/auth/send-email',
      {withCredentials: true,
  })
  if(data.success)
  {
    navigate('/email-verify')
    toast.success(data.message)
  }
}
catch(error)
{
  const message =error.response?.data?.detail || 'An unexpected error occurred';
       toast.error(message);
}
  }
  const logout = async ()=>{
    try{
        const {data} = await axios.get('/api/v1/auth/logout',{
          withCredentials: true,
        })
        data.success && setLoggedIn(false)
        data.success && setUserData(false)
        navigate('/')
    }
    catch(error){
      const message =error.response?.data?.detail || 'An unexpected error occurred';
       toast.error(message);
    }
  }
  return (
   <nav >
  <div className="container mx-auto px-5 py-4 flex justify-between items-center border-4 border-black my-1.5 rounded-2xl">
    <Link
      to="/"
      className="text-3xl font-bold tracking-tight bg-clip-text"
    >
      QWI
    </Link>
    {userData ? (
         <div className="relative group text-xl font-medium cursor-pointer select-none">
  <div className="w-10 h-10 rounded-full bg-black text-white flex items-center justify-center">
    {userData.name?.[0]?.toUpperCase()}
  </div>
  <div className="absolute right-0 mt-2 w-40 bg-white border text-lg border-gray-200 rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transform scale-95 group-hover:scale-100 transition duration-200 z-10">
    <ul className="py-2">
      {!userData.isVerified &&
      <li className="px-4 py-2 hover:bg-gray-100 cursor-pointer transition" onClick={sendVerificationOtp}>Verify Email</li>
      }
      <li onClick={logout} className="px-4 py-2 hover:bg-gray-100 cursor-pointer transition">Logout</li>
    </ul>
  </div>
</div>
        ) : (
          <div className="flex space-x-4">
            <Link 
              to="/login"
              className="group flex items-center px-4 py-1.5 rounded-full text-black font-medium transition duration-150 shadow-md border-3 border-black hover:bg-black hover:text-white"
            >
              Login
            </Link>
          </div>
        )}
    </div>
</nav>

  )
}

export default Navbar
