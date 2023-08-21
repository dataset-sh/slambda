import React from 'react';
import './App.css';
import {AppRoutes} from "./routes";
import {QueryClient, QueryClientProvider} from "@tanstack/react-query";
import {AppContextProvider} from "./features";

const queryClient = new QueryClient()

function App() {
    return (
        <QueryClientProvider client={queryClient}>
            <AppContextProvider>
                <AppRoutes/>
            </AppContextProvider>
        </QueryClientProvider>
    );
}

export default App;
