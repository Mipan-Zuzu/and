import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import Dashboard from './Components/dashboard/index'
import Login from './Components/loginPage/login/login'

const router = createBrowserRouter([
  {
    path: "/",
    element : <Login/>
  },
  {
    path: "/dashboard",
    element : <Dashboard/>
  },
])

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)
