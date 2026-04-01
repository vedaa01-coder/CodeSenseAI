import { Routes, Route } from "react-router-dom";
import AppLayout from "./layouts/app_layout.jsx";
import Home from "./pages/home.jsx";
import Chat from "./pages/chat.jsx";

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/chat" element={<Chat />} />
      </Route>
    </Routes>
  );
}