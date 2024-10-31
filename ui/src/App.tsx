import Home from './pages/Home';
import Login from './pages/Login';
import User from './pages/User';
import { RouterProvider, createBrowserRouter } from 'react-router-dom';
import Root from './pages/Root';
import Error from './pages/Error';
import ProtectedRoute from './components/ProtectedRoute';
import { getAuthToken } from './services/authService';




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
        element: <ProtectedRoute />,
        children: [
          {
            path: '/user',
            element: <User />,
            loader: getAuthToken
          },
        ]
      },

    ],
  },
]);

function App() {
  return <RouterProvider router={router} />;
}

export default App;
