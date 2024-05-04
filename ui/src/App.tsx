import React from 'react';
import Home from './pages/Home';
import Login from './pages/Login';
import User from './pages/User';
import { isAuthenticated } from './services/authService';
import { RouterProvider, createBrowserRouter } from 'react-router-dom';
import Root from './pages/Root';
import Error from './pages/Error';




const router = createBrowserRouter([
  {
    path: '/',
    element: <Root />,
    errorElement: <Error />,
    children: [
      {
        path: '/home',
        element: <Home />,
      },
      {
        path: '/login',
        element: <Login />,
      },
      {
        path: '/user',
        element: <User />,
        loader: isAuthenticated
      },
    ],
  },
]);

function App() {
  return <RouterProvider router={router} />;
}

export default App;
