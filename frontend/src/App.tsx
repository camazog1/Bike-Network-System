import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import Home from './features/Home';
import Auth from './features/Auth';
import Register from './features/Auth/components/Register';
import Bikes from './features/Bikes';
import BikeCreate from './features/Bikes/components/BikeCreate';
import BikeEdit from './features/Bikes/components/BikeEdit';
import Map from './features/Map';
import AppLayout from './layout/AppLayout';
import PublicLayout from './layout/PublicLayout';
import ProtectedRoute from './common/components/ProtectedRoute';

const router = createBrowserRouter([
  {
    element: <PublicLayout />,
    children: [
      { path: '/', element: <Home /> },
      { path: '/login', element: <Auth /> },
      { path: '/register', element: <Register /> },
    ],
  },
  {
    element: <AppLayout />,
    children: [
      {
        element: <ProtectedRoute />,
        children: [
          { path: '/bikes', element: <Bikes /> },
          { path: '/bikes/new', element: <BikeCreate /> },
          { path: '/bikes/:id/edit', element: <BikeEdit /> },
          { path: '/map', element: <Map /> },
        ],
      },
    ],
  },
  {
    path: '*',
    element: (
      <div className="p-12 text-center">
        <h1 className="text-3xl font-semibold text-text mb-4">Page not found</h1>
        <p className="text-text-muted">
          <a href="/" className="text-brand-500 hover:text-brand-600">Go home</a>
        </p>
      </div>
    ),
  },
]);

export default function App() {
  return <RouterProvider router={router} />;
}
