import { BrowserRouter, Routes, Route } from "react-router-dom";
import LandingPage  from './Pages/LandingPage/LandingPage';
import MapPage from "./Pages/MapPage/MapPage";


function App() {
  return (
    <BrowserRouter>
      <Routes>
          <Route path="/" element={<LandingPage />}/>
          <Route path="/map-view" element={<MapPage />}/>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
