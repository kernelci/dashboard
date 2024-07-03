import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import "./App.css";
import Dashboard from "./components/Dashboard/Dashboard";

const queryClient = new QueryClient();

function App(): JSX.Element {
  return (
      <QueryClientProvider client={queryClient}>
      <div className="w-screen h-screen">
        <Dashboard />
      </div>
      </QueryClientProvider>
  );
}

export default App;
