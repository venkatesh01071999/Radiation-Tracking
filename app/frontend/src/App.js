import { BrowserRouter, Routes, Route } from "react-router-dom";
import LandingPage  from './Pages/LandingPage/LandingPage';


function App() {
  return (
    <BrowserRouter>
      <Routes>
          <Route path="/" element={<LandingPage />}>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
