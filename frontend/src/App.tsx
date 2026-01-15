import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { HomePage } from './pages/HomePage';
import { SiteEditPage } from './pages/SiteEditPage';
import { GlobalConfigPage } from './pages/GlobalConfigPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="sites/:siteId" element={<SiteEditPage />} />
          <Route path="config" element={<GlobalConfigPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
