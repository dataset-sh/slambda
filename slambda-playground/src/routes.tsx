import React from "react";
import {HashRouter, Route, Routes} from "react-router-dom";
import {MainAppLayout} from "./layout/MainAppLayout";
import {LogListPage} from "./pages/LogListPage";
import {FunctionViewPage} from "./pages/FunctionViewPage";
import {HomePage} from "./pages/HomePage";

export function AppRoutes() {
    return <HashRouter>
        <Routes>
            <Route element={<MainAppLayout/>}>
                <Route index element={<HomePage/>}/>
                <Route path="/logs" element={<LogListPage/>}/>
                <Route path="/playground" element={<FunctionViewPage/>}/>
            </Route>
        </Routes>
    </HashRouter>
}
