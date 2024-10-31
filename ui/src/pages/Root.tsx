import { Outlet } from 'react-router-dom';

import Header from '../components/Header';
// import AuthProvider from '../AuthProvider';

function RootLayout() {
  // const navigation = useNavigation();

  return (
    <>
    {/* <AuthProvider> */}
      <Header />
      <main>
        {/* {navigation.state === 'loading' && <p>Loading...</p>} */}
        <Outlet />
      </main>
      {/* </AuthProvider> */}
    </>
  );
}

export default RootLayout;
