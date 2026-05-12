import { createRoot } from "react-dom/client";

import { AppShell } from "./components/AppShell";
import "./index.css";
import { PerformancePage } from "./pages/PerformancePage";
import { PublicationsPage } from "./pages/PublicationsPage";
import { TopicReviewPage } from "./pages/TopicReviewPage";

function App() {
  const path = window.location.pathname;
  let page = <TopicReviewPage />;
  if (path.startsWith("/publications")) {
    page = <PublicationsPage />;
  }
  if (path.startsWith("/performance")) {
    page = <PerformancePage />;
  }

  return <AppShell>{page}</AppShell>;
}

createRoot(document.getElementById("root")!).render(<App />);

