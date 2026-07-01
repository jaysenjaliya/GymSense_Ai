import { AnimatePresence, motion } from "framer-motion";
import { Routes, Route, useLocation } from "react-router-dom";

import AuroraBackground from "./components/ui/AuroraBackground.jsx";
import Footer from "./components/Footer.jsx";
import Navbar from "./components/Navbar.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import Landing from "./pages/Landing.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import UploadSession from "./pages/UploadSession.jsx";
import SessionResults from "./pages/SessionResults.jsx";
import History from "./pages/History.jsx";

function Page({ children }) {
  return (
    <motion.main
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.35, ease: "easeOut" }}
      className="flex-1"
    >
      {children}
    </motion.main>
  );
}

export default function App() {
  const location = useLocation();

  return (
    <div className="flex min-h-screen flex-col">
      <AuroraBackground />
      <Navbar />

      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={<Page><Landing /></Page>} />
          <Route path="/login" element={<Page><Login /></Page>} />
          <Route path="/register" element={<Page><Register /></Page>} />
          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<Page><Dashboard /></Page>} />
            <Route path="/upload" element={<Page><UploadSession /></Page>} />
            <Route path="/sessions/:id" element={<Page><SessionResults /></Page>} />
            <Route path="/history" element={<Page><History /></Page>} />
          </Route>
        </Routes>
      </AnimatePresence>

      <Footer />
    </div>
  );
}
