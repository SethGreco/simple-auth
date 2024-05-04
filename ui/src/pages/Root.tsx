import { Outlet } from 'react-router-dom';

import Header from '../components/Header';

function RootLayout() {
  // const navigation = useNavigation();

  return (
    <>
      <Header />
      <main>
        {/* {navigation.state === 'loading' && <p>Loading...</p>} */}
        <Outlet />
      </main>
    </>
  );
}

export default RootLayout;