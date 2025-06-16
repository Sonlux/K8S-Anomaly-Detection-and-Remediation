import { Route, Routes } from "react-router-dom";
import Dashboard from "./pages/DASHBOARD";
import Anomalies from "./pages/ANOMALIES";
import Remediations from "./pages/REMEDIATIONS";
import Insights from "./pages/INSIGHTS";
import Login from "./pages/LOGIN";
import Layout from "./components/Layout";
import Clusters from "./pages/CLUSTERS";
import Pods from "./pages/PODS";
import Settings from "./pages/SETTINGS";
import Chatbot from "./components/CHATBOT"; // Adjust path as needed
import { AnomalyProvider } from "./context/AnomalyContext";
import Nodes from "./pages/NODES";
function App() {
  return (
    <AnomalyProvider>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="anomalies" element={<Anomalies />} />
          <Route path="nodes" element={<Nodes />} />
          <Route path="clusters" element={<Clusters />} />
          <Route path="pods" element={<Pods />} />
          <Route path="settings" element={<Settings />} />
          <Route path="remediations" element={<Remediations />} />
          <Route path="insights" element={<Insights />} />
        </Route>
      </Routes>
    </AnomalyProvider>
  );
}

export default App;
