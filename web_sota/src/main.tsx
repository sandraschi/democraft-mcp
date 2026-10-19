import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import AppLayout from "./components/AppLayout";
import Chat from "./pages/Chat";
import CraftPage from "./pages/CraftPage";
import Dashboard from "./pages/Dashboard";
import Depot from "./pages/Depot";
import HandsIn from "./pages/HandsIn";
import Help from "./pages/Help";
import Logs from "./pages/Logs";
import Onboarding from "./pages/Onboarding";
import Settings from "./pages/Settings";
import Skills from "./pages/Skills";
import Tools from "./pages/Tools";
import "./index.css";

const rootEl = document.getElementById("root");
if (!rootEl) throw new Error("missing #root");
createRoot(rootEl).render(
	<StrictMode>
		<BrowserRouter>
			<Routes>
				<Route element={<AppLayout />}>
					<Route index element={<Dashboard />} />
					<Route path="depot" element={<Depot />} />
					<Route path="inbox" element={<Navigate to="/depot" replace />} />
					<Route path="hands-in" element={<HandsIn />} />
					<Route path="tools" element={<Tools />} />
					<Route path="skills" element={<Skills />} />
					<Route path="chat" element={<Chat />} />
					<Route path="settings" element={<Settings />} />
					<Route path="help" element={<Help />} />
					<Route path="logs" element={<Logs />} />
					<Route path="onboarding" element={<Onboarding />} />
					<Route path="craft/:app" element={<CraftPage />} />
				</Route>
			</Routes>
		</BrowserRouter>
	</StrictMode>,
);
