import React from 'react';
import './App.css';
import {AppRoutes} from "./routes";
import {QueryClient, QueryClientProvider} from "@tanstack/react-query";
import {AppContextProvider} from "./features";
import {createTheme, ThemeProvider} from "@mui/material";
import {green, red} from "@mui/material/colors";

const queryClient = new QueryClient()

const theme = createTheme({
        palette: {
            primary: {
                main: '#00a1ff',
            },
            secondary: {
                main: '#dddddd',
            },
            info: {
                main: '#000000',
            },
            success: {
                main: green[500],
            },
            error: {
                main: red[500],
            },

        },
    }
);


function App() {
    return (
        <QueryClientProvider client={queryClient}>
            <AppContextProvider>
                <ThemeProvider theme={theme}>
                    <AppRoutes/>
                </ThemeProvider>
            </AppContextProvider>
        </QueryClientProvider>
    );
}

export default App;
